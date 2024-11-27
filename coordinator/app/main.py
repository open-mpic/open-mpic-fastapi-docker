import sys
from os.path import dirname
sys.path.append(dirname(__file__) + "/open_mpic_core_python/src")

from fastapi import FastAPI

from importlib import resources

import yaml
from pydantic import TypeAdapter, ValidationError
from open_mpic_core.common_domain.check_request import BaseCheckRequest
from open_mpic_core.common_domain.check_response import CheckResponse
from open_mpic_core.mpic_coordinator.domain.mpic_request import MpicRequest
from open_mpic_core.mpic_coordinator.domain.mpic_request_validation_error import MpicRequestValidationError
from open_mpic_core.mpic_coordinator.mpic_coordinator import MpicCoordinator, MpicCoordinatorConfiguration
from open_mpic_core.common_domain.enum.check_type import CheckType
from open_mpic_core.common_domain.remote_perspective import RemotePerspective

import requests
import random
import os
import json


class MpicCoordinatorLambdaHandler:
    def __init__(self):
        # load environment variables
        self.all_target_perspectives = os.environ['perspective_names'].split("|")
        self.dcv_remotes = json.loads(os.environ['dcv_remotes'])
        self.caa_remotes = json.loads(os.environ['caa_remotes'])
        self.default_perspective_count = int(os.environ['default_perspective_count'])
        self.enforce_distinct_rir_regions = int(os.environ['enforce_distinct_rir_regions']) == 1  # TODO may not need...
        self.global_max_attempts = int(os.environ['absolute_max_attempts']) if 'absolute_max_attempts' in os.environ else None
        self.hash_secret = os.environ['hash_secret']

        self.remotes_per_perspective_per_check_type = {
            CheckType.DCV: {self.all_target_perspectives[i]: self.dcv_remotes[i] for i in range(len(self.all_target_perspectives))},
            CheckType.CAA: {self.all_target_perspectives[i]: self.caa_remotes[i] for i in range(len(self.all_target_perspectives))}
        }

        all_target_perspective_codes = self.all_target_perspectives
        all_possible_perspectives_by_code = MpicCoordinatorLambdaHandler.load_aws_region_config()
        self.target_perspectives = MpicCoordinatorLambdaHandler.convert_codes_to_remote_perspectives(
            all_target_perspective_codes, all_possible_perspectives_by_code)

        self.mpic_coordinator_configuration = MpicCoordinatorConfiguration(
            self.target_perspectives,
            self.default_perspective_count,
            self.enforce_distinct_rir_regions,
            self.global_max_attempts,
            self.hash_secret
        )

        self.mpic_coordinator = MpicCoordinator(
            self.call_remote_perspective,
            self.mpic_coordinator_configuration
        )

        # for correct deserialization of responses based on discriminator field (check type)
        self.mpic_request_adapter = TypeAdapter(MpicRequest)
        self.check_response_adapter = TypeAdapter(CheckResponse)

    @staticmethod
    def load_aws_region_config() -> dict[str, RemotePerspective]:
        """
        Reads in the available perspectives from a configuration yaml and returns them as a dict (map).
        :return: dict of available perspectives with region code as key
        """
        with open("./available_perspectives.yaml") as file:
            aws_region_config_yaml = yaml.safe_load(file)
            aws_region_type_adapter = TypeAdapter(list[RemotePerspective])
            aws_regions_list = aws_region_type_adapter.validate_python(aws_region_config_yaml['available_regions'])
            aws_regions_dict = {region.code: region for region in aws_regions_list}
            return aws_regions_dict

    @staticmethod
    def convert_codes_to_remote_perspectives(perspective_codes: list[str],
                                             all_possible_perspectives_by_code: dict[str, RemotePerspective]) -> list[RemotePerspective]:
        remote_perspectives = []

        for perspective_code in perspective_codes:
            if perspective_code not in all_possible_perspectives_by_code.keys():
                continue  # TODO throw an error? check this case in the validator?
            else:
                fully_defined_perspective = all_possible_perspectives_by_code[perspective_code]
                remote_perspectives.append(fully_defined_perspective)

        return remote_perspectives

    # This function MUST validate its response and return a proper open_mpic_core object type.
    def call_remote_perspective(self, perspective: RemotePerspective, check_type: CheckType, check_request: BaseCheckRequest) -> CheckResponse:


        ## Uses dcv_arn_list, caa_arn_list
        #client = boto3.client('lambda', perspective.code)


        # Get the remote info from the data structure.
        remote_info = self.remotes_per_perspective_per_check_type[check_type][perspective.code]

        # Shuffle to pick a random endpoint order.
        if len(remote_info) > 1:
            print("shuffling")
            random.shuffle(remote_info)

        for endpoint_info in remote_info:
            try:
                url = endpoint_info['url']
                headers = {}
                if 'headers' in endpoint_info:
                    headers = endpoint_info['headers']

                r = requests.post(url, headers=headers, json=check_request.model_dump())

                return self.check_response_adapter.validate_json(r.text)
            except requests.exceptions.RequestException as e:
                print(traceback.format_exc())
                continue
            except ValidationError as e:
                print(traceback.format_exc())
                continue
        #response = client.invoke(  # AWS Lambda-specific structure
        #        FunctionName=function_name,
        #        InvocationType='RequestResponse',
        #        Payload=check_request.model_dump_json()  # AWS Lambda functions expect a JSON string for payload
        #    )
        #response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        #try:
        #    return self.check_response_adapter.validate_json(response_payload['body'])
        #except ValidationError as ve:
        #    # We might want to handle this differently later.
        #    raise ve

    def process_invocation(self, mpic_request: MpicRequest) -> dict:
        return self.mpic_coordinator.coordinate_mpic(mpic_request)
        #try:
        #    mpic_response = self.mpic_coordinator.coordinate_mpic(mpic_request)
        #    return {
        #        'statusCode': 200,
        #        'headers': {'Content-Type': 'application/json'},
        #        'body': mpic_response.model_dump_json()
        #    }
        #except MpicRequestValidationError as e:  # TODO catch ALL exceptions here?
        #    return {
        #        'statusCode': 500,
        #        'headers': {'Content-Type': 'application/json'},
        #        'body': json.dumps({'error': str(e)})
        #    }


# Global instance for Lambda runtime
_handler = None


def get_handler() -> MpicCoordinatorLambdaHandler:
    """
    Singleton pattern to avoid recreating the handler on every Lambda invocation
    """
    global _handler
    if _handler is None:
        _handler = MpicCoordinatorLambdaHandler()
    return _handler


# TODO We need to find a way to bring back transparent error messages with this new parsing model.
#      If the parsing to the MPIC request fails, it returns system internal server errors instead of returning
#      the pydantic error message.
# noinspection PyUnusedLocal
# for now, we are not using context, but it is required by the lambda handler signature
#@event_parser(model=MpicRequest, envelope=envelopes.ApiGatewayEnvelope)  # AWS Lambda Powertools decorator
#def lambda_handler(event: MpicRequest, context):  # AWS Lambda entry point
#    return get_handler().process_invocation(event)


app = FastAPI()

@app.post("/mpic")
def perform_mpic(request: MpicRequest):
    return get_handler().process_invocation(request)



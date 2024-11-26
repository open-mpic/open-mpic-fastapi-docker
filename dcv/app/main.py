import sys
from os.path import dirname
sys.path.append(dirname(__file__) + "/open_mpic_core_python/src")

from fastapi import FastAPI

from open_mpic_core.common_domain.check_request import DcvCheckRequest
from open_mpic_core.common_domain.remote_perspective import RemotePerspective
from open_mpic_core.mpic_dcv_checker.mpic_dcv_checker import MpicDcvChecker
import os


class MpicDcvCheckerLambdaHandler:
    def __init__(self):
        self.perspective = RemotePerspective(rir=os.environ['rir_region'], code=os.environ['code'])
        self.dcv_checker = MpicDcvChecker(self.perspective)

    def process_invocation(self, dcv_request: DcvCheckRequest):
        return self.dcv_checker.check_dcv(dcv_request)
        #status_code = 200
        #if dcv_response.errors is not None and len(dcv_response.errors) > 0:
        #    if dcv_response.errors[0].error_type == '404':
        #        status_code = 404
        #    else:
        #        status_code = 500
        #result = {
        #    'statusCode': status_code,
        #    'headers': {'Content-Type': 'application/json'},
        #    'body': dcv_response.model_dump_json()
        #}
        #return result


# Global instance for Lambda runtime
_handler = None


def get_handler() -> MpicDcvCheckerLambdaHandler:
    """
    Singleton pattern to avoid recreating the handler on every Lambda invocation
    """
    global _handler
    if _handler is None:
        _handler = MpicDcvCheckerLambdaHandler()
    return _handler


# noinspection PyUnusedLocal
# for now, we are not using context, but it is required by the lambda handler signature
def lambda_handler(event, context):  # AWS Lambda entry point
    return get_handler().process_invocation(event)

app = FastAPI()

@app.post("/dcv")
def perform_mpic(request: DcvCheckRequest):
    return get_handler().process_invocation(request)



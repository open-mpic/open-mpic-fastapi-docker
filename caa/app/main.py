import sys
from os.path import dirname
sys.path.append(dirname(__file__) + "/open_mpic_core_python/src")

from fastapi import FastAPI # type: ignore

from open_mpic_core.common_domain.check_request import CaaCheckRequest
from open_mpic_core.common_domain.remote_perspective import RemotePerspective
from open_mpic_core.mpic_caa_checker.mpic_caa_checker import MpicCaaChecker
import os


class MpicCaaCheckerLambdaHandler:
    def __init__(self):
        self.perspective = RemotePerspective(rir=os.environ['rir_region'], code=os.environ['code'])
        self.default_caa_domain_list = os.environ['default_caa_domains'].split("|")
        self.caa_checker = MpicCaaChecker(self.default_caa_domain_list, self.perspective)

    def process_invocation(self, caa_request: CaaCheckRequest):
        return self.caa_checker.check_caa(caa_request)
        #result = {
        #    'statusCode': 200,  # note: must be snakeCase
        #    'headers': {'Content-Type': 'application/json'},
        #    'body': caa_response.model_dump_json()
        #}
        #return result


# Global instance for Lambda runtime
_handler = None


def get_handler() -> MpicCaaCheckerLambdaHandler:
    """
    Singleton pattern to avoid recreating the handler on every Lambda invocation
    """
    global _handler
    if _handler is None:
        _handler = MpicCaaCheckerLambdaHandler()
    return _handler


app = FastAPI()

@app.post("/caa")
def perform_mpic(request: CaaCheckRequest):
    return get_handler().process_invocation(request)



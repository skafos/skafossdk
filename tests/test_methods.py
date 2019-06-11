import skafos
from skafos import models
from skafos.http import generate_required_params
from constants import *

PARAMS = {
    'skafos_api_token': TESTING_API_TOKEN,
    'org_name': TESTING_ORG,
    'app_name': TESTING_APP
}

class TestMethods(object):

    def test_version(self):
        v = skafos.get_version()
        assert isinstance(v, str)

    # Test generating required PARAMS
    def test_generate_params(self):
        required_keys = ["app_name", "org_name", "app_name", "model_name"]
        res = generate_required_params({**PARAMS, **{"model_name": "test_model"}})
        # Check for required keys
        assert all(key in res.keys() for key in required_keys)

    def test_compact_summary(self):
        response = skafos.summary(skafos_api_token=TESTING_API_TOKEN, compact=True)
        # Check response type
        assert isinstance(response, dict)

    def test_full_summary(self):
        required_keys = ["org_name", "app_name", "model_name"]
        response = skafos.summary(skafos_api_token=TESTING_API_TOKEN, compact=False)
        # Check response type
        assert isinstance(response, list)
        # Check nested response type
        assert isinstance(response[0], dict)
        # Check for all required keys
        assert all(key in response[0].keys() for key in required_keys)

    def test_list_versions(self):
        res = models.list_versions(
            model_name=TESTING_MODEL,
            **PARAMS
        )
        # Check response type and verfiy that something comes back from the testing app/model
        assert isinstance(res, list)
        assert len(res) >= 1

    def test_list_versions_empty(self):
        res = models.list_versions(
            model_name=TESTING_MODEL_EMPTY,
            **PARAMS
        )
        # Check response type and verfiy that nothing comes back
        assert isinstance(res, list)
        assert len(res) == 0

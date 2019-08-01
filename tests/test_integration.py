import pytest
import skafos
from skafos import models
from skafos.exceptions import *
from constants import *


PARAMS = {
    'skafos_api_token': TESTING_API_TOKEN,
    'org_name': TESTING_ORG,
    'app_name': TESTING_APP
}


class TestIntegration(object):

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

    def test_model_version_deploy(self):
        res = models.deploy_version(
                model_name=TESTING_MODEL,
                **PARAMS
            )

        assert isinstance(res, type(None))

    def test_list_environments(self):
        res = models.list_environments(
            model_name=TESTING_MODEL,
            **PARAMS
        )

        expected_environments = ["dev", "prod"]
        found_expected_environments = []

        for environment in res: 
            env_name = environment['name'].lower()
            if env_name in expected_environments:
                found_expected_environments.append(env_name)
      
        # Check response type and verfiy that at least dev and prod environment groups come back from testing app/model
        assert isinstance(res, list)
        assert len(res) >= 2
        assert expected_environments.sort() == found_expected_environments.sort()

    # Test another token error by using a fake token
    def test_summary_invalid_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary(skafos_api_token=TESTING_FAKE_TOKEN)

    # Test a failing deploy due to nonexistent environment
    def test_failed_deploy(self):
        with pytest.raises(DeployFailedError):
            models.deploy_version(
                environment="staging",
                model_name=TESTING_MODEL,
                **PARAMS
            )

    # Test a failing download due to empty model version
    def test_fetch_failed_download(self):
        with pytest.raises(DownloadFailedError):
            models.fetch_version(
                model_name=TESTING_MODEL_EMPTY,
                **PARAMS
            )

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

class TestExceptions(object):
    # Test a token error
    def test_missing_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary()

    # Test another token error
    def test_invalid_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary(skafos_api_token=TESTING_FAKE_TOKEN)

    # Test missing param error
    def test_missing_param(self):
        with pytest.raises(InvalidParamError):
            models.upload_version(files="", skafos_api_token=TESTING_FAKE_TOKEN)

    # Test a failing download due to empty model version
    def test_failed_fetch(self):
        with pytest.raises(DownloadFailedError):
            res = models.fetch_version(
                model_name=TESTING_MODEL_EMPTY,
                **PARAMS
            )

    # Test a failed upload due to invalid (fake) file
    def test_invalid_file_upload(self):
        with pytest.raises(InvalidParamError):
            res = models.upload_version(
                files=TESTING_FAKE_FILE,
                model_name=TESTING_MODEL,
                **PARAMS
            )

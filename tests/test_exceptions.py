import pytest
import skafos
from skafos import models
from skafos.exceptions import *
from skafos.http import generate_required_params

from constants import *

PARAMS = {
    'skafos_api_token': TESTING_API_TOKEN,
    'org_name': TESTING_ORG,
    'app_name': TESTING_APP
}

class TestExceptions(object):
    # Test a token error on a summary call with no token
    def test_summary_missing_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary()

    # Test another token error by using a fake token
    def test_summary_invalid_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary(skafos_api_token=TESTING_FAKE_TOKEN)

    # Test missing param error when trying to upload a file
    def test_upload_missing_param(self):
        with pytest.raises(InvalidParamError):
            models.upload_version(files="", skafos_api_token=TESTING_FAKE_TOKEN)

    # Test a failing download due to empty model version
    def test_fetch_failed_download(self):
        with pytest.raises(DownloadFailedError):
            res = models.fetch_version(
                model_name=TESTING_MODEL_EMPTY,
                **PARAMS
            )

    # Test a failed upload due to invalid (fake) file
    def test_upload_invalid_file(self):
        with pytest.raises(InvalidParamError):
            res = models.upload_version(
                files=TESTING_FAKE_FILE,
                model_name=TESTING_MODEL,
                **PARAMS
            )

    # Test generating required PARAMS when missing a value
    def test_generate_params_missing(self):
        with pytest.raises(InvalidParamError):
            # Missing model name here.. should fail
            res = generate_required_params(PARAMS)

"""
Skafos Unit Tests

All unit tests can be run offline and require no connection to any Skafos backend
services. They test bits of logic and handlers of backend responses (mocked). Unit
tests that break should stop a build/deploy in it's tracks.
"""
import pytest
import skafos
from skafos.exceptions import *
from skafos.http import _generate_required_params
from skafos.models import upload_version, _create_filelist
from skafos.models import _make_model_filename, _check_description
from constants import *


PARAMS = {
    'skafos_api_token': TESTING_API_TOKEN,
    'org_name': TESTING_ORG,
    'app_name': TESTING_APP
}


class TestUnit(object):

    # Validate that the version returns as a string
    def test_version(self):
        v = skafos.get_version()
        assert isinstance(v, str)

    # Test generating required PARAMS
    def test_generate_params(self):
        required_keys = ["skafos_api_token", "org_name", "app_name", "model_name"]
        res = _generate_required_params({**PARAMS, **{"model_name": "test_model"}})
        # Check that required keys exist
        assert all(key in res.keys() for key in required_keys)

    # Test generating required PARAMS when missing a value
    def test_generate_params_missing(self):
        with pytest.raises(InvalidParamError):
            # Missing model name here should raise an exception
            res = _generate_required_params(PARAMS)

    # Test making a filelist
    def test_filelist_create(self):
        test_filelist = _create_filelist(TESTING_FAKE_FILE)
        assert isinstance(test_filelist, list)

    # Test creating a filename
    def test_filename_creation(self):
        test_model_filename = _make_model_filename(TESTING_FAKE_FILE)
        assert test_model_filename == TESTING_FAKE_FILE + ".zip"

    # Test creating a filename that's already got a zip extension
    def test_filename_creation_zip(self):
        testing_fake_file_zip = TESTING_FAKE_FILE + ".zip"
        test_model_filename = _make_model_filename(testing_fake_file_zip)
        assert test_model_filename == testing_fake_file_zip

    # Test an invalid description to make sure error is thrown
    def test_invalid_description(self):
        test_description = 1234567
        with pytest.raises(InvalidParamError):
            _check_description(test_description)

    # Test a token error on a summary call with no token
    def test_summary_missing_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary()

    # Test missing param error when trying to upload a file
    def test_upload_missing_param(self):
        with pytest.raises(InvalidParamError):
            upload_version(files="", skafos_api_token=TESTING_FAKE_TOKEN)

    # Test a failed upload due to invalid (fake) file
    def test_upload_invalid_file(self):
        with pytest.raises(InvalidParamError):
            res = upload_version(
                files=TESTING_FAKE_FILE,
                model_name=TESTING_MODEL,
                **PARAMS
            )

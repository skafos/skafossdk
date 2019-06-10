import pytest
from time import sleep

import skafos
from skafos import models
from skafos.exceptions import InvalidTokenError, InvalidParamError


class TestExceptions(object):
    # Force a token error
    def test_missing_token(self):
        with pytest.raises(InvalidTokenError):
            skafos.summary()

    # Force another token error
    def test_invalid_token(self):
        sleep(2)
        with pytest.raises(InvalidTokenError):
            skafos.summary(skafos_api_token="fake-token")

    # Force a missing param error
    def test_missing_param(self):
        with pytest.raises(InvalidParamError):
            models.upload_version(files="", skafos_api_token="fake-token")

class InvalidParamError(Exception):
    """Exception thrown when there is some missing or invalid parameter
    required for one of the SDK utilities."""
    pass


class InvalidTokenError(Exception):
    """Exception thrown when there is either a missing or
    invalid API token when a request is made to Skafos."""
    pass


class UploadFailedError(Exception):
    """Exception thrown when there is an error while uploading
    a model version to Skafos."""
    pass

"""Skafos Python SDK Exceptions"""


class MissingParamError(Exception):
    """Exception thrown when there is some missing parameter
    required for one of the SDK utilities."""
    pass


class InvalidTokenError(Exception):
    """Exception thrown when there is either a missing or
    invalid API token when a request was made to Skafos."""
    pass

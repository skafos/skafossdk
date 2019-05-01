"""
-----------------
Skafos Python SDK
-----------------
Lightweight and flexible python wrapper to save and load machine
learning models to the Skafos platform.
"""
import os
import json
import requests
import logging
from .exceptions import *

API_BASE_URL = "https://api.skafos.wtf/v2"  # production: api.skafos.ai/v2
logger = logging.getLogger(name="skafos")


def get_version():
    """Returns the current version of the Skafos SDK in use."""
    with open(os.path.join(os.path.dirname(__file__),  'VERSION')) as version_file:
        return version_file.read().strip()


def _generate_required_params(args):
    # Generate the parameters to build a Skafos request/endpoint
    params = {}

    # Check for api token first
    if 'skafos_api_token' in args:
        params['skafos_api_token'] = args['skafos_api_token']
    else:
        params['skafos_api_token'] = os.getenv('SKAFOS_API_TOKEN')
    if not params['skafos_api_token']:
        raise InvalidTokenError("Missing Skafos API Token")

    # Grab org name
    if 'org_name' in args:
        params['org_name'] = args['org_name']
    else:
        params['org_name'] = os.getenv('SKAFOS_ORG_NAME')
    if not params['org_name']:
        raise MissingParamError("Missing Skafos Organization Name")

    # Grab app name
    if 'app_name' in args:
        params['app_name'] = args['app_name']
    else:
        params['app_name'] = os.getenv('SKAFOS_APP_NAME')
    if not params['app_name']:
        raise MissingParamError("Missing Skafos App Name")

    # Grab model name
    if 'model_name' in args:
        params['model_name'] = args['model_name']
    else:
        params['model_name'] = os.getenv('SKAFOS_MODEL_NAME')
    if not params['model_name']:
        raise MissingParamError("Missing Skafos Model Name")

    return params


def _call_skafos_api(method, endpoint, payload, head=None):

    if method == 'POST':
        url = API_BASE_URL + endpoint
        response = requests.post(url, data=payload)
    elif method == 'PUT':
        if head:
            response = requests.put(endpoint, data=payload, headers=head)
        else:
            # fail here
    elif method == 'PATCH':
        url = API_BASE_URL + endpoint
        response = requests.patch(url, data=payload)

    # TODO better error handling needed
    if response.status_code == requests.codes.ok:
        content = json.loads(response.content)
        return content


# TODO handle exceptions
def upload_model_version(**kwargs):
    # TODO make better doc string
    """
    Upload a model version (a zipped archive) for a specific app and model directly to Skafos. Optionally zip files upon
    upload, removing that burden from the user. Once model has been uploaded to storage, return a successful response.
    :param skafos_api_token:
    :param org_name:
    :param app_name:
    :param model_name:
    :param files:
    :return:
    """
    # Get required params
    params = _generate_required_params(kwargs)

    # Check for files
    if 'files' not in kwargs:
        # fail here

    # Unzip files TODO figure out this logic
    if isinstance(kwargs['files'], list):
        # do a thing
    elif isinstance(kwargs['files'], str):
        # do a different thing
    else:
        # fail here?

    # Create endpoint
    if 'org_name' in params:
        endpoint = f"/organizations/{params['org_name']}/app/{params['app_name']}/models/{params['model_name']}/"
    else:
        # Default to user org
        endpoint = f"/app/{params['app_name']}/models/{params['model_name']}/"

    # Make request - handle errors
    model_version_res = _call_skafos_api(
        method='POST',
        endpoint=endpoint,
        payload=json.dumps({})
    )

    # Upload model to s3 TODO this one will only return a status code not content - need to tweak handler
    upload_res = _call_skafos_api(
        method='PUT',
        endpoint=model_version_res['presigned_url'],
        payload=json.dumps({})
    )

    # If upload succeeds, update db
    model_version_endpoint = endpoint + f"model_versions/{model_version_res['model_version_id']}"
    data = {"filepath": model_version_res['filepath']}
    final_model_version_res = _call_skafos_api(
        method='POST',
        endpoint=model_version_endpoint,
        payload=json.dumps({data})
    )
    # Return response to the user
    return final_model_version_res


def fetch_model_version(**kwargs):
    """
    Download a model version (a zipped archive) for a specific app and model directly from Skafos.

    :param skafos_api_token:
    :param org_name:
    :param app_name:
    :param model_name:
    :return:
    """
    params = _generate_required_params(kwargs)
    # TODO like everything else

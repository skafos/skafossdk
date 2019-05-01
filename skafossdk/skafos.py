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
from .logger import get_logger

log = get_logger() # TODO
API_BASE_URL = "https://api.skafos.wtf/v2"  # production: api.skafos.ai/v2


class MissingParamError(Exception):
    # TODO
    pass


def get_version():
    # TODO
    pass


def _generate_required_params(args):
    # TODO is this right?
    # Check for api token first
    if 'skafos_api_token' in args:
        token = args['skafos_api_token']
    else:
        token = os.getenv('SKAFOS_API_TOKEN')
    if not token:
        raise MissingParamError

    # Grab app name and model name
    if ('model_name' in args) and ('app_name' in args):
        model_name = args['model_name']
        app_name = args['app_name']
    else:
        model_name = os.getenv('SKAFOS_MODEL_NAME')
        app_name = os.getenv('SKAFOS_APP_NAME')

    if not model_name or not app_name:
        raise MissingParamError

    return {
        'skafos_api_token': token,
        'model_name': model_name,
        'app_name': app_name
    }


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
    :param model_name:
    :param app_name:
    :param files:
    :param compress:
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
    endpoint = f"/sdk/{params['skafos_api_token']}/app/{params['app_name']}/models/{params['model_name']}/"

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


def get_model_version(**kwargs):
    # TODO make better doc string
    """
    Download a model version (a zipped archive) for a specific app and model directly from Skafos. Optionally unzip the
    archive on download, removing that burden from the user.
    :param skafos_api_token:
    :param model_name:
    :param app_name:
    :param decompress:
    :return:
    """
    params = _generate_required_params(kwargs)
    # TODO like everything else


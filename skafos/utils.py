"""
-----------------
Skafos Python SDK
-----------------
Lightweight and flexible python wrapper to save and load machine
learning models to the Skafos platform.
"""
import os
import json
import zipfile
import requests
import logging
from .exceptions import *

API_BASE_URL = "https://api.skafos.wtf/v2"  # production: https://api.skafos.ai/v2
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
    #if not params['org_name']:
    #    raise MissingParamError("Missing Skafos Organization Name")

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

# TODO refactor into a network handler method: def _http_request():
def _model_version_record(endpoint, payload):
    # Create model version record in the BE
    url = API_BASE_URL + endpoint
    r = requests.post(url, data=payload)
    if r.status_code == requests.codes.ok:
        res = r.json()
        return res
    else:
        raise UploadFailedError(f"Failed to create new model version: {r.status_code}")


def _upload(url, payload, header):
    # Put model object to presigned url
    r = requests.put(url, data=payload, headers=header)
    if r.status_code == 200:
        return r.status_code
    else:
        raise UploadFailedError(f"Model version upload failed: {r.status_code}")


def _update_model_version_record(endpoint, payload):
    url = API_BASE_URL + endpoint
    r = requests.patch(url, data=payload)
    if r.status_code == requests.codes.ok:
        res = r.json()
        return res
    else:
        raise UploadFailedError(f"Failed to create new model version: {r.status_code}")


# TODO handle exceptions
def upload_model_version(files, description=None, **kwargs) -> dict:
    #TODO clean up the docstring and make consistent
    """
    Uploads a model version (a zipped archive) for a specific app and model directly to Skafos. Zips files upon
    upload, removing that burden from the user. Once model has been uploaded to storage, returns a successful response.

    :param files:
        Single model file path or list of file paths to zip up and upload to Skafos.
    :type files:
        str or list
    :param description:

    :type description:
        str
    :param \**kwargs:
        Keyword arguments to identify which organization, app, and model to upload the model version to. See below.

    :Keyword Arguments:
        * *skafos_api_token* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            Optional. If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :return:
    """
    # Get required params
    params = _generate_required_params(kwargs)
    header = {"X-API-KEY": params["skafos_api_token"]}

    # Unzip files
    filelist = None
    if isinstance(files, list):
        filelist = files
    elif isinstance(files, str):
        filelist = [files]

    # Create zipped filename TODO check with kevin about how to use right zipfile name here
    zip_name = params['model_name'] if params['model_name'][-4:] == ".zip" else f"{params['model_name']}.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as skazip:
        for zfile in filelist:
            if os.path.isdir(zfile):
                for root, dirs, files in os.walk(zfile):
                    for dfile in files:
                        skazip.write(os.path.join(root, dfile))
            elif os.path.isfile(zfile):
                skazip.write(zfile)

    # Create endpoint
    if 'org_name' in params:
        endpoint = f"/organizations/{params['org_name']}/app/{params['app_name']}/models/{params['model_name']}/"
    else:
        # Default to user org - WHERE does the error come back if they have more than one org?
        endpoint = f"/app/{params['app_name']}/models/{params['model_name']}/"

    # Create request body
    body = {"file_name": zip_name}
    if description and isinstance(description, str):
        body["description"] = description
        # TODO check that description is less than 255 charvar
        # TODO what to do if not string????

    # Make request TODO update to use http_request handler function
    model_version_res = _model_version_record(
        endpoint=endpoint,
        payload=json.dumps({}),
        header=header
    )

    # Upload model to storage
    header["Content-Type"] = "application/octet-stream"
    body = {"file": ""} # TODO need to figure out how to put the actual zip file in this (byte stream)
    upload_res = _upload(
        url=model_version_res['presigned_url'],
        payload=json.dumps({body}),
        header=header
    )

    # If upload succeeds, update db TODO handle success/failure from previous call
    model_version_endpoint = endpoint + f"model_versions/{model_version_res['model_version_id']}"
    _ = header.pop("Content-Type")
    data = {"filepath": model_version_res['filepath']}
    final_model_version_res = _update_model_version_record(
        endpoint=model_version_endpoint,
        payload=json.dumps({data}),
        header=header
    )

    # Return response to the user
    return final_model_version_res

# TODO what does this return?
def fetch_model_version(version=None, **kwargs):
    #TODO clean up the docstring and make consistent

    """
    Download a model version (a zipped archive) for a specific app and model directly from Skafos.

    :param skafos_api_token:
    :param org_name:
    :param app_name:
    :param model_name:
    :param version:
    :return:
    """
    params = _generate_required_params(kwargs)

    # TODO like everything else
    pass


def summary(skafos_api_token=None) -> dict:
    """
    Returns all Skafos organizations, apps, and models that the provided
    API token has access to.

    :param skafos_api_token:
    :type skafos_api_token:
    :returns:

    """

    # Check for token in function, then env, then raise error if not there
    # Do stuff and make request
    # Return python dictionary to the user


    pass


def list_model_versions(**kwargs) -> dict:
    """
    Returns a list of all saved model versions based on API token, organization,
    app, and model names.

    """

    pass

    

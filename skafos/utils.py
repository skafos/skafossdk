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
HTTP_VERBS = ["GET", "POST", "PUT", "PATCH"]
DEFAULT_TIMEOUT = 120
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
        raise InvalidParamError("Missing Skafos Organization Name")

    # Grab app name
    if 'app_name' in args:
        params['app_name'] = args['app_name']
    else:
        params['app_name'] = os.getenv('SKAFOS_APP_NAME')
    if not params['app_name']:
        raise InvalidParamError("Missing Skafos App Name")

    # Grab model name
    if 'model_name' in args:
        params['model_name'] = args['model_name']
    else:
        params['model_name'] = os.getenv('SKAFOS_MODEL_NAME')
    if not params['model_name']:
        raise InvalidParamError("Missing Skafos Model Name")

    return params


def _http_request(method, url, api_token, timeout=None, payload=None):
    # Check that we ae using an appropriate request type
    if method not in HTTP_VERBS:
        raise requests.exceptions.HTTPError("Must use an appropriate HTTP verb")

    # Prepare headers and timeout
    header = {"X-API-TOKEN": api_token, "Content-Type": "application/json"}
    if method == "PUT":
        header["Content-Type"] = "application/octet-stream"
    if not timeout:
        timeout = DEFAULT_TIMEOUT

    try:
        # Prepare request object and send it
        req = requests.Request(method, url, headers=header, data=payload)
        r = req.prepare()
        with requests.Session() as s:
            logger.debug(f"Sending prepared request with url: {url}")
            response = s.send(r, timeout=timeout)
            response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.debug(f"HTTP Error: {err}")
        if response.status_code == 401:
            # We know what it is - raise proper exception to user
            raise InvalidTokenError("Invalid Skafos API Token")
        elif response.status_code == 404:
            # We know what it is - raise proper exception to user
            raise InvalidParamError("Invalid param passed to function. Check your org name, app name, or model name")
        else:
            raise
    except requests.exceptions.ConnectionError as err:
        logger.debug(f"Error connecting to server: {err}")
        raise
    except requests.exceptions.Timeout:
        logger.debug(f"Request timed out at {timeout} seconds, consider increasing timeout")
        raise
    except requests.exceptions.RequestException as err:
        logger.debug(f"Oops, got some other error: {err}")
        raise

    # Return response
    logger.debug("Got a 200 from the server")
    if method == "PUT":
        return response.status_code
    else:
        return response.json()


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
            else:
                raise InvalidParamError("We were unable to find that file. Check to make sure that file is in your working directory.")
    
    # Create endpoint
    if 'org_name' in params:
        endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}/"
    else:
        # Default to user org - WHERE does the error come back if they have more than one org?
        endpoint = f"/apps/{params['app_name']}/models/{params['model_name']}/"

    # Create request body
    body = {"filename": zip_name}
    if description and isinstance(description, str):
        if len(description) > 255:
            print("You provided a description that was more than 255 characters, a model will be saved with a truncated description")
            body['description'] = description[0:255]
        else:
            body['description'] = description

    # Create a model version
    model_version_res = _http_request(
        method="POST",
        url=API_BASE_URL + endpoint + "model_versions",
        payload=json.dumps(body),
        api_token=params["skafos_api_token"]
    )

    # Upload the model
    upload_res=None
    if type(model_version_res)==dict and model_version_res.get('presigned_url'):
        with open(zip_name, 'rb') as data:
            asset_data = data.read()

        upload_res = _http_request(
            method="PUT",
            url=model_version_res['presigned_url'],
            payload=asset_data,
            api_token=params['skafos_api_token']
        )
    else:
        print("Upload model failed")

    # Update the model version with the file path
    final_model_version_res=None
    if upload_res and upload_res==200:
        model_version_endpoint = endpoint + f"model_versions/{model_version_res['model_version_id']}"
        data = {"filepath": model_version_res['filepath']}
        final_model_version_res = _http_request(
            method="PATCH",
            url=API_BASE_URL + model_version_endpoint,
            payload=json.dumps(data),
            api_token=params['skafos_api_token']
        )
    else:
        print("Unable to upload data")
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
    Returns all Skafos organizations, apps, and models that the provided API token has access to.

    :param skafos_api_token:
        Skafos API Token associated with the user account. Get one at https://skafos.ai --> Settings --> Tokens.
    :type skafos_api_token:
        str or None. Checks environment for 'SKAFOS_API_TOKEN' if not passed into the function directly.
    :return:
        Nested dictionary of all organizations, apps, and models, this user has access to.
    :rtype:
        dict
    """
    summary_res = {}

    # Check for api token first
    if not skafos_api_token:
        skafos_api_token = os.getenv("SKAFOS_API_TOKEN")
    if not skafos_api_token:
        raise InvalidTokenError("Missing Skafos API Token")

    # Prepare requests
    method = "GET"
    endpoint = "/organizations"
    res = _http_request(
        method=method,
        url=API_BASE_URL + endpoint,
        api_token=skafos_api_token
    )
    for org in res:
        summary_res[org["display_name"]] = {}
        endpoint = f"/organizations/{org['display_name']}/apps?with_models=true"
        res = _http_request(
            method=method,
            url=API_BASE_URL + endpoint,
            api_token=skafos_api_token
        )
        for app in res:
            summary_res[org["display_name"]][app["name"]] = []
            for model in app["models"]:
                model_meta_data = {k: model[k] for k in model.keys() & {"name", "updated_at"}}
                summary_res[org["display_name"]][app["name"]].append(model_meta_data)
    # Return the summary response to the user
    return summary_res


def list_model_versions(**kwargs) -> list:
    """
    Returns a list of all saved model versions based on API token, organization,
    app, and model names.

    :Keyword Arguments:
        * *skafos_api_token* (``str``) --
            Required. Skafos API Token associated with your user account.
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            Required. Skafos organization name.
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            Required. Skafos app name associated with the above organization.
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            Required. Skafos model name associated with the above organization and app.
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :return:
        List of dictionaries containing model versions that have been successfully uploaded to Skafos.
    :rtype:
        list
    """
    params = _generate_required_params(kwargs)
    endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}/model_versions?order_by=version"
    res = _http_request(
        method="GET",
        url=API_BASE_URL + endpoint,
        api_token=params["skafos_api_token"]
    )
    # Clean up the response so users have something manageable
    versions = []
    for model_version in res:
        versions.append({k: model_version[k] for k in model_version.keys() & {"version", "name", "updated_at", "description"}})
    return versions
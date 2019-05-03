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


def _http_request(method, url, api_token, timeout=None, payload=None):
    # Check that we ae using an appropriate request type
    if method not in HTTP_VERBS:
        raise requests.exceptions.HTTPError("Must use an appropriate HTTP verb")

    # Prepare headers and timeout
    header = {"X-API-KEY": api_token}
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
    except requests.exceptions.ConnectionError as err:
        logger.debug(f"Error connecting to server: {err}")
    except requests.exceptions.Timeout:
        logger.debug(f"Request timed out at {timeout} seconds, consider increasing timeout")
    except requests.exceptions.RequestException as err:
        logger.debug(f"Oops, got some other error: {err}")

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
    Returns all Skafos organizations, apps, and models that the provided API token has access to.

    :param skafos_api_token:
        Skafos API Token associated with your user account. Get one at https://skafos.ai.
    :type skafos_api_token:
        str or None
    :return:
        Dictionary of all organizations, apps, and models, this account has access to.
    """
    summary_res = {}

    # Check for api token first
    if not skafos_api_token:
        skafos_api_token = os.getenv('SKAFOS_API_TOKEN')
    if not skafos_api_token:
        raise InvalidTokenError("Missing Skafos API Token")

    # Prepare requests
    header = {"X-API-Key": skafos_api_token}
    method = "GET"
    endpoint = "/organizations"
    res = _http_request(
        method = method,
        url = API_BASE_URL + endpoint,
        header = header
    )
    for org in res:
        summary_res[org["name"]] = {}
        endpoint = f"/organizations/{org['name']}/apps"
        res = _http_request(
            method= method,
            url = API_BASE_URL + endpoint,
            header = header
        )
        for app in res:
            summary_res[org["name"]][app["name"]] = []
            endpoint = f"/organizations/{org['name']}/apps/{app['name']}/models"
            res = _http_request(
                method = method,
                url = API_BASE_URL + endpoint,
                header = header
            )
            for model in res:
                model_meta_data = {k: model[k] for k in model.keys() & {'id, ''name', 'updated_at', 'public'}}
                summary_res[org["name"]][app["name"]].append(model_meta_data)
    # Print out and return the summary response to the user
    print(summary_res)
    return summary_res


def list_model_versions(**kwargs) -> dict:
    """
    Returns a list of all saved model versions based on API token, organization,
    app, and model names.
    """
    params = _generate_required_params(kwargs)
    endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}/model_versions?=order_by=versions%3Adesc"
    res = _http_request(
        method = "GET",
        url = API_BASE_URL + endpoint,
        api_token = params["skafos_api_token"]
    )
    print(res)
    return res

    

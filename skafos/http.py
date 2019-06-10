import os
import requests
import logging

from .exceptions import *


API_BASE_URL = "https://api.skafos.ai/v2"
DOWNLOAD_BASE_URL = "https://download.skafos.ai/v2"
HTTP_VERBS = ["GET", "POST", "PUT", "PATCH"]
DEFAULT_TIMEOUT = 120
logger = logging.getLogger(name="skafos")


def generate_required_params(args):
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


def http_request(method, url, api_token, header=None, timeout=None, payload=None, stream=False):
    # Check that we ae using an appropriate request type
    if method not in HTTP_VERBS:
        raise requests.exceptions.HTTPError("Must use an appropriate HTTP verb")

    # Prepare headers and timeout
    request_header = {"X-API-TOKEN": api_token, "Content-Type": "application/json"}
    # Update request header with optionally provided header
    if header and isinstance(header, dict):
        request_header.update(header)
    if not timeout:
        timeout = DEFAULT_TIMEOUT

    # Prepare request object and send it
    try:
        req = requests.Request(method, url, headers=request_header, data=payload)
        r = req.prepare()
        with requests.Session() as s:
            logger.debug("Sending prepared request with url: {}".format(url))
            if stream and method == "GET":
                with s.send(r, timeout=timeout, stream=True) as response:
                    response.raise_for_status()
                    fn = url.split("models/")[1].split("?")[0]
                    with open(fn + ".zip", 'wb') as f:
                        for chunk in response.iter_content(chunk_size=512*1024):
                            if chunk:
                                f.write(chunk)
            else:
                response = s.send(r, timeout=timeout)
                response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logger.debug("HTTP Error: {}".format(err))
        if response.status_code == 401:
            # We know what it is - raise proper exception to user
            raise InvalidTokenError("Invalid Skafos API Token")
        elif response.status_code == 404:
            # We know what it is - raise proper exception to user
            if "download" in url:
                raise DownloadFailedError("Model version download failed. Check parameters and that a version actually exists for this model.")
            else:
                raise InvalidParamError("Invalid connection parameters. Check your org name, app name, and model name.")
        else:
            raise
    except requests.exceptions.ConnectionError as err:
        logger.debug("Error connecting to server: {}".format(err))
        raise
    except requests.exceptions.Timeout:
        logger.debug("Request timed out at {} seconds, consider increasing timeout".format(timeout))
        raise
    except requests.exceptions.RequestException as err:
        logger.debug("Oops, got some other error: {}".format(err))
        raise

    # Return response
    logger.debug("Got a 200 from the server")
    return response

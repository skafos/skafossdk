import json
import zipfile
import logging

from .http import *
from .exceptions import *


logger = logging.getLogger("skafos")


def upload_version(files, description=None, **kwargs) -> dict:
    """
    Uploads a model version (a zipped archive) for a specific app and model directly to Skafos. Zips files upon
    upload, removing that burden from the user. Once model has been uploaded to storage, returns a successful response.

    .. note:: If your model file(s) are not in your working directory, Skafos will zip up and preserve the entire
              path pointing to the file(s).

    :param files:
        Single model file path or list of file paths to zip up and upload to Skafos.
    :type files:
        str or list
    :param description:
        Optional. Short description for your model version. Must be less than or equal to 255 characters long.
    :type description:
        str
    :param \**kwargs:
        Keyword arguments to identify which organization, app, and model to upload the model version to. See below.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            Optional. If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :returns:
            A meta data dictionary for the uploaded model version.

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # Upload a model version to Skafos
       models.upload_version(
           skafos_api_token="<your-api-token>",
           org_name="my-organization",
           app_name="my-app",
           model_name="my-model",
           files="my_text_classifier.mlmodel",
           description="My model version upload to Skafos"
       )
    """
    # Get required params
    params = generate_required_params(kwargs)

    # Unzip files
    filelist = None
    if isinstance(files, list):
        filelist = files
    elif isinstance(files, str):
        filelist = [files]

    # Create zipped filename
    zip_name = params["model_name"] if params["model_name"].endswith(".zip") else f"{params['model_name']}.zip"
    body = {"filename": zip_name}

    # Check that they
    if description and isinstance(description, str):
        if len(description) > 255:
            raise InvalidParamError("Description too long. Please provide a description that is less than 255 characters")
        else:
            body["description"] = description
    if description and not isinstance(description, str):
        raise InvalidParamError(f"Please provide a model version description with type = str")

    # Write the zip file
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as skazip:
        for zfile in filelist:
            if os.path.isdir(zfile):
                for root, dirs, files in os.walk(zfile):
                    for dfile in files:
                        skazip.write(os.path.join(root, dfile))
            elif os.path.isfile(zfile):
                skazip.write(zfile)
            else:
                raise InvalidParamError(f"We were unable to find {zfile}. Check to make sure that the file path is correct.")

    # Create endpoint
    endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}/"

    # Create a model version
    model_version_res = http_request(
        method="POST",
        url=API_BASE_URL + endpoint + "model_versions",
        payload=json.dumps(body),
        api_token=params["skafos_api_token"]
    ).json()

    # Upload the model
    if model_version_res.get("presigned_url"):
        with open(zip_name, "rb") as data:
            model_data = data.read()

        logger.info("Uploading model version to Skafos.")
        upload_res = http_request(
            method="PUT",
            url=model_version_res["presigned_url"],
            payload=model_data,
            api_token=params["skafos_api_token"]
        )
    else:
        raise UploadFailedError("Upload failed.")

    # Update the model version with the file path
    if upload_res.status_code == 200:
        model_version_endpoint = endpoint + f"model_versions/{model_version_res['model_version_id']}"
        data = {"filepath": model_version_res["filepath"]}
        final_model_version_res = http_request(
            method="PATCH",
            url=API_BASE_URL + model_version_endpoint,
            payload=json.dumps(data),
            api_token=params["skafos_api_token"]
        ).json()
    else:
        raise UploadFailedError("Upload failed.")

    # Return cleaned response JSON to the user
    logger.info("\nSuccessful Upload:")
    meta = {k: final_model_version_res[k] for k in final_model_version_res.keys() & {"version", "description", "name", "model"}}
    return meta


def fetch_version(version=None, **kwargs):
    """
    Download a model version (a zipped archive) for a specific app and model directly from Skafos to your current
    working directory as <model_name>.zip.

    :param version:
        Version of the model to download. If unspecified, defaults to the latest version
    :type version:
        int
    :param \**kwargs:
        Keyword arguments to identify which organization, app, and model to upload the model version to. See below.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            Optional. If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            Required. If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :return:
        None

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # Fetch the latest version of your model
       models.fetch_version(
           skafos_api_token="<your-api-token>",
           org_name="my-organization",
           app_name="my-app",
           model_name="my-model"
       )

       # Fetch a specific version of your model
       models.fetch_version(
           skafos_api_token="<your-api-token>",
           org_name="my-organization",
           app_name="my-app",
           model_name="my-model",
           version=2
       )
    """

    # Get required params
    params = generate_required_params(kwargs)

    # Get model version and create endpoint.
    if not version:
        endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}"
    elif isinstance(version, int):
        endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}?version={version}"
    else: # You passed in some garbage and so we need to throw an error
        raise InvalidParamError("If specified, the model version must be an integer.")

    # Download the model
    method = "GET"
    res = http_request(
        method=method,
        url=DOWNLOAD_BASE_URL + endpoint,
        api_token=params["skafos_api_token"],
        stream=True
    )

    # Log message
    if res.status_code == 200:
        print("File downloaded.", flush=True)


def list_versions(**kwargs) -> list:
    """
    Returns a list of all saved model versions based on API token, organization,
    app, and model names.

    :Keyword Args:
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

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # List previously saved model versions
       models.list_versions(
           skafos_api_token="<your-api-token>",
           org_name="my-organization",
           app_name="my-app",
           model_name="my-model"
       )
    """
    params = generate_required_params(kwargs)
    endpoint = f"/organizations/{params['org_name']}/apps/{params['app_name']}/models/{params['model_name']}/model_versions?order_by=version"
    res = http_request(
        method="GET",
        url=API_BASE_URL + endpoint,
        api_token=params["skafos_api_token"]
    ).json()
    # Clean up the response so users have something manageable
    versions = []
    for model_version in res:
        versions.append({k: model_version[k] for k in model_version.keys() & {"version", "name", "updated_at", "description"}})
    return versions

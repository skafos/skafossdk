import json
import zipfile
import logging

from .http import *
from .exceptions import *


logger = logging.getLogger("skafos")


def upload_version(files, description=None, **kwargs) -> dict:
    r"""
    Upload a model version (one or more files) for a specific app and model to Skafos. All files
    are automatically zipped together and uploaded to storage. Once successfully uploaded, a dictionary
    of meta data is returned.

    .. note:: If your model file(s) are not in your working directory, Skafos will zip up and preserve the entire
              path pointing to the file(s). We recommend placing your file(s) in your current working directory.

    :param files:
        Single model file path or list of file paths to zip up and upload to Skafos.
    :type files:
        str or list
    :param description:
        *Optional*. Short description for your model version. Must be less than or equal to 255 characters.
    :type description:
        str
    :param \**kwargs:
        Keyword arguments identifying the organization, app, and model for upload. See below.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

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
    zip_name = params["model_name"] if params["model_name"].endswith(".zip") else "{}.zip".format(params['model_name'])
    body = {"filename": zip_name}

    # Check that they
    if description and isinstance(description, str):
        if len(description) > 255:
            raise InvalidParamError("Description too long. Please provide a description that is less than 255 characters")
        else:
            body["description"] = description
    if description and not isinstance(description, str):
        raise InvalidParamError("Please provide a model version description with type = str")

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
                raise InvalidParamError("We were unable to find {}. Check to make sure that the file path is correct.".format(zfile))

    # Create endpoint
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}/".format(**params)

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
        logger.info("Uploading model version to Skafos")
        upload_res = http_request(
            method="PUT",
            url=model_version_res["presigned_url"],
            header={"Content-Type": "application/octet-stream"},
            payload=model_data,
            api_token=params["skafos_api_token"]
        )
    else:
        raise UploadFailedError("Upload failed.")

    # Update the model version with the file path
    if upload_res.status_code == 200:
        model_version_endpoint = endpoint + "model_versions/{model_version_id}".format(**model_version_res)
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
    logger.info("\nSuccessful Upload\n")
    meta = {k: final_model_version_res[k] for k in final_model_version_res.keys() & {"version", "description", "name", "model"}}
    return meta


def fetch_version(version=None, **kwargs):
    r"""
    Download a model version as a zipped archive for a specific app and model from Skafos to your current
    working directory as `<model_name>.zip`.

    :param version:
        Version of the model to download. If unspecified, defaults to the latest version.
    :type version:
        int
    :param \**kwargs:
        Keyword arguments identifying the organization, app, and model for download. See below.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

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

    # Check to warn about overwriting file
    if os.path.exists(params["model_name"] + ".zip"):
        raise DownloadFailedError("A zip file already exists in your working directory with the model name you're trying to download.")

    # Get model version and create endpoint.
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}".format(**params)
    if version:
        if isinstance(version, int):
            endpoint += "?version={}".format(version)
        else:  # You passed in a non-supported version
            raise InvalidParamError("If specified, the model version must be an integer.")

    # Download the model
    logger.info("Fetching model")
    method = "GET"
    res = http_request(
        method=method,
        url=DOWNLOAD_BASE_URL + endpoint,
        api_token=params["skafos_api_token"],
        stream=True
    )

    # Log message
    if res.status_code == 200:
        logger.info("Downloaded as {}".format(params["model_name"] + ".zip"))


def list_versions(**kwargs) -> list:
    r"""
    Return a list of all saved model versions based on organization, app name, and model name.

    :param \**kwargs:
        Keyword arguments identifying the organization, app, and model for version retrieval. See below.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
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
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}/model_versions?order_by=version".format(**params)
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

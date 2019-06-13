import os
import json
import zipfile

from .http import *
from .http import _generate_required_params, _http_request
from .exceptions import *


def _create_filelist(files):
    # Create file list
    if isinstance(files, list):
        return files
    elif isinstance(files, str):
        return [files]
    else:
        raise InvalidParamError("Files must be either a list or a string.")


def _make_model_filename(model_name):
    # Create the name of the zipfile based on the provided model name
    if model_name.endswith(".zip"):
        model_filename = model_name
    else:
        model_filename = "{}.zip".format(model_name)
    # Check if it already exists
    if not os.path.exists(model_filename):
        return model_filename
    else:
        raise InvalidParamError("""A file already exists in your working directory
            with the name {}. In order to not overwrite, you will need to move
            it and try again!""".format(model_filename))

def _check_description(desc):
    # Check that the description (if provided) is a valid string
    if desc:
        if not isinstance(desc, str):
            raise InvalidParamError("Model version description must be a string.")
        elif isinstance(desc, str):
            if len(desc) > 255:
                raise InvalidParamError("""Description is too long. Please
                    provide a description that is less than 255 characters.""")
            else:
                return desc
    else:
        return None


def _zip_archive(name, filelist):
    # Zip a list of files together
    with zipfile.ZipFile(name, "w", zipfile.ZIP_DEFLATED) as skazip:
        for zfile in filelist:
            if os.path.isdir(zfile):
                for root, dirs, files in os.walk(zfile):
                    for dfile in files:
                        skazip.write(os.path.join(root, dfile))
            elif os.path.isfile(zfile):
                skazip.write(zfile)
            else:
                raise InvalidParamError("""We were unable to find {}. Check to
                    make sure that the file path is correct.""".format(zfile))


def _model_version_meta_data(res):
    # Isolate user-required keys for model version meta data
    return {k: res[k] for k in res.keys() & {"version", "description", "name", "model"}}


def upload_version(files, description=None, verbose=True, **kwargs) -> dict:
    r"""
    Upload a model version (one or more files) for a specific app and model to Skafos. All files
    are automatically zipped together and uploaded to storage. Once successfully uploaded, a dictionary
    of meta data is returned.

    .. note:: If your model file(s) are not in your working directory, Skafos will zip up and preserve the entire
              path pointing to the file(s). We recommend placing your file(s) in your current working directory before upload.

    :param files:
        Single model file path or list of file paths to zip up and upload to Skafos.
    :type files:
        str or list
    :param description:
        *Optional*. Short description for your model version. Must be less than or equal to 255 characters.
    :type description:
        str
    :param verbose:
        Control the amount of console print statements you see when working with the SDK. True by default.
    :type verbose:
        boolean
    :param \**kwargs:
        Keyword arguments identifying the organization, app, and model for upload. See below.
    :return:
        A meta data dictionary for the uploaded model version.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # Upload a model version to Skafos
       models.upload_version(
           skafos_api_token="<your-api-token>",
           org_name="<your-organization>",
           app_name="<your-app>",
           model_name="<your-model>",
           files="my_text_classifier.mlmodel",
           description="My model version upload to Skafos"
       )

    :raises:
        * `InvalidTokenError` - if improper API token is used or is missing entirely.
        * `InvalidParamError` - if improper connection params are passed or a zip file exists in your working directory with the same name that Skafos tries to create before upload.
        * `UploadFailedError` - if there's a local network or API related issue.

    """
    # Generate required connection params
    params = _generate_required_params(kwargs)

    # Generate file list
    filelist = _create_filelist(files)

    # Check model version description if provided
    description = _check_description(desc=description)
    if description:
        body["description"] = description

    # Create zipped model filename
    model_filename = _make_model_filename(model_name=params["model_name"])
    body = {"filename": model_filename}

    # Create the zip archive from the filelist
    _zip_archive(name=model_filename, filelist=filelist)
    if verbose:
        print("Created zipped archive to upload to Skafos.", flush=True)

    # Create a model version record
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}/".format(**params)
    model_version_res = _http_request(
        method="POST",
        url=API_BASE_URL + endpoint + "model_versions",
        payload=json.dumps(body),
        api_token=params["skafos_api_token"]
    ).json()
    if verbose:
        print("Created model version record on Skafos.", flush=True)

    # Upload the model to storage
    if model_version_res.get("presigned_url"):
        with open(zip_name, "rb") as data:
            model_data = data.read()
        if verbose:
            print("Started uploading model version to Skafos.", flush=True)
        upload_res = _http_request(
            method="PUT",
            url=model_version_res["presigned_url"],
            header={"Content-Type": "application/octet-stream"},
            payload=model_data,
            api_token=params["skafos_api_token"]
        )
        if verbose:
            print("Finished uploading model version to Skafos.", flush=True)
    else:
        raise UploadFailedError("Model upload failed.")

    # Update the model version with the file path
    if upload_res.status_code == 200:
        model_version_endpoint = endpoint + "model_versions/{model_version_id}".format(**model_version_res)
        data = {"filepath": model_version_res["filepath"]}
        final_model_version_res = _http_request(
            method="PATCH",
            url=API_BASE_URL + model_version_endpoint,
            payload=json.dumps(data),
            api_token=params["skafos_api_token"]
        ).json()
        if verbose:
            print("Updated model version record.", flush=True)
    else:
        raise UploadFailedError("Model upload failed.")

    # Return cleaned response JSON to the user
    print("\nSuccessful model version upload.\n", flush=True)
    meta = _model_version_meta_data(res=final_model_version_res)
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
    :return:
        None

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # Fetch the latest version of your model
       models.fetch_version(
           skafos_api_token="<your-api-token>",
           org_name="<your-organization>",
           app_name="<your-app>",
           model_name="<your-model>"
       )

       # Fetch a specific version of your model
       models.fetch_version(
           skafos_api_token="<your-api-token>",
           org_name="<your-organization>",
           app_name="<your-app>",
           model_name="<your-model>",
           version=2
       )

    :raises:
        * `InvalidTokenError` - if improper API token is used or is missing entirely.
        * `InvalidParamError` - if improper connection parameters are passed or a zip file in your working directory exists with the same name that Skafos is trying to download.
        * `DownloadFailedError` - if there's a local network or API related issue, or if no model version exists.

    """
    # Get required params
    params = _generate_required_params(kwargs)

    # Check and create filename for the model when it gets downloaded
    model_filename = _make_model_filename(model_name=params["model_name"])

    # Get model version and create endpoint
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}".format(**params)
    if version:
        if isinstance(version, int):
            endpoint += "?version={}".format(version)
        else:  # You passed in a non-supported version
            raise InvalidParamError("If specified, the model version must be an integer.")

    # Download the model
    print("Fetching model version.", flush=True)
    method = "GET"
    res = _http_request(
        method=method,
        url=DOWNLOAD_BASE_URL + endpoint,
        api_token=params["skafos_api_token"],
        stream=True
    )

    # Log success message
    if res.status_code == 200:
        print("Downloaded model file as {}.".format(model_filename), flush=True)


# Clean up the response so users have something manageable
def _clean_up_version_list(res):
    versions = []
    for model_version in res:
        version = {k: model_version[k] for k in model_version.keys() & {"version", "name", "updated_at", "description"}}
        versions.append(version)
    return versions


def list_versions(**kwargs) -> list:
    r"""
    Return a list of all saved model versions based on organization, app name, and model name.

    :param \**kwargs:
        Keyword arguments identifying the organization, app, and model for version retrieval. See below.
    :return:
        List of dictionaries containing model versions that have been successfully uploaded to Skafos.

    :Keyword Args:
        * *skafos_api_token* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_API_TOKEN`.
        * *org_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_ORG_NAME`.
        * *app_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_APP_NAME`.
        * *model_name* (``str``) --
            If not provided, it will be read from the environment as `SKAFOS_MODEL_NAME`.

    :Usage:
    .. sourcecode:: python

       from skafos import models

       # List previously saved model versions
       models.list_versions(
           skafos_api_token="<your-api-token>",
           org_name="<your-organization>",
           app_name="<your-app>",
           model_name="<your-model>"
       )

    :raises:
        * `InvalidTokenError` - if improper API token is used or is missing entirely.
        * `InvalidParamError` - if improper connection parameters are passed.

    """
    params = _generate_required_params(kwargs)
    endpoint = "/organizations/{org_name}/apps/{app_name}/models/{model_name}/model_versions?order_by=version".format(**params)
    res = _http_request(
        method="GET",
        url=API_BASE_URL + endpoint,
        api_token=params["skafos_api_token"]
    ).json()

    versions = _clean_up_version_list(res)
    return versions

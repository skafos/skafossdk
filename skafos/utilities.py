import os
from .http import _http_request, API_BASE_URL
from .exceptions import InvalidTokenError


def get_version():
    r"""Returns the current version of the Skafos SDK in use.

    :Usage:
    .. sourcecode:: python

       import skafos

       skafos.get_version()

    """
    with open(os.path.join(os.path.dirname(__file__),  "VERSION")) as version_file:
        return version_file.read().strip()


def _get_organization_models(org_name, api_token):
    endpoint = "/organizations/{}/apps?with_models=true".format(org_name)
    res = _http_request(
        method="GET",
        url=API_BASE_URL + endpoint,
        api_token=api_token
    ).json()
    return res


def _full_summary(organizations, api_token):
    summary_res = []
    for org in organizations:
        org_dict = {"org_name": org["display_name"]}
        apps = _get_organization_models(org_name=org["display_name"], api_token=api_token)
        for app in apps:
            app_dict = org_dict.copy()
            app_dict["app_name"]= app["name"]
            for model in app["models"]:
                model_dict = app_dict.copy()
                model_dict["model_name"] = model["name"]
                summary_res.append(model_dict)
    return summary_res


def _compact_summary(organizations, api_token):
    summary_res = {}
    for org in organizations:
        summary_res[org["display_name"]] = {}
        apps = _get_organization_models(org_name=org["display_name"], api_token=api_token)
        for app in apps:
            summary_res[org["display_name"]][app["name"]] = []
            for model in app["models"]:
                model_meta_data = {k: model[k] for k in model.keys() & {"name", "updated_at"}}
                summary_res[org["display_name"]][app["name"]].append(model_meta_data)
    return summary_res


def summary(skafos_api_token=None, compact=False):
    r"""
    Returns all Skafos organizations, apps, and models that the provided API token has access to.

    .. note:: See the Usage Guide `Setting Up Your Environment` for some tips on using this function best within your workflow.

    :param skafos_api_token:
        Skafos API Token associated with the user account. Checks environment for 'SKAFOS_API_TOKEN' if not passed
        into the function directly. Get one at https://dashboard.skafos.ai --> Account Settings --> Tokens.
    :type skafos_api_token:
        str or None
    :param compact:
        If True, will return a collapsed version of the summary dictionary response. If False (default), will return a
        full response as a list of dictionaries including key names.
    :type compact:
        boolean
    :return:
        List or nested dictionary (compact version) of all organizations, apps, and models this user has access to.

    :Usage:
    .. sourcecode:: python

       import skafos

       skafos.summary(skafos_api_token="<YOUR-SKAFOS-API-TOKEN>", compact=False)

       [{"org_name": "my-organization", "app_name": "my-application", "model_name": "my-model"},
        {"org_name": "my-organization", "app_name": "my-application", "model_name": "my-other-model"}]

    :raises:
        * `InvalidTokenError` - if improper API token is used or is missing entirely.

    """
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
    ).json()

    if not compact:
        summary_res = _full_summary(organizations=res, api_token=skafos_api_token)
    else:
        summary_res = _compact_summary(organizations=res, api_token=skafos_api_token)

    # Return the summary response to the user
    return summary_res

import os
from .http import http_request, API_BASE_URL
from .exceptions import InvalidTokenError


def get_version():
    """Returns the current version of the Skafos SDK in use.

    :Usage:
    .. sourcecode:: python

       import skafos

       skafos.get_version()
    """
    with open(os.path.join(os.path.dirname(__file__),  "VERSION")) as version_file:
        return version_file.read().strip()


def summary(skafos_api_token=None, compact=False) -> dict:
    """
    Returns all Skafos organizations, apps, and models that the provided API token has access to.

    :param skafos_api_token:
        Skafos API Token associated with the user account. Checks environment for 'SKAFOS_API_TOKEN' if not passed
        into the function directly. Get one at https://dashboard.skafos.ai --> Account Settings --> Tokens.
    :type skafos_api_token:
        str or None
    :param compact:
        If True, will return a collapsed version of the summary dictionary response. If False (default), will return a
        fully-exploded response as a list of dictionaries including key names.
    :type compact:
        boolean
    :return:
        Nested dictionary of all organizations, apps, and models this user has access to.

    :Usage:
    .. sourcecode:: python

       import skafos

       skafos.summary(skafos_api_token="<YOUR-SKAFOS-API-TOKEN>")
    """
    # TODO - add sample response to docstring above
    # If not compact, return a list of dictionaries
    if not compact:
        summary_res = []
    else:
        summary_res = {}

    # Check for api token first
    if not skafos_api_token:
        skafos_api_token = os.getenv("SKAFOS_API_TOKEN")
    if not skafos_api_token:
        raise InvalidTokenError("Missing Skafos API Token")

    # Prepare requests
    method = "GET"
    endpoint = "/organizations"
    res = http_request(
        method=method,
        url=API_BASE_URL + endpoint,
        api_token=skafos_api_token
    ).json()
    for org in res:
        if not compact:
            org_dict = {"org_name": org["display_name"]}
        else:
            summary_res[org["display_name"]] = {}
        endpoint = "/organizations/{}/apps?with_models=true".format(org["display_name"])
        res = http_request(
            method=method,
            url=API_BASE_URL + endpoint,
            api_token=skafos_api_token
        ).json()
        for app in res:
            if not compact:
                org_dict["app_name"]= app["name"]
            else:
                summary_res[org["display_name"]][app["name"]] = []
            for model in app["models"]:
                if not compact:
                    org_dict["model_name"] = model["name"]
                    summary_res.append(org_dict)
                else:
                    model_meta_data = {k: model[k] for k in model.keys() & {"name", "updated_at"}}
                    summary_res[org["display_name"]][app["name"]].append(model_meta_data)

    # Return the summary response to the user
    return summary_res


def _get_user_res(opts: dict) -> str:
    options = "\n"
    for k, v in opts.items():
        options += "{} - {}\n".format(k, v)
    print(options, flush=True)
    x = input("Which would you like to choose: ")
    return opts.get(int(x))


def setup_env(skafos_api_token=None):
    print("Skafos Environment Setup", flush=True)

    if skafos_api_token:
        os.environ["SKAFOS_API_TOKEN"] = skafos_api_token

    summary_res = summary(skafos_api_token)

    # Enumerate orgs:
    orgs = dict(enumerate(summary_res.keys()))
    org = _get_user_res(orgs)
    if not org:
        return None

    # Enumerate apps:
    apps = dict(enumerate(summary_res[org].keys()))
    app = _get_user_res(apps)
    if not app:
        return None

    # Enumerate models:
    models = dict(enumerate([m["name"] for m in summary_res[org][app]]))
    model = _get_user_res(models)
    if not model:
        return None

    os.environ["SKAFOS_ORG_NAME"] = org
    os.environ["SKAFOS_APP_NAME"] = app
    os.environ["SKAFOS_MODEL_NAME"] = model

    return "success"

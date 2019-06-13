Setting Up Your Environment
---------------------------
While using the Skafos SDK, here are a few tips for getting your environment set up so you can work most efficiently.


Authorization
=============
All Skafos API calls require authentication through an API Token. You can find or delete your token on the
dashboard's account settings page. Once you have it, we recommend setting it in your environment as follows:

.. sourcecode:: python

   import os

   os.environ["SKAFOS_API_TOKEN"] = "<YOUR-SKAFOS-API-TOKEN>"

This way, your token will persist across all SDK function calls, removing the need to explicitly identify it
in function args.


Which Org, App, Model?
======================
All model version management utilities require you to identify which organization, application, and model you
would like to access. If you are unsure of these details, you can use :func:`skafos.summary()` to
discover that information provided you have set an API Token (as described above).

.. sourcecode:: python

   import skafos

   skafos.summary()

This function will output a dictionary that contains all orgs, apps, and models that your API Token has access to.

**Compact Version - **
Running the summary command with `compact=True` will return a nested dictionary that more efficiently
handles redundant information. However, some users may not find it as easy to work with.

.. sourcecode:: python

   import skafos

   skafos.summary(compact=True)

   {
       "my-organization": {
           "my-application": [
               {
                   "name": "my-model",
                   "updated_at": "2019-06-10T19:17:46"
               },
               {
                   "name": "my-other-model",
                   "updated_at": "2019-06-10T19:22:46"
               }
           ]
       }
   }

**Non-Compact Version - **
Setting `compact=False` (default) will return a more robust response as a list of dictionaries. Some users find
this more convenient because you can copy and paste a single record and pass that as connection parameters to any downstream function.
*See the section below about using a kwargs dictionary of connection parameters.*

.. sourcecode:: python

   import skafos

   skafos.summary(compact=False) # Default version

   [
       {
           "org_name": "my-organization",
           "app_name": "my-application",
           "model_name": "my-model"
       },
       {
           "org_name": "my-organization",
           "app_name": "my-application",
           "model_name": "my-other-model"
       }
   ]

Persisting Access
=================
We suggest one of two approaches to efficiently use the Skafos SDK.

**Using Environment Variables**

Similar to the API Token, you can set environment variables for your org name, app name, and model name.

.. sourcecode:: python

   import os
   from skafos import models

   os.environ["SKAFOS_ORG_NAME"] = "<YOUR-ORG-NAME>"
   os.environ["SKAFOS_APP_NAME"] = "<YOUR-APP-NAME>"
   os.environ["SKAFOS_MODEL_NAME"] = "<YOUR-MODEL-NAME>"


   models.fetch_version(version=2)

   models.list_versions()


This method is best if you plan to do repeated work with a single org/app/model. As shown in the code above, you won't
have to include the params in each function call.

**Using a Dictionary**

Most SDK methods take a dictionary of kwargs containing this info.

.. sourcecode:: python

   from skafos import models

   opts = {
       "org_name": "<YOUR-ORG-NAME>",
       "app_name": "<YOUR-APP-NAME>",
       "model_name": "<YOUR-MODEL-NAME>"
   }

   models.fetch_version(**opts)  # valid function call


Ad-Hoc Access
=============
If you only need to execute a single function call, you can always supply the arguments to the function itself.

.. sourcecode:: python

   from skafos import models

   models.fetch_version(
       org_name="<YOUR-ORG-NAME>",
       app_name="<YOUR-APP-NAME>",
       model_name="<YOUR-MODEL-NAME>"
   )


Exceptions
==========
If you supply an incorrect param or are missing a required param, the SDK will throw a `InvalidParamError` or
`InvalidTokenError` exception.

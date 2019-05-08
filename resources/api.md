# Skafos Python SDK

- Staging: `https://api.skafos.wtf/v2`
- Production: `https://api.skafos.ai/v2`

All endpoints use `SKAFOS_API_TOKEN` supplied in the header for authentication.

## Upload Model Versions
Upload a file, or list of files, compress them to a zip. Make 3 API calls:

**First Call:**
Creates model version record in DB and returns a pre-signed URL for storage. Model version id 
and filepath left empty in DB until after successful upload to storage. 

How will the user know the model_id?

- Request: `POST`
- Path: `/organizations/<org-name-or-id>/apps/<app-name-or-id>/models/<model-name-or-id>/model_versions`
- Body: `{"filename": "", "description": ""}`
- Response: `{"filepath": "", "model_version_id": "", "presigned_url": ""}`
- Errors: 404, 201, 409, 409, 500

Can we get a special message for when an app or model don't exist?
Likely from a 404(not found)/409(conflict) from backend routes and controllers.

**Second Call:**
Uploads model to storage.

- Request: `PUT`
- Header: `{"Content-Type": "application/octet-stream"}`
- URL: Presigned URL from last request response
- Data: file object to upload (byte stream)
- Response: 200 is returned on success, no body

**Third Call:**
Updates the model version record in DB after successful upload.

- Request: `PATCH`
- Path: `/organizations/<org-name-or-id>/apps/<app-name-or-id>/models/<model-name-or-id>/model_versions/<model-version-id>` model_version_id form first request
- Body: `{"filepath": ""}` filepath from first request
- Response: a bunch of metadata

## Downloading a Model Version
Retrieve a model version from storage.
Version not required (it defaults to latest if you not supplied).

- Request: `GET`
- Path: `/organizations/<org-id>/app/<app-name-or-id>/models/<model-name-or-id>?version=<version>`
- Response: 200 if successful and file will download

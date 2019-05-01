# Skafos Python SDK

- Staging: `https://api.skafos.wtf/v2`
- Production: `https://api.skafos.ai/v2`

All endpoints will need to be adjusted to use API-token authentication instead of organization id, etc.

## Create a Model in an App
May not do this in the Python SDK. Likely out of scope. Create a new model.
Think of this as a "bin" for models of a particular type.

- Request: `POST`
- Path: `/organizations/<org-name-or-id>/apps/<app-name-or-id>/models`
- Body: `{"name": "", "description": ""}`
- Response: `{"updated_at": "", "public": "", "name": "", "inserted_at": "", "id": "", "description": "", "app_id": ""}`


## Upload Model Versions
Upload a file, or list of files, compress them to a zip, then hit 2 endpoints:

**First Call:**
Create model version record in postgres and return the s3 pre-signed URL. Model version id 
and filepath left empty in DB until after successful upload to s3. 

How will the user know the model_id?

- Request: `POST`
- Path: `/organizations/<org-name-or-id>/apps/<app-name-or-id>/models/<model-name-or-id>/model_versions`
- Body: `{"model_id": "", "file_name": "", "description": ""}`
- Response: `{"filepath": "", "model_version_id": "", "presigned_url": ""}`
- Errors: 404, 201, 409, 409, 500

Can we get a special message for when an app or model don't exist?
Likely from a 404(not found)/409(conflict) from backend routes and controllers.

**Second Call:**
Upload model to s3: `s3://skafos.staging-mlmodels/<org-id>/<app-id>/<model-id>/<zipfile>`.

- Request: `PUT`
- Header: `{"Content-Type": "application/octet-stream"}`
- URL: Presigned URL from last request response
- File: file object to upload
- Response: 200 is returned on success no body

**Third Call:**
Update the model version record in postgres after successful write to s3.

- Request: `PATCH`
- Path: `/organizations/<org-name-or-id>/apps/<app-name-or-id>/models/<model-name-or-id>/model_versions/<model-version-id>` model_version_id form first request
- Body: `{"filepath": ""}` filepath from first request
- Response: `{}` big thing
- Errors: Generic error thrown when there is an upload error.

## Downloading a Model Version
Retrieve a model version from s3. (Optionally) unzip archive once downloaded.
Likely need a new endpoint for this to supply the user with the ability to pass in their model version (`version`) or default to latest.

- Request: `GET`
- Path: `/organizations/<org-id>/app/<app-name-or-id>/models/<model-name-or-id>/model_versions/<model_version_id>/`
- Response: 200 if successful and file will download

# Skafos Python SDK
<img src="https://raw.githubusercontent.com/skafos/skafossdk/master/resources/skafos_mark.jpg" width="50" height="50" align="left"/>

[Skafos](https://skafos.ai) is the platform for automating the delivery of machine learning models to mobile devices.
We provide this SDK as a Python wrapper for uploading, fetching, and listing model versions from the platform. 

If you're a Data Scientist or Machine Learning Engineer, you're the one entrusted with building robust machine
learning models. This SDK is an interface to the Skafos platform, allowing you to do the
following from your Python development environment:

- **Upload a model version**: Save a new version of your machine learning model to the Skafos platform,
making it available for mobile delivery.
- **Fetch a model version**: Download a previously saved version of your machine learning model from
the Skafos platform.
- **List model versions**: For each of your apps and models, see what model versions you have previously
saved to the Skafos platform.


## Supported Platforms

#### Operating Systems
This is not an exhaustive list of OS that are compatible with `skafos`. These are the one's we've explicitly tested:
- macOS 10.12+
- Linux (Ubuntu 16.0.4+)

#### Cloud Platforms
- Google Colab
- IBM Watson
- *Others coming soon*

## System Requirements
- Python 3+
- [Pip](https://pip.pypa.io/en/stable/installing/) (to download `skafos` from the Python Package Index)


## Installation
You can install `skafos` directly from the Python Package Index [(PyPI)](https://pypi.org/).
```bash
pip install -U skafos
```

Once you've installed `skafos`, you can import the package in your Python environment.
```python
import skafos
skafos.get_version() # returns the current SDK version
```
For more details on installation and usage, see the package documentation.


## Documentation
- The [package documentation](https://sdk.skafos.ai) contains more details on how to use the Skafos SDK.
- The [platform documentation](https://docs.metismachine.io) contains more details on how Skafos delivers
and manages machine learning models on mobile devices.


## Example: Uploading a Model Version

```python
import os
from skafos import models

# Set your API Token first for repeated use
os.environ["SKAFOS_API_TOKEN"] = "<YOUR-SKAFOS-API-TOKEN>"

# You can retrieve this info with skafos.summary()
org_name = "<YOUR-SKAFOS-ORG-NAME>"    # Example: "mike-gmail-com-467h2"
app_name = "<YOUR-SKAFOS-APP-NAME>"    # Example: "Recommender-App"
model_name = "<YOUR-MODEL-NAME>"       # Example: "RecommenderModel"

# Upload model version to Skafos
model_upload_result = models.upload_version(
    files="<path(s)-to-model-file(s)>", # Example: ["../my_recommender_model.mlmodel"]
    org_name=org_name,
    app_name=app_name,
    model_name=model_name
)
```


## Need Help?
Didn't find something you need? Confused by something? Need more guidance?

Please contact us with questions or feedback! Here are two ways:

-  [**Signup for our Slack Channel**](https://join.slack.com/t/metismachine-skafos/shared_invite/enQtNTAxMzEwOTk2NzA5LThjMmMyY2JkNTkwNDQ1YjgyYjFiY2MyMjRkMzYyM2E4MjUxNTJmYmQyODVhZWM2MjQwMjE5ZGM1Y2YwN2M5ODI)
-  [**Find us on Reddit**](https://reddit.com/r/skafos)

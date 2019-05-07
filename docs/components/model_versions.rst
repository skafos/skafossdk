Model Versions
==============
A model version is a particular version or instance of a model. It refers to an actual machine learning model
artifact that was uploaded to Skafos and will be delivered to your iOS application. Skafos auto-versions your
machine learning models when you upload them to the platform. You MUST upload a zipped archive.

.. note:: Do not get confused! A model version refers to a specific instance of a model (with the same :attr:`model_name`).

Each model version has a :attr:`version` and a :attr:`description` that you should use to identify it from others.

.. Skafos SDK documentation master file, created by
   sphinx-quickstart on Wed May  1 15:59:14 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

:github_url: https://github.com/skafos/skafossdk

Skafos SDK Documentation
________________________

.. image:: https://raw.githubusercontent.com/skafos/skafossdk/master/resources/skafos_mark.jpg
   :width: 50px
   :height: 50px
   :align: left

`Skafos <https://skafos.ai/>`_ is the platform for automating the delivery of machine learning models to mobile devices.
We provide this SDK as a Python wrapper for uploading, fetching, and listing model versions from the platform.

If you're a Data Scientist or Machine Learning Engineer, you're the one entrusted with building robust machine
learning models. This SDK is an interface to the Skafos platform, allowing you to do the
following from your Python development environment:

**Upload a model version**: Save a new version of your machine learning model to the Skafos platform,
making it available for mobile delivery.

**Deploy a model version**: Deliver a saved model version to your mobile application over-the-air.

**Fetch a model version**: Download a previously saved version of your machine learning model from
the Skafos platform.

**List model versions**: For each of your apps and models, see what model versions you have previously
saved to the Skafos platform.


Contents
========

.. toctree::
   :glob:
   :maxdepth: 1
   :caption: Installation

   install.rst

.. toctree::
   :glob:
   :maxdepth: 1
   :caption: SDK Reference

   reference/models.rst
   reference/exceptions.rst
   reference/utilities.rst

.. toctree::
   :glob:
   :maxdepth: 1
   :caption: Skafos Components

   components/organizations.rst
   components/apps.rst
   components/models.rst
   components/model_versions.rst

.. toctree::
   :maxdepth: 1
   :caption: Usage Guides

   example_usage/env_setup.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

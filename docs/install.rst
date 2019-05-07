Skafos SDK Installation
-----------------------

The primary method of installing the SDK in your python environment is with pip:

.. code-block:: bash

   pip install skafos

Or, if you prefer to build from source code directly, you can do the following:

.. code-block:: bash

   git clone https://github.com/skafos/skafossdk.git
   cd skafossdk/
   python setup.py

Once installed you should be able to import skafos to your python env as follows:

.. code-block:: python

   import skafos
   skafos.get_version()


.. warning:: The Skafos SDK is only compatible with Python 3.6+.

Changing Storage Backend
========================

Out of the box, LineaPy is the default storage backend for all artifacts.
For certain storage backends in use (e.g., storing model artifacts in MLflow), saving one more copy of the same artifact into LineaPy causes sync issue between the two systems.
Thus, LineaPy supports using different storage backends for certain data types (e.g., ML models).
This support is essential for users to leverage functionalities from both LineaPy and other familiar toolkit (e.g., MLflow).

.. note::

   Storage backend refers to the overall system handling storage and should be distinguished from specific storage locations such as Amazon S3.
   For instance, LineaPy is a storage backend that can use different storage locations.

.. toctree::
   :maxdepth: 1

   mlflow

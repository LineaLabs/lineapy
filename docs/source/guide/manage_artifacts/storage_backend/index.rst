Changing Storage Backend
========================

Out of the box, LineaPy is the default storage backend for all artifacts.
For some existing storage systems(MLflow, database ...) used to save artifacts; saving one more copy in LineaPy causes syncing issue between the two systems.
Thus, LineaPy supports using different storage backends for some data types.
This support is essential for users to leverage functionalities from both LineaPy and their familiar tools.

Currently, LineaPy supports MLflow as a storage backend for ML models.

.. toctree::
   :maxdepth: 1

   mlflow

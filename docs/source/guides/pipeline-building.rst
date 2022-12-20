.. _pipeline_basics:

Building a Pipeline from Development Code
=========================================

.. include:: /snippets/slack_support.rstinc

To generate a pipeline from development code, first ensure variable(s) of interest have been
stored as LineaPy artifacts:

.. code-block:: python

    lineapy.save(<VARIABLE-NAME>, "<artifact_name>")

Then, building a pipeline reduces to “stitching” these artifacts, like so:

.. code-block:: python

    lineapy.to_pipeline(
        pipeline_name="<pipeline_name>",
        artifacts=["<artifact_name>", ...],
        dependencies={
            "<artifact_name>": {"<artifact_name>", ...},
            ...
        },
        output_dir="<output_dirpath>",
        framework="<framework_name>",
    )

where

* ``pipeline_name`` is the name of the pipeline

* ``artifacts`` is the list of artifact names to be used for the pipeline

* ``dependencies`` is the dependency graph among artifacts

    * If artifact A depends on artifacts B and C, then the graph is specified as ``{ A: { B, C } }``

    * If A depends on B and B depends on C, then the graph is specified as ``{ A: { B }, B: { C } }``

* ``output_dir`` is the location to put the files for running the pipeline

* ``framework`` is the name of orchestration framework to use

    * LineaPy currently supports ``"AIRFLOW"`` and ``"SCRIPT"``

    * If ``"AIRFLOW"``, it will generate files that can run Airflow DAGs

    * If ``"SCRIPT"``, it will generate files that can run the pipeline as a Python script

.. note::

    Check :func:`lineapy.to_pipeline` for more detailed API information.

Airflow Example
---------------

For example, consider a simple pipeline that 1) pre-processes raw data and 2) trains a model with the pre-processed data.

.. image:: /_static/images/pipeline-example-diagram.png
    :width: 600
    :align: center
    :alt: Pipeline Example

With the pre-processed data and the trained model stored as LineaPy artifacts (which can be done during development sessions),
building an Airflow pipeline becomes as simple as the following:

.. code:: python

   lineapy.to_pipeline(
      pipeline_name="iris_pipeline",
      artifacts=["iris_preprocessed", "iris_model"],
      dependencies={"iris_model": {"iris_preprocessed"}},
      output_dir="~/airflow/dags/",
      framework="AIRFLOW",
   )

where ``{"iris_model": {"iris_preprocessed"}}`` is a way to indicate that the ``"iris_model"`` artifact
depends on the ``"iris_preprocessed"`` artifact.

Running this creates files (under ``output_dir``) that can be used to execute the pipeline as an Airflow DAG, including:

* ``<pipeline_name>_module.py``: Contains the artifact code refactored and packaged as function(s)

* ``<pipeline_name>_dag.py``: Uses the packaged function(s) to define the framework-specific pipeline

* ``<pipeline_name>_requirements.txt``: Lists any package dependencies for running the pipeline

* ``<pipeline_name>_Dockerfile``: Contains commands to set up the environment to run the pipeline

where ``<pipeline_name>`` is ``iris_pipeline`` in the current example.

Running Locally
---------------

With the pipeline files generated, we can quickly test running the pipeline locally.
First, run the following command to build a Docker image:

.. code:: bash

    docker build -t <image_name> . -f <pipeline_name>_Dockerfile

where ``<pipeline_name>_Dockerfile`` is the name of the automatically generated Dockerfile and
``<image_name>`` is the image name of our choice.

We then stand up a container instance with the following command:

.. code:: bash

    docker run -it -p 8080:8080 <image_name>

For ``framework="AIRFLOW"``, this will result in an Airflow instance
with an executable DAG in it.

.. include:: /snippets/docs_feedback.rstinc

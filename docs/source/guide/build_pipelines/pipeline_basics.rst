Basics
======

Data science workflows revolve around building and refining pipelines, i.e.,
a series of processes that transform data into useful information/product.

Traditionally, this is often manual and time-consuming work as data scientists
(or production engineers) need to transform messy development code into
deployable scripts for the target system (e.g., Airflow).

Having the complete development process stored in artifacts, LineaPy can automate
such code transformation, accelerating transition from development to production.

LineaPy Pipelines
-----------------

In LineaPy, a pipeline is an entity consisting of multiple artifacts and their
dependency relationships. For instance, consider a simple pipeline that
1) pre-processes raw data and 2) trains a model with the pre-processed data.

.. image:: pipeline.png
  :width: 600
  :align: center
  :alt: Pipeline Example

In LineaPy, this corresponds to a pipeline object that contains:

- Pre-processed data artifact
- Trained model artifact
- Dependency between the two artifacts (i.e., trained model depends on pre-processed data)

Once organized into this general form, a pipeline can then remold itself to support various
framework-specific deployments (e.g., Airflow DAGs).

Creating a Pipeline
-------------------

Once we have desired results stored as LineaPy artifacts (which can be done during development),
creating a pipeline reduces to “stitching” these artifacts, like so:

.. code:: python

   import lineapy

   # Load artifacts to use in pipeline building
   preprocessing_art = lineapy.get("iris_preprocessed")
   modeling_art = lineapy.get("iris_model")

   # Create a pipeline using artifacts
   pipeline = lineapy.create_pipeline(
      pipeline_name="demo_airflow_pipeline",
      artifacts=[preprocessing_art.name, modeling_art.name],
      dependencies={modeling_art.name: {preprocessing_art.name}},
   )

where ``{modeling_art.name: {preprocessing_art.name}}`` is a way to indicate that
the trained model depends on the pre-processed data (which then sets the order of computation).

Hence, a LineaPy pipeline is uniquely identified by a list of artifacts (at a version)
and their dependencies.

Saving a Pipeline
-----------------

Note that :func:`lineapy.create_pipeline` returns a pipeline object but does not save it into
the database automatically. To store a pipeline object into the database, we can use the pipeline's
``save()`` method:

.. code:: python

   # Save the pipeline into DB
   pipeline.save()

Alternatively, we can set ``persist=True`` during pipeline creation, like so:

.. code:: python
   :emphasize-lines: 6

   # Create and save a pipeline
   pipeline = lineapy.create_pipeline(
      pipeline_name="demo_airflow_pipeline",
      artifacts=[preprocessing_art.name, modeling_art.name],
      dependencies={modeling_art.name: {preprocessing_art.name}},
      persist=True,
   )

which creates *and* saves the pipeline at once.

Reusing a Pipeline
------------------

What Next?
----------

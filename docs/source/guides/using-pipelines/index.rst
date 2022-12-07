.. _pipelines:

Using Pipelines
===============

Data science workflows revolve around building and refining :ref:`pipelines <pipeline_concept>`.

Traditionally, this is often manual and time-consuming work as data scientists (or production engineers) need to transform messy development code
into deployable scripts for the target system (e.g., Airflow).

Having the complete development process stored in artifacts, LineaPy can automate such code transformation, accelerating transition from development to production.

.. toctree::
   :maxdepth: 1

   pipeline-building
   pipeline-parametrization
   pipeline-testing
   .. pipeline-reusing-precomputed

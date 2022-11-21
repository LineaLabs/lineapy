.. _pipelines:

Pipelines
=========

Data science workflows revolve around building and refining pipelines, i.e., a series of processes that transform data into useful information/product
(read more about pipelines :ref:`here <pipeline_concept>`).

Traditionally, this is often manual and time-consuming work as data scientists (or production engineers) need to transform messy development code
into deployable scripts for the target system (e.g., Airflow).

Having the complete development process stored in artifacts, LineaPy can automate such code transformation, accelerating transition from development to production.

.. toctree::
   :maxdepth: 1

   pipeline_basics
   pipeline_parametrization
   pipeline_testing
   .. pipeline_reusing_precomputed

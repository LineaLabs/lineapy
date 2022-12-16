
    

### Use Case 2: Revisiting Previous Work

Data science is often a team effort where one person's work relies on results from another's. For example,
a data scientist building a model may use features engineered by other colleagues. When using results generated
by other people, we may encounter data quality issues including missing values, suspicious numbers, and
unintelligible variable names. When we encounter these issues, we may need to check how these results came into
being in the first place. Often, this means tracing back the code that was used to generate the result in question.
In practice, this can be a challenging task because we may not know who produced the result. Even if we know who
to ask, that person might not remember where the exact version of the code is stored, or worse, may have overwritten
the code without version control. Additionally, the person may no longer be at the organization and may not have
handed over the relevant knowledge. In any of these cases, it becomes extremely difficult to identify the root any
issues, rendering the result unreliable and even unusable.

.. note::

    To see how LineaPy can help here, check out `discovering and tracing past work <https://github.com/LineaLabs/lineapy/blob/v0.2.x/.colab/discover_and_trace_past_work/discover_and_trace_past_work.ipynb>`_ demo.

Use Case 3: Building Pipelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As our notebooks become more mature, we may use them like pipelines. For example, our notebook might process the latest data to update a dashboard, or pre-process data and dump it into the file system for downstream model development. To keep our results up-to-date, we might be expected to re-execute these processes on a regular basis. Running notebooks manually is a brittle process that's prone to errors, so we may want to set up proper pipelines for production. If relevant engineering support is not available, we need to clean up and refactor our notebook code so that it can be used in orchestration systems or job schedulers, such as cron, Apache Airflow, or Prefect. Of course, this assumes that we already know how these tools work and how to use them &mdash; If not, we need to spend time learning about them in the first place! All this operational work is time-consuming, and detracts from the time that we can spend on our core duties as a data scientist.

.. note::

    To see how LineaPy can help here, check out `creating pipelines <https://github.com/LineaLabs/lineapy/blob/v0.2.x/.colab/create_a_simple_pipeline/create_a_simple_pipeline.ipynb>`_ demo.


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Quickstart

   tutorials/00_lineapy_quickstart


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Concepts

   concepts/artifact
   concepts/artifact-store
   concepts/pipeline


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Tutorials

   tutorials/01_using_artifacts
   tutorials/02_pipeline_building


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Guides

   guides/installation
   guides/configuration/index
   guides/interfaces
   guides/code-cleanup
   guides/package-annotation
   guides/artifact-reuse
   guides/pipeline-building
   guides/pipeline-parametrization
   guides/pipeline-testing
   guides/contribute/index
   guides/troubleshoot
   guides/support


.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: References

   references/api_reference

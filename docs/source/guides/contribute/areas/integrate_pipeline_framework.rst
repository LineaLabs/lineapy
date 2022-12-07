Integrate a New Pipeline Framework
==================================

.. include:: ../../snippets/slack_support.rstinc

One major feature of Lineapy is the ability to create pipelines that run various pipeline orchestration frameworks.
We believe that supporting pipeline frameworks to meet data engineers where they are with their current stacks provides the best user experience for reducing manual work of pipeline writing.

Read more about the concept of a pipeline :ref:`here <pipeline_concept>` and Lineapy Pipelines :ref:`here <pipelines>`.

In this tutorial we will go through how to write an new pipeline integration. We'll first go through important concepts before diving into concrete steps. If you want to dive right into the concrete steps, skip ahead to the :ref:`checklist <pipeline_integration_checklist>`.


This tutorial will use airflow as an illustrative example, but there may not be a one-size-fits-all approach for all integrations so please adapt the content in this guide to suite your individual needs.

The module file
---------------

The module file contains all the user code from the original notebook needed to run a pipeline. The module file is one of a few files that Lineapy generates to create pipelines, an overview of which can be found here :ref:`here <iris_pipeline_module>`.

The module file contains code that is already cleaned and refactored based on parameters passed to a ``to_pipeline`` call and is presented as a python module file. 

This file can and should be used by integrations. The key for new integrations is to figure out how to call these functions within the constraints of their framework. Fortunately, we provide another abstraction to help make this easy. 


What is a TaskDefinition?
--------------------------

TaskDefinition is the abstraction that Lineapy provides integration writers that provides all the information needed to call the functions in the module file.
Our goal is to have TaskDefinition provide modular blocks that can be used by multiple frameworks with some help from Jinja templating to provide framework specific syntax. 

.. note::
    The key idea behind a TaskDefinition is that we believe that a task should correspond to whatever the "unit of execution" is for your framework. 
    For example, in Airflow, this would be the concept of an Operator.

For the latest attributes in TaskDefinition, please refer to our API reference: :class:`lineapy.plugins.task.TaskDefinition`.

.. note::
    If you feel a code block is missing from TaskDefinition create a separate PR to add it along with an example of why your framework needs it.

Getting TaskDefinitions
------------------------

Functions to get TaskDefinitions should be located in ``lineapy/plugins/taskgen.py``.

For integration writer the most important function is ``get_task_definitions``. Given a task breakdown granularity, it will return a dictionary mapping function name to TaskDefinitions. Framework specific pipeline integrations should call this to get TaskDefinitions that can be rendered using framework specific syntax.

Getting dependencies between TaskDefinitions 
---------------------------------------------


Many data pipeline frameworks require some type of specification of the dependencies between the tasks so their schedulers can schedule tasks appropriately.


Currently ``get_task_definitions`` returns TaskDefinitions in a dictionary which when iterated through returns tasks in a topological sorted order. This means if your framework supports setting runtime dependencies between tasks setting a linear execution order will guarantee correctness when executing the pipeline. See AirflowPipelineWriter ``_write_operators`` for an example of this.

.. note::
    Data dependencies is work in progress, and when completed should allow us to specify dependencies in a way to give integration writers parallelizable task graphs.

.. _pipeline_integration_checklist:

Writing a new integration checklist
-----------------------------------

#. Create new pipeline writer file in ``lineapy/plugins/``
#. Register a new ``PipelineType`` in ``lineapy/data/types.py``
#. Add your new pipeline writer to the ``PipelineWriterFactory`` in ``lineapy/plugins/pipeline_writer_factory``
#. Ensure your Pipeline writer will write the module file. 

    * Make sure your Pipeline writer inherits ``_write_module``, usually this will be automatically inherited from BasePipelineWriter
    * Make sure your Pipeline writer implementation of ``write_pipeline_files`` which calls ``_write_module``. 

#. Implement ``_write_dag`` for your pipeline writer.

    Suggested steps for ``_write_dag`` with examples in ``AirflowPipelineWriter``:

    #.  `Get TaskDefinitions <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L159>`_

        .. code-block:: python

            task_defs: Dict[str, TaskDefinition] = get_task_definitions( ... )

    #.  `Handle dependencies between tasks <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L185>`_
        
        .. code-block:: python

            dependencies = {
                task_names[i + 1]: {task_names[i]}
                for i in range(len(task_names) - 1)
            }

    #.  `Render TaskDefinitions <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L181>`_
        
        .. code-block:: python

            TASK_FUNCTION_TEMPLATE = load_plugin_template(
                "task/task_function.jinja"
            )
            rendered_task_defs: List[str] = []
            for task_name, task_def in task_defs.items():
                ...
                task_def_rendered = TASK_FUNCTION_TEMPLATE.render( 
                    ... 
                )
                rendered_task_defs.append(task_def_rendered)

            return rendered_task_defs


    #.  `Render rest of DAG <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L204>`_

        .. code-block:: python

            DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")

            ...

            full_code = DAG_TEMPLATE.render(
                DAG_NAME=self.pipeline_name,
                MODULE_NAME=self.pipeline_name + "_module",
                ...
                task_definitions=rendered_task_defs,
                task_dependencies=task_dependencies,
            )

#. If your framework can be run in a dockerized container, write a Jinja template that sets up an environment with your pipeline framework installed that can run the produced DAGs. Specify the ``docker_template_name`` property so the write ``_write_docker`` function loads the correct Jinja template.

    .. code-block:: python

        @property
        def docker_template_name(self) -> str:
            return "airflow_dockerfile.jinja"



Using Templates
---------------

You may have noticed at this point that the last few bullet points in the checklist involve rendering and using Jinja templates. Jinja templates are Lineapy's preferred way of templating the code that we generate.

All of the templates that are used in Lineapy can be found in the `templates directory <https://github.com/LineaLabs/lineapy/tree/main/lineapy/plugins/jinja_templates>`_. 
These templates are loaded using the ``load_plugin_template`` command as illustrated in the examples above, and can be rendered using the ``render`` method while passing in values for the placeholder variables.

Feel free to skim some of the templates we have already created for an idea on how we use these templates. Online tutorials are also helpful, the "Getting started with Jinja" sections on `this one <https://realpython.com/primer-on-jinja-templating/#get-started-with-jinja>`_ are a good place to start. 

Testing
-------

As a pipeline integration contributor we also greatly appreciate adding tests for your new integration!

Snapshot tests should be added to ``tests/unit/plugins/test_writer.py::test_pipeline_generation`` by adding new parameters corresponding to your framework.
Be sure to also run pytest with the ``--snapshot-update`` flag and commit the snapshot files.

.. code-block:: python
    
    # Example pytest param to test AIRFLOW framework on simple pipeline
    pytest.param(
        "simple",
        "",
        ["a", "b0"],
        "AIRFLOW",
        "airflow_pipeline_a_b0_inputpar",
        {},
        {"dag_flavor": "PythonOperatorPerArtifact"},
        ["b0"],
        id="airflow_pipeline_a_b0_input_parameter_per_artifact",
    )


End to end tests such as the one found for airflow in ``tests/test_pipeline_run_airflow.py`` are also highly recommended but much more involved as they require setting up a environment that can run the framework you are providing an integration for and having APIs to check the dag runs successfully.
Please consult your individual framework's documentation and add these tests if possible.

.. include:: ../../../snippets/docs_feedback.rstinc

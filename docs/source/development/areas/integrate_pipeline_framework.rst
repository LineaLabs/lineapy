Integrate a New Pipeline Framework
==================================

.. include:: ../../snippets/slack_support.rstinc

One major feature of Lineapy is the ability to create pipelines that run various pipeline orchestration frameworks.
We believe that supporting pipeline frameworks to meet data engineers where they are with their current stacks provides the best user experience and reducing manual work for writing pipelines.

In this tutorial we will go through how to write an new pipeline integration. We'll first go through important concepts before diving into concrete steps.
This tutorial will use airflow as an illustrative example, but there may not be a one size fits all approach for all integrations so please adapt the content in this guide to suite your individual needs.

The module file
---------------

The module file contains all the user code from the original notebook needed to run a pipeline. 
The code is already cleaned and refactored code based on parameters passed to a ``to_pipeline call`` and is presented as a python module file. 

This file can and should be used by integrations. Pipeline writers should inherit ``_write_module`` and make sure their inherited or implemented version of ``write_pipeline_files`` calls ``_write_module``. 

The key for new integrations is to figure out how to call these functions within the constraints of their framework. Fortunately, we provide another abstraction to help make this easy. 


What is a task definition?
--------------------------

Task Definition is the abstraction that Linea provides integration writers that provides all the information needed to call the functions in the module file.
Our goal is to have TaskDefinition provide modular blocks that can be used by multiple frameworks with some help from templating to provide framework specific syntax. 

.. note::
    The key idea behind a TaskDefinition is that we believe that a task should correspond to whatever the "unit of execution" is for your framework. 
    For example, in Airflow, this would be the concept of an Operator.

For the latest attributes in TaskDefinition, please refer to our `API reference <https://docs.lineapy.org/en/latest/autogen/lineapy.plugins.html?highlight=TaskDefinition#lineapy.plugins.task.TaskDefinition>`_.

.. note::
    If you feel there a code block is missing from task definition create a separate PR to add it along with an example of why your framework needs it.

Getting task definitions
------------------------

Functions to get TaskDefinitions should be located in ``lineapy/plugins/taskgen.py``.

For integration writer the most important function is ``get_task_definitions``. Given a task breakdown granularity, it will return a dictionary mapping function name to task definitions. Framework specific pipeline integrations should call this to get TaskDefinitions that can be rendered using framework specific syntax.

Getting dependencies between task definitions 
---------------------------------------------


Many data pipeline frameworks require some type of specification of the dependencies between the tasks so their schedulers can schedule tasks appropriately.

Currently ``get_task_definitions`` returns TaskDefinitions in a dictionary which when iterated through returns tasks in a topological sorted order. This means if your framework supports setting runtime dependencies between tasks setting a linear execution order will guarantee correctness when executing the pipeline. See AirflowPipelineWriter ``_write_operators`` for an example of this.

Data dependencies is work in progress, and when completed should allow us to specify dependencies in a way to give integration writers parallelizable task graphs.


Writing a new integration checklist
-----------------------------------

#. Create new pipeline writer file in ``lineapy/plugins/``
#. Register a new ``PipelineType`` in ``lineapy/data/types.py``
#. Add your new pipeline writer to the ``PipelineWriterFactory`` in ``lineapy/plugins/pipeline_writer_factory``
#. Implement ``_write_dag`` for your pipeline writer. 

Suggested steps for ``_write_dag`` with examples in ``AirflowPipelineWriter``:

#.  `Get task definitions <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L159>`_

    .. code-block:: python

        task_defs: Dict[str, TaskDefinition] = get_task_definitions( ... )

#.  `Handle dependencies between tasks <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L185>`_
    
    .. code-block:: python

        dependencies = {
            task_names[i + 1]: {task_names[i]}
            for i in range(len(task_names) - 1)
        }

#.  `Render task definitions <https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L181>`_
    
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
# Integrate a New Pipeline Framework

One major feature of LineaPy is the ability to create pipelines that run various pipeline orchestration frameworks.
We believe that supporting pipeline frameworks to meet data engineers where they are with their current stacks provides the best user experience for reducing manual work of pipeline writing.

In this guide, we will go through how to write an new pipeline integration. We will first go through important concepts before diving into concrete steps. If you want to dive right into the concrete steps, skip ahead to the [checklist](#checklist-for-writing-a-new-integration).

We will use Airflow as an illustrative example, but there may not be a one-size-fits-all approach for all integrations so please adapt the content in this guide to suite your individual needs.

## The Module File

The module file contains all the user code from the original notebook needed to run a pipeline. The module file is one of a few files that LineaPy generates to create pipelines, an overview of which can be found [here](../../usage/pipeline-building.md#airflow-example).

The module file contains code that is already cleaned and refactored based on parameters passed to a [`lineapy.to_pipeline()`][lineapy.api.api.to_pipeline] call and is presented as a Python module file. 

This file can and should be used by integrations. The key for new integrations is to figure out how to call these functions within the constraints of their framework. Fortunately, we provide another abstraction to help make this easy. 

## What is a `TaskDefinition`?

`TaskDefinition` is the abstraction that LineaPy provides integration writers that provides all the information needed to call the functions in the module file.
Our goal is to have `TaskDefinition` provide modular blocks that can be used by multiple frameworks with some help from Jinja templating to provide framework specific syntax. 

!!! tip

    The key idea behind a `TaskDefinition` is that we believe that a task should correspond to whatever the "unit of execution" is for your framework. 
    For example, in Airflow, this would be the concept of an Operator.

For the latest attributes in `TaskDefinition`, please refer to our [API reference][lineapy.plugins.task.TaskDefinition].

!!! note

    If you feel a code block is missing from `TaskDefinition`, create a separate PR to add it along with an example of why your framework needs it.

## Getting `TaskDefinition`s

Functions to get `TaskDefinition`s should be located in [`lineapy/plugins/taskgen.py`](https://github.com/LineaLabs/lineapy/blob/main/lineapy/plugins/taskgen.py).

For integration writer, the most important function is `get_task_graph`. Given a task breakdown granularity, it will return a dictionary mapping function name to `TaskDefinition`s along with a `TaskGraph` that specifies the dependencies needed to be added between tasks. 
Framework specific pipeline integrations should call this to get `TaskDefinition`s that can be rendered using framework specific syntax.

## Checklist for Writing a New Integration

1. Create new pipeline writer file in `lineapy/plugins/`.

2. Register a new `PipelineType` in `lineapy/data/types.py`.

3. Add your new pipeline writer to the `PipelineWriterFactory` in `lineapy/plugins/pipeline_writer_factory`.

4. Ensure your Pipeline writer will write the module file.

    * Make sure your Pipeline writer inherits `_write_module`, usually this will be automatically inherited from BasePipelineWriter

    * Make sure your Pipeline writer implementation of `write_pipeline_files` which calls `_write_module`. 

5. Implement `_write_dag` for your pipeline writer.

    Suggested steps for `_write_dag` with examples in `AirflowPipelineWriter`:

    a. [Get `TaskGraph`](https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L159):

    ```python
    task_defs, task_graph = get_task_graph( ... )
    ```

    b. [Handle dependencies between tasks](https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L185):
        
    ```python
    dependencies = {
        task_names[i + 1]: {task_names[i]}
        for i in range(len(task_names) - 1)
    }
    ```

    c. [Render `TaskDefinition`s](https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L181):
        
    ```python
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
    ```

    d. [Render rest of DAG](https://github.com/LineaLabs/lineapy/blob/d3a0f533ee7a44a4002fbfb86faddd54429b84b5/lineapy/plugins/airflow_pipeline_writer.py#L204):

    ```python
    DAG_TEMPLATE = load_plugin_template("airflow_dag_PythonOperator.jinja")

    ...

    full_code = DAG_TEMPLATE.render(
        DAG_NAME=self.pipeline_name,
        MODULE_NAME=self.pipeline_name + "_module",
        ...
        task_definitions=rendered_task_defs,
        task_dependencies=task_dependencies,
    )
    ```

6. If your framework can be run in a dockerized container, write a Jinja template that sets up an environment with your pipeline framework installed that can run the produced DAGs. Specify the `docker_template_name` property so the write `_write_docker` function loads the correct Jinja template.

    ```python
    @property
    def docker_template_name(self) -> str:
        return "airflow_dockerfile.jinja"
    ```

## Using Templates

You may have noticed at this point that the last few bullet points in the checklist involve rendering and using Jinja templates. Jinja templates are LineaPy's preferred way of templating the code that we generate.

All of the templates that are used in LineaPy can be found in the [templates directory](https://github.com/LineaLabs/lineapy/tree/main/lineapy/plugins/jinja_templates). 
These templates are loaded using the `load_plugin_template()` command as illustrated in the examples above, and can be rendered using the `render()` method while passing in values for the placeholder variables.

Feel free to skim some of the templates we have already created for an idea on how we use these templates. Online tutorials are also helpful, the "Getting started with Jinja" sections in [this one](https://realpython.com/primer-on-jinja-templating/#get-started-with-jinja) are a good place to start.

## Testing

As a pipeline integration contributor we also greatly appreciate adding tests for your new integration!

Snapshot tests should be added to `tests/unit/plugins/test_writer.py::test_pipeline_generation` by adding new parameters corresponding to your framework.
Be sure to also run pytest with the `--snapshot-update` flag and commit the snapshot files.

```python title="Example pytest param to test Airflow framework on a simple pipeline"
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
```

End-to-end tests such as the one found for Airflow in `tests/test_pipeline_run_airflow.py` are also highly recommended but much more involved as they require setting up a environment that can run the framework you are providing an integration for and having APIs to check the dag runs successfully.
Please consult your individual framework's documentation and add these tests if possible.

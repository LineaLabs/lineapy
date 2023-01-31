# Running a Pipeline with Different Parameters

Oftentimes, data scientists/engineers need to run the same pipeline with different parameters.
For instance, they may want to use a different data set for model training.
To produce a parametrized pipeline, use pipeline API's (optional) `input_parameters` argument,
like so:

```python
lineapy.to_pipeline(
    ...
    input_parameters=["<VARNAME1>", ...],
)
```

where `<VARNAME1>` is the name of the variable to be turned into a tunable parameter of the pipeline.

## Airflow Example

For example, the following creates an Airflow pipeline that can train a model on different data sources:

```python hl_lines="5"
    lineapy.to_pipeline(
        pipeline_name="iris_pipeline_parametrized",
        artifacts=["iris_preprocessed", "iris_model"],
        dependencies={"iris_model": {"iris_preprocessed"}},
        input_parameters=["url"],
        output_dir="~/airflow/dags/",
        framework="AIRFLOW",
    )
```

where `url` is a variable in the artifact code that references the source data URL.

To execute the generated Airflow pipeline with a different value of `url`, run:

```bash
airflow dags trigger --conf '{"url": "<NEW-DATA-URL>"}' <pipeline_name>_dag
```

where `<pipeline_name>` is `iris_pipeline_parametrized` in the current example.

Or, if running Airflow on UI, trigger the DAG with `{"url": "<NEW-DATA-URL>"}`
passed as a config JSON.

## Limitations

Currently, `input_parameters` only accepts variables from literal assignment
such as `a = "123"`. For each variable to be parametrized, there should be only one
literal assignment across all artifact code for the pipeline. For instance, if both
`a = "123"` and `a = "abc"` exist in the pipeline's artifact code, we cannot make
`a` an input parameter since its reference is ambiguous, i.e., we are not sure which
literal assignment `a` refers to.

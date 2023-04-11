import kfp
from kfp.components import create_component_from_func


def task_iris_preprocessed(url, variable_df_path: kfp.components.OutputPath(str)):
    import pathlib
    import pickle

    import iris_pipeline_module

    url = str(url)

    df = iris_pipeline_module.get_iris_preprocessed(url)

    pickle.dump(df, open(variable_df_path, "wb"))


def task_split_samples_for_artifact_iris_model_and_downstream(
    random_state,
    test_size,
    variable_df_path: kfp.components.InputPath(str),
    variable_split_samples_path: kfp.components.OutputPath(str),
):
    import pathlib
    import pickle

    import iris_pipeline_module

    random_state = int(random_state)

    test_size = float(test_size)

    df = pickle.load(open(variable_df_path, "rb"))

    split_samples = (
        iris_pipeline_module.get_split_samples_for_artifact_iris_model_and_downstream(
            df, random_state, test_size
        )
    )

    pickle.dump(split_samples, open(variable_split_samples_path, "wb"))


def task_iris_model(
    variable_split_samples_path: kfp.components.InputPath(str),
    variable_mod_path: kfp.components.OutputPath(str),
):
    import pathlib
    import pickle

    import iris_pipeline_module

    split_samples = pickle.load(open(variable_split_samples_path, "rb"))

    mod = iris_pipeline_module.get_iris_model(split_samples)

    pickle.dump(mod, open(variable_mod_path, "wb"))


def task_iris_model_evaluation(
    variable_mod_path: kfp.components.InputPath(str),
    variable_split_samples_path: kfp.components.InputPath(str),
    variable_mod_eval_test_path: kfp.components.OutputPath(str),
):
    import pathlib
    import pickle

    import iris_pipeline_module

    mod = pickle.load(open(variable_mod_path, "rb"))

    split_samples = pickle.load(open(variable_split_samples_path, "rb"))

    mod_eval_test = iris_pipeline_module.get_iris_model_evaluation(mod, split_samples)

    pickle.dump(mod_eval_test, open(variable_mod_eval_test_path, "wb"))


def task_setup():
    import pathlib
    import pickle

    import iris_pipeline_module

    pass


def task_teardown():
    import pathlib
    import pickle

    import iris_pipeline_module

    pass


iris_preprocessed_component = create_component_from_func(
    task_iris_preprocessed, base_image="iris_pipeline:lineapy"
)

split_samples_for_artifact_iris_model_and_downstream_component = (
    create_component_from_func(
        task_split_samples_for_artifact_iris_model_and_downstream,
        base_image="iris_pipeline:lineapy",
    )
)

iris_model_component = create_component_from_func(
    task_iris_model, base_image="iris_pipeline:lineapy"
)

iris_model_evaluation_component = create_component_from_func(
    task_iris_model_evaluation, base_image="iris_pipeline:lineapy"
)

setup_component = create_component_from_func(
    task_setup, base_image="iris_pipeline:lineapy"
)

teardown_component = create_component_from_func(
    task_teardown, base_image="iris_pipeline:lineapy"
)


client = kfp.Client(host="http://localhost:3000")


@kfp.dsl.pipeline(
    name="iris_pipeline_dag",
)
def iris_pipeline(url, test_size, random_state):

    task_iris_preprocessed = iris_preprocessed_component(url)
    task_split_samples_for_artifact_iris_model_and_downstream = (
        split_samples_for_artifact_iris_model_and_downstream_component(
            random_state, test_size, task_iris_preprocessed.outputs["variable_df"]
        )
    )
    task_iris_model = iris_model_component(
        task_split_samples_for_artifact_iris_model_and_downstream.outputs[
            "variable_split_samples"
        ]
    )
    task_iris_model_evaluation = iris_model_evaluation_component(
        task_iris_model.outputs["variable_mod"],
        task_split_samples_for_artifact_iris_model_and_downstream.outputs[
            "variable_split_samples"
        ],
    )
    task_setup = setup_component()
    task_teardown = teardown_component()

    task_iris_model.after(task_split_samples_for_artifact_iris_model_and_downstream)

    task_iris_model_evaluation.after(task_iris_model)

    task_iris_model_evaluation.after(
        task_split_samples_for_artifact_iris_model_and_downstream
    )

    task_iris_preprocessed.after(task_setup)

    task_split_samples_for_artifact_iris_model_and_downstream.after(
        task_iris_preprocessed
    )

    task_teardown.after(task_iris_model_evaluation)


# Specify argument values for your pipeline run.
pipeline_arguments = {
    "url": "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    "test_size": 0.33,
    "random_state": 42,
}

# Create a pipeline run, using the client you initialized in a prior step.
client.create_run_from_pipeline_func(iris_pipeline, arguments=pipeline_arguments)

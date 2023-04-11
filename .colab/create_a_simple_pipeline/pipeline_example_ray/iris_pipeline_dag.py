import pathlib
import pickle

import iris_pipeline_module
import ray

ray.init(runtime_env={"working_dir": "."}, storage="/tmp")


@ray.remote(num_returns=1)
def task_iris_preprocessed(url):

    url = str(url)

    df = iris_pipeline_module.get_iris_preprocessed(url)

    return df


@ray.remote(num_returns=1)
def task_split_samples_for_artifact_iris_model_and_downstream(
    random_state, test_size, df
):

    random_state = int(random_state)

    test_size = float(test_size)

    split_samples = (
        iris_pipeline_module.get_split_samples_for_artifact_iris_model_and_downstream(
            df, random_state, test_size
        )
    )

    return split_samples


@ray.remote(num_returns=1)
def task_iris_model(split_samples):

    mod = iris_pipeline_module.get_iris_model(split_samples)

    return mod


@ray.remote(num_returns=1)
def task_iris_model_evaluation(mod, split_samples):

    mod_eval_test = iris_pipeline_module.get_iris_model_evaluation(mod, split_samples)

    return mod_eval_test


# Specify argument values for your pipeline run.
pipeline_arguments = {
    "url": "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    "test_size": 0.33,
    "random_state": 42,
}

df = task_iris_preprocessed.remote(pipeline_arguments["url"])
split_samples = task_split_samples_for_artifact_iris_model_and_downstream.remote(
    pipeline_arguments["random_state"], pipeline_arguments["test_size"], df
)
mod = task_iris_model.remote(split_samples)
mod_eval_test = task_iris_model_evaluation.remote(mod, split_samples)

# Execute actors to get remote objects
# Make changes here to access any additional objects needed.
ray.get([mod_eval_test])

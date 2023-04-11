import pickle

import dvc.api
import iris_pipeline_module


def task_split_samples_for_artifact_iris_model_and_downstream(random_state, test_size):

    random_state = int(random_state)

    test_size = float(test_size)

    df = pickle.load(open("df.pickle", "rb"))

    split_samples = (
        iris_pipeline_module.get_split_samples_for_artifact_iris_model_and_downstream(
            df, random_state, test_size
        )
    )

    pickle.dump(split_samples, open("split_samples.pickle", "wb"))


if __name__ == "__main__":
    random_state = dvc.api.params_show()["random_state"]
    test_size = dvc.api.params_show()["test_size"]
    task_split_samples_for_artifact_iris_model_and_downstream(random_state, test_size)

import pickle

import dvc.api
import iris_pipeline_module


def task_iris_preprocessed(url):

    url = str(url)

    df = iris_pipeline_module.get_iris_preprocessed(url)

    pickle.dump(df, open("df.pickle", "wb"))


if __name__ == "__main__":
    url = dvc.api.params_show()["url"]
    task_iris_preprocessed(url)

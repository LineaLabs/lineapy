import pickle

import iris_pipeline_module


def task_iris_model():

    split_samples = pickle.load(open("split_samples.pickle", "rb"))

    mod = iris_pipeline_module.get_iris_model(split_samples)

    pickle.dump(mod, open("mod.pickle", "wb"))


if __name__ == "__main__":
    task_iris_model()

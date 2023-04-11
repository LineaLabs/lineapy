import pickle

import iris_pipeline_module


def task_iris_model_evaluation():

    mod = pickle.load(open("mod.pickle", "rb"))

    split_samples = pickle.load(open("split_samples.pickle", "rb"))

    mod_eval_test = iris_pipeline_module.get_iris_model_evaluation(mod, split_samples)

    pickle.dump(mod_eval_test, open("mod_eval_test.pickle", "wb"))


if __name__ == "__main__":
    task_iris_model_evaluation()

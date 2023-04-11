import argparse

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split


def get_iris_preprocessed(url):
    df = pd.read_csv(url)
    color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
    df["variety_color"] = df["variety"].map(color_map)
    num_map = {"Setosa": 0, "Versicolor": 1, "Virginica": 2}
    df["variety_num"] = df["variety"].map(num_map)
    return df


def get_split_samples_for_artifact_iris_model_and_downstream(
    df, random_state, test_size
):
    X = df[["petal.length", "petal.width"]]
    y = df["variety_num"]
    split_samples = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return split_samples


def get_iris_model(split_samples):
    X_train = split_samples[0]
    y_train = split_samples[2]
    mod = LogisticRegression(multi_class="multinomial")
    mod.fit(X_train, y_train)
    return mod


def get_iris_model_evaluation(mod, split_samples):
    X_test = split_samples[1]
    y_test = split_samples[3]
    y_test_pred = mod.predict(X_test)
    mod_eval_test = classification_report(y_test, y_test_pred, digits=3)
    return mod_eval_test


def run_session_including_iris_preprocessed(
    url="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    test_size=0.33,
    random_state=42,
):
    # Given multiple artifacts, we need to save each right after
    # its calculation to protect from any irrelevant downstream
    # mutations (e.g., inside other artifact calculations)
    import copy

    artifacts = dict()
    df = get_iris_preprocessed(url)
    artifacts["iris_preprocessed"] = copy.deepcopy(df)
    split_samples = get_split_samples_for_artifact_iris_model_and_downstream(
        df, random_state, test_size
    )
    mod = get_iris_model(split_samples)
    artifacts["iris_model"] = copy.deepcopy(mod)
    mod_eval_test = get_iris_model_evaluation(mod, split_samples)
    artifacts["iris_model_evaluation"] = copy.deepcopy(mod_eval_test)
    return artifacts


def run_all_sessions(
    url="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    test_size=0.33,
    random_state=42,
):
    artifacts = dict()
    artifacts.update(
        run_session_including_iris_preprocessed(url, test_size, random_state)
    )
    return artifacts


if __name__ == "__main__":
    # Edit this section to customize the behavior of artifacts
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        default="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    )
    parser.add_argument("--test_size", type=float, default=0.33)
    parser.add_argument("--random_state", type=int, default=42)
    args = parser.parse_args()
    artifacts = run_all_sessions(
        url=args.url,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    print(artifacts)

import copy

import pandas as pd
from sklearn.linear_model import LinearRegression


def get_url1_for_artifact_iris_model_and_downstream():
    url1 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    return url1


def get_iris_model(url1):
    train_df = pd.read_csv(url1)
    mod = LinearRegression()
    mod.fit(
        X=train_df[["petal.width"]],
        y=train_df["petal.length"],
    )
    return mod


def get_iris_petal_length_pred(mod, url1):
    pred_df = pd.read_csv(url1)
    petal_length_pred = mod.predict(X=pred_df[["petal.width"]])
    return petal_length_pred


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    url1 = get_url1_for_artifact_iris_model_and_downstream()
    mod = get_iris_model(url1)
    artifacts.append(copy.deepcopy(mod))
    petal_length_pred = get_iris_petal_length_pred(mod, url1)
    artifacts.append(copy.deepcopy(petal_length_pred))
    return artifacts


if __name__ == "__main__":
    run_all()

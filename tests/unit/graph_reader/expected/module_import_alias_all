import copy

import pandas as pd


def get_df():
    df = pd.DataFrame({"a": [1, 2]})
    return df


def get_df2(df):
    df2 = pd.concat([df, df])
    return df2


def run_all():
    # Multiple return variables detected, need to save the variable
    # right after calculation in case of mutation downstream
    artifacts = []
    df = get_df()
    artifacts.append(copy.deepcopy(df))
    df2 = get_df2(df)
    artifacts.append(copy.deepcopy(df2))
    return artifacts


if __name__ == "__main__":
    run_all()

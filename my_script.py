from os import chdir

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

chdir("examples")


def linea_model_housing():
    cleaned_data = pd.read_csv("outputs/cleaned_data_housing.csv")
    dropped = cleaned_data.dropna()
    train, val = train_test_split(cleaned_data, test_size=0.3, random_state=42)
    X_train = train.drop(["SalePrice"], axis=1)
    y_train = train.loc[:, "SalePrice"]
    linear_model = LinearRegression(fit_intercept=True)
    linear_model.fit(X_train, y_train)
    from joblib import dump

    dump(linear_model, "outputs/linea_model_housing.joblib")


linea_model_housing()

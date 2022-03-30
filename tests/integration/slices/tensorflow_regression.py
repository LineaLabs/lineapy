# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/tensorflow-docs/site/en/tutorials/keras/regression.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[tensorflow_regression]'

get_ipython().system("pip install -q seaborn")
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

url = "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"
column_names = [
    "MPG",
    "Cylinders",
    "Displacement",
    "Horsepower",
    "Weight",
    "Acceleration",
    "Model Year",
    "Origin",
]
raw_dataset = pd.read_csv(
    url, names=column_names, na_values="?", comment="\t", sep=" ", skipinitialspace=True
)
dataset = raw_dataset.copy()
dataset = dataset.dropna()
dataset["Origin"] = dataset["Origin"].map({(1): "USA", (2): "Europe", (3): "Japan"})
dataset = pd.get_dummies(dataset, columns=["Origin"], prefix="", prefix_sep="")
train_dataset = dataset.sample(frac=0.8, random_state=0)
train_features = train_dataset.copy()
train_labels = train_features.pop("MPG")
normalizer = tf.keras.layers.Normalization(axis=-1)
normalizer.adapt(np.array(train_features))


def build_and_compile_model(norm):
    model = keras.Sequential(
        [
            norm,
            layers.Dense(64, activation="relu"),
            layers.Dense(64, activation="relu"),
            layers.Dense(1),
        ]
    )
    model.compile(loss="mean_absolute_error", optimizer=tf.keras.optimizers.Adam(0.001))
    return model


dnn_model = build_and_compile_model(normalizer)
history = dnn_model.fit(
    train_features, train_labels, validation_split=0.2, verbose=0, epochs=100
)
dnn_model.save("dnn_model")

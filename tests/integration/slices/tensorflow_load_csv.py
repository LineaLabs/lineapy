# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/tensorflow-docs/site/en/tutorials/load_data/csv.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[tensorflow_load_csv]'

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers

titanic = pd.read_csv("https://storage.googleapis.com/tf-datasets/titanic/train.csv")
titanic_features = titanic.copy()
titanic_labels = titanic_features.pop("survived")
inputs = {}
for name, column in titanic_features.items():
    dtype = column.dtype
    if dtype == object:
        dtype = tf.string
    else:
        dtype = tf.float32
    inputs[name] = tf.keras.Input(shape=(1,), name=name, dtype=dtype)
numeric_inputs = {
    name: input for name, input in inputs.items() if input.dtype == tf.float32
}
x = layers.Concatenate()(list(numeric_inputs.values()))
norm = layers.Normalization()
norm.adapt(np.array(titanic[numeric_inputs.keys()]))
all_numeric_inputs = norm(x)
all_numeric_inputs
preprocessed_inputs = [all_numeric_inputs]
for name, input in inputs.items():
    if input.dtype == tf.float32:
        continue
    lookup = layers.StringLookup(vocabulary=np.unique(titanic_features[name]))
    one_hot = layers.CategoryEncoding(max_tokens=lookup.vocab_size())
    x = lookup(input)
    x = one_hot(x)
    preprocessed_inputs.append(x)
preprocessed_inputs_cat = layers.Concatenate()(preprocessed_inputs)
titanic_preprocessing = tf.keras.Model(inputs, preprocessed_inputs_cat)
tf.keras.utils.plot_model(
    model=titanic_preprocessing, rankdir="LR", dpi=72, show_shapes=True
)
titanic_features_dict = {
    name: np.array(value) for name, value in titanic_features.items()
}
features_dict = {name: values[:1] for name, values in titanic_features_dict.items()}
titanic_preprocessing(features_dict)


def titanic_model(preprocessing_head, inputs):
    body = tf.keras.Sequential([layers.Dense(64), layers.Dense(1)])
    preprocessed_inputs = preprocessing_head(inputs)
    result = body(preprocessed_inputs)
    model = tf.keras.Model(inputs, result)
    model.compile(
        loss=tf.losses.BinaryCrossentropy(from_logits=True),
        optimizer=tf.optimizers.Adam(),
    )
    return model


titanic_model = titanic_model(titanic_preprocessing, inputs)
titanic_model.fit(x=titanic_features_dict, y=titanic_labels, epochs=10)
titanic_model.save("test")

# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/tensorflow-decision-forests/documentation/tutorials/beginner_colab.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[tensorflow_decision_forests_beginner]'

import numpy as np
import pandas as pd
import tensorflow_decision_forests as tfdf

try:
    from wurlitzer import sys_pipes
except:
    from colabtools.googlelog import CaptureLog as sys_pipes
get_ipython().system(
    "wget -q https://storage.googleapis.com/download.tensorflow.org/data/palmer_penguins/penguins.csv -O /tmp/penguins.csv"
)
dataset_df = pd.read_csv("/tmp/penguins.csv")
label = "species"
classes = dataset_df[label].unique().tolist()
dataset_df[label] = dataset_df[label].map(classes.index)


def split_dataset(dataset, test_ratio=0.3):
    """Splits a panda dataframe in two."""
    test_indices = np.random.rand(len(dataset)) < test_ratio
    return dataset[~test_indices], dataset[test_indices]


train_ds_pd, test_ds_pd = split_dataset(dataset_df)
train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train_ds_pd, label=label)
test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test_ds_pd, label=label)
model_1 = tfdf.keras.RandomForestModel()
model_1.compile(metrics=["accuracy"])
with sys_pipes():
    model_1.fit(x=train_ds)
evaluation = model_1.evaluate(test_ds, return_dict=True)
model_1.save("/tmp/my_saved_model")

# This is the manual slice of:
#  lineapy.file_system
# from file:
#  sources/tensorflow-docs/site/en/tutorials/structured_data/preprocessing_layers.ipynb

# To verify that linea produces the same slice, run:
#  pytest -m integration --runxfail -vv 'tests/integration/test_slice.py::test_slice[tensorflow_preprocessing_layers]'

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers

dataset_url = (
    "http://storage.googleapis.com/download.tensorflow.org/data/petfinder-mini.zip"
)
csv_file = "datasets/petfinder-mini/petfinder-mini.csv"
tf.keras.utils.get_file("petfinder_mini.zip", dataset_url, extract=True, cache_dir=".")
dataframe = pd.read_csv(csv_file)
dataframe["target"] = np.where(dataframe["AdoptionSpeed"] == 4, 0, 1)
dataframe = dataframe.drop(columns=["AdoptionSpeed", "Description"])
train, val, test = np.split(
    dataframe.sample(frac=1), [int(0.8 * len(dataframe)), int(0.9 * len(dataframe))]
)


def df_to_dataset(dataframe, shuffle=True, batch_size=32):
    df = dataframe.copy()
    labels = df.pop("target")
    df = {key: value[:, tf.newaxis] for key, value in dataframe.items()}
    ds = tf.data.Dataset.from_tensor_slices((dict(df), labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(dataframe))
    ds = ds.batch(batch_size)
    ds = ds.prefetch(batch_size)
    return ds


def get_normalization_layer(name, dataset):
    normalizer = layers.Normalization(axis=None)
    feature_ds = dataset.map(lambda x, y: x[name])
    normalizer.adapt(feature_ds)
    return normalizer


def get_category_encoding_layer(name, dataset, dtype, max_tokens=None):
    if dtype == "string":
        index = layers.StringLookup(max_tokens=max_tokens)
    else:
        index = layers.IntegerLookup(max_tokens=max_tokens)
    feature_ds = dataset.map(lambda x, y: x[name])
    index.adapt(feature_ds)
    encoder = layers.CategoryEncoding(num_tokens=index.vocabulary_size())
    return lambda feature: encoder(index(feature))


batch_size = 256
train_ds = df_to_dataset(train, batch_size=batch_size)
val_ds = df_to_dataset(val, shuffle=False, batch_size=batch_size)
all_inputs = []
encoded_features = []
for header in ["PhotoAmt", "Fee"]:
    numeric_col = tf.keras.Input(shape=(1,), name=header)
    normalization_layer = get_normalization_layer(header, train_ds)
    encoded_numeric_col = normalization_layer(numeric_col)
    all_inputs.append(numeric_col)
    encoded_features.append(encoded_numeric_col)
age_col = tf.keras.Input(shape=(1,), name="Age", dtype="int64")
encoding_layer = get_category_encoding_layer(
    name="Age", dataset=train_ds, dtype="int64", max_tokens=5
)
encoded_age_col = encoding_layer(age_col)
all_inputs.append(age_col)
encoded_features.append(encoded_age_col)
categorical_cols = [
    "Type",
    "Color1",
    "Color2",
    "Gender",
    "MaturitySize",
    "FurLength",
    "Vaccinated",
    "Sterilized",
    "Health",
    "Breed1",
]
for header in categorical_cols:
    categorical_col = tf.keras.Input(shape=(1,), name=header, dtype="string")
    encoding_layer = get_category_encoding_layer(
        name=header, dataset=train_ds, dtype="string", max_tokens=5
    )
    encoded_categorical_col = encoding_layer(categorical_col)
    all_inputs.append(categorical_col)
    encoded_features.append(encoded_categorical_col)
all_features = tf.keras.layers.concatenate(encoded_features)
x = tf.keras.layers.Dense(32, activation="relu")(all_features)
x = tf.keras.layers.Dropout(0.5)(x)
output = tf.keras.layers.Dense(1)(x)
model = tf.keras.Model(all_inputs, output)
model.compile(
    optimizer="adam",
    loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
    metrics=["accuracy"],
)
model.fit(train_ds, epochs=10, validation_data=val_ds)
model.save("my_pet_classifier")

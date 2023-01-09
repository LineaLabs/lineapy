# Discovering and Reusing Past Work

Once connected to an artifact store (it can be an individual or shared one), we can query existing artifacts, like so:

```python
lineapy.artifact_store()
```

which would print a list looking as the following:

```
iris_preprocessed:0 created on 2022-09-29 01:22:39.612871
iris_preprocessed:1 created on 2022-09-29 01:22:41.336159
iris_preprocessed:2 created on 2022-09-29 01:22:43.511112
iris_model:0 created on 2022-09-29 01:22:45.381132
iris_model:1 created on 2022-09-29 01:22:46.786414
iris_model:2 created on 2022-09-29 01:22:47.990517
iris_model:3 created on 2022-09-29 01:22:49.366484
toy_artifact:0 created on 2022-09-29 01:22:50.189060
toy_artifact:1 created on 2022-09-29 01:22:50.676276
toy_artifact:2 created on 2022-09-29 01:22:51.084704
```

Each line contains three pieces of information about an existing artifact: its name, version, and time of creation.
Hence, for an artifact named `iris_model`, we have four versions created at different times.

Now, say we are interested in reusing the first version of this artifact. We can retrieve the desired artifact as follows:

```python
model_artifact = lineapy.get("iris_model", version=0)
```

Note that what has been retrieved and saved in `model_artifact` is not the model itself; it is the model *artifact*,
which contains more than the model itself, e.g., the code that was used to generate the model. Hence, to resuse the model,
we need to extract the artifact's value:

```python
model = model_artifact.get_value()
```

However, we actually do not fully know how to reuse this model as we are missing the memory (or knowledge, if the artifact
was created by someone else) of its context such as input details. Thankfully, the artifact also stores the code that was
used to generate its value, so we can check it out:

```python
print(data_artifact.get_code())
```

which prints:

```
import lineapy
from sklearn.linear_model import LinearRegression

art_df_processed = lineapy.get("iris_preprocessed", version=2)
df_processed = art_df_processed.get_value()
mod = LinearRegression()
mod.fit(
    X=df_processed[["petal.width", "d_versicolor", "d_virginica"]],
    y=df_processed["sepal.width"],
)
```

With this, we now know the source and shape of the data that was used to train this model,
which enables us to adapt and reuse the model in our context. Specifically, we can check out the
training data by loading the corresponding artifact, like so:

```python
art_df_processed = lineapy.get("iris_preprocessed", version=2)
df_processed = art_df_processed.get_value()
print(df_processed)
```

Based on the values in the data, we would have a more concrete understanding of the model and its job,
which would enable us to make new predictions, like so:

```python
import pandas as pd

# Create data to make predictions on
df = pd.DataFrame({
    "petal.width": [1.3, 5.2, 0.3, 1.5, 4.9],
    "d_versicolor": [1, 0, 0, 1, 0],
    "d_virginica": [0, 1, 0, 0, 1],
})

# Make new predictions
df["sepal.width.pred"] = model.predict(df)
```

This example illustrates the benefit of LineaPy's unified storage framework:
encapsulating both value and code as well as other metadata, LineaPy's artifact store
enables the user to explore the history and relations among different works,
hence rendering them more reusable.

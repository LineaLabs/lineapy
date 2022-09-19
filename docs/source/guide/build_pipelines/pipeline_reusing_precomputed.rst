Reusing Pre-Computed Artifact Values
====================================

A pipeline often consists of components that require different execution frequencies.
For a pipeline that includes model training and prediction, for instance, we can expect
that model training would demand less frequent execution than prediction since a trained model
can be used to make multiple rounds of predictions (with different data sets). Hence, we want
to be able to reuse pre-computed values for certain pipeline components rather than recomputing
them from the scratch every time we run the pipeline. This capacity is especially valuable for
pipeline components that involve long computation (e.g., large model training). 

As a concrete example, consider the following development code:

.. code-block:: python

    import pandas as pd
    from sklearn.linear_model import LinearRegression

    import lineapy


    # Load train data
    url1 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    train_df = pd.read_csv(url1)

    # Initiate the model
    mod = LinearRegression()

    # Fit the model
    mod.fit(
        X=train_df[["petal.width"]],
        y=train_df["petal.length"],
    )

    # Save the fitted model as an artifact
    lineapy.save(mod, "iris_model")

    # Load data to predict
    url2 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    pred_df = pd.read_csv(url2)

    # Make predictions
    petal_length_pred = mod.predict(X=pred_df[["petal.width"]])

    # Save the predictions
    lineapy.save(petal_length_pred, "iris_petal_length_pred")

Now, if we simply run

.. code-block:: python

    lineapy.to_pipeline(
        artifacts=["iris_model", "iris_petal_length_pred"],
        framework="SCRIPT",
        input_parameters=["url2"],
        pipeline_name="iris",
        output_dir="./iris_pipeline/",
    )

we get a pipeline where the model gets re-trained every time the pipeline is executed:

.. code-block:: python
   :emphasize-lines: 12, 13, 14, 15, 16

    # ./iris_pipeline/iris_module.py

    import argparse

    import pandas as pd
    from sklearn.linear_model import LinearRegression


    def get_iris_model():
        url1 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
        train_df = pd.read_csv(url1)
        mod = LinearRegression()
        mod.fit(
            X=train_df[["petal.width"]],
            y=train_df["petal.length"],
        )
        return mod


    def get_iris_petal_length_pred(mod, url2):
        pred_df = pd.read_csv(url2)
        petal_length_pred = mod.predict(X=pred_df[["petal.width"]])
        return petal_length_pred


    def run_session_including_iris_model(
        url2="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    ):
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        mod = get_iris_model()
        artifacts["iris_model"] = copy.deepcopy(mod)
        petal_length_pred = get_iris_petal_length_pred(mod, url2)
        artifacts["iris_petal_length_pred"] = copy.deepcopy(petal_length_pred)
        return artifacts

    [...]

Again, this is not ideal because model (re-)training may involve long computation. Instead, we can run

.. code-block:: python
   :emphasize-lines: 5

    lineapy.to_pipeline(
        artifacts=["iris_model", "iris_petal_length_pred"],
        framework="SCRIPT",
        input_parameters=["url2"],
        reuse_pre_computed_artifacts=["iris_model"],
        pipeline_name="iris",
        output_dir="./iris_pipeline_reusing_precomputed/",
    )

to get a more efficient pipline, like so:

.. code-block:: python
   :emphasize-lines: 12

    # ./iris_pipeline_reusing_precomputed/iris_module.py

    import argparse

    import pandas as pd
    from sklearn.linear_model import LinearRegression


    def get_iris_model():
        import lineapy

        mod = lineapy.get("iris_model", 9).get_value()
        return mod


    def get_iris_petal_length_pred(mod, url2):
        pred_df = pd.read_csv(url2)
        petal_length_pred = mod.predict(X=pred_df[["petal.width"]])
        return petal_length_pred


    def run_session_including_iris_model(
        url2="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    ):
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        mod = get_iris_model()
        artifacts["iris_model"] = copy.deepcopy(mod)
        petal_length_pred = get_iris_petal_length_pred(mod, url2)
        artifacts["iris_petal_length_pred"] = copy.deepcopy(petal_length_pred)
        return artifacts

    [...]

As shown, ``get_iris_model()`` now simply loads the pre-computed value for the model instead of recomputing it
all over again.

.. warning::

    Reuse of pre-computed artifacts is currently not supported for ``framework="AIRFLOW"``.
    Hence, the generated Airflow DAG file would recompute all artifacts in the pipeline.

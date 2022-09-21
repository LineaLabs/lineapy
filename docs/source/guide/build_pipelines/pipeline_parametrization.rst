Parametrization
===============

Oftentimes, data scientists/engineers need to run the same pipeline with different parameters.
For instance, they may want to use a different data set for model training and/or prediction.
To produce a parametrized pipeline, we can use pipeline API's (optional) ``input_parameters`` argument.

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
        dependencies={"iris_petal_length_pred": {"iris_model"}},
        pipeline_name="iris",
        output_dir="./iris_pipeline/",
    )

we get an "inflexible" pipeline where data sources are fixed rather than tunable:

.. code-block:: python
   :emphasize-lines: 8, 19

    # ./iris_pipeline/iris_module.py

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


    def get_iris_petal_length_pred(mod):
        url2 = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
        pred_df = pd.read_csv(url2)
        petal_length_pred = mod.predict(X=pred_df[["petal.width"]])
        return petal_length_pred


    def run_session_including_iris_model():
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        mod = get_iris_model()
        artifacts["iris_model"] = copy.deepcopy(mod)
        petal_length_pred = get_iris_petal_length_pred(mod)
        artifacts["iris_petal_length_pred"] = copy.deepcopy(petal_length_pred)
        return artifacts


    def run_all_sessions():
        artifacts = dict()
        artifacts.update(run_session_including_iris_model())
        return artifacts


    if __name__ == "__main__":
        # Edit this section to customize the behavior of artifacts
        artifacts = run_all_sessions()
        print(artifacts)

Instead, we can run

.. code-block:: python
   :emphasize-lines: 5

    lineapy.to_pipeline(
        artifacts=["iris_model", "iris_petal_length_pred"],
        framework="SCRIPT",
        dependencies={"iris_petal_length_pred": {"iris_model"}},
        input_parameters=["url1", "url2"],  # Specify variables to parametrize
        pipeline_name="iris",
        output_dir="./iris_pipeline_parametrized/",
    )

to get a parametrized pipline, like so:

.. code-block:: python
   :emphasize-lines: 9, 19, 26, 27, 43, 44

    # ./iris_pipeline_parametrized/iris_module.py

    import argparse

    import pandas as pd
    from sklearn.linear_model import LinearRegression


    def get_iris_model(url1):
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
        url1="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        url2="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    ):
        # Given multiple artifacts, we need to save each right after
        # its calculation to protect from any irrelevant downstream
        # mutations (e.g., inside other artifact calculations)
        import copy

        artifacts = dict()
        mod = get_iris_model(url1)
        artifacts["iris_model"] = copy.deepcopy(mod)
        petal_length_pred = get_iris_petal_length_pred(mod, url2)
        artifacts["iris_petal_length_pred"] = copy.deepcopy(petal_length_pred)
        return artifacts


    def run_all_sessions(
        url1="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        url2="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
    ):
        artifacts = dict()
        artifacts.update(run_session_including_iris_model(url1, url2))
        return artifacts


    if __name__ == "__main__":
        # Edit this section to customize the behavior of artifacts
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--url1",
            type=str,
            default="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        )
        parser.add_argument(
            "--url2",
            type=str,
            default="https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv",
        )
        args = parser.parse_args()
        artifacts = run_all_sessions(
            url1=args.url1,
            url2=args.url2,
        )
        print(artifacts)

As shown, we now have ``url1`` and ``url2`` factored out as easily tunable parameters of the pipeline,
which allows us to run it with various data sources beyond those we started with (hence increasing the
pipeline's utility).

.. warning::

    Currently, ``input_parameters`` only accepts variables from literal assignment
    such as ``a = "123"``. For each variable to be parametrized, there should be only one
    literal assignment across all artifact code for the pipeline. For instance, if both
    ``a = "123"`` and ``a = "abc"`` exist in the pipeline's artifact code, we cannot make
    ``a`` an input parameter since its reference is ambiguous, i.e., we are not sure which
    literal assignment ``a`` refers to.

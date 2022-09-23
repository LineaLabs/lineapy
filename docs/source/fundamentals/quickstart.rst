.. _quickstart:

Quick Start
===========

.. note::

    Make sure that you have LineaPy installed. You can find relevant instructions 
    in the :ref:`Installation <setup>` section.

Once LineaPy is installed, we are ready to start using the package. We start with a simple
example using the `Iris dataset <https://en.wikipedia.org/wiki/Iris_flower_data_set>`_ to demonstrate how to use LineaPy to 1) store a variable's history, 2) get its cleaned-up code,
and 3) build an executable pipeline for the variable.

.. code:: python

    import lineapy
    import pandas as pd
    from sklearn.linear_model import LinearRegression, ElasticNet

    # Load data
    url = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    df = pd.read_csv(url)

    # Some very basic feature engineering
    color_map = {"Setosa": 0, "Versicolor": 1, "Virginica": 2}
    df["variety_color"] = df["variety"].map(color_map)
    df2 = df.copy()
    df2["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
    df2["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)

    # Initialize two models
    model1 = LinearRegression()
    model2 = ElasticNet()

    # Fit both models
    model1.fit(
        X=df2[["petal.width", "d_versicolor", "d_virginica"]],
        y=df2["sepal.width"],
    )
    model2.fit(
        X = df[["petal.width", "variety_color"]],
        y = df["sepal.width"],
    )


Now, we reach the end of our development session and decide to save the ElasticNet model.
We can store the model as a LineaPy :ref:`artifact <concepts>` as follows:

.. code:: python

    # Store the model as an artifact
    lineapy.save(model2, "iris_elasticnet_model")

A LineaPy artifact encapsulates both the value *and* code, so we can easily retrieve
the model's code, like so:

.. code:: python

    # Retrieve the model artifact
    artifact = lineapy.get("iris_elasticnet_model")

    # Check code for the model artifact
    print(artifact.get_code())

which will print:

.. code:: none

    import pandas as pd
    from sklearn.linear_model import ElasticNet

    df = pd.read_csv(
        "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    )
    color_map = {"Setosa": 0, "Versicolor": 1, "Virginica": 2}
    df["variety_color"] = df["variety"].map(color_map)
    model2 = ElasticNet()
    model2.fit(
        X=df[["petal.width", "variety_color"]],
        y=df["sepal.width"],
    )

Note that these are the minimal essential steps to produce the model. That is, LineaPy has automatically
cleaned up the original code by removing extraneous operations that do not affect the model.

Say we are now asked to retrain the model on a regular basis to account for any updates in the source data.
We need to set up a pipeline to train the model, and LineaPy make it as simple as a single line of code:

.. code:: python

    lineapy.to_pipeline(
        artifacts=["iris_elasticnet_model"],
        input_parameters=["url"],  # Specify variable(s) to parametrize
        pipeline_name="iris_model_pipeline",
        output_dir="output/",
        framework="AIRFLOW",
    )

which generates several files that can be used to execute the pipeline from the UI or CLI.

In sum, LineaPy automates time-consuming, manual steps in a data science workflow, helping us move
our work into production more quickly.

.. note::

    To learn more about LineaPy's API, check out `this <https://docs.lineapy.org/en/latest/tutorials/00_api_basics.html>`_ tutorial.

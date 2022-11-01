.. _quickstart:

Quick Start
===========

.. note::

    Make sure that you have LineaPy installed and loaded in your environment. You can find relevant instructions 
    in :ref:`Installation <setup>` and :ref:`Interfaces <interfaces>`.

.. include:: ../snippets/slack_support.rstinc

Once LineaPy is installed and loaded, you are ready to start using the package. Let's look at a simple
example using the `Iris dataset <https://en.wikipedia.org/wiki/Iris_flower_data_set>`_ to demonstrate
how to use LineaPy to 1) store a variable's history, 2) get its cleaned-up code,
and 3) build an executable pipeline for the variable.

The following development code fits a linear regression model to the Iris dataset:

.. code:: python

    import lineapy
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    # Load data
    url = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    df = pd.read_csv(url)

    # Map each species to a color
    color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
    df["variety_color"] = df["variety"].map(color_map)

    # Plot petal vs. sepal width by species
    df.plot.scatter("petal.width", "sepal.width", c="variety_color")
    plt.show()

    # Create dummy variables encoding species
    df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
    df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)

    # Initiate the model
    mod = LinearRegression()

    # Fit the model
    mod.fit(
        X=df[["petal.width", "d_versicolor", "d_virginica"]],
        y=df["sepal.width"],
    )

Let's say you're happy with your above code, and you've decided to save the trained model. You can store the model as a LineaPy :ref:`artifact <concepts>` with the following code:

.. code:: python

    # Save the model as an artifact
    lineapy.save(mod, "iris_model")

A LineaPy artifact encapsulates both the value *and* code, so you can easily retrieve
the model's code, like so:

.. code:: python

    # Retrieve the model artifact
    artifact = lineapy.get("iris_model")

    # Check code for the model artifact
    print(artifact.get_code())

The print statement will output:

.. code:: none

    import pandas as pd
    from sklearn.linear_model import LinearRegression

    url = "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
    df = pd.read_csv(url)
    color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
    df["variety_color"] = df["variety"].map(color_map)
    df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
    df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)
    mod = LinearRegression()
    mod.fit(
        X=df[["petal.width", "d_versicolor", "d_virginica"]],
        y=df["sepal.width"],
    )

Note that these are the minimal essential steps to produce the model. That is, LineaPy has automatically
cleaned up the original code by removing extraneous operations that do not affect the model (e.g., plotting).

Let's say you're asked to retrain the model on a regular basis to account for any updates in the source data.
You need to set up a pipeline to train the model --- LineaPy makes this as simple as a single function call:

.. code:: python

    lineapy.to_pipeline(
        artifacts=["iris_model"],
        input_parameters=["url"],  # Specify variable(s) to parametrize
        pipeline_name="iris_model_pipeline",
        output_dir="output/",
        framework="AIRFLOW",
    )

This command generates several files that can be used to execute the pipeline from the UI or CLI. (Check this
:ref:`tutorial <pipeline_basics>` for more details.)

In short, LineaPy automates time-consuming, manual steps in a data science workflow, helping us get
our work to production more quickly and easily.

.. note::

    To learn more about LineaPy's API, check out `this <https://docs.lineapy.org/en/latest/tutorials/00_api_basics.html>`_ tutorial.

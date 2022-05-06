Refactoring Code
================

LineaPy's artifacts store the complete development history in intelligent graph representation,
and this enables automatic transformation of the development code.

An important application of such transformation is “program slicing” where the development code is
“sliced” to only retain minimal necessary operations generating the final state/object of interest
(e.g., trained model).

Traditionally, a major bottleneck in any data science work is refactoring messy development code into
clean, production-ready code, so LineaPy's support for automatic code clean-up can boost the productivity
and impact of data science teams.

For instance, say we are a botanical data scientist modeling the relationship between different parts of
the iris flower, and we end up with the following development code:

.. code:: python

   import os
   import lineapy
   import pandas as pd
   import matplotlib.pyplot as plt
   from sklearn.linear_model import LinearRegression

   # Load data
   df = pd.read_csv("https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv")

   # View data
   df

   # Plot petal vs. sepal width
   df.plot.scatter("petal.width", "sepal.width")
   plt.show()

   # Calculate correlation coefficient
   df[["petal.width", "sepal.width"]].corr(method="pearson")

   # Initiate the model
   lm_1 = LinearRegression()

   # Fit the model
   lm_1.fit(
      X=df[["petal.width"]],
      y=df["sepal.width"],
   )

   # Check result
   print(f"Coefficient for petal.width: {lm_1.coef_[0]}")

   # Check species and their counts
   df["variety"].value_counts()

   # Create dummy variables encoding species
   df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
   df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)

   # View data
   df

   # Initiate the model
   lm_2 = LinearRegression()

   # Fit the model
   lm_2.fit(
      X=df[["petal.width", "d_versicolor", "d_virginica"]],
      y=df["sepal.width"],
   )

   # Check result
   print(f"Coefficient for petal.width: {lm_2.coef_[0]}")
   print(f"Coefficient for d_versicolor: {lm_2.coef_[1]}")
   print(f"Coefficient for d_virginica: {lm_2.coef_[2]}")

   # Map each species to a color
   color_map = {"Setosa": "green", "Versicolor": "blue", "Virginica": "red"}
   df["variety_color"] = df["variety"].map(color_map)

   # Plot petal vs. sepal width by species
   df.plot.scatter("petal.width", "sepal.width", c="variety_color")
   plt.show()

   # Create interaction terms for species
   df["i_versicolor"] = df["petal.width"] * df["d_versicolor"]
   df["i_virginica"] = df["petal.width"] * df["d_virginica"]

   # Initiate the model
   lm_3 = LinearRegression()

   # Fit the model
   lm_3.fit(
      X=df[["petal.width", "d_versicolor", "d_virginica", "i_versicolor", "i_virginica"]],
      y=df["sepal.width"],
   )

   # Check result
   print(f"Coefficient for petal.width: {lm_3.coef_[0]}")
   print(f"Coefficient for d_versicolor: {lm_3.coef_[1]}")
   print(f"Coefficient for d_virginica: {lm_3.coef_[2]}")
   print(f"Coefficient for i_versicolor: {lm_3.coef_[3]}")
   print(f"Coefficient for i_virginica: {lm_3.coef_[4]}")

As shown, the code interweaves various plots, models, and print statements, reflecting dynamic nature
of the development stage of data science work.

Say we are interested in productionizing the second model (``lm_2``). Normally, this would involve manually
sifting through the entire code to identify relevant parts only. We can cut through such manual labor with
the help of LineaPy.

First, we store the model as a LineaPy artifact:

.. code:: python

   # Save desired model as an artifact
   artifact = lineapy.save(lm_2, "linear_model_v2")

Then, we simply ask for its "sliced" code, like so:

.. code:: python

   # Get "sliced" code
   print(artifact.get_code())

And we get:

.. code:: none

   import pandas as pd
   from sklearn.linear_model import LinearRegression

   df = pd.read_csv(
      "https://raw.githubusercontent.com/LineaLabs/lineapy/main/examples/tutorials/data/iris.csv"
   )
   df["d_versicolor"] = df["variety"].apply(lambda x: 1 if x == "Versicolor" else 0)
   df["d_virginica"] = df["variety"].apply(lambda x: 1 if x == "Virginica" else 0)
   lm_2 = LinearRegression()
   lm_2.fit(
      X=df[["petal.width", "d_versicolor", "d_virginica"]],
      y=df["sepal.width"],
   )

which is more concise and manageable than what we initially had --- a long, messy collection of various operations.

In practice, development scripts/notebooks by data scientists are much longer and more complicated than this simple example.
Hence, LineaPy's automatic code refactoring can save considerable time for data scientists to move their work into production.

.. note::

   This does not mean that we lost other parts of the development code. We can still access the artifact's
   full session code (including comments) with ``artifact.get_session_code()``. This should come in handy when trying to remember
   or understand the original development context of a given artifact.

If you want hands-on practice on code refactoring with LineaPy,
check out `this <https://github.com/LineaLabs/lineapy/blob/main/examples/tutorials/01_refactor_code.ipynb>`_ tutorial notebook.

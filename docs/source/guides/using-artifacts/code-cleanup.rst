.. _code_cleanup:

Cleaning up Development Code
============================

.. include:: ../../snippets/slack_support.rstinc

Data science development is characterized by nimble, iterative experimentation and exploratory data analysis.
Data scientists explore many possibilities before reaching the final result. The rapid exploration process often
leads to long, messy code, the majority of which has no impact on the final result.

Code cleanup is hence an essential step for moving data science work into production. Yet, it often becomes a major
bottleneck as it involves manual inspection of long, messy code that sometimes does not make sense even to its own
author. With the complete development history stored in artifacts, LineaPy enables automatic code cleanup,
facilitating transition to production.

Example
-------

Say we are a botanical data scientist modeling the relationship between different parts of
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
   lineapy.save(lm_2, "linear_model_v2")

Then, we simply ask for its cleaned-up code, like so:

.. code:: python

   # Retrieve the model artifact
   artifact = lineapy.get("linear_model_v2")

   # Get cleaned-up code
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
Note that the cleaned-up code above is a subset of the original development code. That is, LineaPy "condensed" the
original code by removing extraneous operations that do not affect the artifact we care about, i.e., ``lm_2``.

.. note::

   This does not mean that we lost other parts of the development code. We can still access the artifact's
   full session code (including comments) with ``artifact.get_session_code()``. This should come in handy when trying to remember
   or understand the original development context of a given artifact.

.. note::

   In fact, ``lineapy.save()`` itself returns the artifact object, so we could have simply
   executed ``artifact = lineapy.save(lm_2, "linear_model_v2")`` above.

In practice, development scripts/notebooks by data scientists are much longer and more complicated than this simple example.
Hence, LineaPy's automatic code clean-up can save considerable time for data scientists to move their work into production.

Annotating Third-Party APIs
---------------------------

Python ecosystem offers a lot of interesting and useful packages that are not part of the core distribution.
These third-party packages often come with their own new APIs, and LineaPy is not guaranteed to handle all
of them properly when removing extraneous code. For such "unrecognized" APIs, we can add
instructions for LineaPy, which we call "package annotation".

For instance, without relevant package annotation, running

.. code-block:: python

   import pyperclip

   pyperclip.copy("This wont show up without annotations")
   tmp_var = pyperclip.paste()
   artifact = lineapy.save(tmp_var, "annotated_text")

   print(artifact.get_code())

would display

.. code-block:: none

   import pyperclip

   tmp_var = pyperclip.paste()

where the ``pyperclip.copy`` step is missing. This is because ``lineapy`` does not recognize it
as an API that modifies the caller (``pyperclip``, in this case) and hence skips it
during the relevant code cleanup.

We can annotate the ``pyperclip`` package by creating a YAML file looking as follows:

.. code-block:: yaml

   # ./pyperclip.annotations.yaml

   - module: pyperclip
     annotations:
       - criteria:
           function_names:
             - copy
             - paste
         side_effects:
           - mutated_value:
               self_ref: SELF_REF

where

* ``module`` refers to the third-party package/module that the annotation is associated with.

* ``criteria`` specifies what each annotation is *for*. In this example, it instructs that the annotation is for ``copy`` and ``paste`` functions in the module.

* ``side_effects`` specifies what each annotation is *about*. In this example, it instructs that the annotation is about mutation of the function caller.

In sum, these instructions tell ``lineapy`` to recognize ``copy`` and ``paste`` functions in the ``pyperclip`` module
as APIs that mutate their caller, and to treat them as such in relevant downstream tasks such as code cleanup.

.. note::

   For more details on annotation keywords, check this :ref:`page <annotate_package>`.

To make the annotation take effect, we run:

.. code-block:: bash

   lineapy annotate add "./pyperclip.annotations.yaml" --name="pyperclip_annotations" 

where ``"pyperclip_annotations"`` is a name of our choice.

Now, if we reload ``lineapy`` and run the original code above, we get the correct code cleanup displayed:

.. code-block:: none

   import pyperclip

   pyperclip.copy("This wont show up without annotations")
   tmp_var = pyperclip.paste()

.. warning::

   Annotations added this way are valid in the local environment only.
   To integrate new annotations into the ``lineapy`` source code, the YAML file
   should be created or updated in `lineapy/annotations/external/ <https://github.com/LineaLabs/lineapy/tree/main/lineapy/annotations/external>`_,
   following contribution instructions :ref:`here <contribution_setup_and_basics>`.

To view imported annotations, run:

.. code-block:: bash

   lineapy annotate list

To delete imported annotations, run:

.. code-block:: bash

   lineapy annotate delete --name=[NAME-OF-ANNOTATION]

where ``[NAME-OF-ANNOTATION]`` is ``"pyperclip_annotations"`` in this example.

Known Issues
------------

We discuss few cases in which LineaPy's code cleanup might lead to issues, and what steps can be taken by the user to get around them.

Unvisited Conditional
^^^^^^^^^^^^^^^^^^^^^

Suppose we have a code which has conditionals in them, for example:

.. code:: python

   import lineapy
   
   lst = []
   var = 10

   if var > 5:
      lst.append(10)
      var += 10
   else:
      lst.append(20)
      var += 20

   lineapy.save(var, 'variable')

In this example, if we try to obtain the cleaned up code for the artifact as follows:

.. code:: python

   artifact = lineapy.get('variable')
   print(artifact.get_code())

We note that the cleaned-up code outputted is as follows:

.. code:: python

   var = 10

   if var > 5:
      var += 10
   else:
      lst.append(20)
      var += 20
   
Note that in case we visit the ``else`` branch in the cleaned-up code, we would encounter a Runtime Error 
saying that the name ``lst`` is not defined. The reason for this behavior is that while creating the Linea 
Graph, LineaPy executes the user code to obtain run-time information, which enables LineaPy to create fairly
accurate cleaned-up code. However, in the case of conditionals, only one branch would be visited and hence we
would not have accurate run-time information about the instructions in the non-visited branch. We make an 
approximation in this case, which is to include all the instructions in the branches which are not visited.

Since we are not able to perform analysis within the non-visited branch, we do not have the information required
to know that the variable ``lst`` which is being included due to the non-included ``else`` branch, is defined
outside the ``if`` block, and hence the definition of ``lst`` gets sliced out as it is not required for the 
final collected artifact. 

To get around this behavior, the user can manually edit the source code by deleting the instruction within the 
non-visited branch which does not contribute to the artifact, or as an alternative, the user can add dummy 
variable declarations to ensure the code does not crash, as shown below:

.. code:: python

   import lineapy
   
   lst = []
   var = 10

   if var > 5:
      lst.append(10)
      var += 10
   else:
      var += 20

   lineapy.save(var, 'variable')

OR

.. code:: python

   import lineapy
   
   lst = []
   var = 10

   if var > 5:
      lst.append(10)
      var += 10
   else:
      lst = []
      lst.append(20)
      var += 20

   lineapy.save(var, 'variable')

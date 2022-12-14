.. _code_cleanup:

Cleaning up Messy Development Code
==================================

.. include:: /snippets/slack_support.rstinc

Data science development is characterized by nimble, iterative experimentation and exploratory
data analysis, which often results in a messy development code. Code cleanup is hence an essential
step for moving data science work into production. With the complete development history stored in
artifacts, LineaPy enables automatic code cleanup, facilitating transition to production.

First, identify the variable of interest in the development code. For instance, we might be
interested in cleaning up the development code for ``model3`` in it.

Then, store the variable as an artifact:

.. code-block:: python

    artifact = lineapy.save(model3, "best_model")

And simply ask for its cleaned-up code:

.. code:: python

   print(artifact.get_code())

This will return code relevant to the artifact only. That is, LineaPy has condensed
the original code by removing extraneous operations that do not affect the artifact
we care about (e.g., plotting and print statements).

.. note::

   This does not mean that we lost other parts of the development code. We can still access
   the artifact's full session code (including comments) with ``artifact.get_session_code()``.
   This should come in handy when trying to remember or understand the original development
   context of a given artifact.

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

.. include:: /snippets/docs_feedback.rstinc

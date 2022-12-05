Unvisited Conditional
=====================

.. include:: ../../../snippets/slack_support.rstinc

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
   
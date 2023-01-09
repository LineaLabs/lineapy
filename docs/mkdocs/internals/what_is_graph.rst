What is a LineaPy Graph?
------------------------

In LineaPy, we create a graph as we execute Python code, of every function that
was called and its dependencies. We use this graph to do "program slicing,"
meaning that we can understand all the code that is required to reproduce some
value in your program.

As well as the program graph, we also store some information about how things
were executed and the source code the graph was derived from.

We persist our graph structure to SQL (currently SQLite) using SQAlchemy,
an ORM. The :mod:`lineapy.data.types` file stores the graph nodes
and the :mod:`lineapy.db.relational` file stores the SQLAlchemy wrappers.

TODO: Visual of SQL table relationships

We have 6 different types of nodes in our graph currently. They all have an ID,
and then have different attributes to describe their behavior. Each node conceptually
has some "value" at runtime, so that when a node refers to another node, it can
refer to its value.

Example:

This is an example file that when traced will make all six nodes:

.. code-block:: python

   import lineapy
   from math import inf

   x = [inf]
   for i in range(10):
      x.append(i)

   res = str(i + len(x))


These are the nodes that would be created from tracing this code
(note that some attributes, like the session ID and source code references
have been elided in the interest of transparency. The IDs are also UUIDs normally,
but I have given them names for readability):

.. code-block:: python

   # The import node represents importing some module, in this case `math`.
   ImportNode(
      id='math',
      name='math',
   )

   # A lookup node is similar to an import, but it looks up some name of a function
   # from the builtins, in this case `getattr`
   LookupNode(
      id='getattr',
      name='getattr'
   )
   # The literal node represents a literal primitive python value, like strings, ints,
   # floats, etc. In this case it is the string "inf"
   LiteralNode(
      id='inf_str',
      value='inf'
   )
   # When we import something from a module, this is translated as an import
   # followed by a getattr call. This is represented by a CallNode, which
   # represents calling some function with some arguments.
   # In this case it gets the `inf` attribute from the `math` module.
   CallNode(
      id='inf',
      function_id='getattr',
      positional_args=['math', 'inf_str']
   )
   # We have our own internal functions, all prefixed with `l_` that we use
   # to implement certain python behavior. l_list takes a number of arguments
   # and makes a list out of them. You might ask, why don't we just use the builtin
   # `list`? Well that takes in some iterable as it's first argument.
   # Another way to look at `l_list` is a function equivalent of the built in
   # `[]` syntax.
   LookupNode(
      id='l_list',
      name='l_list'
   )
   # We then finally are able to create `x` by calling l_list with infinity
   CallNode(
      id='x',
      function_id='l_list',
      positional_args=['inf']
   )

   # Now we have a for loop. We currently "black box" this, treating it as a string
   # which we end up `exec` through `l_exec_statement`
   LiteralNode(
      id='loop_str',
      value='for i in range(10):\n    x.append(i)'
   )
   # We use our builtin `l_exec_statement` to compile and execute this code
   LookupNode(
      id='l_exec_statement',
      value='l_exec_statement'
   )
   # Now we can actually call this string. Also notice that we pass in `x`
   # as a dependency of this node, as a "global read" meaning that this node
   # reads the global `x` we defined, for the node with id `x`.
   CallNode(
      id='loop',
      function_id='l_exec_statement',
      positional_args=['loop_str'],
      global_reads={"x": "x"}
   )
   # Executing this loop creates a "mutate node" for value of x,
   # meaning that any later references to x should refer to this mutate node,
   # so that the code that mutated it, the loop, is also included implicitly
   # as a dependency
   MutateNode(
      id='x_mutated',
      source_id='x'
      call_id='loop'
   )
   # Executing this loop actually also sets the global `i`. We represent this
   # with a GlobalNode, representing the global variable set by some call (we'll
   # talk about how we detect the setting later):
   GlobalNode(
      id='i_global',
      name='i',
      call_id='loop'
   )

   # Now when computing the result, we can point to this global node `i_global`
   # as our input, as well as the mutate node
   LookupNode(
      id='len',
      value='len'
   )
   CallNode(
      id='len_x',
      function_id='len',
      positional_args=['x_mutated'],
   )
   LookupNode(
      id='add',
      value='add'
   )
   CallNode(
      id='added',
      function_id='add',
      positional_args=['i_global', 'len_x'],
   )
   LookupNode(
      id='str',
      value='str'
   )
   CallNode(
      id='res',
      function_id='str',
      positional_args=['added'],
   )

This can also be seen by visualizing the artifact.

.. code-block:: python

   import lineapy

   artifact = lineapy.save(res, "res")
   artifact.visualize()

.. image:: ../../_static/images/example_graph.png
  :width: 800
  :alt: Visualization of graph generated from example code.


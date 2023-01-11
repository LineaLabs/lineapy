Creating Graphs
---------------

One main part of the codebase involves creating a graph from Python code.

We create this graph at runtime as we execute the Python code. We start
with the AST of the Python and visit that as we turn it into a graph.

That goes through a number of steps, which we outline below, from outside in:

1. Entrypoint
~~~~~~~~~~~~~

We currently support two ways to start tracing from LineaPy. The CLI,
which is used to trace Python scripts, and our Jupyter integration which is
used in Jupyter Notebooks and IPython. Both of them go from source, to AST,
to a graph.

CLI
++++

In :mod:`lineapy.cli.cli` we support running a Python file from the
CLI. That can produce some output, such as (1) printing out sliced code/graph,
and (2) optionally to airflow file.

Exceptions
**********

We also call `set_custom_excepthook` which is used to override Python's
`sys.excepthook` so that if an exception is raised from executing user's code
then we ignore all the frames added by `lineapy` (see "Exception handling" later
in the doc).

Jupyter / IPython
+++++++++++++++++

We also supporting tracing using IPython (and so by proxy, Jupyter).

This is implemented in the :mod:`lineapy.editors.ipython` file. That class
provides three main entry points:

#. `start()`: Starts tracing by adding a function to `input_transformers_post <https://ipython.readthedocs.io/en/stable/config/inputtransforms.html#string-based-transformations>`_ which takes in a list of strings of the cell contents, and returns a list of strings which are executed by IPython.
#. `stop()`: Stops the tracing, removing this function from the `input_transformers_post`.
#. `visualize()`: output a visual of the current state of the graph.

In our input transformer, we save the code from the cell in a global
and return the same lines from every cell, which call out to a function
in the `ipython` module, `_end_cell`, which looks at the lines of code,
transforms them through LineaPy, and optionally returns a value if one should
be "returned" from the cell (i.e. if the last line is an expression that does not
end with a ';').

Exceptions
**********

IPython does not use `sys.excepthook` so we have to take a different approach
for handling exceptions in Jupyter. Instead, we set override the
`_get_exc_info` method on the IPython shell, to have the same effect.

2. Parsing the AST
~~~~~~~~~~~~~~~~~~

Once we have initialized lineapy with the user's code, we traverse that through the
python AST using a visitor defined in :mod:`lineapy.transformer.node_transformer`.

As we traverse the AST, we create nodes for each piece of it.

3. Creating nodes
~~~~~~~~~~~~~~~~~

This `NodeTransformer` relies on an :class:`lineapy.instrumentation.tracer.Tracer`
to actually create the nodes.

The general process to create a node is:

#. Create new instance of some `Node` subclass defined in `types.py`, giving it a new UUID.
#. Then in `process_node` pass the newly created node to the `Executor` to execute it, and return any "side effects" that happen
#. We react to those side effects, by potentially adding more nodes to the graph (which goes through step 1 one more time).
#. Write this node to the database.

We go into these side effects lower down, since they pertain to multiple layers.

4. Executing nodes
~~~~~~~~~~~~~~~~~~

As mentioned above, the `Tracer` passes on the responsibility of executing the
node to the :class:`lineapy.execution.executor.Executor`. This is responsible
for keeping a mapping of each node and its value after being executed.

It returns a number of "side effects" which say things like "Node xxx was modified"
that the tracer can then handle. These are created based on the `inspect_function`'s
side effects that are described below.

5. Determine function side effects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When we try to execute a `CallNode`, we need to know things like "does this
modify any of its arguments?" to understand how it affects the graph.

This reasoning is implemented in :mod:`lineapy.execution.inspect_function`
which is basically one big switch statement, that understands certain
Python functions. If some function is not being sliced properly,
it is likely due to it being missing from this file.

This also returns a list of "side effects," which bubble up to the Executor.
However, unlike the side effects returned from the executor, which refer to things
by their node ID, in the `inspect_function`, the side effects instead refer to
which arg/kwargs/value was modified. So it would say instead "The first arg was modified".

This is to keep the inspect_function from having to know anything about nodes,
and instead just about describing the side effects given some Python function call
and values.
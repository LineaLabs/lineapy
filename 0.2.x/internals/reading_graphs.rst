Reading graphs
--------------

After we have created a graph, we can perform a number of operations on it.

Many of these use the :mod:`lineapy.data.graph` object which represents
a collection of nodes. It can sort them topologically and by line number, meaning
that any node will come after its parents, and all nodes with line numbers will
be sorted by those as well.

Note: It currently also include the session context, but we don't really use this from the
graph. We could remove this

Re-execution (steps 4-5)
~~~~~~~~~~~~~~~~~~~~~~~~

We can re-execute a graph to re-run the Python function calls that were saved in it.

We keep the executor separate from the tracer, in order to facilitate this, so that
we only need the `Executor` for re-execution, using the `execute_graph` method,
which simply iterates through a number of nodes and executes each of them.

This is currently tested in our end to end tests, by re-executing every graph,
but it is not currently exposed to the user.

Slicing
~~~~~~~

One common use of a graph is to "slice it", meaning removing the nodes
that are not ancestors of some input nodes.

We can use this then to output a "clean up" source code, where any
lines that are not required to reproduce some result are removed.
What this means is that the graph structure needs to represent program
dependence, which is why some of our more complicated analysis are required.

This is implemented in :mod:`lineapy.graph_reader.program_slice`.

Visualizing
~~~~~~~~~~~

We currently supporting visualizing a graph using Graphviz for debugging
and teaching purposes. This is implemented in the
:mod:`lineapy.visualizer` directory with three main files:

#. :mod:`lineapy.visualizer`: Provides a `Visualizer` object which is the publicly exposed
   interface for visualizing a graph. In supports creating it for a number of
   different scenarios, each with their own configurations set. For example,
   we want to show more detail in our testing than in our public API.
   The visualizer also optionally supports taking a `Tracer` object, along
   with the required `Graph` object, to show more details that are present
   in that object, like the variable assignments. However, this is not always
   available, like when visualizing only a certain artifact, which can happen
   during re-execution, so the tracer is unavailable.
   It also supports a number of ways to viewing the visualization, like
   as SVG, PDF, or as Jupyter Output.
#. :mod:`lineapy.visualizer.graphviz`: This files manages actually creating the graphviz source
   using the `Graphviz <https://graphviz.readthedocs.io/en/stable/index.html>`_
   library. It renders each edge and node, and also renders a legend.
#. :meth:`lineapy.visualizer.visual_graph.to_visual_graph`: This takes in the Graph and (optional) Tracer and returns
   a list of nodes and edges in a form that is closer to how Graphviz works.
   The goal of having this extra abstraction layer, as opposed to just emitting
   graphviz directly, is ensure a logically consistent rendering. It is similar
   to the MVC paradigm, or like React's components. This would be equivalent
   to the props, where as the graphviz file is equivalent to taking those
   props and then rendering them.

Whenever a new node type is added, or any is modified, the graphviz and visual_graph
files should be updated to handle it.

Outputting to airflow
~~~~~~~~~~~~~~~~~~~~~

On top of just slicing the code, we also support creating an Airflow DAG out
of the resulting code. This is currently implemented through string templating
in :class:`lineapy.plugins.pipeline_writers.AirflowPipelineWriter` to create a file that airflow can understand.

All of the code is currently saved in one `PythonOperator`.

This is exposed to users in two ways:

1. In the cli through the `--export-slice-to-airflow-dag` flag, which will
   save the resulting DAG to the current directory.
2. In our API (usable in a script or in Jupyter) through the `to_airflow` method
   on a saved artifact. This is implemented in :mod:`lineapy.graph_reader.apis`.
   Instead of saving to the current directory, this tries to find Airflow's
   DAGs folder, by looking at the `AIRFLOW_HOME` environment variable and saving it
   in there, so it is picked up by Airflow automatically.



Put it all together
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from sklearn.linear_model import LogisticRegression
   from sklearn.preprocessing import LabelEncoder

   train = pd.read_csv("data/sample_train_data.csv")

   train['DeviceInfo'] = LabelEncoder().fit_transform(list(train['DeviceInfo'].values))

   y = train['isFraud'].copy()

   train = train.drop('isFraud', axis=1)
   train = train.fillna(-1)

   regression_model = LogisticRegression().fit(train, y)

.. image:: ../../_static/images/sample_graph.png
  :width: 800
  :alt: Sample visualization of Graph


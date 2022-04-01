# Visualizer

We use `graphviz` to show the internal state of lineapy. We use the graphs
to support demos and debugging/tests. 

The graph can be created two ways: (1) with the tracer, which will contain more
rich run-time information, such as the variable names, and mutation nodes, and 
(2) without run time information, such as when we load the artifact from the database.

There are four different ways to access the visualizer currently, with slightly
different configurations (you can find the full list in `__init__.py`):

- ipython
- snapshots
- cli
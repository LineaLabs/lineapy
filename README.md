# `lineapy`

Lineapy is a Python library for capturing, analyzing, and automating data science workflows.

[![Coverage Status](https://coveralls.io/repos/github/LineaLabs/lineapy/badge.svg?t=jgH0YL)](https://coveralls.io/github/LineaLabs/lineapy)

## Our Vision

On a high-level, Linea traces the code executed to get an **"understanding" of the code, and its context**. These understanding of your development process allow Linea to provide a set of tools that help you get more value out of your work.

### Linea Concepts

A natural unit of organization for these code are variables in the code---both their value and the code used to create them. Our features revolve around these units, which we call _artifacts_.

## Features

We are still early in the process, and we currently support the following features:

- Code cleanup: often when working with data, we don't know what efforts will pan out. When we do have something we want to keep, we can save it as an artifact and create a version of the code that only includes the pieces neccesary to recreate that artifact. This is called "Program Slicing" in the literature. Linea's slicing feature makes it easy to share and re-execute these work.
- Saving and getting artifacts from different sessions/notebooks/scripts.

### Future Features

We are working towards a number of other features and have [created issues to describe some of them in Github, tagged with `User Story`](https://github.com/LineaLabs/lineapy/labels/User%20Story), which include:

- Automatic creation of [Airflow DAGs](https://github.com/LineaLabs/lineapy/issues/236) (and related systems) from Linea artifacts. Note that we take a radically different approach that tools like Papermill, because we are actually _analyzing the code_ to automatically instrument the optimizations.
- Metadata search e.g. "Find all charts that use this column from this table" [see issues on analyzing data sources](https://github.com/LineaLabs/lineapy/issues/22) and [analyzing SQL](https://github.com/LineaLabs/lineapy/issues/272)).
- Hosted storage of Linea artifacts (currently, only the local version is supported).

If you have any feedback for us, please get in touch! We welcome feedback on Github, either by commenting on existing issues or creating new ones. You can also find us on [Twitter](https://twitter.com/linealabs) and [Slack](https://lineacommunity.slack.com/)!

## Installing

You can run linea either by cloning the repository or by using our Docker image.

### Docker

1. First install Docker and then authenticate to the [Github Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
   so you can pull our private image.
2. Now you can pull and run our image to slice Python code:

```bash
$ cat my_script.py
x = 1 + 2
y = x + 3
assert y == 4

$ docker run --rm -v $PWD:/app -w /app ghcr.io/linealabs/lineapy:main lineapy my_script.py --print-graph
...
```

### Repository

You can also run Linea by cloning this repository and running the `lineapy`:

```bash
$ git clone git@github.com:LineaLabs/lineapy.git
$ cd lineapy
# Linea currently requires Python 3.9
$ pip install -e .
$ lineapy --slice "p value" tests/housing.py
...
```

## Usage

These features are currently exposed via two surfaces, one is the CLI and the other is Jupyter, supporting all notebook interfaces.

### CLI

Currently, you can run Linea as CLI command to slice your Python code to extract
only the code that is necessary to recompute some result. Along the way, Linea
stores the semantics of your code into a database, which we are working on exposing
as well.

```bash
$ lineapy --help
Usage: lineapy [OPTIONS] FILE_NAME

Options:
  --mode TEXT          Either `memory`, `dev`, `test`, or `prod` mode
  --slice TEXT         Print the sliced code that this artifact depends on
  --export-slice TEXT  Requires --slice. Export the sliced code that {slice}
                       depends on to {export_slice}.py
  --print-source       Whether to print the source code
  --print-graph        Whether to print the generated graph code
  --verbose            Print out logging for graph creation and execution
  --visualize     Visualize the resulting graph with Graphviz
  --help               Show this message and exit.

# Run linea on a Python file to analyze it.
# --visualize creates a visual representaiton of the underlying graph and displays it
$ lineapy --print-source --visualize tests/simple.py
...
# Use --slice to slice the code to that which is needed to recompute an artifact
$ lineapy --print-source tests/housing.py --slice 'p value'
...
```

### Jupyter and IPython

You can also run Linea interactively in a notebook or IPython.

The easiest way to do this to tell IPython to load the `lineapy` extension
by default, by setting the `InteractiveShellApp.extensions` extension to include
`lineapy`.

If you are developing from this repository, we have created some ipython config files
which have this enabled. So you can turn on tracing by telling IPython to look
at those:

```python
$ env IPYTHONDIR=$PWD/.ipython ipython
env IPYTHONDIR=$PWD/.ipython ipython
Python 3.9.7 (default, Sep 16 2021, 08:50:36)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.29.0 -- An enhanced Interactive Python. Type '?' for help.
[16:48:07] INFO     Connecting to Linea DB at sqlite:///.linea/db.sqlite

In [1]: import lineapy
   ...: x = 100
   ...: y = x + 500
   ...: z = x - 10
   ...: print(lineapy.save(z, "z").code)
x = 100
z = x - 10
```

This also works for starting `jupyter notebook` or `jupyter lab`, or any other
frontend which uses the ipython kernel.

You can also add `c.InteractiveShellApp.extensions = ["lineapy"]`
to your own IPython config (found by running `ipython locate profile default`).

_See [`ipython`'s documentation on their configuration](https://ipython.readthedocs.io/en/stable/config/intro.html) for more information_

For a larger example, you can look at [`examples/Explorations.ipynb`](./examples/Explorations.ipynb)

If you have an existing notebook, you can try running it through linea, to see if it
still works, and to save the resulting graph. For example:

```bash
env IPYTHONDIR=$PWD/.ipython jupyter nbconvert --to notebook --execute examples/Explorations.ipynb --inplace --allow-errors
```

If you would like to change the database that linea talks to, you can use the
`LINEA_DATABASE_URL` env variable. For example, to set it to `sqlite:///:memory:`
to use an in memory database instead of writing to disk.

### Web UI

We were previously working on a web based user interface to browse executions, but we are currently focusing on the API experience (in both Jupyter and the CLI).

## Installing

You can run linea either by cloning the repository or by using our Docker image.

### Docker

1. First install Docker and then authenticate to the [Github Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
   so you can pull our private image.
2. Now you can pull and run our image to slice Python code:

```bash
$ cat my_script.py
x = 1 + 2
y = x + 3
assert y == 6

$ docker run --rm -v $PWD:/app -w /app ghcr.io/linealabs/lineapy:main lineapy my_script.py --print-graph
...
```

## Known Bugs in Python Language Support

In order to properly slice your code, we have to understand different Python language features and libraries. We are working to add coverage to support all of Python, as well as make our analysis more accurate. We have [a number of open issues to track what things we know we don't support in Python, tagged under `Language Support`](https://github.com/LineaLabs/lineapy/labels/Language%20Support). Feel free to open more if come accross code that doesn't run or doesn't properly slice.

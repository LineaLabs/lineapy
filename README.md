# `lineapy`

Lineapy is a Python library for capturing, analyzing, and automating data science workflows.

[![Coverage Status](https://coveralls.io/repos/github/LineaLabs/lineapy/badge.svg?t=jgH0YL)](https://coveralls.io/github/LineaLabs/lineapy)

## Features

On a high-level, Linea traces the code executed to get an understanding of the code, persist the related code and variable state, and capture the execution context, such as who and when the code was executed.

These understanding of your development process in turn allows Linea to provide a set of tools that help you get more value out of your work. A natural unit of organization for these code are variables in the code---both their value and the code used to create them. Our features revolve around these units, which we call _artifacts_.

We currently support the following features:

- Code cleanup: often when working with data, we don't know what efforts will pan out. When we do have something we want to keep, we can save it as an artifact and create a version of the code that only includes the pieces neccesary to recreate that artifact. This is called "Program Slicing" in the literature. Linea's slicing feature makes it easy to share and re-execute these work.

We are working towards a number of other features and have [created issues to describe some of them in Github, tagged with `User Story`](https://github.com/LineaLabs/lineapy/labels/User%20Story), which include:

- Automatic creation of [Airflow DAGs](https://github.com/LineaLabs/lineapy/issues/236) (and related systems) from Linea artifacts
- Metadata search e.g. "Find all charts that use this column from this table" [see issues on analyzing data sources](https://github.com/LineaLabs/lineapy/issues/22) and [analyzing SQL](https://github.com/LineaLabs/lineapy/issues/272))
- Hosted storage of Linea artifacts

If you have any feedback for us, please get in touch! We welcome feedback on Github, either by commenting on existing issues or creating new ones. You can also find us on [Twitter](https://twitter.com/linealabs) and [Slack](https://lineacommunity.slack.com/)!

## Python Language Support

In order to properly slice your code, we have to understand different Python language features and libraries. We are working to add coverage to support all of Python, as well as make our analysis more accurate. We have [a number of open issues to track what things we know we don't support in Python, tagged under `Language Support`](https://github.com/LineaLabs/lineapy/labels/Language%20Support). Feel free to open more if come accross code that doesn't run or doesn't properly slice.

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

### Interactive

**⚠️ The user experience for the notebook is still very much in progress and will change in the near future.**
We have opened [an issue](https://github.com/LineaLabs/lineapy/issues/298) to track some of these pain points. ⚠️

You can also run Linea from an Juptyer notebook or IPython.

First, import linea and start the tracing:

```python
import lineapy.ipython
lineapy.ipython.start()
```

Now, ever subsequent cell will be traced. Let's say you run a few more lines
and publish a result:

```python
import lineapy
# please follow the `import lineapy` import pattern

x = 100
y = x + 500
z = x - 10
lineapy.save(z, "z")
```

Then you can stop tracing and slice the code:

```python
res = lineapy.ipython.stop()
print(res.slice("z"))
# Prints out
# x = 100
# z = x - 10
```

For a full example, you can look at [`tests/test_notebook.ipynb`](./tests/test_notebook.ipynb)

If you have an existing notebook, you can try running it through linea, to see if it
still works, and to save the resulting graph. For example:

```bash
env LINEA_VISUALIZATION_NAME=output_graph jupyter nbconvert --to notebook --execute notebook_name.ipynb --inplace --ExecutePreprocessor.extra_arguments=--IPKernelApp.extensions=lineapy
```

### Web UI

We were previously working on a web based user interface to browse executions, but we are currently focusing on the Python and command line experience.

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

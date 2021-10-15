# `lineapy`

Lineapy is a Python library for capturing, analyzing, and automating data science workflows.

[![Coverage Status](https://coveralls.io/repos/github/LineaLabs/lineapy/badge.svg?t=jgH0YL)](https://coveralls.io/github/LineaLabs/lineapy)

## Features

On a high-level, Linea traces the code executed to get an understanding of the code, persist the related code and variable state, and capture the execution context, such as who and when the code was executed.

These understanding of your development process in turn allows Linea to provide a
set of tools that help you get more values out of our work. 
A natural unit of organization for these code are variables in the code---both their value and the code used to create them. Our features revolve around these units, which we call 
_artifact_s.

We currently support the following features:

- Code cleanup: often when working with data, we don't know what efforts will pan out. When we do have something we want to keep, . This is called "Program Slicing" in the literature.
Linea's slicing feature makes it easy to share and re-execute these work.

There are many others on our road map. If you have any feedback for us, please get in touch! We are on [Twitter](https://twitter.com/linealabs) and [Slack](https://lineacommunity.slack.com/)!

These features are currently exposed via two surfaces, one is the CLI and the 
other is Jupyter (Lab/Notebook).
### CLI

Currently, you can run Linea as CLI command to slice your Python code to extract
only the code that is necessary to recompute some result. Along the way, Linea
stores the semantics of your code into a database, which we are working on exposing
as well.

We are working to add support for more Python constructs. We currently don't support
much control flow, function mutation, or all function definitions.

```bash
$ lineapy --help
Usage: lineapy [OPTIONS] FILE_NAME

Options:
  --mode TEXT     Either `memory`, `dev`, `test`, or `prod` mode
  --slice TEXT    Print the sliced code that this artifact depends on
  --print-source  Whether to print the source code
  --print-graph   Whether to print the generated graph code
  --verbose       Print out logging for graph creation and execution
  --help          Show this message and exit.

# Run linea on a Python file to analyze it.
# Use --print-graph to print out the graph it creates
$ lineapy --print-source --print-graph tests/simple.py
...
# Use --slice to slice the code to that which is needed to recompute an artifact
$ lineapy --print-source tests/housing.py --slice 'p value'
...
```

### Interactive

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

x = 100
y = x + 500
z = x - 10
lineapy.linea_publish(z, "z")
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

$ docker run --rm -v $PWD:/app -w /app ghcr.io/linealabs/lineapy:main my_script.py --print-graph
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

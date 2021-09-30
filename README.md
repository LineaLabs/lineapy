# `lineapy`

Lineapy is a Python library for analyzing data science workflows.

TODO: Insert terminal gif of running lineapy slicing on datascience file.

## Features

Currently, you can run Linea as CLI command to slice your Python code to extract
only the code that is neccesary to recompute some result. Along the way, Linea
stores the semantics of your code into a database, which we are working on exposing
as well.

We are working to add support for more Python contructs. We currently don't support
much control flow, function mutation, or all function definitions.

```bash
$ lineapy --help
...
```

### Installing

You can run linea either by cloning the repository or by using our Docker image.

### Docker

1. First install Docker and then authenticate to the [Github Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
   so you can pull our private image.
2. Now you can pull and run our image to slice Python code:

```bash
$ cat my_script.py
....
$ docker run --rm -v $PWD:/app -w /app ghcr.io/LineaLabs/lineapy:latest my_script.py
...
```

### Repository

You can also run Linea by cloning this repository and running the `lineapy`:

```bash
$ git clone git@github.com:LineaLabs/lineapy.git
$ cd lineapy
# Linea currently requires Python 3.9
$ pip install -e .

$ cat examples/housing_data.py
some file
# Linea will analyze your file in order to slice your code for a certain artifact.
$ lineapy --slice "prediction_var_name" examples/housing_data.py
some sliced code
```

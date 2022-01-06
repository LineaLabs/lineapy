<p align="center">
    <a href="https://linea.ai/">
      <img src="https://linea.ai/logo-negative-trsp-nopadding.png" width="550">
    </a>
</p>
<br />

[![Python](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml/badge.svg)](https://github.com/LineaLabs/lineapy/actions/workflows/python-app.yml)


Lineapy is a Python library for capturing, analyzing, and automating data 
science workflows.

On a high-level, Linea traces the code executed to get an 
**understanding of the code and its context**. 
These understanding of your development process allow Linea to 
provide a set of tools that help you get more value out of your work.

A natural unit of organization for these code are variables in the code---both 
their value and the code used to create them. Our features revolve around these 
units, which we call _artifacts_.

## Features

We are still early in the process, and we currently support the following features:

- **Code cleanup**: often when working with data, we don't know what efforts 
will pan out. When we do have something we want to keep, we can save it as an 
artifact and create a version of the code that only includes the pieces necessary 
to recreate that artifact. This is called "Program Slicing" in the literature. 
Linea's slicing feature makes it easy to share and re-execute these work.
  - This is done automatically by calling the `lineapy.save` API on the variable of interest.
  - `/tests/housing.py` contains an example.
- **Pipeline extraction**: Automatic creation of [Airflow DAGs](https://github.com/LineaLabs/lineapy/issues/236) (and related systems) from Linea artifacts. Note that we take a radically different approach that tools like Papermill, because we are actually _analyzing the code_ to automatically instrument the optimizations.
  - This is done via the API `.to_airflow()` on a linea artifact that is returned either through `.save` or `.get`.
    By default, the generated airflow file is placed under your home directory's `airflow/dag` folders.
  - `examples/Demo_1_Preprocessing.ipynb` and `examples/Demo_2_Modeling.ipynb` contains two end-to-end examples.
- **Artifact store**: Saving and getting artifacts from different sessions/notebooks/scripts.
  - This is done via `lineapy.get` API of artifacts that were saved via `lineapy.save`.
  - You can also view a catalog of saved artifacts through the API `lineapy.catalog`.
  - `examples/1_Explorations.ipynb` + `/examples/2_APIs.ipynb` contains an example for all three APIs.

### Future Features

We are working towards a number of other features and have [created issues to describe some of them in Github, tagged with `User Story`](https://github.com/LineaLabs/lineapy/labels/User%20Story), which include:

- Metadata search e.g. "Find all charts that use this column from this table" 
[see issues on analyzing data sources](https://github.com/LineaLabs/lineapy/issues/22) 
and [analyzing SQL](https://github.com/LineaLabs/lineapy/issues/272)).
- Enhanced execution based versioning.
- Integration with existing infra, e.g., AWS, Airflow
- Support execution scale up, e.g., automatically creating the same version of the code with Dask.

If you have any feedback for us, please get in touch! We welcome feedback on 
Github, either by commenting on existing issues or creating new ones. You can 
also find us on [Twitter](https://twitter.com/linealabs) and [Slack](https://lineacommunity.slack.com/)!

## Installing

You can run `lineapy` through three options:
1. Github CodeSpaces
2. Docker image
3. DIY: clone the repository

We'll describe the options below.

### Github Codespaces

Click the green "<> Code" button above (in the homepage), and in the "Codespaces" 
tab you can click on the gray button "New codespace".

The first time you load it might take a while to download Docker. Once the 
VS Code interface loads, after a few seconds, the "PORTS" tab on the lower 
panel should load (per the image below).

![Screenshot of VS Code ports on Codespaces](./ports.png)

If you click on the globe icon (🌐) next to JupyterLab, it will open port 8888.
If you click the same globe icon next to Airflow, it will open port 8080.

By default, lab will have two demo notebooks open. Run Demo 1, and then Demo 2
to the end, then you will see the Airflow jobs deployed in the dashboard!

### Docker

1. First install Docker and then authenticate to the [Github Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
   so you can pull our private image.
2. Now you can pull and run our image to slice Python code:

```bash
$ docker run --rm -v $PWD:/app -w /app ghcr.io/linealabs/lineapy:main lineapy --slice "p value" tests/housing.py
...
```

### Repository

You can also run Linea by cloning this repository and running the `lineapy`:

```bash
$ git clone git@github.com:LineaLabs/lineapy.git
$ cd lineapy
# Linea currently requires Python 3.8+
$ pip install -r requirements.txt
$ python setup.py install
$ lineapy --slice "p value" tests/housing.py
...
```

Note that if you are not using Codespaces and are manually running Airflow and JupyterLab, 
we also created convenient Makefile configs to start Airflow (`make airflow_start`) on 
[`localhost:8080`](http://localhost:8080) and JupyterLab (`make jupyterlab_start`)
on [`localhost:8888`](http://localhost:8888).


## Specific Instructions for Cli and Jupyter

These features are currently exposed via two surfaces, one is the CLI and the
other is Jupyter, supporting all notebook interfaces.

### CLI

Currently, you can run Linea as CLI command to slice your Python code to extract
only the code that is necessary to recompute some result. Along the way, Linea
stores the semantics of your code into a database, which we are working on exposing
as well.

```bash
$ lineapy --help
Usage: lineapy [OPTIONS] FILE_NAME

Options:
  --db-url TEXT                   Set the DB URL. If None, will default to
                                  reading from the LINEA_DATABASE_URL env
                                  variable and if that is not set then will
                                  default to sqlite:///{LINEA_HOME}/db.sqlite.
                                  Note that {LINEA_HOME} will be replaced with
                                  the root linea home directory. This is the
                                  first directory found which has a .linea
                                  folder
  --slice TEXT                    Print the sliced code that this artifact
                                  depends on
  --export-slice TEXT             Requires --slice. Export the sliced code
                                  that {slice} depends on to {export_slice}.py
  --export-slice-to-airflow-dag, --airflow TEXT
                                  Requires --slice. Export the sliced code
                                  from all slices to an Airflow DAG {export-
                                  slice-to-airflow-dag}.py
  --airflow-task-dependencies TEXT
                                  Optional flag for --airflow. Specifies tasks
                                  dependencies in Airflow format, i.e. 'p
                                  value' >> 'y' or 'p value', 'x' >> 'y'. Put
                                  slice names under single quotes.
  --print-source                  Whether to print the source code
  --print-graph                   Whether to print the generated graph code
  --verbose                       Print out logging for graph creation and
                                  execution
  --visualize                     Visualize the resulting graph with Graphviz
  --help                          Show this message and exit.

# Run linea on a Python file to analyze it.
# --visualize creates a visual representation of the underlying graph and displays it
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

## Known Bugs in Python Language Support

In order to properly slice your code, we have to understand different Python 
language features and libraries. We are working to add coverage to support all 
of Python, as well as make our analysis more accurate. We have 
[a number of open issues to track what things we know we don't support in Python, tagged under `Language Support`](https://github.com/LineaLabs/lineapy/labels/Language%20Support). 
Feel free to open more if come across code that doesn't run or doesn't properly slice.

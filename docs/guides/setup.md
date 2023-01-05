# Installation and Setup

## Installing LineaPy

### Prerequisites

LineaPy runs on `Python>=3.7` and `IPython>=7.0.0`. It does not come with a Jupyter installation,
so you will need to [install one](https://jupyter.org/install) for interactive computing.

### Basics

To install LineaPy, run:

```bash
pip install lineapy
```

If you want to run the latest version of LineaPy directly from the source, follow instructions
[here](contributing/setup.md#installation).

!!! info

    By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
    However, SQLite has several limitations, one of which is that it does not support multiple concurrent
    writes to a database (it will result in a database lock). If you want to use a more robust database,
    please follow [instructions](configuration/storage-location.md#storing-artifact-metadata-in-postgresql) for using PostgreSQL.

### Extras

LineaPy offers several extras to extend its core capabilities:

| Version  | Installation Command            | Enables                                              |
| -------- | ------------------------------- | ---------------------------------------------------- |
| minimal  | `pip install lineapy[minimal]`  | Minimal dependencies for LineaPy                     |
| dev      | `pip install lineapy[dev]`      | All LineaPy dependencies for testing and development |
| s3       | `pip install lineapy[s3]`       | Dependencies to use S3 to save artifact              |
| graph    | `pip install lineapy[graph]`    | Dependencies to visualize LineaPy node graph         |
| postgres | `pip install lineapy[postgres]` | Dependencies to use PostgreSQL backend               |

!!! note

    The `minimal` version of LineaPy does not include `black` or `isort`, which
    may result in less organized output code and scripts.

### JupyterHub

LineaPy works with JupyterHub!

If LineaPy is installed by an admin, it will be accessible to every user. The admin can set the LineaPy 
extension to be automatically loaded by adding `c.InteractiveShellApp.extensions = ["lineapy"]` in 
[ipython_config.py](https://ipython.readthedocs.io/en/stable/config/intro.html).

If LineaPy is installed by an individual user, it will be accessible to that particular
user only as long as they do not have a write permission on the shared environment.
In this case, the user will need to run `%load_ext lineapy` at the top of their session
as explained below.

## Running LineaPy

### Jupyter and IPython

To use LineaPy in an interactive computing environment such as Jupyter Notebook/Lab or IPython, load its extension by executing the following command at the top of your session:

```python
%load_ext lineapy
```

Please note:

- You must run this as the first command in a given session. Executing it in the middle of a session will lead to erroneous behaviors by LineaPy.

- This command loads the extension for the current session only. It does not carry over to different sessions, so you will need to repeat it for each new session.

Alternatively, you can launch the environment with the `lineapy` command, like so:

```bash
lineapy jupyter notebook
```

```bash
lineapy jupyter lab
```

```bash
lineapy ipython
```

This will automatically load the LineaPy extension in the corresponding interactive shell application,
and you will not need to manually load it for every new session.

!!! tip

    If your Jupyter environment has multiple kernels, choose `Python 3 (ipykernel)` which `lineapy` defaults to.

### Hosted Jupyter Environment

In hosted Jupyter notebook environments such as JupyterHub, Google Colab, Kaggle, Databricks or in any other 
environments that are not started using CLI (such as Jupyter extension within VS Code), you need to 
install `lineapy` directly within your notebook first via:

```bash
!pip install lineapy
```

Then you can manually load `lineapy` extension with :

```python
%load_ext lineapy
```

!!! note

    For environments with `IPython<7.0`, you need to upgrade the package before the above steps:

    ```bash
    !pip install --upgrade ipython
    ```

    and restart the notebook runtime.

### CLI

You can also use LineaPy as a CLI command or runnable Python module. To see available options, run the following commands:

```bash
# LineaPy as a CLI command
lineapy python --help
```

or

```bash
# LineaPy as a runnable Python module
python -m lineapy --help
```

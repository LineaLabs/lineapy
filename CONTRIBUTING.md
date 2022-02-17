# Contributing to lineapy

**Table of contents**
   1. [Where to Start?]()
      1. [Build & Read the Docs]()
      2. [Set up the Environment]()
      3. [Our Git Model]()
      4. [Contribute]()
   2. [Testing]()
      1. [Snapshots]()
      2. [XFail Tests]()
      3. [Integration Tests]()
      4. [Notebook Tests]()
      5. [Slow Tests]()
      6. [Airflow Tests]()
      7. [Additional Notes on Docker Testing]()
   3. [Debugging]()
      1. [VSC]()
      2. [Visual Graphs]()
      3. [Logging]()
      4. [Debug Flags]()
      5. [Additional Utilities]()
         1. [AST Inspection]()
         2. [Github Actions]()
   4. [Additional Notes]()
      1. [Performance Profiling]()
      2. [Known Issues]()
      3. [Using venv instead of Conda]()
      4. [Further Readings]()

## Where to Start

### 1.1. Build & read the docs

Run the following command in the root directory

```bash
sphinx-autobuild docs/source/ docs/build/html/
```

Note - *if you're modifying the docs:* Any changes in the rst files in the `/docs` directory will be detected and the html refreshed. However, changes in the doc strings in code will not be picked up, and you'll have to rebuild the docs to refresh.

We recommend you at least read the following sections in the docs before getting started.
* What is a Linea Graph
* Creating Graphs
* Reading Graphs


### 1.2. Set up the environment
There are two main ways to set up `lineapy` locally either using Conda or using Docker. If you prefer to use venv instead of Conda, then please follow the instructions [here]()


#### First-time Setup

First download the submodules so you can run our tests:

```
git submodule update --init --recursive .
```

#### Conda

```bash
conda create --name lineapy python=3.9 \
    postgresql \
    graphviz \
    cmake # needed for building deps of numpy tutorial on mac
conda activate lineapy
pip install -r requirements.txt
pip install -e .

# verify everything works as expected
lineapy --help
pytest tests
```

(We support python 3.8+ for now and you can initialize a conda environment with python 3.8 as well if you desire)



##### Export to Airflow (Optional)

Sliced code can be exported to an Airflow DAG using the following command:

```bash
lineapy python tests/housing.py --slice "p value" --airflow sliced_housing_dag
```

This creates a `sliced_housing_dag.py` file in the current dir. It can be executed with:

```bash
airflow db init
airflow dags test sliced_housing_dag_dag $(date '+%Y-%m-%d') -S .
```

#### Docker + Makefile

##### Prerequisites

Remove the following folders (if they exist) and create a Docker network
```bash
rm -rf build dist
docker network create lineapy
```

To build the Lineapy container, run `make build` (you can pass in arguments with `args=`, i.e. `make build args=--no-cache`)
To open bash within the container, run `make bash`. One can either use bash for dev or can connect to remote runtimes inside a container using extensions available for the editor of choice.
`make tests` executes the test suite.

To build Lineapy contained with Airflow, run `make build-airflow`. `make tests-airflow` runs airflow tests.
`make airflow-up` is one command that will bring up a standalone local Airflow server on port 8080.
Login and password will be printed on command line output. Please note that this mode used SQLite DB and is not meant for heavy workloads.

### 1.3. Our Git model

We use [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow) for commits to `lineapy`.

### 1.4. Contribute

To contribute, please follow these steps:

A. Create a new branch and set its upstream

```bash
git checkout -b TicketOrBranchName
git branch --set-upstream-to=origin/<branch> TicketOrBranchName
```


B. Work on code

C. Add your code changes `git add new_code_files`

D. [`pre-commit`](https://github.com/pre-commit/pre-commit) your changes

```bash
# Installs pre commit hook to run linting before commit:
pre-commit install
# To manually run hooks:
pre-commit
# To force a run even when there are no changes
pre-commit run --all-files
```

Note that the pre-commit hook does not run the tests, since these are time
consuming and you might not want to have to wait to run them on every commit.

The pre commit config also pins the versions of the packages. To update them to
the latest, run `pre-commit autoupdate`.


E. finally run tests `pytest tests`

F. Repeat steps B-E until there are no more errors

G. Commit your code

```bash
git commit -m "message with detailed description"
git push
```

H. Create a PR to merge your branch

Note - if you're using Docker as your local environment, please check [here]() for additional details about testing

## 2. Testing

```bash
mypy . # TODO is this line optional
black --line-length 79 --check . # TODO is this line optional
pytest tests
```


### 2.1. Snapshots

Some tests use [`syrupy`](https://github.com/tophat/syrupy) for snapshot test,
to make it easier to update generate code and graphs.
If you mean to change the tracing or graph spec, or add a new test that uses it,
then run `pytest --snapshot-update` to update the saved snapshots.
If using docker, you can use `make test args="--snapshot-update"` to update snapshots.

We also generate snapshots for a visualization of the graph as SVG. These are
only used to help in the diffs, not for testing. They will be regenerated by
default only when a snapshot is updated or created. To force them to
regenerate, use the `--svg-update` CLI option. They are not regenerated by
default, since their source is not deterministic.

### 2.2. XFail

We also use [pytest's xfail](https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail) to mark tests that are expected to fail, because of a known bug. To have them run anyway, run `--run-xfail`.


### 2.3. Integration tests

There are also integration tests that are tested against external libraries. These tests
also take a while and many of them are currently xfailing. To run them, use
`pytest tests -m "integration"` (in the root dir).

### 2.4. Notebook tests

We currently have notebooks that are also evaluated in the tests, and the
outputs are compared.

If you want to re-run all the notebooks and update their outputs, run:

```bash
make notebooks
# You can also re-run and save a particular notebook with
make tests/notebook/test_visualize.ipynb
```

Or you can open it in a notebook UI (JupyterLab, JupyterNotebook, VS Code, etc.)
and re-run it manually

### 2.5. Slow tests

Some tests have been marked "slow". These typically take > 0.5s and can be skipped
by passing the args `pytest tests -m "not slow"` when running pytest.


### 2.6. Airflow tests

We also added some tests which run airflow to verify that it works on the code we produce.
These also take a lot longer, they create their own virtualenv
with airflow in it, and create a new airflow DB. By default, those are not run.
To run them, use `pytests tests -m "airflow"` when running pytest.


### 2.7. Additional notes on Docker testing

If using Docker, please add appropriate tests and ensure all tests are working using
`make test`. Any args to pytest can be passed using args="xxx". e.g., individual
tests can be run using `make test args="<path_to_test_file>"`.

Please ensure linting and `typecheck`s are done before commiting your code. When using docker, this can be done using `make lint` and `make typecheck` respectively. A
pre-commit hook that runs `make blackfix lint typecheck build test` will fix
any fixable issues and ensure build and test works.


## 3. Debugging

### 3.1. VSC

`.vscode/launch.json` has a VSC debug configuration for `lineapy` which executes `lineapy python --slice "p value" tests/housing.py` through VSC "Run and Debug" dialog.

### 3.2. Visual Graphs


Sometimes it's helpful to see a visual representation of the graph
and the tracers state, while debugging a test. Run the tests with `--visualize`
to have it save a `tracer.pdf` file whenever it run an execution.

Note: This requires graphviz to be installed.


### 3.3. Logging

We have logging set up as well, which can be printed while running the tests
to help with debugging:

```bash
pytest --log-cli-level INFO
```

If you would like to see the logs pretty printed, using
[Rich's custom log handler](https://rich.readthedocs.io/en/stable/logging.html)
you have to disable pytests built in handler disable its stdout capturing:

```bash
pytest -p no:logging -s
```

### 3.4. Debug Flags

By default, linea will rewrite any exceptions raised during the normal
execution of users code to attempt to match Python's behavior. To disable our
custom exception handling, set the `LINEA_NO_EXCEPTIONS` environment variable
to any value.

### 3.5 Additional Utilities

#### 3.5.1. AST Inspection

If you want to inspect the AST of some Python code for debugging, you can run:

```bash
./tests/tools/print_ast.py 'hi(a=10)'
```

**Verifying the specs**

```bash
./tests/tools/test_validate_annotation_spec.py
```
#### 3.5.2. Github Actions

Tests are run on Github Actions. If you are trying to debug a failure that
happens on Github Actions, you can try using [`act`](https://github.com/nektos/act),
which will run it locally through Docker.

```bash
brew install act
act
# When it prompts, the "medium" image seems to work out alright.
```


## 4. Additional Notes

### 4.1. Performance Profiling

Please see [this]() for notes on profiling.

### 4.2. Known Issues

Note - on macOS Monterey & using conda's Python 3.8.11, installing the requirements fails due to a failure in building fastparquet==0.7.2
Downgrading to 0.7.0 solves the issue - simply change the fastparquet version in requirements.txt

### 4.3. Using venv instead of Conda

If you prefer using venv, then you need to install the following prerequisites first

* Python

Note - for Apple users, DON'T use the native Python that comes with macOS, instead install one from brew
```bash
brew install python #for the latest version or python@3.8
```

* OpenSSL, postgres, and graphviz

```bash
brew install openssl
brew install postgresql
brew install graphviz
```

* Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

Now you're ready to create your venv


```bash
python3.9 -m venv lineapy # or python3.8
source lineapy/bin/activate

pip install -r requirements.txt
pip install -e .

# verify everything works as expected
lineapy --help
pytest tests
```

### 4.4. Further Readings
The [Docker]() and [make]() files are good starting point to see the main components of `lineapy`

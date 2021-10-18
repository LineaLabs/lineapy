# Contributing

This repository contains a few different components:

- A **transformer** which traces the Python AST and generates a graph from it, using the tracer.
- A **tracer** that adds nodes to the graph (and then executes them with the executor)
- A **dataflow graph** which is stored in SQLite and represents a Python execution
- An **executor** which takes the graph and can run it as Python code

## First-time Setup

### Conda
```bash
conda create --name lineapy-env python=3.9
conda activate lineapy-env
# added quotes to make zsh compliant
pip install -e ".[dev]" --user
```

### Docker + Makefile
To build the container, run `make build`
To open bash within the container, run `make bash`. One can either use bash for dev or can connect to remote runtimes inside a container using extensions available for the editor of choice.

Before committing, please add appropriate tests and ensure all tests are working using
`make test`. In case a snapshot needs updating, you can use `make test args="--snapshot-update"` to update snapshots.
Individual tests can be run using `make test args="<path_to_test_file>"`.
Additionally, linting and typechecks can be done using `make lint` and `make typecheck` respectively.


## Debugging (in VSC)

`.vscode/launch.json` has a VSC debug configuration for `lineapy` which executes `lineapy --slice "p value" tests/housing.py` through VSC "Run and Debug" dialog.

## Tests

```bash
mypy -p lineapy
black --line-length 79 --check .
pytest tests/
```

### Logging

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

### Snapshots

Some tests use use [`syrupy`](https://github.com/tophat/syrupy) for snapshot test, to make it easier to update generate code and graphs.
If you mean to change the tracing or graph spec, or added a new test that uses it, then run `pytest --snapshot-update` to update the saved snapshots.

### Code Coverage

The code coverage statistics are printed after the tests finish. It also generates
an HTML file which can be used to look line by line, what is covered and what is not.
Open this with `open htmlcov/index.html` after the tests finish.

### XFail

Also we use [pytest's xfail](https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail) to mark tests that are expected to fail, because of a known bug. To have them run anyway, run `--run-xfail`.

### Notebooks

We currently have a notebook that is also evaluated in the tests, and the
outputs are compared.

If you want to update the notebook output, you can run:

```bash
jupyter nbconvert --to notebook --execute tests/test_notebook.ipynb --inplace --log-level=DEBUG
```

Or you can open it in a notebook UI (JupyterLab, JupyterNotebook, VS Code, etc.)
and re-run it manually

## Visual Graphs

Sometimes it's helpful to see a visual representation of the graph
and the tracers state, while debugging a test. Run the tests with `--visualize`
to have it save a `tracer.pdf` file whenever it run an execution.

Note: This requires graphviz to be installed.

## Performance Profiling

We have had luck using the [py-spy](https://github.com/benfred/py-spy) tool,
which runs your Python script in a seperate process and samples it, to
profile our tests to get a rough sense of how long things take:

```bash
# Run with sudo so it can inspect the subprocess
sudo py-spy record \
    # Save as speedscope so we can load in the browser
    --format speedscope \
    # Group by function name, instead of line number
    --function \
    # Increase the sampling rate from 100 to 200 times per second
    -r 200  -- pytest tests/
```

After creating your trace, you can load it [in
Speedscope](https://www.speedscope.app/).

In this example, we are inspecting calls to `transform`.
We see that it cumulatively takes up 12% of total time and that most of the time inside of it is spent visiting imports, as well as commiting to the DB:

<img width="2560" alt="Screen Shot 2021-10-12 at 2 29 10 PM" src="https://user-images.githubusercontent.com/1186124/137037002-18f29bd8-db02-4924-9855-5f3db9d2d0ee.png">

## Inpsecting AST

If you want to inspect the AST of some Python code for debugging, you can run:

```bash
./tests/tools/print_ast.py 'hi(a=10)'
```

## Github Actions

The tests are run on Github Actions. If you are trying to debug a failure that happens on Github Actions, you can try using [`act`](https://github.com/nektos/act), which will run it locally through docker:

```bash
brew install act
act
# When it prompts, the "medium" image seems to work out alright.
```

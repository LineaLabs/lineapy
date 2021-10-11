# Contributing

This repository contains a few different components:

- A **transformer** which traces the Python AST and generates a graph from it, using the tracer.
- A **tracer** that adds nodes to the graph (and then executes them with the executor)
- A **dataflow graph** which is stored in SQLite and represents a Python execution
- An **executor** which takes the graph and can run it as Python code

## First-time Setup

```bash
conda create --name lineapy-env python=3.9
conda activate lineapy-env
pip install -e .[dev] --user
```

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

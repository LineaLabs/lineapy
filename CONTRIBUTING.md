# Contributing

This repository contains a few different components:

-   A **transformer** which traces the Python AST and generates a graph from it, using the tracer.
-   A **tracer** that adds nodes to the graph (and then executes them with the executor)
-   A **dataflow graph** which is stored in SQLite and represents a Python execution
-   An **executor** which takes the graph and can run it as Python code
-   A **server** which exposes a REST API of the graph that `linea-server` accesses. This is currently not being kept up to date.

## First-time Setup

```bash
conda create --name lineapy-env python=3.9
conda activate lineapy-env
pip install -e .[dev] --user
```

## Tests

```bash
mypy -p lineapy
black --line-length 79 --check .
pytest
```

## Debugging (in VSC)
`.vscode/launch.json` has a VSC debug configuration for `lineapy` which executes `lineapy --slice "p value" tests/housing.py` through VSC "Run and Debug" dialog.

### Snapshots

Some tests use use [`syrupy`](https://github.com/tophat/syrupy) for snapshot test, to make it easier to update generate code and graphs.
If you mean to change the tracing or graph spec, or added a new test that uses it, then run `pytest --snapshot-update` to update the saved snapshots.

### Code Coverage

The code coverage statistics are printed after the tests finish. It also generates
an HTML file which can be used to look line by line, what is covered and what is not.
Open this with `open htmlcov/index.html` after the tests finish.

### XFail

Also we use [pytest's xfail](https://docs.pytest.org/en/latest/how-to/skipping.html#xfail-mark-test-functions-as-expected-to-fail) to mark tests that are expected to fail, because of a known bug. To have them run anyway, run `--run-xfail`.

### Inpsecting AST

If you want to inspect the AST of some Python code for debugging, you can run:

```bash
./tests/tools/print_ast.py 'hi(a=10)'
```

### Github Actions

The tests are run on Github Actions. If you are trying to debug a failure that happens on Github Actions, you can try using [`act`](https://github.com/nektos/act), which will run it locally through docker:

```bash
brew install act
act
# When it prompts, the "medium" image seems to work out alright.
```

### Static end to end test/demo

**Note:** These end to end tests may not work currently, since we have not kept
the REST API up to date.

For a static end to end test along with [linea-server](https://github.com/LineaLabs/linea-server)

```bash
python -m tests.setup_integrated_tests
python lineapy/app/application.py
```

`setup_integrated_tests.py` creates the stub data that the flask application then serves.

Then head over to [linea-server](https://github.com/LineaLabs/linea-server) and
run the usual commands there (`python application.py` and `yarn start` in
the `/server` and `/frontend` folders respectively)

Note that if you are running these on EC2, you need to do tunneling on **three**
ports:

-   One for the lineapy flask app, which is currently on 4000
-   One for the linea-server flask app, which is on 5000
-   And one for the linea-server dev server (for the React app), which is on 3000

For Yifan's machine, the tunneling looks like the following:

```bash
ssh -N -f -L localhost:3000:0.0.0.0:3000 ubuntu@3.18.79.230
ssh -N -f -L localhost:5000:0.0.0.0:5000 ubuntu@3.18.79.230
ssh -N -f -L localhost:4000:0.0.0.0:4000 ubuntu@3.18.79.230
```

## Running the servers live

Coming soon!

## Best practices

For any Jupyter Notebooks that you think your reviewer might directly comment on,
please run `jupyter nbconvert --to script` and commit the corresponding .py script to make comments easier.

## Dev notes

Something weird about the `tests/test_flask_app.py`; please double check even if pytest is passing.

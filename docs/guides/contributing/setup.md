# Setup and Basics

## Installation

### Cloning Repo

First [fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the `lineapy` repo.
Then, [clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository)
the forked repo to your development environment:

```bash
cd <PATH-TO-DESIRED-LOCATION>
git clone <URL-TO-FORKED-REPO>
```

To keep the forked repo in sync with the original one, set an "upstream":

```bash
git remote add upstream https://github.com/LineaLabs/lineapy.git
```

### Setting up Virtual Environment

!!! note

    Here, we use [venv](https://docs.python.org/3/library/venv.html) for virtual environment setup
    because it comes with Python core distribution. If you prefer a different option (e.g.,
    [conda](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)),
    you can skip this section.

When done cloning, move into the repo and initiate a virtual environment:

```bash
cd <FORKED-REPO-NAME>
python -m venv env
```

where `<FORKED-REPO-NAME>` is `lineapy` unless modified during/after forking.

This creates `env/` subfolder inside the repo, and you can activate the associated virtual environment like so:

```bash
source env/bin/activate
```

To deactivate the virtual environment, you can type:

```bash
deactivate
```

!!! warning

    If you use a different name for this virtual environment subfolder, you will need to register the new name in
    several config files including `.gitignore`, `.flake8`, `pyproject.toml` lest it will create friction for
    other workflows such as pre-commit. Hence, we strongly recommend you name the subfolder `env/` as instructed above.

### Installing Dependencies

Once the virtual environment is activated, install packages necessary for running and developing `lineapy`:

```bash
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
pip install -e '.[dev]'
```

Note that this may take a while to complete.

## Running LineaPy

During development, you may want to check how your changes affect the behavior of the package.
LineaPy supports several interfaces to run on, and the relevant instructions are documented :ref:`here <interfaces>`.
Please select the most convenient option for you.

!!! note

    When running LineaPy, make sure that the virtual environment has been activated.

## Development

### Making Changes

With development dependencies installed, you are now ready to contribute to the source code!
First, make a separate branch for your development work. Please use an informative name so that
others can get good sense of what your changes are about.

```bash
git checkout -b <NEW-BRANCH-NAME>
```

After making changes you desire, save them to your development branch:

```bash
git add <PATH-TO-CHANGED-FILE>
git commit -m "<COMMIT-MESSAGE>"
```

!!! info

    To learn more about saving changes in Git, check this [tutorial](https://www.atlassian.com/git/tutorials/saving-changes).

!!! info

    LineaPy provides several [pre-commit](https://pre-commit.com/) hooks to automatically standardize styles and formats
    across its codebase.

    To run these hooks automatically upon every new commit:

    ```bash
    pre-commit install
    ```

    To run the hooks even when there are no changes:

    ```bash
    pre-commit run --all-files
    ```

    LineaPy's pre-commit hooks do not run tests since tests are too time-consuming to run on every commit. For testing, see the section below.

Note that these changes have been saved only locally at this point, and you need to "push" them to your forked repo on GitHub:

```bash
git push
```

If the new (development) branch has not been pushed before, you will need to create its counterpart on GitHub with:

```bash
git push --set-upstream origin <NEW-BRANCH-NAME>
```

### Testing Changes

Testing is an important part of `lineapy`'s development as it ensures that all features stay functional after changes.
Hence, we strongly recommend you add tests for changes you introduce (check this [tutorial](ADD-LINK) for adding tests).

To run all tests (beware that this may take a while to complete):

```bash
pytest tests
```

Or, to run select tests (e.g., those that you added/modified):

```bash
# Example: Run all tests in a folder
pytest tests/unit/plugins

# Example: Run all tests in a file
pytest tests/unit/plugins/test_writer.py

# Example: Run a particular test
pytest tests/unit/plugins/test_writer.py::test_pipeline_generation

# Example: Run a parametrized test with a particular set of parameter values
pytest tests/unit/plugins/test_writer.py::test_pipeline_generation[script_pipeline_a0_b0]
```

### Integrating Changes

As you make your changes in your development branch, it is very possible that the original `lineapy` repo is updated by other developers.
To ensure that your changes are compatible with these updates by others, you will need to regularly "sync" your development branch with the original
`lineapy` repo. You can do this by first syncing the `main` branch between your local (forked) repo and the original `lineapy` repo:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

Then, sync your development branch with the updated `main` branch:

```bash
git checkout <DEV-BRANCH-NAME>
git rebase main
```

!!! note

    If updates in the original `lineapy` repo are not compatible with changes in your development branch,
    you will need to resolve merge conflict(s). Check this
    [tutorial](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line)
    to learn how.

    If the issue persists, please get in touch with LineaPy's core development team on [Slack](ADD-LINK).

Once you are content with your changes and ready to integrate them into the original `lineapy` project,
you can open a pull request following instructions [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).
Make sure that `base repository` is set to `LineaLabs/lineapy` and `base` to `main`. To facilitate the review,
please provide as much detail as possible about your changes in your pull request.

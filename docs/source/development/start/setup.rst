.. _contribution_setup_and_basics:

Setup and Basics
================

.. include:: ../../snippets/slack_support.rstinc

.. _contribution_install:

Installation
------------

Cloning Repo
************

First `fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ the ``lineapy`` repo.
Then, `clone <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`_
the forked repo to your development environment:

.. code:: bash

    cd <PATH-TO-DESIRED-LOCATION>
    git clone <URL-TO-FORKED-REPO>

To keep the forked repo in sync with the original one, set an "upstream":

.. code:: bash

    git remote add upstream https://github.com/LineaLabs/lineapy.git

Setting up Virtual Environment
******************************

When done cloning, move into the repo and initiate a virtual environment:

.. code:: bash

    cd <FORKED-REPO-NAME>
    python -m venv env

where ``<FORKED-REPO-NAME>`` is ``lineapy`` unless modified during/after forking.

This creates ``env/`` subfolder inside the repo, and you can activate the associated virtual environment like so:

.. code:: bash

    source env/bin/activate

To deactivate the virtual environment, you can type:

.. code:: bash

    deactivate

Installing Dependencies
***********************

Once the virtual environment is activated, install packages necessary for running and developing ``lineapy``:

.. code:: bash

    pip install --upgrade pip
    pip install --upgrade setuptools
    pip install -r requirements.txt
    pip install -e '.[dev]'

Note that this may take a while to complete.

Making Changes
--------------

With development dependencies installed, you are now ready to contribute to the source code!
First, make a separate branch for your development work. Please use an informative name so that
others can get good sense of what your changes are about.

.. code:: bash

    git checkout -b <NEW-BRANCH-NAME>

After making changes you desire, save them to your development branch:

.. code:: bash

    git add <PATH-TO-CHANGED-FILE>
    git commit -m "<COMMIT-MESSAGE>"

.. note::

    To learn more about saving changes in Git, check this `tutorial <https://www.atlassian.com/git/tutorials/saving-changes>`_.

Note that these changes have been saved only locally at this point, and you need to "push" them to your forked repo on GitHub:

.. code:: bash

    git push

If the new (development) branch has not been pushed before, you will need to create its counterpart on GitHub with:

.. code:: bash

    git push --set-upstream origin <NEW-BRANCH-NAME>

Testing Changes
---------------

Testing is an important part of ``lineapy``'s development as it ensures that all features stay functional after changes.
Hence, we strongly recommend you add tests for changes you introduce (check this :ref:`tutorial <add_test>` for adding tests).

To run all tests (beware that this may take a while to complete):

.. code:: bash

    pytest tests

Or, to run a particular test (e.g., one that you added/modified):

.. code:: bash

    pytest <PATH-TO-TEST-FILE>

Integrating Changes
-------------------

As you make your changes in your development branch, it is very possible that the original ``lineapy`` repo is updated by other developers.
To ensure that your changes are compatible with these updates by others, you will need to regularly "sync" your development branch with the original
``lineapy`` repo. You can do this by first syncing the ``main`` branch between your local (forked) repo and the original ``lineapy`` repo:

.. code:: bash

    git fetch upstream
    git checkout main
    git merge upstream/main

Then, sync your development branch with the updated ``main`` branch:

.. code:: bash

    git checkout <DEV-BRANCH-NAME>
    git rebase main

.. note::

    If updates in the original ``lineapy`` repo are not compatible with changes in your development branch,
    you will need to resolve merge conflict(s). Check this
    `tutorial <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line>`_
    to learn how.

Once you are content with your changes and ready to integrate them into the original ``lineapy`` project,
you can open a pull request following instructions `here <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork>`_.
Make sure that ``base repository`` is set to ``LineaLabs/lineapy`` and ``base`` to ``main``. To facilitate the review,
please provide as much detail as possible about your changes in your pull request.

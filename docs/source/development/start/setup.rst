.. _contribution_setup_and_basics:

Setup and Basics
================

.. include:: ../../snippets/slack_support.rstinc

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

    git branch -b <NEW-BRANCH-NAME>
    git branch --set-upstream-to=origin/<NEW-BRANCH-NAME> <NEW-BRANCH-NAME>

After making changes you desire, save them to your development branch:

.. code:: bash

    git add <PATH-TO-CHANGED-FILE>
    git commit -m "<COMMIT-MESSAGE>"

.. note::

    To learn more about saving changes in Git, check this `tutorial <https://www.atlassian.com/git/tutorials/saving-changes>`_.

Note that these changes have been saved only locally at this point, and you need to "push" them to your forked repo on GitHub:

.. code:: bash

    git push

Testing Changes
---------------

Testing is an important part of ``lineapy``'s development as it ensures that all features stay functional after changes.
Hence, we strongly recommend you create and add tests for the changes you introduce (check this :ref:`tutorial <add_test>` for adding tests).

To run all tests (beware that this may take a while to complete):

.. code:: bash

    pytest tests

Or, to run a particular test (e.g., one that you added/modified):

.. code:: bash

    pytest <PATH-TO-TEST-FILE>

Integrating Changes
-------------------

[TODO: Add instructions for how to open PR against original repo]

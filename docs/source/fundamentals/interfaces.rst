.. _interfaces:

Interfaces
==========

.. include:: ../snippets/slack_support.rstinc

Jupyter and IPython
-------------------

To use LineaPy in an interactive computing environment such as Jupyter Notebook/Lab or IPython, load its extension with:

.. code:: python

    %load_ext lineapy

executed at the top of your session. Please note:

- You will need to run this as the first command in a given session; executing it in the middle of a session will lead to erroneous behaviors by LineaPy.

- This loads the extension to the current session only, i.e., it does not carry over to different sessions; you will need to repeat it for each new session.

Alternatively, you can launch the environment with the ``lineapy`` command, like so:

.. code:: bash

    lineapy jupyter notebook

.. code:: bash

    lineapy jupyter lab

.. code:: bash

    lineapy ipython

This will automatically load the LineaPy extension in the corresponding interactive shell application,
and you will not need to manually load it for every new session.

.. note::

    If your Jupyter environment has multiple kernels, choose ``Python 3 (ipykernel)`` which ``lineapy`` defaults to.

Hosted Jupyter Environment
--------------------------

In hosted Jupyter notebook environments such as JupyterHub, Google Colab, Kaggle, Databricks or in any other 
environments that are not started using CLI (such as Jupyter extension within VS Code), you need to 
install ``lineapy`` directly within your notebook first via:

.. code:: bash

    !pip install lineapy

Then you can manually load ``lineapy`` extension with :

.. code:: python

    %load_ext lineapy

For environments with older versions ``IPython<7.0`` like Google Colab, you need to upgrade the ``IPython>=7.0`` module before the above steps, you can upgrade ``IPython`` via:

.. code:: bash

    !pip install --upgrade ipython

and restart the notebook runtime:

.. code:: python

    exit()

Finally, you can start setting up LineaPy as described previously.

CLI
---

You can also use LineaPy as a CLI command or a runnable Python module. Run:

.. code:: bash

    # LineaPy as a CLI command
    lineapy python --help

or

.. code:: bash

    # LineaPy as a runnable Python module
    python -m lineapy --help

to see available options.

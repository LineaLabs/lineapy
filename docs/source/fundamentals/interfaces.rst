.. _interfaces:

Interfaces
==========

Jupyter and IPython
-------------------

To use LineaPy in an interactive computing environment such as Jupyter Notebook/Lab or IPython,
launch the environment with the ``lineapy`` command, like so:

.. code:: bash

    $ lineapy jupyter notebook

.. code:: bash

    $ lineapy jupyter lab

.. code:: bash

    $ lineapy ipython

Each will automatically load the LineaPy extension in the corresponding interactive shell application.

Or, if the application is already running without the extension loaded, which can happen
when we start the Jupyter server with ``jupyter notebook`` or ``jupyter lab`` without ``lineapy``,
you can load it on the fly with:

.. code:: python

    %load_ext lineapy

executed at the top of your session. Please note:

- You will need to run this as the first command in a given session; executing it in the middle of a session will lead to erroneous behaviors by LineaPy.

- This loads the extension to the current session only, i.e., it does not carry over to different sessions; you will need to repeat it for each new session.

.. note::

    LineaPy works with JupyterHub!

    If LineaPy is installed by the admin, it will be accessible to every user and the admin can set the LineaPy 
    extension to be automatically loaded by adding ``c.InteractiveShellApp.extensions = ["lineapy"]`` in 
    `ipython_config.py <https://ipython.readthedocs.io/en/stable/config/intro.html>`_.

    If LineaPy is installed by an individual user during their session, it will be accessible to that particular
    user only as long as they do not have a write permission on the shared environment.
    In this case, the user will need to run ``%load_ext lineapy`` as explained above.

CLI
---

We can also use LineaPy as a CLI command. Run:

.. code:: bash

    $ lineapy python --help

to see available options.

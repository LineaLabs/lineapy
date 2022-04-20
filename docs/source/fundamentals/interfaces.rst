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

Or, if the application is already running without the extension loaded, you can load it
on the fly with:

.. code:: python

    %load_ext lineapy

executed at the top of your session. Please note:

- You will need to run this as the first command in a given session; executing it 
in the middle of a session will lead to erroneous behaviors by LineaPy.

- This loads the extension to the current session only, i.e. it does not carry over
to different sessions; you will need to repeat it for each new session.

CLI
---

We can also use LineaPy as a CLI command. Run:

.. code:: bash

    $ lineapy python --help

to see available options.

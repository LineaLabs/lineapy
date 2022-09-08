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

For environments with older versions ``IPython<7.0`` like Google Colab, we need to upgrade the ``IPython>=7.0`` module before the above steps, we can upgrade ``IPython`` via:

.. code:: bash

    !pip install --upgrade ipython

and restart the notebook runtime:

.. code:: python

    exit()

Finally, we can start setting up LineaPy as described previously.

CLI
---

We can also use LineaPy as a CLI command. Run:

.. code:: bash

    $ lineapy python --help

to see available options.


Python Module
-------------

Lineapy is also a runnable python module. 

.. code:: bash

    $ python -m lineapy --help

and works the same as using the CLI.

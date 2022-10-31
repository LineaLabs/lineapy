.. _setup:

Installation
============

.. include:: ../snippets/slack_support.rstinc

Prerequisites
-------------

LineaPy runs on ``Python>=3.7`` and ``IPython>=7.0.0``. It does not come with a Jupyter installation,
so you will need to `install one <https://jupyter.org/install>`_ for interactive computing.

Basics
------

To install LineaPy, run:

.. code:: bash

    pip install lineapy

If you want to run the latest version of LineaPy directly from the source, follow instructions
:ref:`here <contribution_install>`.

.. note::

    By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
    However, SQLite has several limitations, one of which is that it does not support multiple concurrent
    writes to a database (it will result in a database lock). If you want to use a more robust database,
    please follow :ref:`instructions <postgres>` for using PostgreSQL.

Extras
------

LineaPy offers several extras to extend its core capabilities:

+----------+---------------------------------------+----------------------------------------------------------+
| Version  | Installation Command                  | Enables                                                  |
+==========+=======================================+==========================================================+
| minimal  | :code:`pip install lineapy[minimal]`  | Minimal dependencies for LineaPy                         |
+----------+---------------------------------------+----------------------------------------------------------+
| dev      | :code:`pip install lineapy[dev]`      | All LineaPy dependencies for testing and development     |
+----------+---------------------------------------+----------------------------------------------------------+
| s3       | :code:`pip install lineapy[s3]`       | Dependencies to use S3 to save artifact                  |
+----------+---------------------------------------+----------------------------------------------------------+
| graph    | :code:`pip install lineapy[graph]`    | Dependencies to visualize LineaPy node graph             |
+----------+---------------------------------------+----------------------------------------------------------+
| postgres | :code:`pip install lineapy[postgres]` | Dependencies to use PostgreSQL backend                   |
+----------+---------------------------------------+----------------------------------------------------------+

.. note::

    The ``minimal`` version of LineaPy does not include ``black`` or ``isort``, which
    may result in less organized output code and scripts.

JupyterHub
----------

LineaPy works with JupyterHub!

If LineaPy is installed by an admin, it will be accessible to every user. The admin can set the LineaPy 
extension to be automatically loaded by adding ``c.InteractiveShellApp.extensions = ["lineapy"]`` in 
`ipython_config.py <https://ipython.readthedocs.io/en/stable/config/intro.html>`_.

If LineaPy is installed by an individual user, it will be accessible to that particular
user only as long as they do not have a write permission on the shared environment.
In this case, the user will need to run ``%load_ext lineapy`` at the top of their session
as explained :ref:`here <interfaces>`.

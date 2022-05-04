.. _setup:

Installation
============

To install LineaPy, run:

.. code:: bash

    $ pip install lineapy

Or, if you want the latest version of LineaPy directly from the source, run:

.. code:: bash

    $ pip install git+https://github.com/LineaLabs/lineapy.git --upgrade

Followings are extras to extend core LineaPy capabilities

+----------+---------------------------------------+----------------------------------------------------------+
| extra    | pip install command                   | enables                                                  |
+==========+=======================================+==========================================================+
| minimal  | :code:`pip install lineapy[minimal]`  | Bare bone dependencies for LineaPy                       |
+----------+---------------------------------------+----------------------------------------------------------+
| dev      | :code:`pip install lineapy[dev]`      | All LineaPy tests and contributing related dependencies  |
+----------+---------------------------------------+----------------------------------------------------------+
| graph    | :code:`pip install lineapy[graph]`    | Dependencies to visualize LineaPy node graph             |
+----------+---------------------------------------+----------------------------------------------------------+
| postgres | :code:`pip install lineapy[postgres]` | Dependencies to use PostgreSQL backend                   |
+----------+---------------------------------------+----------------------------------------------------------+

Note that, the minimal version of LineaPy does not include black and isort as dependencies.
This may result less organized output codes and scripts.

.. note::

    By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
    However, SQLite has several limitations, one of which is that it does not support multiple concurrent
    writes to a database (it will result in a database lock). If you want to use a more robust database,
    please follow :ref:`instructions <postgres>` for using PostgreSQL.

Using JupyterHub
================

LineaPy works with JupyterHub. 

If LineaPy is installed by the admin, it will be accessible to every user and the admin can set LineaPy 
extension loaded as default by adding :code:`c.InteractiveShellApp.extensions = ['lineapy']` in 
ipython_config.py_. The :code:`.linea` folder will be created in the user's home directory.
 
If LineaPy is installed by an individual user during their session, LineaPy will only be accessible to the 
user who installs LineaPy as long as the user does not have write permission on the shared environment.
In this case, the user will need to run :code:`%load_ext lineapy` in the notebook to use LineaPy.

.. _ipython_config.py: https://ipython.readthedocs.io/en/stable/config/intro.html



    
    


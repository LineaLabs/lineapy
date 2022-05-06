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

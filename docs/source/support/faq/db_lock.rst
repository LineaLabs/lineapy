Why do I get an error for database lock?
========================================

.. include:: ../../snippets/slack_support.rstinc

By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
However, SQLite has several limitations, one of which is that it does not support multiple concurrent
writes to a database (it will result in a database lock). Such concurrent writes to a database can happen,
for instance, when multiple scripts or notebook sessions are running at the same time.
If your SQLite is locked, you can unlock it by terminating the exact process locking the file. Specifically,
navigate to your home directory and run:

.. code:: bash

    $ fuser .lineapy/db.sqlite

which will list process ID(s) connecting to the database, like so:

.. code:: none

    .lineapy/db.sqlite: 78638

You can then terminate the troublesome process(es) with:

.. code:: bash

    $ kill 78638

which will unlock the database.

.. warning::

    Be cautious about terminating a process as it may result in loss of ongoing work. For instance, if your notebook
    involved heavy computation and the database got locked while storing the result as an artifact, you may consider
    storing it in a different form (e.g., a Parquet file) before terminating the notebook's process.

If database locking is a persisting issue in your usage, we recommend you use a more robust database such as PostgreSQL,
for which relevant instructions can be found :ref:`here <postgres>`.


Why do I get an error for "module 'black' has no attribute"?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Lineapy uses the `black library <https://pypi.org/project/black/>`_ to format produced code. Make sure you have the version of black as specified in `LineaPy's requirements.txt <https://github.com/LineaLabs/lineapy/blob/main/requirements.txt>`_.
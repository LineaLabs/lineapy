FAQ
===

Why Do I get an Error for Database Lock?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
However, SQLite has several limitations, one of which is that it does not support multiple concurrent
writes to a database (it will result in a database lock). Such concurrent writes to a database can happen,
for instance, when multiple scripts or notebook sessions are running at the same time.
If your SQLite is locked, you can unlock it by killing the exact process locking the file. Specifically,
navigate to your home directory and run:

.. code:: bash

    $ fuser .linea/db.sqlite

which will list process ID(s) connecting to the database, like so:

.. code:: none

    .linea/db.sqlite: 78638

You can then terminate the troublesome process(es) with:

.. code:: bash

    $ kill 78638

which will unlock the database.

.. warning::

    Be discreet in terminating a process as it may result in loss of ongoing work. Ensure to save relevant work
    before terminating any process.

If database locking is a persisting issue in your usage, we recommend you use a more robust database such as PostgreSQL,
for which relevant instructions can be found :ref:`here <postgres>`.

FAQ
===

Why Do I Get an Error for Database Lock?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
However, SQLite has several limitations, one of which is that it does not support multiple concurrent
writes to a database (it will result in a database lock). Such concurrent writes to a database can happen,
for instance, when multiple scripts or notebook sessions are running at the same time.
If your SQLite is locked, you can unlock it by terminating the exact process locking the file. Specifically,
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

    Be cautious about terminating a process as it may result in loss of ongoing work. For instance, if your notebook
    involved heavy computation and the database got locked while storing the result as an artifact, you may consider
    storing it in a different form (e.g., a Parquet file) before terminating the notebook's process.

If database locking is a persisting issue in your usage, we recommend you use a more robust database such as PostgreSQL,
for which relevant instructions can be found :ref:`here <postgres>`.

Why do I get "No context set"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you run into initiation errors, such as the following

.. code-block::

    ---------------------------------------------------------------------------
    RuntimeError                              Traceback (most recent call last)
    /tmp/ipykernel_101389/3008679649.py in <module>
        8     y = pd.read_sql("select * from test", conn)
        9 
    ---> 10 art = lineapy.save(y, "y")
        11 print(art.code)

    ~/linea-dev/lineapy/lineapy/api/api.py in save(reference, name)
        40         information we have stored about the artifact (value, version), and other automation capabilities, such as `to_airflow`.
        41     """
    ---> 42     execution_context = get_context()
        43     executor = execution_context.executor
        44     db = executor.db

    ~/linea-dev/lineapy/lineapy/execution/context.py in get_context()
        87 def get_context() -> ExecutionContext:
        88     if not _current_context:
    ---> 89         raise RuntimeError("No context set")
        90 
        91     return _current_context

    RuntimeError: No context set


This could be because you are running vanilla jupyter, e.g., ``>jupyter notebook``, instead, you should do ``>lineapy jupyter notebook`` (or ``>lineapy jupyter lab`` if you are using lab). Similarly, for python CLI, you should do ``>lineapy python your_file.py``, rather than ``>python your_file.py``.

If your notebook is stuck in a frozen state, it's likely due to SQLite locking up---please restart (we are actively working on eliminating these edge cases).

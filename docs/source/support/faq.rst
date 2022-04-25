FAQ
===

Why Do I get an Error for Database Lock?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, LineaPy uses SQLite for artifact store, which keeps the package light and simple.
However, SQLite has several limitations, one of which is that it does not support multiple concurrent
writes to a database (it will result in a database lock). Such concurrent writes to a database can happen,
for instance, when multiple scripts or notebook sessions are running at the same time.
If your SQLite is locked, you can unlock it by killing the exact process(PID) locking the file.  
If this is a persisting issue in your usage, we recommend you use a more robust database such as PostgreSQL
(relevant instructions can be found :ref:`here <postgres>`).

.. _postgres:

Storing Artifact Metadata in PostgreSQL
=======================================

.. include:: ../../../snippets/slack_support.rstinc

By default, LineaPy uses SQLite to store artifact metadata (e.g., name, version, code), which keeps the package light and simple.
Given the limitations of SQLite (e.g., single write access to a database at a time), however,
we may want to use a more advanced database such as PostgreSQL.

Run PostgreSQL with Docker
--------------------------

The easiest way to use PostgreSQL with LineaPy is through `Docker <https://docs.docker.com/get-docker/>`_.
We can spin up a PostgreSQL instance with Docker using the following command:

.. code:: bash

    $ docker run --name lineaPostgres -p 15432:5432 -e POSTGRES_USER=postgresuser -e POSTGRES_PASSWORD=postgrespwd -e POSTGRES_DB=postgresdb -d postgres

where

* ``--name lineaPostgres`` sets the Docker container name as ``lineaPostgres``
* ``-p 15432:5432`` exposes PostgreSQL at port 15432 (5432 is the default PostgreSQL port within the Docker image)
* ``-e POSTGRES_USER=postgresuser`` sets the username as ``postgresuser``
* ``-e POSTGRES_PASSWORD=postgrespwd`` sets the password as ``postgrespwd``
* ``-e POSTGRES_DB=postgresdb`` sets the database name as ``postgresdb``
* ``-d postgres`` specifies the name of the official PostgreSQL Docker image

To validate whether the Docker container has been started successfully, run:

.. code:: bash

    $ docker ps -a | grep lineaPostgres

which will show the container information if it exists, as the following:

.. code:: none

    1b68ae97e029   postgres   "docker-entrypoint.s…"   6 hours ago   Up 6 hours   0.0.0.0:15432->5432/tcp   lineaPostgres

.. note::

    You may experience trouble launching the container if the container name or port is already occupied.
    If so, simply change the container name or port and relaunch the container as instructed above.
    Or, you can remove the conflicting container with ``docker rm -f CONTAINER_ID`` where ``CONTAINER_ID``
    is the ID of the conflicting container to remove (e.g., ``1b68ae97e029`` above).

Install Database Adapter
------------------------

To support interaction between Python and PostgreSQL, we need to install a database adapter. A popular choice
is a Python package called ``psycopg2``, which can be installed as follows:

.. code:: bash

    $ pip install psycopg2

Connect LineaPy with PostgreSQL
-------------------------------

Now that the new database is in place, we need to make LineaPy recognize and use it.
We can do this by exporting the database connection string into an environmental variable
``LINEAPY_DATABASE_URL``, like so:

.. code:: bash

    $ export LINEAPY_DATABASE_URL=postgresql://postgresuser:postgrespwd@localhost:15432/postgresdb

Note that this has to be done prior to using LineaPy so that the environment variable exists in runtime.

.. note::

    If you want to use PostgreSQL as the default backend, you can make the environment variable
    persist across sessions by defining it in ``.bashrc`` or ``.zshrc``.

You can check the connection between LineaPy and PostgreSQL with:

.. code:: python

    >>> from lineapy.db.db import RelationalLineaDB
    >>> print(RelationalLineaDB.from_environment().url)

which will print:

.. code:: none

    postgresql://postgresuser:postgrespwd@localhost:15432/postgresdb

if successful. Otherwise, it will default back to SQLite and print:

.. code:: none

    sqlite:///.lineapy/db.sqlite

Known Issues
------------

If you are using PostgreSQL as your database, you might encounter the following error:

.. code:: none

    NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres


This is caused by a change in SQLAlchemy where they dropped support for DB URLs of the form ``postgres://``.
Using ``postgresql://`` instead should fix this error.

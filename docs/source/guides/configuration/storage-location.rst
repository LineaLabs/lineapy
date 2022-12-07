Changing Storage Location
=========================

.. include:: ../../snippets/slack_support.rstinc

By default, the serialized values and the metadata are stored in ``.lineapy/linea_pickles/``
and ``.lineapy/db.sqlite``, respectively, where ``.lineapy/`` is created under
the system's home directory.

This default location can be overridden by modifying the configuration file:

.. code:: json

    {
        "artifact_storage_dir": [NEW-PATH-TO-STORE-SERIALIZED-VALUES],
        "database_url": [NEW-DATABASE-URL-FOR-STORING-METADATA],
        ...
    }

or making these updates in each interactive session:

.. code:: python

    lineapy.options.set('artifact_storage_dir', [NEW-PATH-TO-STORE-SERIALIZED-VALUES])
    lineapy.options.set('database_url', [NEW-DATABASE-URL-FOR-STORING-METADATA])

The best way to configure these filesystems is through the ways officially recommended by the cloud storage providers.
For instance, if you want to configure your AWS credential to use an S3 bucket as your artifact storage directory,
you should configure your AWS account just like official using tools(`AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html>`_ or `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_) you are using to access AWS,
and LineaPy will use the default AWS credentials to access the S3 bucket just like ``pandas`` and ``fsspec``.

Some filesystems might need extra configuration.
In ``pandas``, you can pass these configurations as ``storage_options`` in ``pandas.DataFrame.to_csv(storage_options={some storage options})``,
where the `storage_options` is a filesystem-specific dictionary pass into `fsspec.filesystem <https://filesystem-spec.readthedocs.io/en/latest/api.html>`_ .
In LineaPy, you can use exactly the same ``storage_options`` to handle these extra configuration items, and you can set them with

.. code:: python

    lineapy.options.set('storage_options',{'same storage_options as you use in pandas.io.read_csv'})

or you can put them in the LineaPy configuration files.

Note that, LineaPy does not support configuring these items as LINEAPY environmental variables or CLI options, since passing a dictionary through these two methods are a little bit awkward.
Instead, if you want ot use environmental variables, you should configure it through the official way from the storage provider and ``LineaPy`` should be able to handle these extra configuration items directly.

Note that, which ``storage_options`` items you can set are depends on the filesystem you are using.

.. _postgres:

Storing Artifact Metadata in PostgreSQL
---------------------------------------

.. include:: ../../../snippets/slack_support.rstinc

By default, LineaPy uses SQLite to store artifact metadata (e.g., name, version, code), which keeps the package light and simple.
Given the limitations of SQLite (e.g., single write access to a database at a time), however,
we may want to use a more advanced database such as PostgreSQL.

Run PostgreSQL with Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^^^^^^^^^^^^^

To support interaction between Python and PostgreSQL, we need to install a database adapter. A popular choice
is a Python package called ``psycopg2``, which can be installed as follows:

.. code:: bash

    $ pip install psycopg2-binary

Connect LineaPy with PostgreSQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
^^^^^^^^^^^^

If you are using PostgreSQL as your database, you might encounter the following error:

.. code:: none

    NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres

This is caused by a change in SQLAlchemy where they dropped support for DB URLs of the form ``postgres://``.
Using ``postgresql://`` instead should fix this error.

.. include:: ../../snippets/docs_feedback.rstinc

.. _s3:

Storing Artifact Values in Amazon S3
------------------------------------

.. include:: ../../../snippets/slack_support.rstinc

To use S3 as LineaPy's serialized value location, you can run the following command in your notebook to change your storage backend:

.. code:: python

    lineapy.options.set('artifact_storage_dir', 's3://your-bucket/your-artifact-folder')

You should configure your AWS account just like you would for `AWS CLI <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html>`_ or `boto3 <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`_,
and LineaPy will use the default AWS credentials to access the S3 bucket.

If you want to use other profiles available in your AWS configuration, you can set the profile name with:

.. code:: python

    lineapy.options.set('storage_options', {'profile': 'ANOTHER_AWS_PROFILE'})

which is equivalent to setting your environment variable ``AWS_PROFILE`` to the profile name.

If you really need to set your AWS credentials directly in the running session (strongly discouraged as it may result in accidentally saving these credentials in plain text), you can set them with:

.. code:: python

    lineapy.options.set('storage_options', {'key': 'AWS KEY', 'secret': 'AWS SECRET'})

which is equivalent to setting environment variables ``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``.

To learn more about which S3 configuration items that you can set in ``storage_options``, you can see the parameters of `s3fs.S3FileSystem <https://s3fs.readthedocs.io/en/latest/api.html>`_ since ``fsspec`` is passing ``storage_options`` items to ``s3fs.S3FileSystem`` to access S3 under the hood.

.. include:: ../../snippets/docs_feedback.rstinc

Changing Storage Location
=========================

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

.. toctree::
   :maxdepth: 1

   postgres
   s3

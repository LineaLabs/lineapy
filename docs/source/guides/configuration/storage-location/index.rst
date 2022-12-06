Changing Storage Location
=========================

You can change the artifact storage location by setting the `LINEAPY_ARTIFACT_STORAGE_DIR` environmental variable, 
or other ways mentioned in the above section.

For instance, if you want to use a local directory, e.g., ``~/lineapy/artifact_store``, as your artifact storage location and start IPython you can

- Adding ``{"artifact_storage_dir": "/lineapy/artifact_store"}`` in configuration file: and run ``lineapy ipython``
- In environmental variable: ``export LINEAPY_ARTIFACT_STORAGE_DIR=/lineapy/artifact_store && lineapy ipython`` 
- In CLI options: ``lineapy --artifact-storage-dir='/lineapy/artifact_store' ipython``

or you can start ipython as usual then run ``lineapy.options.set('artifact_storage_dir', '/lineapy/artifact_store')`` at the beginning of the ipython session.

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

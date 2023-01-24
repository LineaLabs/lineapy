# Changing Storage Location

Under the hood, LineaPy stores artifacts as two data structures:

- Serialized artifact values (i.e., pickle files)
- Database that stores artifact metadata (e.g., timestamp, version, code, pointer to the serialized value)

By default, the serialized values and the metadata are stored in `.lineapy/linea_pickles/`
and `.lineapy/db.sqlite`, respectively, where `.lineapy/` is created under the system's home directory.

These default locations can be overridden by modifying the configuration file:

``` title="lineapy_config.json"
{
    "artifact_storage_dir": [NEW-PATH-TO-STORE-SERIALIZED-VALUES],
    "database_url": [NEW-DATABASE-URL-FOR-STORING-METADATA],
    ...
}
```

or by making these updates in each interactive session:

```python
lineapy.options.set('artifact_storage_dir', [NEW-PATH-TO-STORE-SERIALIZED-VALUES])
lineapy.options.set('database_url', [NEW-DATABASE-URL-FOR-STORING-METADATA])
```

!!! note

    The session should be reset when the storage location gets changed since we cannot
    retrieve previous information from the new database. Hence, when setting storage location
    in an interactive session, it should be done at the beginning.

!!! warning

    When updating storage location, make sure that `artifact_storage_dir` and `database_url`
    get updated hand in hand. If not, artifact retrieval may suffer an error.

The best way to configure these filesystems is through the ways officially recommended by the cloud storage providers.
For instance, if you want to configure your AWS credential to use an S3 bucket as your artifact storage directory,
you should configure your AWS account using relevant official tools
(e.g., [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html),
[`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)),
and LineaPy will use the default AWS credentials to access the S3 bucket just like `pandas` and `fsspec`.

Some filesystems might need extra configuration. In `pandas`, you can pass these configurations as
`storage_options` in `pandas.DataFrame.to_csv(storage_options={some storage options})`,
where the `storage_options` is a filesystem-specific dictionary pass into
[`fsspec.filesystem`](https://filesystem-spec.readthedocs.io/en/latest/api.html).
In LineaPy, you can use exactly the same `storage_options` to handle these extra configuration items,
and you can set them with

```python
lineapy.options.set('storage_options',{'same storage_options as you use in pandas.io.read_csv'})
```

or you can put them in the LineaPy configuration files.

Note that, LineaPy does not support configuring these items as environmental variables or CLI options,
since passing a dictionary through these two methods are a little bit awkward.
Instead, if you want ot use environmental variables, you should configure it through the official way
from the storage provider and `LineaPy` should be able to handle these extra configuration items directly.

Note that, which `storage_options` items you can set are depends on the filesystem you are using.

## Storing Artifact Metadata in PostgreSQL

By default, LineaPy uses SQLite to store artifact metadata (e.g., name, version, code),
which keeps the package light and simple. Given the limitations of SQLite (e.g., single write access
to a database at a time), however, we may want to use a more advanced database such as PostgreSQL.

To make LineaPy recognize and use a PostgreSQL database, we can export the database connection string
into the relevant environmental variable, like so:

```bash
export LINEAPY_DATABASE_URL=postgresql://postgresuser:postgrespwd@localhost:15432/postgresdb
```

Note that this has to be done prior to using LineaPy so that the environment variable exists in runtime.

!!! tip

    If you want to use PostgreSQL as the default backend, you can make the environment variable
    persist across sessions by defining it in `.bashrc` or `.zshrc`.

You can check the connection between LineaPy and PostgreSQL with:

```python
from lineapy.db.db import RelationalLineaDB
print(RelationalLineaDB.from_environment().url)
```

which will print:

```
postgresql://postgresuser:postgrespwd@localhost:15432/postgresdb
```

if successful. Otherwise, it will default back to SQLite and print:

```
sqlite:///.lineapy/db.sqlite
```

!!! bug

    If you are using PostgreSQL as your database, you might encounter the following error:

    ```
    NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres
    ```

    This is caused by a change in SQLAlchemy where they dropped support for DB URLs of the form `postgres://`.
    Using `postgresql://` instead should fix this error.

## Storing Artifact Values in Amazon S3

To use S3 as LineaPy's serialized value location, you can run the following command
in your notebook to change your storage backend:

```python
lineapy.options.set('artifact_storage_dir', 's3://your-bucket/your-artifact-folder')
```

You should configure your AWS account just like you would for
[AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) or
[`boto3`](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html),
and LineaPy will use the default AWS credentials to access the S3 bucket.

If you want to use other profiles available in your AWS configuration, you can set the profile name with:

```python
lineapy.options.set('storage_options', {'profile': 'ANOTHER_AWS_PROFILE'})
```

which is equivalent to setting your environment variable `AWS_PROFILE` to the profile name.

If you really need to set your AWS credentials directly in the running session (strongly discouraged
as it may result in accidentally saving these credentials in plain text), you can set them with:

```python
lineapy.options.set('storage_options', {'key': 'AWS KEY', 'secret': 'AWS SECRET'})
```

which is equivalent to setting environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

To learn more about which S3 configuration items that you can set in `storage_options`, you can see
the parameters of [`s3fs.S3FileSystem`](https://s3fs.readthedocs.io/en/latest/api.html)
since `fsspec` is passing `storage_options` items to `s3fs.S3FileSystem` to access S3 under the hood.

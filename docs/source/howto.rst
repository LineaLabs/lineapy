.. _howto:

Common issues faced during installation or running using lineapy

Guide for beginners
===================

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


It's likely that lineapy is not setup properly.
For Jupyter Notebooks, we currently require that you start it with :code:`env IPYTHONDIR=$PWD/.ipython jupyter notebook`
(changing it soon to :code:`lineapy jupyter notebook` or :code:`lineapy jupyter lab` if you are using that).
If that does not work, please try running ``%load_ext lineapy`` in your notebook.

If your notebook is stuck in a frozen state, please restart (we are actively working on eliminating these edge cases).

If you are using PostgreSQL as your database, you might encounter the following error:

.. code-block::

    NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:postgres


This is caused by a change in SQLAlchemy where they dropped support for db urls of the form `postgres://` 
Using `postgresql://` instead should fix this error.

Guide for developers
=====================

You can find details about how to setup your dev environment and the testing
process in our doc: `CONTRIBUTING <https://github.com/LineaLabs/lineapy/blob/main/CONTRIBUTING.md>`__.

.. _testingairflow:

Testing Airflow DAGs
---------------------

Every time `to_airflow` is called, a Dockerfile and a requirements.txt with the dag name as prefix will be generated in the same folder.
Build a docker image using the dockerfile to set up an image with a test airflow instance. This standalone instance can be used to test your dag.
To build an image, run the following command:
.. code-block::
    
    docker build -t <image_name> . -f <dagname>_Dockerfile

To then stand up an airflow instance with the dag in it, run the following command:
.. code-block::
    
    docker run -it -p 8080:8080 <image_name>


Guide for contributors
======================

There are currently three ways to contribute!

1. You can try out our tool and complete our `survey <https://docs.google.com/forms/d/1K9Ch7_SC7KWgvxTC2wnnfUer8FXN-xojFlYoJastRG4/viewform?edit_requested=true>`__.
2. If you are here to contribute new library annotations, :ref:`review the documentation here <lib_annotations>`.
3. You can find issues on `Github with the label "help wanted" <https://github.com/LineaLabs/lineapy/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22>`__.

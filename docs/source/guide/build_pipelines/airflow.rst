.. _testingairflow:

Running Airflow DAGs
--------------------

Every time :func:`lineapy.to_pipeline` is called, a Dockerfile and a ``requirements.txt`` with the dag name as prefix will be generated in the same folder.
When using ``framework="AIRFLOW"``, we can use the dockerfile that is output to set up an image with a test airflow instance. 
This standalone instance can be used to test your dag. To build an image, run the following command:

.. code:: bash

    docker build -t <image_name> . -f <dagname>_Dockerfile

To then stand up an airflow instance with the dag in it, run the following command:

.. code:: bash

    docker run -it -p 8080:8080 <image_name>


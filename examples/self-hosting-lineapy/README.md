Prerequisites
-------------
* The latest version of this demo cloned from the lineapy repository.
```
git clone git@github.com:LineaLabs/lineapy.git
cd lineapy/examples/self-hosting-lineapy/
git pull
```

* Docker and [Docker compose](https://docs.docker.com/compose/install/). Make sure you have [Compose V2](https://docs.docker.com/compose/#compose-v2-and-the-new-docker-compose-command) and the new `docker compose` command.
The easiest way to install Docker compose is to install Docker Desktop for [Mac](https://docs.docker.com/desktop/install/mac-install/), [Windows](https://docs.docker.com/desktop/install/windows-install/), or [Linux](https://docs.docker.com/desktop/install/linux-install/).

* Make sure to give your containers enough memory to run, we found 2GB to work well for Airflow. Instructions for setting resource limits if using Docker Desktop can be found here for [Mac](https://docs.docker.com/desktop/settings/mac/#resources), [Windows](https://docs.docker.com/desktop/settings/windows/#resources), and [Linux](https://docs.docker.com/desktop/settings/linux/#resources).

Introduction
------------
The goal of this demo is to create an easy to run, local data science
development environment that showcases the capabilities of LineaPy. The demo
gives users an easy way to run end-to-end tutorials and prototype solutions
to their problems using LineaPy. This demo is self contained but if you would
like to familiarize yourself with LineaPy's capabilites, the [colab notebook demos](https://github.com/LineaLabs/lineapy#what-problems-can-lineapy-solve) are a great place to start.


This demo uses `docker compose` to orchestrate running the following services locally:

* A Jupyter Lab setup with a LineaPy development environment that includes:
    * A requirements.txt to easily manage Python dependencies in the dev environment.
    * A LineaPy config file to connect the LineaPy environment to the hosted storage and DB.
    * Mounted shared volumes under `work` directory that are shared with Airflow.

* A Postgres database to act as a remote LineaPy DB to store:
    * LineaPy Artifact's State and Metadata

* A local S3 compatible object store (we use [minio](http://min.io/)) to store:
    * LineaPy Artifact's Values
    * Data to be used in the development environment

* A standalone instance of Airflow that includes:
    * A requirements.txt to easily manage Python dependencies in the Airflow environment.
    * An airflow.cfg file to manage Airflow's configurations.
    * Mounted shared volumes that can pick up Airflow DAGs from the dev environment automatically.

* To be implemented:
    * A dashboard for rendering user data (possibly Grafana) from Postgres or other sources.
    * Additional orchestration platforms such as Kubeflow or MLFlow (coming soon!).

Running the Demo
---

OPTIONAL - Configure ports before starting. The default ports for various services can be changed in the `.env` file in case there's a conflict with existing services or projects running on `localhost`.


To start the demo

1. Run `docker compose pull` to pull the latest container images.

2. Run `docker compose up --wait`, which will start and wait for all containers to be healthy. Once all containers are started they will be run in the background.

3. Services will be reachable at the following address (unless you modify the default ports in the `.env` file):
   - Jupyter - `http://localhost:8888`
   - Airflow - `http://localhost:8080`
   - Postgres - Docker port 5432
   - Minio s3 storage - Docker port 9000
   - Minio web console - `http://localhost:9001` username `lineapy` and password `lineapypassword`

4. In the Jupyter environment, navigate to the `work/examples` directory.

5. Walk through and run all the cells in the `housing_example.ipynb` notebook. Note how the data is loaded from minio s3.

6. After the to_pipeline call, switch over to Airflow and you should see the LineaPy generated DAG has been automatically picked up (you may have to refresh the Airflow browser page if it was already loaded).

7. Run the DAG in Airflow and see the resulting output file in Minio S3 storage under `s3://data/outputs/cleaned_data_housing.csv`

8. To stop the demo, run `docker compose down`. Alternatively, run `docker compose down -v` to stop the services and delete the shared storage and database.

Note: This example can also be run in the foreground using `docker compose up` (i.e., without the wait flag). If so, logs (including warnings and errors) will be visible in the terminal. Make sure to wait for all containers to be healthy before proceeding with the demo (e.g., by running `docker ps`). Pressing `Ctrl+C` will not fully stop the demo environment, please refer to the instructions above to fully stop the services and cleanup state.


Managing Python Dependencies
-----------------------
A `requirements.txt` file is dynamically installed during container startup for both the Jupyter and
Airflow containers to manage user dependencies respectively.

These two requirements files are kept separate because LineaPy can prune out unused packages and return only needed dependencies for pipeline execution when generating pipelines. This means not every dependency in the Jupyter environment will be needed in the Airflow environment.

For example, say a user is running a notebook in their Jupyter environemnt, and realize that they require
`seaborn`. They can add it to the `lineapy-notebook/requirements.txt` file,
then issue the command `docker compose restart notebook` to restart
the development environment notebook, which will install the dependency and reload the
service states.

After creating a pipeline in the notebook, LineaPy will generate the pipeline's `requirements.txt` file, which should be manually copied/appended to the requirements for `airflow/requirements.txt` since these are the requirements needed for pipeline execution. Issuing the command `docker compose restart airflow` to restart the Airflow environment will install the new dependency there.


Lineapy Configuration
---------------------

This demo configures Lineapy with non-default options to demonstrate how to connect the `notebook` environment to the services hosting Lineapy. Documentation on Lineapy configuration can be found [here](https://docs.lineapy.org/en/latest/references/configurations.html). Specifically, this demo configures Lineapy using a configuration file, which can be found under `lineapy-notebook/lineapy_config.json` and is mounted in the `notebook` container under `~/.lineapy/lineapy_config.json`.

Important to this demo are `storage_options`, `artifact_storage_dir`, and `database_url` options.
`database_url` points to the DB hosting the artifact store.
`artifact_storage_dir` points to the s3 storage that contains artifact store values, and
`storage_options` helps lineapy connect to the s3 storage.


Additional Details About this Demo
----------------------

This demo creates 4 services to demonstrate how LineaPy would likely be hosted in non-local environments.

The `notebook` container is built in the `lineapy-notebook` directory and based on the `jupyter/minimal-notebook` image. LineaPy and dependencies are pip installed in the Dockerfile and notably, the entrypoint for the Dockerfile is changed to a custom `notebook-start.sh` script.
This script installs additional `requirements.txt` dependencies on container start which is more convenient than rebuilding the image when new dependencies are needed by data scientists. The jupyter launch command is also changed to use `lineapy jupyter`. Finally, `lineapy_config.json` is bind mounted to the `${HOME}/.lineapy` directory of the jupyter user where it is automatically picked up on when LineaPy starts. Key configurations here are, pointing `artifact_storage_dir` to the remote s3 bucket, setting `storage_options` to use correct credentials that are passed to fsspec library, and pointing `database_url` to the remote postgres instance.

The `airflow` container is built in the `airflow` directory and is based off of the `apache/airflow` image. The startup is done by `airflow-start.sh` which calls a `airflow standalone` command (this should not be used for production environments since standalone is _very_ limited in configurability and is designed for local testing only). A key addition here is that the Airflow worker environment for pipelines must install the dependencies specified by the `pipeline_requirements` file that LineaPy generates. This is made easier by having the Airflow environment also install from a `requirements.txt` file on container start. `airflow.cfg` is also specified and bind mounted, and `min_file_process_interval` and ` dag_dir_list_interval` are lowered so that Airflow detects DAGs more quickly.

The `notebook` and `airflow` containers communicate through a pair of shared mounted volumes named `shared-airflow-dags-volume` and
`shared-airflow-plugins-volume`. These volumes are mounted as the `dags/` and `plugins/` directory respectively in the Airflow environment. This allows the data scientist in the dev notebook environment to save their DAGs and have them conveniently show up in Airflow automatically without copying files manually.

The `postgres-lineapy` container hosts a PostgreSQL instance. This is preferred over the sqlite default to handle potential concurrent requests. This can and should be hosted non-locally.

The `minio` container is used to host a remote s3 environment. For the purposes of this demo two buckets are created by an ephemeral `createbuckets` container. `lineapy-artifact-store` is used to host the LineaPy artifact directory, and `data` is used to simulate user data that data scientists may need access to during their development process. In this demo environment the `data` bucket is pre populated with data from `./examples/data/` directory by bind mounting the directory to the container under `/tmp/examples/data` and then using a `mc cp` command to copy it into the bucket.

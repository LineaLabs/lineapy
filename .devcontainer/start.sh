#!/bin/bash
# Modified from https://docs.docker.com/config/containers/multi-service_container/

# turn on bash's job control
set -m

# Start the first process
make jupyterlab_start &> /tmp/jupyterlab_log &

# Start the second process
make airflow_home airflow_start &> /tmp/airflow_log &

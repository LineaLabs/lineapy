#!/bin/bash
# Modified from https://docs.docker.com/config/containers/multi-service_container/

# Start the first process
make jupyterlab_start &
  
# Start the second process
make airflow_start &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?
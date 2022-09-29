#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# LineaPy extensions (c) Linea Labs

set -e

# The Jupyter command to launch
# JupyterLab by default
DOCKER_STACKS_JUPYTER_CMD="${DOCKER_STACKS_JUPYTER_CMD:=lab}"

if [[ -n "${JUPYTERHUB_API_TOKEN}" ]]; then
    echo "WARNING: using start-singleuser.sh instead of start-notebook.sh to start a server associated with JupyterHub."
    exec /usr/local/bin/start-singleuser.sh "$@"
fi

wrapper=""
if [[ "${RESTARTABLE}" == "yes" ]]; then
    wrapper="run-one-constantly"
fi

if [[ -f /requirements.txt ]]
then
    echo "Installing system requirements."
    pip3 install -r /requirements.txt
fi

# Verify lineapy environment is set up correctly
lineapy python /verify_environment.py

# shellcheck disable=SC1091,SC2086
exec /usr/local/bin/start.sh ${wrapper} lineapy jupyter ${DOCKER_STACKS_JUPYTER_CMD} "--NotebookApp.token=''"

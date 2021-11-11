# This file was modified from https://github.com/microsoft/vscode-dev-containers/blob/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
FROM python:3.9

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends graphviz \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

COPY setup.py /workspaces/lineapy/
COPY lineapy/__init__.py /workspaces/lineapy/lineapy/

RUN pip --no-cache-dir install -e "/workspaces/lineapy/[dev]" \
   && rm -rf /workspaces/lineapy

ENV IPYTHONDIR=/workspaces/lineapy/.ipython

CMD jupyter lab --ServerApp.token='' --port 8888 --allow-root --ip 0.0.0.0 --ServerApp.allow_origin=*
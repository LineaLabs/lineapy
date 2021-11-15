# This file was modified from https://github.com/microsoft/vscode-dev-containers/blob/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
FROM python:3.9

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends graphviz \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/lineapy
COPY . /workspaces/lineapy

# Create airflow venv
RUN make /tmp/airflow_venv

# Install lineapy requirements
RUN pip --no-cache-dir --disable-pip-version-check install -e ".[dev]"

# Setup git lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install git-lfs && git lfs install

CMD .devcontainer/start.sh
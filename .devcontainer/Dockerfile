# This file was modified from https://github.com/microsoft/vscode-dev-containers/blob/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
ARG IMAGE_NAME=ghcr.io/linealabs/lineapy:optimize-codespace-startup
FROM $IMAGE_NAME

WORKDIR /workspaces/lineapy
COPY . /workspaces/lineapy

CMD .devcontainer/start.sh
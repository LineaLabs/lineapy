# syntax=docker/dockerfile:1.2
# Pin syntax as Docker reccomens
# https://docs.docker.com/language/python/build-images/#create-a-dockerfile-for-python
FROM python:3.9.7


WORKDIR /usr/src/base

COPY . .

RUN pip install -e .

ENTRYPOINT [ "lineapy" ]


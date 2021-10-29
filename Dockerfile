# syntax=docker/dockerfile:1.2
# Pin syntax as Docker reccomens
# https://docs.docker.com/language/python/build-images/#create-a-dockerfile-for-python
FROM python:3.9.7-slim

RUN apt-get update && apt-get -y install git graphviz && apt clean && apt-get autoclean && apt-get autoremove

WORKDIR /usr/src/base

# small hack to not keep building all the time
COPY ./setup.py ./
COPY ./lineapy/__init__.py ./lineapy/
RUN pip install -e .[dev]

COPY . .

CMD [ "lineapy" ]

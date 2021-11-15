# syntax=docker/dockerfile:1.2
# Pin syntax as Docker reccomens
# https://docs.docker.com/language/python/build-images/#create-a-dockerfile-for-python
FROM python:3.9.7-slim

RUN apt-get update && apt-get -y install git graphviz make && apt clean && apt-get autoclean && apt-get autoremove

WORKDIR /usr/src/base

# small hack to not keep building all the time
COPY ./setup.py ./
COPY ./lineapy/__init__.py ./lineapy/
COPY ./airflow-requirements.txt ./
COPY ./Makefile ./

RUN pip --disable-pip-version-check install -e .[dev] && make /tmp/airflow_venv && pip cache purge

# Setup git lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install git-lfs && git lfs install


COPY . .

CMD [ "lineapy" ]

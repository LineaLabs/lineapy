# syntax=docker/dockerfile:1.2
# Pin syntax as Docker reccomens
# https://docs.docker.com/language/python/build-images/#create-a-dockerfile-for-python
FROM python:3.8.12-slim

RUN apt-get update && apt-get -y install git graphviz make && \
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
    && apt-get install git-lfs && git lfs install && apt clean && apt-get autoclean && apt-get autoremove

WORKDIR /usr/src/base

# small hack to not keep building all the time
COPY ./setup.py ./
COPY ./README.md ./
COPY ./lineapy/__init__.py ./lineapy/
COPY ./airflow-requirements.txt ./
COPY ./Makefile ./

ENV AIRFLOW_HOME=/usr/src/airflow_home
ENV AIRFLOW_VENV=/usr/src/airflow_venv

#RUN mkdir /usr/src/airflow_home
RUN pip --disable-pip-version-check install -e .[dev] && make airflow_venv && pip cache purge

COPY . .

CMD [ "lineapy" ]

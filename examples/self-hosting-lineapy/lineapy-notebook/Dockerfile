ARG OWNER=jupyter
# If you need ARM set ARCH to "aarch64-"
ARG ARCH
ARG BASE_CONTAINER=$OWNER/minimal-notebook:${ARCH}latest
FROM $BASE_CONTAINER

LABEL maintainer="LineaPy Project <chris.hoge@linea.ai>"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

USER root

# curl required for health check
RUN apt update -y
RUN apt install -y curl

# switch back to notebook user so permissions on files are correct
USER $NB_UID

# prevent pip timing out on slow internet connections
RUN export PIP_DEFAULT_TIMEOUT=1000

# deps for lineapy
RUN pip install -U pip
RUN pip install fsspec s3fs psycopg2-binary

# install lineapy
RUN pip install lineapy==0.2.1

# other nice to have libraries
RUN pip install pandas==1.4.3 scikit-learn==1.1.2 seaborn==0.11.2

COPY notebook-start.sh /usr/local/bin/notebook-start.sh

# Make mountpoints for airflow so that they are mounted as non-root
RUN mkdir -p /home/jovyan/work/airflow/dags
RUN mkdir -p /home/jovyan/work/airflow/plugins

ENTRYPOINT ["tini", "-g", "--"]
CMD ["notebook-start.sh"]

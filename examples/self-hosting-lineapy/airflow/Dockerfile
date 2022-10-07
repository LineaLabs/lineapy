FROM apache/airflow:slim-latest-python3.10

USER $AIRFLOW_UID

# prevent pip timing out on slow internet connections
RUN export PIP_DEFAULT_TIMEOUT=1000

# deps for lineapy
RUN pip install -U pip
RUN pip install fsspec s3fs psycopg2-binary

# install lineapy
RUN pip install lineapy==0.2.1

# other nice to have libraries
RUN pip install pandas==1.4.3 scikit-learn==1.1.2

COPY airflow.cfg /opt/airflow/airflow.cfg
COPY airflow-start.sh /airflow-start.sh

USER root
RUN chown $AIRFLOW_UID /opt/airflow/airflow.cfg
RUN chown $AIRFLOW_UID /airflow-start.sh
RUN chmod +x /airflow-start.sh
USER $AIRFLOW_UID

RUN mkdir /opt/airflow/plugins

ENV AIRFLOW_HOME=/opt/airflow

ENTRYPOINT ["/airflow-start.sh"]
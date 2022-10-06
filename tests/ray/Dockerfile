FROM rayproject/ray

# RUN mkdir /tmp/installers
# WORKDIR /tmp/installers

# # copy all the requirements to run the current dag
COPY ./start.sh ./
# COPY ./{{ pipeline_name }}_requirements.txt ./
# # install the required libs
# RUN pip install -r ./{{ pipeline_name }}_requirements.txt

# WORKDIR /opt/airflow/dags
# COPY . .

# WORKDIR /opt/airflow

EXPOSE 6379

CMD [ "bash", "./start.sh"]

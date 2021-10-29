base_imagename=ghcr.io/linealabs/lineapy
service_name=lineapy
export IMAGE_NAME=${base_imagename}:main
export IMAGE_NAME_AIRFLOW=${base_imagename}-airflow:main

build:
	docker-compose build \
	${args} \
	${service_name}

build-airflow:
	docker-compose build \
	${args} \
	${service_name}-airflow

airflow-up:
	docker-compose up \
	${args} \
	${service_name}-airflow

bash:
	docker-compose run --rm ${service_name} /bin/bash

bash-airflow:
	docker-compose run --rm ${service_name}-airflow /bin/bash

test:
	docker-compose run --rm ${service_name} pytest ${args} --snapshot-update --no-cov -m "not slow" -m "not airflowtest" tests/

test-airflow:
	docker-compose run --rm ${service_name}-airflow pytest ${args} --snapshot-update --no-cov -m "airflowtest" tests/

lint:
	docker run --rm -v "${PWD}":/apps alpine/flake8:latest --verbose . && \
	docker-compose run --rm ${service_name} isort . --check

blackfix:
	docker run --rm -v "${PWD}":/data cytopia/black .

typecheck:
	#docker run --rm -v "${PWD}":/data cytopia/mypy .
	docker-compose run --rm ${service_name} mypy -p lineapy
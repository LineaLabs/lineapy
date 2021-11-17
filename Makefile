base_imagename=ghcr.io/linealabs/lineapy
service_name=lineapy
export IMAGE_NAME=${base_imagename}:main
export IMAGE_NAME_AIRFLOW=${base_imagename}-airflow:main
export AIRFLOW_HOME?=/tmp/airflow_home
AIRFLOW_VENV?=/tmp/airflow_venv

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
	docker-compose run --rm ${service_name} pytest ${args} --snapshot-update --no-cov -m "not slow" -m "not airflow" tests/

test-airflow:
	docker-compose run --rm ${service_name}-airflow pytest ${args} --snapshot-update --no-cov -m "airflow" tests/

lint:
	docker run --rm -v "${PWD}":/apps alpine/flake8:latest --verbose . && \
	docker-compose run --rm ${service_name} isort . --check

blackfix:
	docker run --rm -v "${PWD}":/data cytopia/black .

typecheck:
	#docker run --rm -v "${PWD}":/data cytopia/mypy .
	docker-compose run --rm ${service_name} mypy -p lineapy


# Add pattern for all notebook files to re-execute them when they change
# so that we can update them for the tests easily.
# https://stackoverflow.com/questions/2483182/recursive-wildcards-in-gnu-make
NOTEBOOK_FILES = $(shell find . -type f -name '*.ipynb' -not -path '*/.ipynb_checkpoints/*' -not -path './docs/*')
notebooks: $(NOTEBOOK_FILES)

# Force to be re-run always
# https://stackoverflow.com/questions/26226106/how-can-i-force-make-to-execute-a-recipe-all-the-time
# TODO: Possibly switch to jupyter execute?
# https://twitter.com/palewire/status/1458083565191655424
%.ipynb: FORCE
	@echo Running "$@"
	jupyter nbconvert --to notebook --execute $@ --allow-errors --inplace

FORCE: ;


$(AIRFLOW_VENV): 
	python -m venv ${AIRFLOW_VENV}
	${AIRFLOW_VENV}/bin/pip install --disable-pip-version-check -r airflow-requirements.txt


${AIRFLOW_HOME}:
	mkdir -p ${AIRFLOW_HOME}
	cp -f airflow_webserver_config.py ${AIRFLOW_HOME}/webserver_config.py

airflow_start: ${AIRFLOW_HOME}
	env AIRFLOW__CORE__LOAD_EXAMPLES=False \
		AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL=1 \
		AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=1 \
		bash -c "source ${AIRFLOW_VENV}/bin/activate && ./airflow_start.py"




clean_airflow:
	rm -rf ${AIRFLOW_HOME} ${AIRFLOW_VENV}
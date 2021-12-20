base_imagename=ghcr.io/linealabs/lineapy
service_name=lineapy
export IMAGE_NAME=${base_imagename}:main
export IMAGE_NAME_AIRFLOW=${base_imagename}-airflow:main
export AIRFLOW_HOME?=/usr/src/airflow_home
export AIRFLOW_VENV?=/usr/src/airflow_venv

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

build-docs:
	docker-compose run --rm ${service_name} /bin/bash -c "cd docs && rm -rf source/build source/autogen && SPHINX_APIDOC_OPTIONS=members sphinx-apidoc -d 2 -f -o ./source/autogen ../lineapy/ && make html"

test:
	docker-compose run --rm ${service_name} pytest ${args} --snapshot-update --no-cov -m "not slow" -m "not airflow" tests/

test-github-action:
	docker-compose run --rm ${service_name} pytest ${args}

test-airflow:
	docker-compose run --rm ${service_name}-airflow pytest ${args} --snapshot-update --no-cov -m "airflow" tests/

lint:
	docker run --rm -v "${PWD}":/apps alpine/flake8:latest --verbose . && \
	docker-compose run --rm ${service_name} isort . --check

blackfix:
	docker run --rm -v "${PWD}":/data cytopia/black .

typecheck:
	docker-compose run --rm ${service_name} mypy .

typecheck-dev:
	docker-compose run --rm ${service_name} mypy -p lineapy

export IPYTHONDIR=${PWD}/.ipython

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
	env IPYTHONDIR=${PWD}/.ipython jupyter nbconvert --to notebook --execute $@ --allow-errors --inplace

FORCE: ;

export JUPYTERLAB_WORKSPACES_DIR=${PWD}/jupyterlab-workspaces

airflow_venv: 
	python -m venv ${AIRFLOW_VENV}
	${AIRFLOW_VENV}/bin/pip install --disable-pip-version-check -r airflow-requirements.txt


airflow_home: 
	mkdir -p ${AIRFLOW_HOME}
	cp -f airflow_webserver_config.py ${AIRFLOW_HOME}/webserver_config.py


airflow_start:  
		env AIRFLOW__CORE__LOAD_EXAMPLES=False \
		AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL=1 \
		AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=1 \
		bash -c 'source ${AIRFLOW_VENV}/bin/activate && airflow standalone'


jupyterlab_start:
	jupyter lab --ServerApp.token='' --port 8888 --allow-root --ip 0.0.0.0 --ServerApp.allow_origin=*

clean_airflow:
	rm -rf ${AIRFLOW_HOME} ${AIRFLOW_VENV}
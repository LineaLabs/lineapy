SHELL=/bin/bash
base_imagename=ghcr.io/linealabs/lineapy
service_name=lineapy
export IMAGE_NAME=${base_imagename}:main
export IMAGE_NAME_AIRFLOW=${base_imagename}-airflow:main
export AIRFLOW_HOME?=/usr/src/airflow_home
export AIRFLOW_VENV?=/usr/src/airflow_venv
BACKEND?=sqlite
export POSTGRES_PASSWORD=supersecretpassword
ifeq ("$(BACKEND)","PG")
	export LINEAPY_DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@postgres:5432/postgres
endif

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

pg-up:
	docker-compose up \
	${args} \
	postgres &

wait_for_deps:
	docker-compose up ${args} wait_for_deps

deps:
	@if [ "${BACKEND}" == "PG" ] ; then \
		make pg-up wait_for_deps;\
	fi

down:
	docker-compose down	

bash: 
	make deps
	docker-compose run --rm ${service_name} /bin/bash

bash-airflow:
	docker-compose run --rm ${service_name}-airflow /bin/bash

build-docs:
	cd docs && python gen_ref_pages.py && mkdocs serve

test:
	make deps
	docker-compose run --rm ${service_name} pytest ${args} --snapshot-update --no-cov -m "not (slow or airflow or ray or dvc or kubeflow or argo or integration)" tests/

test-github-action:
	docker-compose run --rm ${service_name} pytest ${args}

# needs pytest-xdist installed to run tests in parallel. also sqlite db should not be used as multiple users cannot write to it
# postgres db has been tested and found to be working fine. in future commits, pg can be added as a dependent service in the docker-compose. 
# Additionally, the package pg and psycopg2 should be installed in the main service.
test-parallel:
	make deps
	docker-compose run --rm ${service_name} pytest ${args} -n 3 --dist=loadscope --snapshot-update --no-cov -m "not (slow or airflow or ray or dvc or kubeflow or argo or integration)" tests/

test-airflow:
	docker-compose run --rm ${service_name}-airflow pytest ${args} --snapshot-update --no-cov -m "airflow" tests/

# Update pipeline integration specific snapshots.
test-pipelines:
	docker-compose run --rm ${service_name} pytest ${args} --snapshot-update --no-cov -m "airflow or argo or dvc or ray or kubeflow" tests/unit/plugins/framework_specific/**/test_writer_*.py

lint:
	docker run --rm -v "${PWD}":/apps alpine/flake8:latest --verbose . 
#	this seems to be causing issues with our submodules. skipping for now
#	&& \ 
#	docker-compose run --rm ${service_name} isort . --check

blackfix:
	docker run --rm -v "${PWD}":/data cytopia/black .

lint-dev:
	flake8 --verbose . && \
	isort . --check

blackfix-dev:
	black .

typecheck:
	docker-compose run --rm ${service_name} dmypy run -- --follow-imports=skip .

typecheck-dev:
	dmypy run -- --follow-imports=skip .


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
	lineapy jupyter nbconvert --to notebook --execute $@ --allow-errors --inplace

FORCE: ;

export JUPYTERLAB_WORKSPACES_DIR=${PWD}/jupyterlab-workspaces

airflow_venv: 
	python -m venv ${AIRFLOW_VENV}
	${AIRFLOW_VENV}/bin/pip install --disable-pip-version-check -r test_pipeline_airflow_req.txt


airflow_home: 
	mkdir -p ${AIRFLOW_HOME}/dags
	cp -f airflow_webserver_config.py ${AIRFLOW_HOME}/webserver_config.py


airflow_start:  
		env AIRFLOW__CORE__LOAD_EXAMPLES=False \
		AIRFLOW__SCHEDULER__MIN_FILE_PROCESS_INTERVAL=1 \
		AIRFLOW__SCHEDULER__DAG_DIR_LIST_INTERVAL=1 \
		bash -c 'source ${AIRFLOW_VENV}/bin/activate && airflow standalone'


jupyterlab_start:
	lineapy jupyter lab --ServerApp.token='' --port 8888 --allow-root --ip 0.0.0.0 --ServerApp.allow_origin=*

clean_airflow:
	rm -rf ${AIRFLOW_HOME} ${AIRFLOW_VENV}

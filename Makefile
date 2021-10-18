imagename=lineapy
build:
	docker-compose build \
	${args} \
	${imagename}

bash:
	docker-compose run --rm ${imagename} /bin/bash

test:
	docker-compose run --rm ${imagename} pytest ${args}

lint:
	docker run --rm -v "${PWD}":/apps alpine/flake8:latest --verbose .

blackfix:
	docker run --rm -v "${PWD}":/data cytopia/black .

typecheck:
	#docker run --rm -v "${PWD}":/data cytopia/mypy .
	docker-compose run --rm ${imagename} mypy .
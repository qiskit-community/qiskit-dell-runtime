DOCKER_CMD=docker
DOCKER_BASE=harbor.dell.com/dojo-harbor/qre

test: acceptance unit

acceptance: 
	pip3 install .
	pytest acceptance_tests/

unit:
	pip3 install .
	pytest --full-trace tests/

component:
	pip3 install .
	pytest component_tests/
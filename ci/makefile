DOCKER_CMD=docker
FLY_CMD=fly
DOCKER_BASE=harbor.dell.com/dojo-harbor/qre

all: build
build: build_test_image37 build_test_image38 build_test_image39 build_deploy_image
push: push_test_image37 push_test_image38 push_test_image39 push_deploy_image

build_deploy_image:
	$(DOCKER_CMD) build ./docker/deploy/ -t $(DOCKER_BASE)/deploy

push_deploy_image:
	$(DOCKER_CMD) push $(DOCKER_BASE)/deploy

build_test_image37: export PY_V=3.7
build_test_image37:
	envsubst < ./docker/test_base/dockerfile | $(DOCKER_CMD) build -t $(DOCKER_BASE)/test-base:$(PY_V) -

push_test_image37: export PY_V=3.7
push_test_image37: 
	$(DOCKER_CMD) push $(DOCKER_BASE)/test-base:$(PY_V)

build_test_image38: export PY_V=3.8
build_test_image38:
	envsubst < ./docker/test_base/dockerfile | $(DOCKER_CMD) build -t $(DOCKER_BASE)/test-base:$(PY_V) -

push_test_image38: export PY_V=3.8
push_test_image38: 
	$(DOCKER_CMD) push $(DOCKER_BASE)/test-base:$(PY_V)

build_test_image39: export PY_V=3.9
build_test_image39:
	envsubst < ./docker/test_base/dockerfile | $(DOCKER_CMD) build -t $(DOCKER_BASE)/test-base:$(PY_V) -

push_test_image39: export PY_V=3.9
push_test_image39: 
	$(DOCKER_CMD) push $(DOCKER_BASE)/test-base:$(PY_V)

# build_test_image38:
# 	$(DOCKER_CMD) build ./test_base/ -t $(DOCKER_BASE)/test_base:$(PY_V)

# build_test_image39:
# 	$(DOCKER_CMD) build ./test_base/ -t $(DOCKER_BASE)/test_base:$(PY_V)

deploy: 
	$(FLY_CMD) -t dojo set-pipeline -p qiskit-emulator -c ./pipeline.yaml -l ../../qre-secrets/secrets.yaml
	
clean:
DOCKER_CMD=docker
DOCKER_BASE=harbor.dell.com/dojo-harbor/qre

all: build_orchestrator_image build_executor_image

build_orchestrator_image:
	$(DOCKER_CMD) build ./orchestrator/ -t $(DOCKER_BASE)/orchestrator

build_executor_image:
	$(DOCKER_CMD) build ./executor/ -t $(DOCKER_BASE)/executor

push:
	$(DOCKER_CMD) push $(DOCKER_BASE)/orchestrator
	$(DOCKER_CMD) push $(DOCKER_BASE)/executor

deploy: 
	envsubst < qre.yaml | kubectl apply -f -
	
clean:
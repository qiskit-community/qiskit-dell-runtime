DOCKER_CMD=docker
DOCKER_BASE=$(DOCKER_REPO)/$(QDR_NS)

all: build_base_qiskit_image build_base_qdr_image build_orchestrator_image build_executor_image 

ddev: all push redeploy

full_restart: clean all push deploy_no_sso

build_base_qiskit_image:
	$(DOCKER_CMD) build ./qiskit_base/ --build-arg DOCKER_REPO=$(DOCKER_REPO) -t $(DOCKER_BASE)/qiskit

build_base_qdr_image:
	$(DOCKER_CMD) build --build-arg QDR_NS=$(QDR_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ../ -t $(DOCKER_BASE)/qdr-base

build_orchestrator_image:
	$(DOCKER_CMD) build --build-arg QDR_NS=$(QDR_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ./orchestrator/ -t $(DOCKER_BASE)/qdr-orchestrator

build_executor_image:
	$(DOCKER_CMD) build --build-arg QDR_NS=$(QDR_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ./executor/ -t $(DOCKER_BASE)/qdr-executor

push:
	$(DOCKER_CMD) push $(DOCKER_BASE)/qiskit
	$(DOCKER_CMD) push $(DOCKER_BASE)/qdr-base
	$(DOCKER_CMD) push $(DOCKER_BASE)/qdr-orchestrator
	$(DOCKER_CMD) push $(DOCKER_BASE)/qdr-executor

deploy_with_sso: 
	envsubst < ./deployments/qdr.yaml | \
	sed "s/QDRCERTS/`cat $(QDR_CERTS_DIR)/qdrcerts.crt|base64 -w0`/g" | \
	kubectl apply -f -
	envsubst < ./deployments/orch_sso.yaml | kubectl apply -f -

deploy_no_sso: 
	envsubst < ./deployments/qdr.yaml | \
	sed "s/QDRCERTS/`cat $(QDR_CERTS_DIR)/qdrcerts.crt|base64 -w0`/g" | \
	kubectl apply -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -

clean:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/qdr.yaml | kubectl delete -f -
	
redeploy:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -




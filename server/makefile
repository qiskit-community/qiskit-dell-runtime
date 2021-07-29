DOCKER_CMD=docker
DOCKER_BASE=$(DOCKER_REPO)/$(QRE_NS)

all: build_base_qiskit_image build_base_qre_image build_orchestrator_image build_executor_image 

ddev: all push redeploy

full_restart: clean all push deploy_no_sso

build_base_qiskit_image:
	$(DOCKER_CMD) build ./qiskit_base/ --build-arg DOCKER_REPO=$(DOCKER_REPO) -t $(DOCKER_BASE)/qiskit

build_base_qre_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ../ -t $(DOCKER_BASE)/qre-base

build_orchestrator_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ./orchestrator/ -t $(DOCKER_BASE)/orchestrator

build_executor_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) --build-arg DOCKER_REPO=$(DOCKER_REPO) ./executor/ -t $(DOCKER_BASE)/executor

push:
	$(DOCKER_CMD) push $(DOCKER_BASE)/qiskit
	$(DOCKER_CMD) push $(DOCKER_BASE)/qre-base
	$(DOCKER_CMD) push $(DOCKER_BASE)/orchestrator
	$(DOCKER_CMD) push $(DOCKER_BASE)/executor

deploy_with_sso: 
	envsubst < ./deployments/qre.yaml | \
	sed "s/QRECERTS/`cat $(QRE_CERTS_DIR)/qrecerts.crt|base64 -w0`/g" | \
	kubectl apply -f -
	envsubst < ./deployments/orch_sso.yaml | kubectl apply -f -

deploy_no_sso: 
	envsubst < ./deployments/qre.yaml | \
	sed "s/QRECERTS/`cat $(QRE_CERTS_DIR)/qrecerts.crt|base64 -w0`/g" | \
	kubectl apply -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -

clean:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/qre.yaml | kubectl delete -f -
	
redeploy:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -




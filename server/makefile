DOCKER_CMD=docker
DOCKER_BASE=harbor.dell.com/dojo-harbor/$(QRE_NS)

all: build_base_qiskit_image build_base_qre_image build_orchestrator_image build_executor_image 

ddev: all push redeploy

full_restart: clean all push deploy_no_sso

build_base_qiskit_image:
	$(DOCKER_CMD) build ./qiskit_base/ -t $(DOCKER_BASE)/qiskit

build_base_qre_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) ../ -t $(DOCKER_BASE)/qre-base

build_orchestrator_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) ./orchestrator/ -t $(DOCKER_BASE)/orchestrator

build_executor_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=$(QRE_NS) ./executor/ -t $(DOCKER_BASE)/executor

push:
	$(DOCKER_CMD) push $(DOCKER_BASE)/qiskit
	$(DOCKER_CMD) push $(DOCKER_BASE)/qre-base
	$(DOCKER_CMD) push $(DOCKER_BASE)/orchestrator
	$(DOCKER_CMD) push $(DOCKER_BASE)/executor

deploy_with_sso: 
	envsubst < ./deployments/qre.yaml | kubectl apply -f -
	kubectl create secret -n $(QRE_NS) generic certs --from-file $(QRE_CERTS_DIR)/ionq_qpu.crt --from-file $(QRE_CERTS_DIR)/ionq_simulator.crt --from-file $(QRE_CERTS_DIR)/qrecerts.crt
	envsubst < ./deployments/orch_sso.yaml | kubectl apply -f -

deploy_no_sso: 
	envsubst < ./deployments/qre.yaml | kubectl apply -f -
	kubectl create secret -n $(QRE_NS) generic certs --from-file $(QRE_CERTS_DIR)/ionq_qpu.crt --from-file $(QRE_CERTS_DIR)/ionq_simulator.crt --from-file $(QRE_CERTS_DIR)/qrecerts.crt
	envsubst < ./deployments/orch.yaml | kubectl apply -f -

clean:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/qre.yaml | kubectl delete -f -
	
redeploy:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -




DOCKER_CMD=docker
DOCKER_BASE=harbor.dell.com/dojo-harbor/qre-dev

all: build_base_qiskit_image build_base_qre_image build_orchestrator_image build_executor_image 

ddev: all push redeploy

full_restart: clean all push deploy

build_base_qiskit_image:
	$(DOCKER_CMD) build ./qiskit_base/ -t $(DOCKER_BASE)/qiskit

build_base_qre_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=qre-dev ../ -t $(DOCKER_BASE)/qre-base

build_orchestrator_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=qre-dev ./orchestrator/ -t $(DOCKER_BASE)/orchestrator

build_executor_image:
	$(DOCKER_CMD) build --build-arg QRE_NS=qre-dev ./executor/ -t $(DOCKER_BASE)/executor

push:
	$(DOCKER_CMD) push $(DOCKER_BASE)/qiskit
	$(DOCKER_CMD) push $(DOCKER_BASE)/qre-base
	$(DOCKER_CMD) push $(DOCKER_BASE)/orchestrator
	$(DOCKER_CMD) push $(DOCKER_BASE)/executor

deploy: 
	envsubst < ./deployments/qre.yaml | kubectl apply -f -
	kubectl create secret -n qre-dev generic certs --from-file executor/backend_certs/ionq_qpu.crt --from-file executor/backend_certs/ionq_simulator.crt --from-file orchestrator/qrecerts.crt
	envsubst < ./deployments/orch.yaml | kubectl apply -f -

clean:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/qre.yaml | kubectl delete -f -
	
redeploy:
	envsubst < ./deployments/orch.yaml | kubectl delete -f -
	envsubst < ./deployments/orch.yaml | kubectl apply -f -




from kubernetes import client, config
import uuid
import yaml
import subprocess

YAML = """
---
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
  namespace: qre
spec:
  containers:
    - name: {pod_name}
      image: harbor.dell.com/dojo-harbor/qre/qre-executor
      env:
      - name: ORCH_HOST
        value: {orch_host}
      - name: PROGRAM_ID
        value: {program_id}
"""


class KubeClient():
    def __init__(self):
        config.load_incluster_config()
        # config.load_kube_config()
        self._api = client.CoreV1Api()

    def run(self, program_id, inputs_str):
        pod_name = "qre-" + str(uuid.uuid1())[-12:]
        orch_host = "http://qre-orchestrator"
        pod_yaml = YAML.format(pod_name=pod_name, orch_host=orch_host, program_id=program_id)
        pod_obj = yaml.safe_load(pod_yaml)
        self._api.create_namespaced_pod(body=pod_obj, namespace="qre")

    def run_dev(self, program_id, inputs_str):
        subprocess.call(['sh', 'scripts/runexecutordev.sh', program_id, inputs_str])
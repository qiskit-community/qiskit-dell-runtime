from kubernetes import client, config
import uuid
import yaml
import subprocess
import os



YAML = """
---
apiVersion: v1
kind: Pod
metadata:
  name: {pod_name}
  namespace: {namespace}
spec:
  containers:
    - name: {pod_name}
      image: harbor.dell.com/dojo-harbor/qre/executor
      env:
      - name: ORCH_HOST
        value: {orch_host}
      - name: PROGRAM_ID
        value: {program_id}
      - name: JOB_ID
        value: {job_id}
      - name: INPUTS_STR
        value: |
          {inputs_str}
  restartPolicy: Never
"""


class KubeClient():
    def __init__(self):
        if "DEV" in os.environ:
          self.run = self.run_dev
        else:
          config.load_incluster_config()
          self._api = client.CoreV1Api()
          self._namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

    def run(self, **options):
        program_id = options["program_id"]
        inputs_str = options["inputs_str"]
        job_id = options["job_id"]
        pod_name = options["pod_name"]
        orch_host = "http://qre-orchestrator"
        pod_yaml = YAML.format(pod_name=pod_name, namespace=self._namespace, inputs_str=inputs_str, orch_host=orch_host, program_id=program_id, job_id=job_id)
        pod_obj = yaml.safe_load(pod_yaml)
        self._api.create_namespaced_pod(body=pod_obj, namespace=self._namespace)

    def run_dev(self, **options):
        program_id = options["program_id"]
        inputs_str = options["inputs_str"]
        kafka_servers = options["kafka_servers"]
        kafka_topic = options["kafka_topic"]
        kafka_key = options["kafka_key"]
        subprocess.call(['sh', 'scripts/runexecutordev.sh', program_id, inputs_str, kafka_servers, kafka_topic, kafka_key])

    def cancel(self, pod_name):
        self._api.delete_namespaced_pod(pod_name, namespace=self._namespace)

    def get_pod_status(self, pod_name):
        podlist = self._api.list_namespaced_pod(self._namespace).items
        for pod in podlist:
          if pod.metadata.name == pod_name:
            return pod.status.phase
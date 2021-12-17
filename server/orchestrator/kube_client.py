from kubernetes import client, config
from kubernetes.client.rest import ApiException
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
      image: {image_repo}/{namespace}/qdr-executor
      env:
      - name: DATA_TOKEN
        value: {data_token}
      - name: MESSAGE_TOKEN
        value: {msg_token}
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
        data_token = options['data_token']
        msg_token = options['msg_token']
        image_repo = options['image_repo']
        orch_host = "http://qdr-orchestrator"
        pod_yaml = YAML.format(pod_name=pod_name, image_repo=image_repo, msg_token=msg_token, data_token=data_token, namespace=self._namespace, inputs_str=inputs_str, orch_host=orch_host, program_id=program_id, job_id=job_id)
        pod_obj = yaml.safe_load(pod_yaml)
        self._api.create_namespaced_pod(body=pod_obj, namespace=self._namespace)

    def cancel(self, pod_name):
        self._api.delete_namespaced_pod(pod_name, namespace=self._namespace)

    def get_pod_status(self, pod_name):
        podlist = self._api.list_namespaced_pod(self._namespace).items
        for pod in podlist:
          if pod.metadata.name == pod_name:
            return pod.status.phase

    def check_pod_existence(self, pod_name):
      resp = None
      try:
          resp = self._api.read_namespaced_pod(name=pod_name,namespace=self._namespace)
          return True
      except ApiException as e:
          if e.status != 404:
              print("Unknown error: %s" % e)
              return None
      if not resp:
          return False
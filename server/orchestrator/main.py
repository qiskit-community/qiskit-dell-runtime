import os
import flask
from flask import Flask, Response
import logging
import json
from logging.config import fileConfig
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
app = Flask(__name__)

from .kube_client import KubeClient
from .models import DBService, RuntimeProgram
from kafka import KafkaConsumer, TopicPartition

db_service = DBService()
kube_client = KubeClient()

path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
fileConfig(os.path.join(path, 'logging_config.ini'))
logger = logging.getLogger(__name__)
KAFKA_SERVERS = os.getenv("KAFKA_SERVERS")

@app.route('/program', methods=['POST'])
def upload_runtime_program():
    json_data = flask.request.json
    
    program = RuntimeProgram()
    program.program_id = json_data['program_id']
    program.name = json_data['name']
    program.program_metadata = json.dumps(json_data['program_metadata'])
    program.data = bytes(json_data['data'], 'utf-8')
    db_service.save_runtime_program(program)
    return (json_data['program_id'], 200)

@app.route('/program', methods=['GET'])
def programs():
    result = db_service.fetch_runtime_programs()
    logger.debug(f"GET /program: {result}")
    json_result = json.dumps(result)
    return Response(json_result, status=200, mimetype="application/json")

# this URL needs to be a lot more restrictive in terms of security
# 1. only available to internal call from other container
# 2. only allow fetch of data of assigned program
@app.route('/program/<program_id>/data', methods=['GET'])
def program_data(program_id):
    result = db_service.fetch_runtime_program_data(program_id)
    return Response(result, 200, mimetype="application/binary")

@app.route('/status', methods=['GET'])
def get_status():
    json_result = json.dumps(False)
    return Response(json_result, 200, mimetype="application/json")

@app.route('/program/<program_id>/job', methods=['POST'])
def run_program(program_id):
    inputs_str = flask.request.json

    job_id = generate_job_id()
    options = {
        "program_id": program_id,
        "inputs_str": inputs_str,
        "kafka_servers": KAFKA_SERVERS,
        "kafka_topic": job_id,
        "kafka_key": "0"
    }
    kube_client.run_dev(**options)
    # create job and return later
    return Response(job_id, 200, mimetype="application/json")

@app.route('/jobs/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    print(type(job_id))

    consumer = KafkaConsumer(bootstrap_servers="localhost:9092", group_id="0")
    partition = TopicPartition(job_id, 0)
    consumer.assign([partition])
    commoff = consumer.committed(partition)
    if commoff == None:
        consumer.seek_to_beginning()
    else:
        consumer.seek(partition, commoff)
    messages = []
    end_offsets = consumer.end_offsets([partition])
    for i in range(commoff, end_offsets[partition]):
        msg = next(consumer)
        messages.append(json.loads(msg.value))

    consumer.close()
    res_str = json.dumps(messages, cls=RuntimeEncoder)
    return Response(res_str, 200, mimetype="application/json")
    
def generate_job_id():
    return "1"
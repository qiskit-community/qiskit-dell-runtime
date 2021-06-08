import os
import flask
from flask import Flask, Response
import logging
import json
from logging.config import fileConfig

app = Flask(__name__)

from .kube_client import KubeClient
from .models import DBService, RuntimeProgram

db_service = DBService()
kube_client = KubeClient()

path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
fileConfig(os.path.join(path, 'logging_config.ini'))
logger = logging.getLogger(__name__)

@app.route('/program', methods=['POST'])
def upload_runtime_program():
    json_data = flask.request.json
    logger.debug(f'POST /program: {json_data}')
    
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

@app.route('/program/<program_id>/job', methods=['POST'])
def run_program(program_id):
    inputs_str = flask.request.json

    logger.debug(f'POST run program: {inputs_str}')
    
    kube_client.run_dev(program_id, inputs_str)
    # create job and return later
    return Response('', 200, mimetype="application/json")
    
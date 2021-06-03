import flask
from flask import Flask, Response
import logging
import json
from logging.config import fileConfig

app = Flask(__name__)

from .models import DBService, RuntimeProgram

db_service = DBService()

fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)

@app.route('/program', methods=['POST'])
def upload_runtime_program():

    
    json_data = flask.request.json
    logger.debug(f'POST /program: {json_data}')
    
    program = RuntimeProgram()
    program.program_id = json_data['program_id']
    program.name = json_data['name']
    if 'description' in json_data:
        program.description = json_data['description']
    program.data = bytes(json_data['data'], 'utf-8')
    db_service.save_runtime_program(program)
    return (json_data['program_id'], 200)

@app.route('/program', methods=['GET'])
def programs():
    result = db_service.fetch_runtime_programs()
    logger.debug(f"GET /program: {result}")
    json_result = json.dumps(result)
    return Response(json_result, status=200, mimetype="application/json")
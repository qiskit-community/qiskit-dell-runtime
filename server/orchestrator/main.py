import flask
from flask import Flask
import logging
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
    return ('', 200)

@app.route('/program', methods=['GET'])
def programs():
    return ([{'test': 'test1'}], 200)
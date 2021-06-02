import flask
from flask import Flask
import logging
from logging.config import fileConfig

app = Flask(__name__)

from .models import DBService

db_service = DBService()

fileConfig('logging_config.ini')
logger = logging.getLogger(__name__)

@app.route('/program', methods=['POST'])
def upload_runtime_program():
    logger.debug('POST /program')
    json_data = flask.request.json
    logger.debug(f'POST /program: {json_data}')
    # db_service.save_runtime_program()
    return ('', 200)

@app.route('/program', methods=['GET'])
def programs():
    return ([{'test': 'test1'}], 200)
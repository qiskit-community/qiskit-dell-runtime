import os
import flask
from flask import Flask, Response
import logging
import json
from logging.config import fileConfig
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
app = Flask(__name__)
import uuid
from datetime import datetime
import io
import shutil

from .kube_client import KubeClient
from .models import DBService, RuntimeProgram, Job

db_service = DBService()
kube_client = KubeClient()

ACTIVE="Active"
INACTIVE="Inactive"
CREATING="Creating"
RUNNING = "Running"
COMPLETED = "Completed"
FAILED = "Failed"
CANCELED = "Canceled"
POD_ERROR = "Error"
POD_SUCCESS = "Succeeded"
POD_UNKNOWN = "Unknown"
POD_PENDING = "Pending"

STATUS_PRECEDENCE = [COMPLETED, FAILED, CANCELED, POD_ERROR, POD_SUCCESS, RUNNING, POD_PENDING, CREATING]


path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-1])
fileConfig(os.path.join(path, 'logging_config.ini'))
logger = logging.getLogger(__name__)

def random_id():
    new_uuid = uuid.uuid4()
    return str(new_uuid)[-12:]

@app.route('/program', methods=['POST'])
def upload_runtime_program():
    # json_data = json.loads(flask.request.form)
    logger.debug(f"POST /program")


    # Ensure that every entry in DB is "valid" - i.e. that there's something
    # for each field even if it's empty string/dict.
    # Also do error checking on client side to make sure that even if 
    # somethin sneaks in it doesn't break the funcs

    logger.debug(f'{flask.request.form}')
    program = RuntimeProgram()
    new_id = random_id()
    program.program_id = new_id
    program.name = flask.request.form.get("name") if flask.request.form.get("name") else new_id
    program.data_type = flask.request.form.get("data_type") if flask.request.form.get("data_type") else "STRING"
    program.program_metadata = flask.request.form.get("program_metadata") if flask.request.form.get("program_metadata") else "{}"
    
    logger.debug(f'form data type: {program.data_type}')

    if not flask.request.form.get("data"):
        logger.debug("Reading directory")
        file_list = flask.request.files
        logger.debug(f"file list: {file_list}")
        for z in file_list.values():
            logger.debug("reading file")
            program.data = z.read()
    else:
        program.data = bytes(flask.request.form.get("data"), 'utf-8')

    program.status = ACTIVE
    db_service.save_runtime_program(program)
    return (new_id, 200)

@app.route('/program/<program_id>/update', methods=['POST'])
def update_runtime_program(program_id):
    form_data = flask.request.form
    
    name = None
    data = None
    data_type = None
    program_metadata = None
    if form_data.get("name"):
        name = form_data.get("name")

    if not form_data.get("data"):
        logger.debug("Reading directory")
        file_list = flask.request.files
        logger.debug(f"file list: {file_list}")
        for z in file_list.values():
            logger.debug("reading file")
            data = z.read()
    else:
        data = bytes(form_data.get("data"), 'utf-8')

    if form_data.get("data_type"):
        data_type = form_data.get("data_type")
    if form_data.get("program_metadata"):
        program_metadata = form_data.get("program_metadata")
    
    db_service.update_runtime_program(program_id, name, data, program_metadata, data_type)
    return ("", 200)

@app.route('/program', methods=['GET'])
def programs():
    result = db_service.fetch_runtime_programs()
    logger.debug(f"GET /program: {result}")
    json_result = json.dumps(result)
    return Response(json_result, status=200, mimetype="application/binary")

# this URL needs to be a lot more restrictive in terms of security
# 1. only available to internal call from other container
# 2. only allow fetch of data of assigned program
@app.route('/program/<program_id>/data', methods=['GET'])
def program_data(program_id):
    result = db_service.fetch_runtime_program_data(program_id)

    bytestream = io.BytesIO(result['data'])

    content_type = "application/zip" if result['data_type'] == "DIR" else "text/plain"
    logger.debug(f'get program {program_id} data: content type: {content_type}')

    return flask.send_file(bytestream, mimetype=content_type)

@app.route('/program/<program_id>/delete', methods=['GET'])
def delete_program(program_id):
    db_service.delete_runtime_program(program_id)
    return Response(None, 200, mimetype="application/binary")

@app.route('/status', methods=['GET'])
def get_status():
    json_result = json.dumps(False)
    return Response(json_result, 200, mimetype="application/json")

@app.route('/program/<program_id>/job', methods=['POST'])
def run_program(program_id):
    inputs_str = flask.request.json

    job_id = random_id()
    pod_name = "qre-" + str(uuid.uuid1())[-24:]    
    options = {
        "program_id": program_id,
        "inputs_str": inputs_str,
        "job_id": job_id,
        "pod_name": pod_name
    }

    db_job = Job()
    db_job.job_id = job_id
    db_job.program_id = program_id
    db_job.job_status = CREATING
    db_job.pod_name = pod_name
    db_service.save_job(db_job)

    kube_client.run(**options)
    # create job and return later
    return Response(job_id, 200, mimetype="application/json")

@app.route('/job/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    try:
        logger.debug(f'GET /job/{job_id}/status')
        update_pod_status(job_id)
        result = db_service.fetch_status(job_id)

        # Returns the higher precedent final status (i.e. job completed > pod failed/succeeded)
        return Response(higherStatus(result), 200, mimetype="application/binary")

# '''
#     job status | pod status
#     -----------------------
#     Creating     Pending
#     Creating     Succeeded
#     Creating     Failed
#     Creating     Running
#     Running      Running
#     Running      Failed
#     Completed    Running
#     Completed    Failed
#     Completed    Succeeded
#     Failed       Failed
#     Failed       Succeeded
#     Canceled     Succeeded/Failed


#     Precedence of job/pod status to return to client:
#     -------------------------------------------------
#     Job completed/failed/canceled FINAL
#     Pod Failed -- way to tell why? FINAL
#     Pod succeeded -- it's done? 
#     Job running/pod running?
#     Pod pending/unknown
#     Job creating
# '''

    except:
        return Response("", 204, mimetype="application/binary")

@app.route('/job/<job_id>/status', methods=['POST'])
def update_job_status(job_id):
    status = flask.request.json
    logger.debug(f"GET /job/{job_id}/status: {status}")

    db_service.update_job_status(job_id, status)
    return ("", 200)

@app.route('/job/<job_id>/cancel', methods=['GET'])
def cancel_job(job_id):
    update_pod_status(job_id)
    status = db_service.fetch_status(job_id)
    logger.debug(f"GET /job/{job_id}/cancel")
    if isFinal(status):
        return ("Job no longer running", 204)
    else:
        try:
            pod_name = db_service.fetch_pod_name(job_id)
            kube_client.cancel(pod_name)
            db_service.update_job_status(job_id, CANCELED)
            return ("", 200)
        except:
            return ("Job no longer running", 204)

# TODO check for runtime to make sure only executor 
# for this specific job can call this URL 
@app.route('/job/<job_id>/message', methods=['POST'])
def add_message(job_id):
    data = flask.request.data
    db_service.save_message(job_id, data)
    return ("", 200)

# TODO determine whether kubernetes pod is launched


@app.route('/job/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    try:
        logger.debug(f"GET /job/{job_id}/results")
        result = db_service.fetch_messages(job_id, None)
        return Response(json.dumps({"messages": result}), 200, mimetype="application/binary")
    except:
        return Response(json.dumps({"messages": []}), 204, mimetype="application/binary")

@app.route('/job/<job_id>/results/<timestamp>', methods=['GET'])
def get_new_job_results(job_id, timestamp):
    try:
        logger.debug(f"GET /job/{job_id}/results/{timestamp}")
        tstamp = datetime.fromisoformat(timestamp)
        result = db_service.fetch_messages(job_id, tstamp)
        return Response(json.dumps({"messages": result}), 200, mimetype="application/binary")
    except:
        return Response(json.dumps({"messages": []}), 204, mimetype="application/binary")

@app.route('/job/<job_id>/delete_message', methods=['GET'])
def delete_message(job_id):
    db_service.delete_message(job_id)
    return Response(None, 200)

def update_pod_status(job_id):
    pod_name = db_service.fetch_pod_name(job_id)
    pod_status = kube_client.get_pod_status(pod_name)
    if pod_status == FAILED:
        pod_status = POD_ERROR

    db_service.update_pod_status(job_id, pod_status)

def isFinal(status):
    if STATUS_PRECEDENCE.index(status['job_status']) < STATUS_PRECEDENCE.index(POD_ERROR):
        return status['job_status']
    elif STATUS_PRECEDENCE.index(status['pod_status']) < STATUS_PRECEDENCE.index(RUNNING):
        return status['pod_status']
    else:
        return None

def higherStatus(status):
    return status['job_status'] if STATUS_PRECEDENCE.index(status['job_status']) <= STATUS_PRECEDENCE.index(status['pod_status']) else status['pod_status']
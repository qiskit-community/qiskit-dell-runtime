import os
import flask
from flask import Flask, Response, session
from flask_session import Session
import logging
import json
from logging.config import fileConfig
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit_emulator import EmulatorProvider
import requests
import waitress

app = Flask(__name__)
import uuid
from datetime import datetime
import io
import shutil

from kube_client import KubeClient
from models import DBService, RuntimeProgram, Job, User

emulator_provider = EmulatorProvider()

db_service = DBService()
kube_client = KubeClient()

#TODO: Implement logic for when there is not SSO attached.
#      It's probable that some folks won't want it?

#TODO: Export to environment variables, not hard-coded strs.
app.config["SECRET_KEY"] = os.getenv("SSO_SECRET_KEY")
app.config["SESSION_TYPE"] = os.getenv("SSO_SESSION_TYPE")
TOKEN_URL = os.getenv("SSO_TOKEN_URL")
AUTH_URL = os.getenv("SSO_AUTH_URL")
INFO_URL = os.getenv("SSO_INFO_URL")

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

pending_logins = {}

Session(app)

def random_id():
    new_uuid = uuid.uuid4()
    return str(new_uuid)[-12:]

@app.route('/program', methods=['POST'])
def upload_runtime_program():
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code
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
    program.user_id = db_service.fetch_user_id(user_name)
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

    #TODO: Refactor into function
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_program_owner(program_id)):
        return f"User is not authorized to access program {program_id}", 401
    
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
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code
    result = db_service.fetch_runtime_programs(session["user_id"])
    logger.debug(f"GET /program: {result}")
    json_result = json.dumps(result)
    return Response(json_result, status=200, mimetype="application/binary")

# this URL needs to be a lot more restrictive in terms of security
# 1. only available to internal call from other container
# 2. only allow fetch of data of assigned program
# 3. no way to associate with user like everything else
@app.route('/program/<program_id>/data', methods=['GET'])
def program_data(program_id):
    result = db_service.fetch_runtime_program_data(program_id)

    bytestream = io.BytesIO(result['data'])

    content_type = "application/zip" if result['data_type'] == "DIR" else "text/plain"
    logger.debug(f'get program {program_id} data: content type: {content_type}')

    return flask.send_file(bytestream, mimetype=content_type)

@app.route('/program/<program_id>/delete', methods=['GET'])
def delete_program(program_id):
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_program_owner(program_id)):
        return f"User is not authorized to delete program {program_id}", 401

    db_service.delete_runtime_program(program_id)
    return Response(None, 200, mimetype="application/binary")

@app.route('/status', methods=['GET'])
def get_status():
    json_result = json.dumps(False)
    return Response(json_result, 200, mimetype="application/json")

@app.route('/backends', methods=['GET'])
def get_backends():
    backends = emulator_provider.runtime.backends()
    result = []
    for backend in backends:
        backend_config = backend.configuration()
        result.append({
            'name': backend_config.backend_name,
            'backend_name': backend_config.backend_name,
            'description': backend_config.description,
            'n_qubits': backend_config.n_qubits,
            'basis_gates': backend_config.basis_gates
        })
    json_result = json.dumps(result)
    return Response(json_result, 200, mimetype="application/json")

@app.route('/program/<program_id>/job', methods=['POST'])
def run_program(program_id):
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_program_owner(program_id)):
        return f"User is not authorized to delete program {program_id}", 401

    inputs_str = flask.request.json

    job_id = random_id()
    pod_name_dupe = True
    while pod_name_dupe:
        pod_name = "qre-" + str(uuid.uuid4())[-24:]
        pod_name_dupe = kube_client.check_pod_existence(pod_name)
        logger.debug(f"pod {pod_name} exists: {pod_name_dupe}")
        if pod_name_dupe == None:
            return "Kubernetes error occurred", 500  

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
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_job_owner(job_id)):
        return f"User is not authorized to get job status for {job_id}", 401

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

# Need to be sure that this is coming from container, not some goober
@app.route('/job/<job_id>/status', methods=['POST'])
def update_job_status(job_id):
    status = flask.request.json
    logger.debug(f"GET /job/{job_id}/status: {status}")

    db_service.update_job_status(job_id, status)
    return ("", 200)

@app.route('/job/<job_id>/cancel', methods=['GET'])
def cancel_job(job_id):
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_job_owner(job_id)):
        return f"User is not authorized to cancel job {job_id}", 401

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



@app.route('/job/<job_id>/results', methods=['GET'])
def get_job_results(job_id):
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_job_owner(job_id)):
        return f"User is not authorized to get results for {job_id}", 401

    try:
        logger.debug(f"GET /job/{job_id}/results")
        result = db_service.fetch_messages(job_id, None)
        return Response(json.dumps({"messages": result}), 200, mimetype="application/binary")
    except:
        return Response(json.dumps({"messages": []}), 204, mimetype="application/binary")

@app.route('/job/<job_id>/results/<timestamp>', methods=['GET'])
def get_new_job_results(job_id, timestamp):
    user_name, code = is_authenticated()
    if code != 200:
        return "User is not authenticated", code

    if not (session["user_id"] == db_service.fetch_job_owner(job_id)):
        return f"User is not authorized to get results for {job_id}", 401
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


@app.route("/callback/<attempt_id>", methods=["GET", "POST"])
def callback(attempt_id):
    logger.debug("Hit Callback")
    pending_logins[attempt_id] = "https" + flask.request.url[4:]
    
    return "<html><head><script>window.close();</script></head></html>"

@app.route("/tokeninfo/<attempt_id>", methods=["GET", "POST"])
def get_token_info(attempt_id):
    logger.debug("Hit Get Token Info")
    if pending_logins[attempt_id] is not None:
        urls = json.dumps({"cb_url": pending_logins[attempt_id], "token_url": TOKEN_URL})
        del pending_logins[attempt_id]
        return Response(urls, 200, mimetype="application/binary")
    else:
        return Response(None, 204)

@app.route("/login", methods=["GET", "POST"])
def login():
    logger.debug("Hit Login")
    id = random_id()
    pending_logins[id] = None
    # Eventually this will pull SSO login link from env vars
    return Response(json.dumps({"auth_url": AUTH_URL, "id": id}), 200, mimetype="application/binary")



@app.route("/authenticate", methods=["POST"])
def authenticate():
    logger.debug("Hit Authenticate")
    req_json = flask.request.json
    token = req_json["token"]

    headers = {"Authorization": "Bearer" + token}
    resp = requests.get(
        INFO_URL, headers=headers)
    json_resp = resp.json()

    if "error" in json_resp.keys():
        return "Invalid Token", 401

    username = json_resp["user_name"]
    session["user_name"] = username

    user_id = db_service.fetch_user_id(username)
    if not user_id:
        new_user = User()
        new_user.user_name = username
        db_service.save_user(new_user)
        user_id = db_service.fetch_user_id(username)

    session["user_id"] = user_id

    print("User logged in: {}".format(session["user_name"]))
    return username, 200

@app.route("/is_authenticated", methods=["GET"])
def is_authenticated():
    if not session.get("user_name"):
        return "Not authenticated", 401
    return session.get("user_name"), 200


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

if __name__=="__main__":
    waitress.serve(app, host='0.0.0.0', port=8080)


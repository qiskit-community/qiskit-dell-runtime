from qiskit_emulator import EmulatorProvider
from qiskit_emulator.emulator_runtime_job import EmulatorRuntimeJob
import unittest
from qiskit import QuantumCircuit, execute, transpile
from qiskit_emulator import EmulatorProvider
from qiskit.providers import JobStatus
import unittest
from urllib.parse import urljoin
import os, requests
import json
# import pytest_mysql
from server.orchestrator.models import DBService, Job, User, RuntimeProgram, Message, db_service
import pytest
from datetime import datetime
from time import sleep
ACCEPTANCE_URL = os.getenv('ACCEPTANCE_URL')
RUNTIME_PROGRAM = """
from qiskit.compiler import transpile, schedule


def main(
    backend,
    user_messenger,
    circuits,
    **kwargs,
):

    user_messenger.publish({'results': 'intermittently'})

    circuits = transpile(
        circuits,
    )

    if not isinstance(circuits, list):
        circuits = [circuits]

    # Compute raw results
    result = backend.run(circuits, **kwargs).result()

    user_messenger.publish({'results': 'finally'})
    user_messenger.publish(result.to_dict(), final=True)
    print("job complete successfully")
"""
RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}

# mysql_proc = pytest_mysql.factories.mysql_proc(port=3307)


def test_fetch_program_owner():
    db_service = DBService()

    rp = RuntimeProgram()
    rp.program_id = "12"
    rp.user_id = 1
    rp.name = "test program"
    rp.data = b'test program'
    rp.program_metadata = "meta"
    rp.status = 'Active'
    rp.data_type = "DIR"

    db_service.save_runtime_program(rp)

    assert(db_service.fetch_program_owner("12") == 1)

def test_fetch_job_owner():
    db_service = DBService()

    rp = RuntimeProgram()
    rp.program_id = "12"
    rp.user_id = 1
    rp.name = "test program"
    rp.data = b'test program'
    rp.program_metadata = "meta"
    rp.status = 'Active'
    rp.data_type = "DIR"

    db_service.save_runtime_program(rp)

    jb = Job()
    jb.job_id = "123"
    jb.program_id = "12"
    jb.job_status = "Completed"
    jb.pod_name = "pod"
    jb.pod_status = "Running"
    jb.data_token = "USED"

    db_service.save_runtime_program(jb)


    assert(db_service.fetch_job_owner("123") == 1)

def test_see_programs():
    db_service = DBService()

    rp = RuntimeProgram()
    rp.program_id = "14"
    rp.user_id = 1
    rp.name = "test program"
    rp.data = b'test program'
    rp.program_metadata = "meta"
    rp.status = 'Active'
    rp.data_type = "DIR"

    db_service.save_runtime_program(rp)

    rp = RuntimeProgram()
    rp.program_id = "13"
    rp.user_id = 1
    rp.name = "test program"
    rp.data = b'test program'
    rp.program_metadata = "meta"
    rp.status = 'Active'
    rp.data_type = "DIR"

    db_service.save_runtime_program(rp)

    rp = RuntimeProgram()
    rp.program_id = "12"
    rp.user_id = 2
    rp.name = "test program"
    rp.data = b'test program'
    rp.program_metadata = "meta"
    rp.status = 'Active'
    rp.data_type = "DIR"

    db_service.save_runtime_program(rp)

    assert(len(db_service.fetch_runtime_programs(1)) == 2)

def test_use_job_token():
    db_service = DBService()

    jb = Job()
    jb.job_id = "123"
    jb.program_id = "12"
    jb.job_status = "Completed"
    jb.pod_name = "pod"
    jb.pod_status = "Running"
    jb.data_token = "token"

    db_service.save_runtime_program(jb)

    db_service.use_job_token("123")

    assert(db_service.fetch_job_token("123") == "USED")

def test_fetch_messages_timestamp():
    db_service = DBService()

    db_service.save_message("123", "this message")

    msgs = db_service.fetch_messages("123", None)

    assert(len(msgs) == 1)
    ts = datetime.fromisoformat(msgs[0]["timestamp"])

    sleep(2)

    db_service.save_message("123", "another message")

    newmsgs = db_service.fetch_messages("123", ts)

    assert(len(newmsgs) == 1)


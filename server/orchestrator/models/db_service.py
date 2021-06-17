
from .base import Session, engine, Base
from .runtime_program_model import RuntimeProgram
from .message_model import Message
from sqlalchemy.orm import load_only
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

ACTIVE="Active"
INACTIVE="Inactive"

class DBService():
    def __init__(self):
        Base.metadata.create_all(engine)

    def save_message(self, job_id, data):
        message = Message()
        message.job_id = job_id
        message.data = data
        message.creation_date = datetime.now()
        session = Session()
        try:
            session.add(message)
            session.commit()
        finally:
            session.close()

    def save_runtime_program(self, runtime_program: RuntimeProgram):
        session = Session()
        try:
            session.add(runtime_program)
            session.commit()
        finally:
            session.close()

    def delete_runtime_program(self, program_id):
        session = Session()
        try:
            prog = session.query(RuntimeProgram).filter_by(program_id=program_id).one()
            logger.debug(f"Found {prog} with status {prog.status}")
            setattr(prog, "status", INACTIVE)       
            session.commit()
        finally:
            session.close()

    def fetch_message(self, job_id):
        try:
            session = Session()
            fields = ['data']
            job = session.query(Message).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.data
        finally:
            session.close()

    def delete_message(self, job_id):
        try:
            session = Session()
            jobs = session.query(Message).filter_by(job_id=job_id).all()
            for job in jobs:
                session.delete(job)
            session.commit()
            return
        finally:
            session.close()
    
    def fetch_runtime_program_data(self, program_id):
        try:
            session = Session()
            fields = ['data']
            program = session.query(RuntimeProgram).filter_by(program_id=program_id).filter_by(status=ACTIVE).options(load_only(*fields)).one()
            return program.data
        finally:
            session.close()

    def fetch_runtime_programs(self):
        result = []
        # programs = RuntimeProgram.query.all()
        try:
            session = Session()
            fields = ['program_id', 'name', 'program_metadata']
            programs = session.query(RuntimeProgram).filter_by(status=ACTIVE).options(load_only(*fields)).all()
            logger.debug(f"Found {len(programs)} programs")
            for program in programs:
                result.append({
                    'program_id': program.program_id,
                    'name': program.name,
                    'program_metadata': program.program_metadata
                })
            return result
        finally:
            session.close()



# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# Copyright 2021 Dell (www.dell.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .base import Session, engine, Base
from .runtime_program_model import RuntimeProgram
from .message_model import Message
from .job_model import Job
from .user_model import User
from sqlalchemy.orm import load_only
from datetime import datetime
import logging
import json


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

    def save_job(self, job: Job):
        session = Session()
        try:
            session.add(job)
            session.commit()
        finally:
            session.close()

    def save_user(self, user: User):
        session = Session()
        try:
            session.add(user)
            session.commit()
        finally:
            session.close()
    
    def fetch_job_owner(self, job_id):
        try:
            session = Session()
            fields = ['program_id']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            logger.debug(f'program id of job {job_id} : {job.program_id}')
            return self.fetch_program_owner(job.program_id)
        finally:
            session.close()

    def fetch_program_owner(self, program_id):
        try:
            session = Session()
            fields = ['user_id']
            program = session.query(RuntimeProgram).filter_by(program_id=program_id).options(load_only(*fields)).one()
            logger.debug(f'user id of program {program_id} : {program.user_id}')
            return program.user_id
        finally:
            session.close()

    def update_runtime_program(self, program_id, name, data, program_metadata, data_type):
        session = Session()
        try:
            prog = session.query(RuntimeProgram).filter_by(program_id=program_id).one()
            if name:
                setattr(prog, "name", name)
            if data:
                setattr(prog, "data", data)
            if type:
                setattr(prog, "data_type", data_type)
            if program_metadata:
                pm = json.loads(program_metadata)
                meta = json.loads(prog.program_metadata)
                for (key,value) in pm.items():
                    if value:
                        meta[key] = value
                meta_str = json.dumps(meta)
                setattr(prog, "program_metadata", meta_str)
            session.commit()
        finally:
            session.close()

    def update_pod_status(self, job_id, status):
        session = Session()
        try:
            job = session.query(Job).filter_by(job_id=job_id).one()
            setattr(job, "pod_status", status)
            session.commit()
        finally:
            session.close()
    
    def update_job_status(self, job_id, status):
        session = Session()
        try:
            job = session.query(Job).filter_by(job_id=job_id).one()
            setattr(job, "job_status", status)
            session.commit()
        finally:
            session.close()

    def fetch_pod_name(self, job_id):
        try:
            session = Session()
            fields = ['pod_name']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.pod_name
        finally:
            session.close()

    def fetch_user_id(self, username):
        try:
            session = Session()
            fields = ['id']
            user = session.query(User).filter_by(user_name=username).options(load_only(*fields)).one()
            return user.id
        except:
            return None
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

    def fetch_messages(self, job_id, timestamp):
        try:
            session = Session()
            fields = ['data', 'creation_date']
            all_messages = session.query(Message).filter_by(job_id=job_id).options(load_only(*fields)).all()
            new_messages = []
            for msg in all_messages:
                if not timestamp or timestamp < msg.creation_date:
                    new_messages.append({"data": json.loads(msg.data), "timestamp": str(msg.creation_date)})
            return new_messages
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
            fields = ['data', 'data_type']
            program = session.query(RuntimeProgram).filter_by(program_id=program_id).filter_by(status=ACTIVE).options(load_only(*fields)).one()
            resp = {"data": program.data, "data_type": program.data_type}
            return resp
        finally:
            session.close()

    def fetch_runtime_programs(self, user_id):
        result = []
        # programs = RuntimeProgram.query.all()
        try:
            session = Session()
            fields = ['program_id', 'name', 'program_metadata']
            programs = session.query(RuntimeProgram).filter_by(status=ACTIVE).filter_by(user_id=user_id).options(load_only(*fields)).all()
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

    def fetch_status(self, job_id):
        try:
            session = Session()
            fields = ['job_status', 'pod_status']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return {'job_status': job.job_status, 'pod_status': job.pod_status}
        finally:
            session.close()

    def fetch_job_token(self, job_id):
        try:
            session = Session()
            fields = ['data_token']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.data_token
        finally:
            session.close()

    def use_job_token(self, job_id):
        try:
            session = Session()
            job = session.query(Job).filter_by(job_id=job_id).one()
            setattr(job, "data_token", "USED")
            session.commit()
        finally:
            session.close()

    def fetch_msg_token(self, job_id):
        try:
            session = Session()
            fields = ['msg_token']
            job = session.query(Job).filter_by(job_id=job_id).options(load_only(*fields)).one()
            return job.msg_token
        finally:
            session.close()

    def use_msg_token(self, job_id):
        try:
            session = Session()
            job = session.query(Job).filter_by(job_id=job_id).one()
            setattr(job, "msg_token", "USED")
            session.commit()
        finally:
            session.close()



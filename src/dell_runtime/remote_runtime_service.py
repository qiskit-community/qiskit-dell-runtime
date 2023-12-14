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


import shutil
from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple, Any
from urllib.parse import urljoin
import requests
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers import ProviderV1 as Provider
import logging
import copy
import json
import os

import time
from requests_oauthlib import OAuth2Session
from .emulator_runtime_job import EmulatorRuntimeJob
import webbrowser

logger = logging.getLogger(__name__)

DIR = "DIR"
STRING = "STRING"
TOKEN = os.getenv("TOKEN")
QDR_ID = os.getenv("QDR_ID")

session = requests.Session()

class RemoteRuntimeService():
    def __init__(self, provider: Provider, host: str) -> None:
        self.provider = provider
        self.host = host
        status_response = self._get("/status")
        if not (status_response[0] == 200):
            raise Exception("Wrong status code from host: {}".format(self.host))

        sso_enabled = json.loads(self._get("/sso_enabled")[2])
        if not sso_enabled:
            if not QDR_ID:
                self.new_non_sso_user()
            else:
                res = self._get(f"/existing_user/{QDR_ID}")
                if res[0] >= 300:
                    raise Exception(f"Error logging in existing user: Code {res[0]}")
                elif json.loads(res[2]) != True:
                    print(f"User {QDR_ID} not found. Creating new user!")
                    self.new_non_sso_user()
        else:
            if not TOKEN:
                access_token = self.get_new_token()
            else: 
                access_token = TOKEN

            try:
                resp = self.login_with_token(access_token)
                if not resp[0] == 200: 
                    access_token = self.get_new_token()
                    resp = self.login_with_token(access_token)
                    if not resp[0] == 200:
                        raise Exception("Unable to Authenticate with SSO")
            except Exception as e:
                print('Hit exception', e)
                # return False
        

        self._programs = {}
        self._backends = {}

    def _post(self, path, data):
        url = urljoin(self.host, path)
        logger.debug(f"POST {url}: {data}")
        req = session.post(url, json=data)

        res = (req.status_code, req.reason, req.text)
        logger.debug(f"POST {url} RESPONSE: {res}")
        return res

    def _post_program(self, path, data, files: Optional[Dict] = None):
        url = urljoin(self.host, path)
        logger.debug(f"POST {url}: {data}")
        req = session.post(url, data=data, files=files)

        res = (req.status_code, req.reason, req.text)
        logger.debug(f"POST {url} RESPONSE: {res}")
        return res
    
    def _get(self, path):
        url = urljoin(self.host, path)
        logger.debug(f"GET {url}")
        req = session.get(url)
        res = (req.status_code, req.reason, req.text)
        logger.debug(f"GET {url} RESPONSE: {res}")
        return res

    def backends(self, refresh: bool = False):
        if refresh or (self._backends == {}):
            res = self._get('/backends')
            if res[0] != 200:
                logger.error(f'Cannot fetch backends: {res[0]}')
            else:
                backend_list = json.loads(res[2])
                self._backends = backend_list
        return self._backends
        
    def programs(self, refresh: bool = False):
        if refresh or (self._programs == {}):
            res = self._get('/program')
            if res[0] != 200:
                logger.error(f'Cannot fetch programs: {res[0]}')
            else:
                proglist = json.loads(res[2])
                self._programs = {}
                for prog in proglist:
                    program_metadata = json.loads(prog['program_metadata'])
                    if not program_metadata:
                        program_metadata = {}
                    self._programs[prog['program_id']] = RuntimeProgram(program_name=prog['name'], 
                                                        program_id=prog['program_id'], 
                                                        **program_metadata)

        return self._programs


    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        if (not refresh) and program_id in self._programs:
            return self._programs[program_id]
        else:
            self.programs(refresh=True)
            if program_id in self._programs:
                return self._programs[program_id]
            else:
                return None

    # copied from IBMQ Provider
    def pprint_programs(self, refresh: bool = False) -> None:
        """Pretty print information about available runtime programs.

        Args:
            refresh: If ``True``, re-query the server for the programs. Otherwise
                return the cached value.
        """
        programs = self.programs(refresh).values()
        for prog in programs:
            print("="*50)
            print(str(prog))

    def upload_program(
            self,
            data: Union[bytes, str],
            program_id: Optional[str] = None,
            metadata: Optional[Union[Dict, str]] = None,
    ) -> str:

        # We removed this because the orchestrator assigns the actual program ID.
        # That is now the name in the DB, as well, if none is provided.
        
        # careful of hash collision
        # if program_id == None:
        #     program_id = hex(hash((data, name, version)))[-16:]
        #     if name is None:
        #         name = program_id


        metadata = self._merge_metadata(metadata=metadata)

        prog_name = None if 'name' not in metadata else metadata.pop('name'),
        print(metadata)
        str_metadata = json.dumps(metadata)

        data_type = STRING

        req_body = {
            'data': None,
            'name': prog_name,
            'data_type': data_type,  
            'program_metadata': str_metadata
        }

        if os.path.isdir(data):
            logger.debug(f"Have directory: {data}")
            dirsplit = data.split("/")
            if dirsplit[-1] == "":
                if not os.path.isfile(data + "program.py"):
                    raise Exception("program.py is required for directory upload")
                if os.path.isfile(data + "executor.py") or os.path.isfile(data + "params.json"):
                    raise Exception("executor.py and params.json are unallowable names in directory")
                zipname = dirsplit[-2]
            else:
                if not os.path.isfile(data + "/program.py"):
                    raise Exception("program.py is required for directory upload")
                if os.path.isfile(data + "/executor.py") or os.path.isfile(data + "/params.json"):
                    raise Exception("executor.py and params.json are unallowable names in directory")
                zipname = dirsplit[-1]

            zipped = shutil.make_archive(zipname, "zip", data)
            logger.debug(f"made: {zipped}")
            filename = zipped.split("/")[-1]
            # self._program_data[program_hash] = (zipped, DIR)

            req_body['data_type'] = DIR
            with open(zipped, "rb") as z:
                res = self._post_program('/program', data=req_body, files={filename: z})
            os.remove(zipped)
        elif os.path.isfile(data):
            filename = data.split("/")[-1]

            with open(data, "rb") as f:
                res = self._post_program('/program', data=req_body, files={filename: f})
        else:
            req_body['data'] = data
            res = self._post_program('/program', data=req_body)

        
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
        else:
            logger.debug(f"Received program_id: {res[2]}")
            return res[2]

    def delete_program(
        self,
        program_id: str,
    ) -> str:
        res = self._get(f'/program/{program_id}/delete')
        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
            return False
        else:
            logger.debug(f"Deleted {program_id} successfully")
            return True
    
    def run(
            self,
            program_id: str,
            options: Dict,
            inputs: Dict,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Type[ResultDecoder]] = None
    ) -> EmulatorRuntimeJob:
        serialized_inputs = json.dumps(inputs, cls=RuntimeEncoder)
        res = self._post('/program/{}/job'.format(program_id), serialized_inputs)
        if (res[0] != 200):
            raise Exception('Something went bad')
        job = EmulatorRuntimeJob(res[2], self.host, session=session, callback = callback)
        return job

    def update_program(
            self,
            program_id: str,

            # We include data as a field even though we don't get it
            # back from program() as part of RuntimeProgram.
            # We are assuming it gets updated.

            data: Optional[Union[bytes, str]] = None,
            metadata: Optional[Union[Dict, str]] = None,
            name: Optional[str] = None,
            max_execution_time: Optional[int] = None,
            description: Optional[str] = None,
            spec: Optional[Dict] = None,
    ):
        metadata = self._merge_metadata(metadata=metadata, name=name, max_execution_time=max_execution_time, description=description, spec=spec)

        prog_name = None if 'name' not in metadata else metadata.pop('name')
        str_metadata = json.dumps(metadata)

        req_body = {
            'program_id': program_id,
            'data': None,
            'name': prog_name,
            'data_type': None,  
            'program_metadata': str_metadata
        }

        if data:
            req_body['data_type'] = STRING

            if os.path.isdir(data):
                logger.debug(f"Have directory: {data}")
                dirsplit = data.split("/")
                if dirsplit[-1] == "":
                    if not os.path.isfile(data + "program.py"):
                        raise Exception("program.py is required for directory upload")
                    if os.path.isfile(data + "executor.py") or os.path.isfile(data + "params.json"):
                        raise Exception("executor.py and params.json are unallowable names in directory")
                    zipname = dirsplit[-2]
                else:
                    if not os.path.isfile(data + "/program.py"):
                        raise Exception("program.py is required for directory upload")
                    if os.path.isfile(data + "/executor.py") or os.path.isfile(data + "/params.json"):
                        raise Exception("executor.py and params.json are unallowable names in directory")
                    zipname = dirsplit[-1]

                zipped = shutil.make_archive(zipname, "zip", data)
                logger.debug(f"made: {zipped}")
                filename = zipped.split("/")[-1]
                # self._program_data[program_hash] = (zipped, DIR)

                req_body['data_type'] = DIR
                with open(zipped, "rb") as z:
                    res = self._post_program(f'/program/{program_id}/update', data=req_body, files={filename: z})
                os.remove(zipped)
            elif os.path.isfile(data):
                filename = data.split("/")[-1]

                with open(data, "rb") as f:
                    res = self._post_program(f'/program/{program_id}/update', data=req_body, files={filename: f})
            else:
                req_body['data'] = data
                res = self._post_program(f'/program/{program_id}/update', data=req_body)
        else:
            res = self._post_program(f'/program/{program_id}/update', data=req_body)

        if res[0] != 200:
            logger.error(f"Received {res[0]} as status code")
            return False
        else:
            logger.debug(f"Successfully updated program {program_id}")
            return True

    # copied from IBM runtime service
    def _merge_metadata(
            self,
            metadata: Optional[Dict] = None,
            **kwargs: Any
    ) -> Dict:
        """Merge multiple copies of metadata.
        Args:
            metadata: Program metadata.
            **kwargs: Additional metadata fields to overwrite.
        Returns:
            Merged metadata.
        """
        merged = {}
        metadata = metadata or {}
        metadata_keys = ['name', 'max_execution_time', 'description', 'spec']
        for key in metadata_keys:
            if kwargs.get(key, None) is not None:
                merged[key] = kwargs[key]
            elif key in metadata.keys():
                merged[key] = metadata[key]
        return merged
    def login_with_token(self, access_token):
        token_obj = {
            "token": access_token,
        }
        return self._post("/authenticate", data=token_obj)

    def get_new_token(self):
        res = self._get("/login")
        login_info = json.loads(res[2])
        client_id = login_info['client_id']
        client_secret = login_info['client_secret']
        scope = [x.strip() for x in login_info["scope"].split(',')]
        redirect_uri = urljoin(self.host, f"/callback")
        global oauth 
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)


        authorization_url, state = oauth.authorization_url(
            login_info["auth_url"]
        )
        print(f"Opening webpage {authorization_url}\n")
        
        webbrowser.open_new(authorization_url)

        urls = {}
        while not urls:
            res = self._get(f"/tokeninfo/{state}")
            if res[0] == 200:
                urls = json.loads(res[2])
            else:
                time.sleep(2)
        
        global access_token
        token = oauth.fetch_token(
            urls["token_url"],
            client_secret=client_secret,
            authorization_response=urls["cb_url"],
        )

        #print(f'dell sso token response: {token}')

        return token["access_token"]

    def new_non_sso_user(self):
        res = self._get("/new_user")
        if res[0] != 200:
            raise Exception(f"Error creating a new user: Code {res[0]}")
        new_id = res[2]
        os.environ['QDR_ID'] = new_id
        global QDR_ID
        QDR_ID = new_id
        print(f"=======\n\nYour qdr ID is: {new_id}.\nSave this ID and run 'export QDR_ID=<your id>' to access your programs in future sessions.")
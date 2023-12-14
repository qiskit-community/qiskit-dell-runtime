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


from typing import List, Dict, Optional, Callable, Type, Union, NamedTuple, Any
from qiskit.providers.ibmq.runtime import RuntimeProgram, RuntimeJob, ResultDecoder
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers import ProviderV1 as Provider
import hashlib
import copy
from datetime import datetime 
from pathlib import Path
import os
import json
import logging
import shutil
import copy

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from . import emulation_executor
from .emulator_runtime_job import EmulatorRuntimeJob

DIR = "DIR"
STRING = "STRING"

QDR_DIR = os.path.expanduser("~") + "/.qdr"
from .backend_provider import BackendProvider

class EmulatorRuntimeService():
    def __init__(self, provider: Provider) -> None:
        self.provider = provider
        self._programs = {}
        self._program_data = {}
        self._nextjobID = "1"
        self.backend_provider = BackendProvider()

    def backends(self) -> None:
        return self.backend_provider.backends()

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
            metadata: Optional[Union[Dict, str]] = None,
    ) -> str:

        metadata = copy.deepcopy(metadata)
        # metadata = self._merge_metadata(metadata=metadata)
        # careful of hash collision
        program_hash = hex(hash((data, None if 'name' not in metadata else metadata['name'], None if 'description' not in metadata else metadata['description'],)))[-16:]
        if 'name' not in metadata:
            name = program_hash
        else: 
            name = metadata.pop('name')

        # data can be one of three things:
        # Filename -> read to string, send
        # Directory -> zip, send
        # String -> send

        if os.path.isdir(data):
            logger.debug(f"Have directory: {data}")
            if not os.path.isdir(QDR_DIR):
                os.mkdir(QDR_DIR)
            dirsplit = data.split("/")
            if dirsplit[-1] == "":
                if not os.path.isfile(data + "program.py"):
                    raise Exception("program.py is required for directory upload")
                if os.path.isfile(data + "executor.py") or os.path.isfile(data + "params.json"):
                    raise Exception("executor.py and params.json are unallowable names in directory")
                zipname = QDR_DIR + "/" + dirsplit[-2]
            else:
                if not os.path.isfile(data + "/program.py"):
                    raise Exception("program.py is required for directory upload")
                if os.path.isfile(data + "/executor.py") or os.path.isfile(data + "/params.json"):
                    raise Exception("executor.py and params.json are unallowable names in directory")
                zipname = QDR_DIR + "/" + dirsplit[-1]

            zipped = shutil.make_archive(zipname, "zip", data)
            logger.debug(f"made: {zipped}")
            self._program_data[program_hash] = (zipped, DIR)
        elif os.path.isfile(data):
            with open(data, "r") as f:
                self._program_data[program_hash] = (f.read(), STRING)
        else:
            logger.debug(f"Have string: {data}")
            self._program_data[program_hash] = (data, STRING)
        
        self._programs[program_hash] = RuntimeProgram(
            program_id = program_hash,
            creation_date= datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            program_name = name,
            **metadata
        )
        return program_hash

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        if program_id in self._programs:
            return self._programs[program_id]
        else:
            return None

    def programs(self, refresh: bool = False) -> List[RuntimeProgram]:
        return self._programs.copy()

    def run(
            self,
            program_id: str,
            options: Dict,
            inputs: Dict,
            callback: Optional[Callable] = None,
            result_decoder: Optional[Type[ResultDecoder]] = None
    ) -> EmulatorRuntimeJob:
        if program_id in self._programs:
            program = self._programs[program_id]
            program_data = self._program_data[program_id]

            executor = emulation_executor.EmulationExecutor(program, program_data, options, inputs)
            job = EmulatorRuntimeJob(self._nextjobID, None, executor=executor, callback = callback)
            self._nextjobID = str(int(self._nextjobID) + 1)
            return job
        else:
            return None

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
            spec: Optional[Dict] = None
    ):
        metadata = self._merge_metadata(metadata=metadata, name=name, max_execution_time=max_execution_time, description=description, spec=spec)
        metadata.pop('name', None)

        if data:
            if os.path.isdir(data):
                logger.debug(f"Have directory: {data}")
                if not os.path.isdir(QDR_DIR):
                    os.mkdir(QDR_DIR)
                dirsplit = data.split("/")
                if dirsplit[-1] == "":
                    if not os.path.isfile(data + "program.py"):
                        raise Exception("program.py is required for directory upload")
                    if os.path.isfile(data + "executor.py") or os.path.isfile(data + "params.json"):
                        raise Exception("executor.py and params.json are unallowable names in directory")
                    zipname = QDR_DIR + "/" + dirsplit[-2]
                else:
                    if not os.path.isfile(data + "/program.py"):
                        raise Exception("program.py is required for directory upload")
                    if os.path.isfile(data + "/executor.py") or os.path.isfile(data + "/params.json"):
                        raise Exception("executor.py and params.json are unallowable names in directory")
                    zipname = QDR_DIR + "/" + dirsplit[-1]

                zipped = shutil.make_archive(zipname, "zip", data)
                logger.debug(f"made: {zipped}")
                self._program_data[program_id] = (zipped, DIR)
            elif os.path.isfile(data):
                with open(data, "r") as f:
                    self._program_data[program_id] = (f.read(), STRING)
            elif type(data) == Union[bytes, str]:
                logger.debug(f"Have string: {data}")
                self._program_data[program_id] = (data, STRING)


        # self._program_data[program_id] = data if data else self._program_data[program_id]
        self._programs[program_id] = RuntimeProgram(
            program_id = program_id,
            creation_date= self._programs[program_id].creation_date,
            program_name = self._programs[program_id].name if name is None else name,
            **metadata
        )

        return True
        
    def delete_program(self, program_id: str) -> None:
        try:
            del self._programs[program_id]
            del self._program_data[program_id]
            return True
        except:
            return False

    def job(self, job_id: str) -> EmulatorRuntimeJob:
        print("Do nothing")

    def jobs(self, limit: int = 10, skip: int = 0) -> List[EmulatorRuntimeJob]:
        return []

    def delete_job(self, job_id: str) -> None:
        print("Do Nothing")

    def logout(self) -> None:
        print("Do Nothing")

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

    def _tuple_to_dict(self, metadata: Dict) -> None:
        """Convert fields in metadata from named tuples to dictionaries.
        Args:
            metadata: Metadata to be converted.
        """
        for key in ['parameters', 'return_values', 'interim_results']:
            doc_list = metadata.pop(key, None)
            if not doc_list or isinstance(doc_list[0], dict):
                continue
            metadata[key] = [dict(elem._asdict()) for elem in doc_list]

    



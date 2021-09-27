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


from typing import Text
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import declarative_base, registry
from dataclasses import dataclass
from sqlalchemy import MetaData
from sqlalchemy.sql.sqltypes import TEXT

from .base import Base

@dataclass
class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)
    job_id = Column(String(64))
    program_id = Column(String(64))
    job_status = Column(String(64))
    pod_name = Column(String(64))
    pod_status = Column(String(64))
    data_token = Column(String(64))
    msg_token = Column(String(64))
#!/usr/bin/env python
# coding: utf-8

# In[2]:
from dell_runtime import DellRuntimeProvider
from qiskit import QuantumCircuit
import pandas as pd
from time import sleep
import os
import base64
import shutil
import json

# here = os.path.dirname(os.path.realpath(__file__))
# zipped = shutil.make_archive(here + "/tmp", "zip", here + "/qkad")
# with open(zipped, "rb") as z:
#     data = z.read()
# data = base64.urlsafe_b64encode(data)
# sdata = str(data, "utf-8")
# bdata = bytes(sdata, "utf-8")

# sdata = str(bdata, "utf-8")

# obj = {
#     'data': sdata,
#     'data_type': "DIR"
# }

# jsonstr = json.dumps(obj)
# ljson = json.loads(jsonstr)

# bdata = bytes(ljson['data'], "utf-8")
# b64data = base64.urlsafe_b64decode(bdata)

# with open(zipped, "wb") as temp:
#     temp.write(b64data)
# shutil.unpack_archive(zipped, extract_dir=here + "/qkad1", format="zip")
# os.remove(zipped)




provider = DellRuntimeProvider()



RUNTIME_PROGRAM_METADATA = {
    "max_execution_time": 600,
    "description": "Qiskit test program"
}


provider.remote(os.getenv("SERVER_URL"))
here = os.path.dirname(os.path.realpath(__file__))

program_id = provider.runtime.upload_program(here + "/qkad", metadata=RUNTIME_PROGRAM_METADATA)

job = provider.runtime.run(program_id, options=None, inputs={})

res = job.result(timeout=1000)
print(res)

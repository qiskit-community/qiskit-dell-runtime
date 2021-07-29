ARG QRE_NS
ARG DOCKER_REPO

FROM $DOCKER_REPO/$QRE_NS/qiskit

RUN mkdir -p /var/qre/qiskit_emulator

COPY requirements.txt /var/qre/

RUN pip3 install -r /var/qre/requirements.txt
COPY qiskit_emulator/ /var/qre/qiskit_emulator/


COPY requirements-docs.txt /var/qre/
COPY requirements-test.txt /var/qre/

COPY README.md /var/qre/
COPY setup.cfg /var/qre/
COPY setup.py /var/qre/
RUN cd /var/qre/ && pip3 install . 





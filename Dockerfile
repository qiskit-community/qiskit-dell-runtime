ARG QDR_NS
ARG DOCKER_REPO

FROM $DOCKER_REPO/qdr-qiskit

RUN mkdir -p /var/qdr/dell_runtime

COPY requirements.txt /var/qdr/

RUN pip3 install -r /var/qdr/requirements.txt
COPY dell_runtime/ /var/qdr/dell_runtime/


COPY requirements-docs.txt /var/qdr/
COPY requirements-test.txt /var/qdr/

COPY README.md /var/qdr/
COPY setup.cfg /var/qdr/
COPY setup.py /var/qdr/
RUN cd /var/qdr/ && pip3 install . 





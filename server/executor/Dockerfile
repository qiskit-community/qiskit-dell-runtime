ARG QDR_NS
ARG DOCKER_REPO

FROM $DOCKER_REPO/$QDR_NS/qdr-base

COPY ./requirements.txt /var/qiskit-runtime/
RUN pip3 install -r /var/qiskit-runtime/requirements.txt
RUN mkdir -p /var/qiskit-runtime
COPY ./executor.py /var/qiskit-runtime/
COPY ./startup.py /var/qiskit-runtime/
# COPY ./backend_certs/ /var/qiskit-runtime/backend_certs/
COPY ./user_messenger_client.py /var/qiskit-runtime/
COPY ./logging_config.ini /var/qiskit-runtime/
CMD cd /var/qiskit-runtime/ && python3 startup.py



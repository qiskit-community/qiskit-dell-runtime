FROM harbor.dell.com/dojo-harbor/python

COPY ./requirements.txt /var/qiskit-runtime/
RUN pip3 install -r /var/qiskit-runtime/requirements.txt
RUN mkdir -p /var/qiskit-runtime
COPY ./executor.py /var/qiskit-runtime/
COPY ./startup.py /var/qiskit-runtime/
COPY ./user_messenger_client.py /var/qiskit-runtime/
CMD python3 /var/qiskit-runtime/startup.py
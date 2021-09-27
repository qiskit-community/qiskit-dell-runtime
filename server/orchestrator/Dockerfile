ARG QDR_NS
ARG DOCKER_REPO

FROM $DOCKER_REPO/qdr-base

RUN apt-get update && apt-get install -y python3-flask default-libmysqlclient-dev build-essential
RUN mkdir /app
COPY ./requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
# COPY ./qdrcerts.crt /usr/local/share/ca-certificates
# COPY ./qdrcerts.crt /etc/ssl/certs/qdrcerts.pem
# RUN update-ca-certificates
COPY ./main.py /app/
RUN cat /app/main.py
COPY ./kube_client.py /app/
COPY ./__init__.py /app/
COPY ./logging_config.ini /app/
COPY ./models /app/models
ENV FLASK_APP /app/main.py
# ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

EXPOSE 8080
CMD cd /app && python3 main.py

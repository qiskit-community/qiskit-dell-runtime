FROM harbor.dell.com/dojo-harbor/qre/qre-base

RUN apt-get update && apt-get install -y python3-flask default-libmysqlclient-dev build-essential
RUN mkdir /app
COPY ./requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY ./qrecerts.crt /usr/local/share/ca-certificates
COPY ./qrecerts.crt /etc/ssl/certs/qrecerts.pem
RUN update-ca-certificates
COPY ./main.py /app/
COPY ./kube_client.py /app/
COPY ./__init__.py /app/
COPY ./logging_config.ini /app/
COPY ./models /app/models
# use waitress later
ENV FLASK_APP /app/main.py
ENV REQUESTS_CA_BUNDLE /etc/ssl/certs/ca-certificates.crt

EXPOSE 8080
CMD cd /app && python3 main.py

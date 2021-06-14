FROM harbor.dell.com/dojo-harbor/python

RUN apt-get update && apt-get install -y python3-flask default-libmysqlclient-dev build-essential
RUN mkdir /app
COPY ./requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY ./main.py /app/
COPY ./kube_client.py /app/
COPY ./__init__.py /app/
COPY ./logging_config.ini /app/
COPY ./models /app/models
# use waitress later
ENV FLASK_APP /app/main.py

EXPOSE 8080
CMD flask run -h 0.0.0.0 -p 8080
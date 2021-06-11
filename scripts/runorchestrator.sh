DB_HOST=localhost \
DB_PORT=3306 \
DB_USER=root \
DB_PASSWORD=password \
DB_NAME=mysql \
KAFKA_SERVERS=localhost:9092 \
KAFKA_TOPIC=jobs_results \
FLASK_APP=$PWD/server/orchestrator/main.py \
flask run -p 8080
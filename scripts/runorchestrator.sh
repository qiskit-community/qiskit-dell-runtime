DB_HOST=localhost \
DB_PORT=3306 \
DB_USER=root \
DB_PASSWORD=password \
DB_NAME=mysql \
FLASK_APP=$PWD/server/orchestrator/main.py \
flask run -p 8080
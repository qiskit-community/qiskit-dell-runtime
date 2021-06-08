
echo "HEY PARAMS ${2}" && \
cp server/executor/executor.py /root/workspace/qre-runtime-test/executor.py && \
cp server/executor/user_messenger_client.py /root/workspace/qre-runtime-test/user_messenger_client.py && \
ORCH_HOST=http://127.0.0.1:8080 \
PROGRAM_ID=$1 \
INPUTS_STR=$2 \
python server/executor/startup.py
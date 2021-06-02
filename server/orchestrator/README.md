```
docker build  . -t harbor.dell.com/dojo-harbor/qre/qre-orchestrator
docker push harbor.dell.com/dojo-harbor/qre/qre-orchestrator
```

To connect to mysql using mysql client in kubernetes:
```
kubectl run -it -n qre --rm --image=harbor.dell.com/dojo-harbor/qre/mysql:5.6 --restart=Never mysql-client -- mysql -h mysql -u qre -pqre
```


```
docker run -d \
    -e MYSQL_ROOT_PASSWORD=password \
    -e MYSQL_DATABASE=qre \ 
    -e MYSQL_USER=qre \
    -e MYSQL_PASSWORD=qre \
    --volume=/home/geoff/mysql_data:/var/lib/mysql \
    -p 6603:3306 \
    harbor.dell.com/dojo-harbor/qre/mysql:5.6
```
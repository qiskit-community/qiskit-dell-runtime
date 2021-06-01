```
docker build  . -t harbor.dell.com/dojo-harbor/qre/qre-orchestrator
docker push harbor.dell.com/dojo-harbor/qre/qre-orchestrator
```

```
kubectl run -it -n qre --rm --image=harbor.dell.com/dojo-harbor/qre/mysql:5.6 --restart=Never mysql-client -- mysql -h mysql -u qre -pqre
```

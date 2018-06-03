CONTAINERS="mqrecv-cell-update mqrecv-event mqrecv-gps-update mqrecv-firmware-update mqrecv-mt-file simchatcelery"

for con in ${CONTAINERS} ; do
    docker pull gcr.io/geotool-test/${con}:v${GIT_VER}
done
docker pull gcr.io/geotool-test/simchatserver:v${GIT_VER}

for con in ${CONTAINERS} ; do
    docker stop ${con} || true
    docker rm ${con} || true
    docker run -dt --restart=always -e CELERY_BROKER_URL="amqp://10.1.1.4" -e GEO_API_HOST=10.1.1.4:8000 -e MQ_HOST=10.1.1.4 -e DBHOST=10.1.1.4 -e DB_POOL_MAX=10 -e DB_POOL_MIN=1 --name=${con} gcr.io/geotool-test/${con}:v${GIT_VER} -vvv
done

docker stop simchatserver || true
docker rm simchatserver || true
docker run -dt --restart=always --name=simchatserver -e MQ_HOST=10.1.1.4 -p 65533:65533 gcr.io/geotool-test/simchatserver:v${GIT_VER} -vv -s 10.1.1.4:8000
(docker ps -a | grep "xited" | awk '{print $1}' | xargs docker rm) || true
(docker images | grep none | awk '{print $3}' | xargs docker rmi) || true

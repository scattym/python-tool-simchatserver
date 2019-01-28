CONTAINERS="mqrecv-cell-update mqrecv-event mqrecv-gps-update mqrecv-firmware-update mqrecv-mt-file meitrackbot"

for con in ${CONTAINERS} ; do
    docker pull gcr.io/geotool-test/${con}:v${GIT_VER}
done
docker pull gcr.io/geotool-test/simchatserver:v${GIT_VER}

docker stop simchatserver || true
docker rm simchatserver || true
docker run -dt --restart=always --name=simchatserver -e MT_UPDATE_HOST=home.scattym.com -e MT_UPDATE_PORT=65533 -e MQ_HOST=10.1.1.4 -p 65533:65533 gcr.io/geotool-test/simchatserver:v${GIT_VER} -vv -s 10.1.1.4:8000

for con in ${CONTAINERS} ; do
    docker stop ${con} || true
    docker rm ${con} || true
    docker run -dt --link=simchatserver --restart=always -e SCS_HOST=simchatserver -e CELERY_BROKER_URL="amqp://10.1.1.4" -e GEO_API_HOST=10.1.1.4:8000 \
    -e MQ_HOST=10.1.1.4 -e DBHOST=10.1.1.4 -e DB_POOL_MAX=10 -e DB_POOL_MIN=1 --name=${con} gcr.io/geotool-test/${con}:v${GIT_VER} -vvv
done
docker stop simchatcelery || true
docker rm simchatcelery || true
docker run -dt --link=simchatserver --restart=always -e SCS_HOST=simchatserver -e CELERY_BROKER_URL="amqp://10.1.1.4" -e GEO_API_HOST=10.1.1.4:8000 \
    -e MQ_HOST=10.1.1.4 -e DBHOST=10.1.1.4 -e DB_POOL_MAX=10 -e DB_POOL_MIN=1 -e FLOWER_BROKER="amqp://guest:guest@10.1.1.4:5672//" \
    -e FLOWER_BROKER_API="http://guest:guest@10.1.1.4:15672/api/" -p 5555:5555 --name=simchatcelery gcr.io/geotool-test/simchatcelery:v${GIT_VER}

docker stop simchatflower || true
docker rm simchatflower || true
docker run -dt --link=simchatserver --restart=always -e SCS_HOST=simchatserver -e CELERY_BROKER_URL="amqp://10.1.1.4" -e GEO_API_HOST=10.1.1.4:8000 \
    -e MQ_HOST=10.1.1.4 -e DBHOST=10.1.1.4 -e DB_POOL_MAX=10 -e DB_POOL_MIN=1 -e FLOWER_BROKER="amqp://guest:guest@10.1.1.4:5672//" \
    -e FLOWER_BROKER_API="http://guest:guest@10.1.1.4:15672/api/" -p 5555:5555 --name=simchatflower gcr.io/geotool-test/simchatflower:v${GIT_VER}


(docker ps -a | grep "xited" | awk '{print $1}' | xargs docker rm) || true
(docker images | grep none | awk '{print $3}' | xargs docker rmi) || true

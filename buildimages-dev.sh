docker build --tag=simchatserver-base-dev:interim . -f dockerfiles/simchatserver-base-dev/Dockerfile
docker build --tag=gcr.io/geotool-test/simchatserver:v${GIT_VER} . -f dockerfiles/simchatserver/Dockerfile-dev
docker build --tag=gcr.io/geotool-test/mqrecv-cell-update:v${GIT_VER} . -f dockerfiles/mqrecv-cell-update/Dockerfile
docker build --tag=gcr.io/geotool-test/mqrecv-event:v${GIT_VER} . -f dockerfiles/mqrecv-event/Dockerfile-dev
docker build --tag=gcr.io/geotool-test/mqrecv-gps-update:v${GIT_VER} . -f dockerfiles/mqrecv-gps-update/Dockerfile-dev
docker build --tag=gcr.io/geotool-test/mqrecv-firmware-update:v${GIT_VER} . -f dockerfiles/mqrecv-firmware-update/Dockerfile-dev
docker build --tag=gcr.io/geotool-test/mqrecv-mt-file:v${GIT_VER} . -f dockerfiles/mqrecv-mt-file/Dockerfile-dev
docker build --tag=gcr.io/geotool-test/simchatcelery:v${GIT_VER} . -f dockerfiles/simchatcelery/Dockerfile-dev
# Run the following line from the command line to build and start this image
# docker build -t kungfauxpandas . && docker run -p 8000:8000 -p 8080:8080 -it kungfauxpandas
#
#FROM python:3.6.5-alpine as base
# for some reason, alpine image takes 30min - 1h+ to build python packages
# debian stretch base image takes like 2 minutes
# keeping old alpine stuff in case I figure it out or want to test further
FROM python:3.6.5 as base
FROM base as builder

#RUN apk add --no-cache --update gcc gfortran freetype-dev libpng-dev build-base openblas-dev python3-dev
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gfortran libfreetype6-dev libpng-dev libopenblas-dev unzip && apt-get clean

RUN mkdir /app
WORKDIR /app

RUN wget https://github.com/CUD2V/kungfauxpandas/archive/master.zip; \
  unzip master.zip; \
  rm master.zip; \
  cd kungfauxpandas-master/sourcecode/python; \
  pip --no-cache-dir install -r requirements.txt; \
  cd ../scripts ;\
  chmod +x ./docker_startup.sh

WORKDIR /app/kungfauxpandas-master/sourcecode/scripts

EXPOSE 8000 8080

# in case I want to test without committing
# ADD docker_startup.sh /app/kungfauxpandas-master/sourcecode/scripts/docker_startup.sh

CMD ["/bin/bash", "docker_startup.sh", ">>", "/app/docker_startup.log", "2>&1"]

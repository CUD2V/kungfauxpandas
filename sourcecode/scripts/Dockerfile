FROM python:3.6.5-alpine as base
FROM base as builder

RUN apk add --no-cache --update gcc gfortran freetype-dev libpng-dev build-base openblas-dev python-dev
RUN mkdir /app
WORKDIR /app

RUN wget https://github.com/CUD2V/kungfauxpandas/archive/master.zip; \
  unzip master.zip; \
  cd kungfauxpandas-master/sourcecode/python; \
  pip install -r requirements.txt; \
  cd ../scripts ;\
  chmod +x ./startup.sh

FROM base
COPY --from=builder /app /app
WORKDIR /app/kungfauxpandas-master/sourcecode/scripts

EXPOSE 8000 8080

CMD ["/bin/bash", "/startup.sh"]

# https://busybox.net/downloads/BusyBox.html
# docker build -t kungfauxpandas . && docker run -p 8000:8000 -p 8080:8080 -it kungfauxpandas
# pip install -i https://pypi.fcio.net/simple/ -r requirements.txt

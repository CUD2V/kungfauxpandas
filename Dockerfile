FROM python:3.6.5-alpine as base
FROM base as builder

RUN apk add --no-cache --update gcc gfortran freetype-dev libpng-dev build-base openblas-dev
RUN mkdir /app
WORKDIR /app

RUN wget https://github.com/CUD2V/kungfauxpandas/archive/master.zip; \
  unzip master.zip; \
  cd kungfauxpandas-master/sourcecode/python; \
  pip install virtualenv; \
  virtualenv kungfauxpandas; \
  source kungfauxpandas/bin/activate; \
  pip install -r requirements.txt

FROM base
COPY --from=builder /app /app
WORKDIR /app

EXPOSE 8080

CMD ["python", "-m http.server", "8080"]


# https://busybox.net/downloads/BusyBox.html
# docker build -t kungfauxpandas . && docker run -it kungfauxpandas
# pip install -i https://pypi.fcio.net/simple/ -r requirements.txt

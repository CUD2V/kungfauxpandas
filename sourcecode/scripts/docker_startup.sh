#! /bin/bash

pwd

env

cd ../html
python -m http.server 8080 >> /app/http_server.log 2>&1

cd ../python
hug -p 8000 -f web-service.py >> /app/web_service.log 2>&1

#tail -f /app/web_service.log

cleanup ()
{
kill -s SIGTERM $!
exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]
do
    echo -n "."
    sleep 10 &
    wait $!
done

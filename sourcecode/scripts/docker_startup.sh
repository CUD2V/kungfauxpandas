#! /bin/bash
cd ../html
python -m http.server 8080 >> /app/http_server.log 2>&1

cd ../python
hug -p 8000 -f web-service.py >> /app/web_service.log 2>&1

#tail -f /app/web_service.log

while :; do
  sleep 100
  echo -n "."
done

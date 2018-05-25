#! /bin/bash
cd ../html
python -m http.server 8080 &

cd ../python
hug -p 8000 -f web-service.py &

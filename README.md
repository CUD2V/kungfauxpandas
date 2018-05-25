# faker-prototype

This data synthesis process was created using Python. In order to make it easier for others to replicate the environment, a Conda environment export has been provided as well as a virtualenv requirements file.

## Python Setup
To run the software, download/clone this repository and then run the appropriate command below based on your Python distribution:

### Conda users

From the base directory of the repository:

```
cd sourcecode/python/
conda env create -f environment.yml
```

### Virtualenv users

From the base directory of the repository:

```
cd sourcecode/python/
virtualenv kungfauxpandas
source kungfauxpandas/bin/activate
pip install -r requirements.txt
```

## Running the software

Currently two methods are provided - a web interface (utilizing a REST API) or Python class

### Web UI/API

#### Start a web server:
From the base directory of the repository:
```
cd sourcecode/html
python -m http.server 8080
```

#### Start the Hug REST API server:
From the base directory of the repository:
```
cd sourcecode/python
hug -p 8000 -f web-service.py
```

## For those interested in how we created the Conda or virtualenv files:

### To save conda env

From the base directory of the repository:

```
cd sourcecode/python/
conda create -n kungfauxpandas python=3.6
conda activate kungfauxpandas
conda install cython pandas numpy scipy jupyter matplotlib
pip install hug
conda env export -n kungfauxpandas | grep -v "^prefix: " > environment.yml
```


### Steps to create the virtualenv

From the base directory of the repository:

```
cd sourcecode/python/
virtualenv kungfauxpandas
source kungfauxpandas/bin/activate
pip install cython numpy scipy pandas matplotlib jupyter hug
pip freeze > requirements.txt
```

## About the Docker image

### Create the docker image

Clone the git repo and from the base of the repo run the following:

```
cd sourcecode/scripts
docker build -t kungfauxpandas .
```

If you want to run the docker image you just created:

```
docker run -p 8000:8000 -p 8080:8080 -it kungfauxpandas
 ```

### Make the docker image available via dockerhub

```
docker login --username=blackspot
docker images
# find image id and replace <imageid> with the actual id
docker tag <imageid> blackspot/synthesis:latest
docker push blackspot/synthesis:latest
```



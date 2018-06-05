# Kung Faux Pandas: Simplifying privacy protection

There are many barriers to data access and data sharing, especially in the domain of machine learning on health care data. Legal constraints such as HIPAA protect patient privacy but slow access to data and limit reproducibility. This repository contains an end-to-end system called *Kung Faux Pandas* for easily generating de-identified or synthetic data which is statistically similar to given real data but lacks sensitive information. This system focuses on data synthesis and de-identification narrowed to a specific research question to allow for self-service data access without the complexities required to generate an entire population of data that is not needed for a given research project. Kung Faux Pandas is an open source publicly available system that lowers barriers to HIPAA- and GDPR-compliant data sharing for enabling reproducibility and other purposes.

This data synthesis process was created using Python. In order to make it easier for others to replicate the environment, a range of environments are supported: Conda environment export, virtualenv requirements file, and a docker image with the latest code.

## Python Setup
To run the software, download/clone this repository and then run the appropriate command below based on your Python distribution:

### Conda users

From the base directory of the repository:

```
cd sourcecode/python/
conda env create -f environment.yml
conda activate kungfauxpandas
```

### Virtualenv users

From the base directory of the repository:

```
cd sourcecode/python/
virtualenv kungfauxpandas
source kungfauxpandas/bin/activate
pip install -r requirements.txt
```

### Install plugin(s)

This software provides a method for adding new plugins for data synthesis. The only method fully included with this repository is a kernel density estimation method based on scipy's gaussian KDE (see
  [scipy.stats.gaussian_kde](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gaussian_kde.html)). We have developed plugins for [DataSynthesis](https://github.com/DataResponsibly/DataSynthesizer) and are currently working on one for [Synthetic dataset Generation Framework](https://vbinds.ch/projects/sgf/index.html). In order to use a plugin, you must download additional software.

#### DataSynthesis
From the base directory of the repository:

```
cd plugins/
git clone https://github.com/DataResponsibly/DataSynthesizer.git
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

Use the provided docker image by executing the following:

```
docker pull blackspot/synthesis
```

### How to (re)create the docker image

Clone the git repo and from the base of the repo run the following:

```
cd sourcecode/scripts
docker build -t kungfauxpandas .
```

If you want to run the docker image you just created:

```
docker run -p 8000:8000 -p 8080:8080 -it kungfauxpandas
 ```

### How we make the docker image available via dockerhub

```
docker login --username=blackspot
docker images
# find image id and replace <imageid> with the actual id
docker tag <imageid> blackspot/synthesis:latest
docker push blackspot/synthesis:latest
```

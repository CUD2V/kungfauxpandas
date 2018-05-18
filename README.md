# faker-prototype

This data synthesis process was created using Python. In order to make it easier for others to replicate the environment, a Conda environment export has been provided as well as a virtualenv requirements file.

To run the software, download/clone this repository and then run the appropriate command below based on your Python distribution:

## Conda users

From the base directory of the repository:

```
cd sourcecode/python/
conda env create -f environment.yml
```

## Virtualenv users

From the base directory of the repository:

```
cd sourcecode/python/
virtualenv kungfauxpandas
source kungfauxpandas/bin/activate
pip install -r requirements.txt
```

## For those interested in how we created the Conda or virtualenv files:

### To save conda env

From the base directory of the repository:

```
cd sourcecode/python/
conda create -n faker python=3.6
source activate faker
conda install pandas numpy scipy jupyter matplotlib
conda env export -n faker | grep -v "^prefix: " > environment.yml
```


### Steps to create the virtualenv

From the base directory of the repository:

```
cd sourcecode/python/
virtualenv kungfauxpandas
source kungfauxpandas/bin/activate
pip install numpy scipy pandas matplotlib jupyter
pip freeze > requirements.txt
```

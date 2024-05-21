#!/bin/bash

# salloc a node before you run this cause the petsc config uses srun

rm -fr packages
mkdir packages

cd packages

wget https://ftp.mcs.anl.gov/pub/petsc/petsc-3.19.tar.gz
tar -xvf petsc-3.19.tar.gz

ml gcc mvapich2 mkl python/3.9.12-rkxvr6

pip3 install --user configure
# pip3 install --upgrade configure

cp ../petsc_configure.py ./petsc-3.19.6
# see configure options before you configure
cd petsc-3.19.6
python petsc_configure.py --mpich-only --dryrun
python petsc_configure.py --mpich-only
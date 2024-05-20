#!/bin/bash

# salloc a node before you run this

mkdir lib

cd lib

wget https://ftp.mcs.anl.gov/pub/petsc//petsc-3.19.tar.gz
tar -xvf petsc-3.19.tar.gz

ml gcc mvapich2 mkl python/3.9.12-rkxvr6

pip3 install --user configure
cp petsc_configure.py ./petsc-3.19.6
python ./petsc_configure.py --mpich-only
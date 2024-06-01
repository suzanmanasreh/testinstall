#!/bin/bash

ml gcc mvapich2 python/3.9.12-rkxvr6
cd packages
wget https://github.com/Reference-LAPACK/lapack/archive/refs/tags/v3.12.0.tar.gz
tar -xvf v3.12.0.tar.gz
cd lapack-3.12.0
cp ../../make.inc ./
# why isn't make -j 8 faster?
make
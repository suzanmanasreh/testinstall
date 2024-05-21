#!/bin/bash

ml cmake/3.23.1-yuuito

rm -fr build
mkdir build
cd build
cmake .. -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
## Install PETSc
1. `bash commands.sh`
2. Follow PETSc make instructions given in output. The `make check` command results in errors related to multi-threading + multiple MPI processes for me.
```shell
make PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH> all
make PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH> check
```
2. set environment variable for CMake
```shell
export PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH>
```

## Run PETSc examples
1. `bash test.sh`
2. `make`
3. `./ex5f`

## Install PETSc
1. `bash commands.sh`
2. Follow PETSc make instructions given in output. The `make check` command results in errors related to multi-threading + multiple MPI processes for me.
```shell
make PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH> all
make PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH> check
```
2. set environment variables for CMake
```shell
export PETSC_DIR=<PETSC_DIR> PETSC_ARCH=<PETSC_ARCH>
```

## Run PETSc examples
1. `bash test.sh`
2. `cd build`
3. `make`
4. `./ex19f` or `./ex1f` or `./ex19` depending on what file is being built in `CMakeLists.txt`. most files from `./examples` folder give compiler errors except for `ex19.F90`


Checklist: 
- [X] PETSc
- [ ] ~~LAPACK95~~ why doesn't [this](https://github.com/steleman/fortran2018-examples/blob/b2c892a595d38aa2e317fb656754f7927df69246/array/CMakeLists.txt#L14) work
- [ ] LAPACK
- [ ] Spherepack
- [ ] FFTW
- [ ] NetCDF
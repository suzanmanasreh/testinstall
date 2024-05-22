#
#  This is a sample CMakeLists.txt suitable for direct use with a new PETSc application or
#  you can add fragments of material below to an existing applications CMakeLists.txt
#
#  Usage:  To build ex1 from ex1.c
#    rm -fr build
#    mkdir build
#    cd build
#    cmake ..
#    make
#    ./ex1
#
#  By default it gets both the compiler information and the library information from PETSc
#
include(CMakePrintHelpers)
cmake_minimum_required(VERSION 3.1.0)

set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
set(BLA_VENDOR Intel10_64lp)

message("before petsc pkg config")

# set root of location to find PETSc's pkg-config
set(PETSC $ENV{PETSC_DIR}/$ENV{PETSC_ARCH})
set(ENV{PKG_CONFIG_PATH} ${PETSC}/lib/pkgconfig)

message("after petsc pkg config")
message(${PETSC})

# Remove the lines below if you do not wish to have PETSc determine the compilers
execute_process ( COMMAND pkg-config PETSc --variable=ccompiler COMMAND tr -d '\n' OUTPUT_VARIABLE C_COMPILER)
SET(CMAKE_C_COMPILER ${C_COMPILER})
execute_process ( COMMAND pkg-config PETSc --variable=cxxcompiler COMMAND tr -d '\n' OUTPUT_VARIABLE CXX_COMPILER)
if (CXX_COMPILER)
  SET(CMAKE_CXX_COMPILER ${CXX_COMPILER})
  SET(CMAKE_CXX_LINK_EXECUTABLE "${CMAKE_CXX_LINK_EXECUTABLE} -ldl")
endif (CXX_COMPILER)
execute_process ( COMMAND pkg-config PETSc --variable=fcompiler COMMAND tr -d '\n' OUTPUT_VARIABLE FORTRAN_COMPILER)
cmake_print_variables(FORTRAN_COMPILER)

if (FORTRAN_COMPILER)
  message(${FORTRAN_COMPILER})
  SET(CMAKE_Fortran_COMPILER ${FORTRAN_COMPILER})
  # set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} -I${PETSC_DIR}/include -I${PETSC_DIR}/${PETSC_ARCH}/include")
  add_compile_options(-ffree-line-length-none -fallow-argument-mismatch -freal-4-real-8 -O3)
  add_link_options(-ldl -lstdc++ -Wl,--copy-dt-needed-entries)
  enable_language(Fortran C CXX)

  # SET(CMAKE_Fortran_LINK_EXECUTABLE "${CMAKE_Fortran_LINK_EXECUTABLE} -ldl")
endif (FORTRAN_COMPILER)

if(NOT DEFINED ENV{MKLROOT})
  message(FATAL_ERROR "MKL not detected via MKLROOT environment variable")
endif()


# find_file(src
# NAMES makefile
# HINTS $ENV{MKLROOT}
# PATH_SUFFIXES interfaces/lapack95
# NO_DEFAULT_PATH
# REQUIRED
# )


#  tells CMake to build the application ex1 from the source file ex1.c
#  this must appear AFTER the compilers are set
project(myexe)
add_executable(myexe exl95.F90)

find_package(PkgConfig REQUIRED)
find_package(LAPACK REQUIRED)

pkg_search_module(PETSC REQUIRED IMPORTED_TARGET PETSc)

# target_link_libraries(myexe LAPACK::LAPACK)

target_link_libraries(myexe LAPACK::LAPACK PkgConfig::PETSC)

if (PETSC_FOUND)
  message("PETSc found")
endif(PETSC_FOUND)
if (LAPACK_FOUND)
  message(STATUS "LAPACK libraries: ${LAPACK_LIBRARIES}")
endif(LAPACK_FOUND)

set(BLA_F95 ON)

cmake_path(CONVERT "$ENV{MKLROOT}" TO_CMAKE_PATH_LIST MKLROOT NORMALIZE)
message(STATUS "MKLROOT: ${MKLROOT}")

set(FC $ENV{FC})
if(FC)
  message(STATUS "FC: ${FC}")
  execute_process(COMMAND make libintel64 INSTALL_DIR=${CMAKE_CURRENT_BINARY_DIR} interface=lp64 FC=${FC}
    WORKING_DIRECTORY $ENV{MKLROOT}/interfaces/lapack95)
endif(FC)

set(LAPACK95_INCLUDE_DIRS $ENV{MKLROOT}/include/intel64/lp64)
set(LAPACK95_LIBRARIES $ENV{MKLROOT}/lib/intel64_lin/libmkl_lapack95_lp64.a)
    
# list(INSERT LAPACK95_LIBRARIES 0 $ENV{MKLROOT}/lib/intel64_lin/libmkl_lapack95_lp64.a)

message(STATUS "LAPACK95_INCLUDE_DIRS: ${LAPACK95_INCLUDE_DIRS}")
message(STATUS "LAPACK95_LIBRARIES: ${LAPACK95_LIBRARIES}")
# find_package(LAPACK95 REQUIRED)

if(LAPACK95_FOUND)
  message("LAPACK95 FOUND")
endif(LAPACK95_FOUND)

target_link_libraries(myexe ${LAPACK95_LIBRARIES})
target_include_directories(myexe PRIVATE ${LAPACK95_INCLUDE_DIRS})
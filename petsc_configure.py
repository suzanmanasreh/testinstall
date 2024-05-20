#!/usr/bin/env python
""" Configuration helper for PETSc

Execute from PETSC_DIR

Note that older versions of PETSc require Python 2

Run with -h to see arguments

Adds a thin extra layer around PETSc's configuration script,
to help combine commonly-used combinations of configuration options and
construct meaningful PETSC_ARCH values.

Proceeds by collecting the set of passed arguments and processing them
before sending them to PETSc's configure script.
This logic will likely be somewhat brittle. Always do a sanity check
and look at the options that are actually being sent. This script should
be simple enough to figure out what's going on.
"""

from __future__ import print_function
import sys
import os
import argparse
import re


def main():
    """ Main script logic """
    args, options_in = get_args()
    options = process_args(options_in, args)
    petsc_configure(options, args)


def get_args():
    """ Retrieve custom arguments and remaining arguments"""
    parser = argparse.ArgumentParser(
        description='Compute arguments to pass to PETSc\'s configure script')
    parser.add_argument(
        '--archmod',
        default=None,
        help="additional terms in arch name, usually from a branch e.g \"maint\"")
    parser.add_argument(
        '--dryrun',
        action="store_true",
        help="don't actually configure")
    parser.add_argument(
        '--extra',
        type=int,
        default=1,
        help="common extra packages (integer value, see script for now) ")
    parser.add_argument(
        '--prefix-auto',
        action="store_true",
        help="set --prefix to a standard location (in this directory)")
    parser.add_argument(
        '--mpich-only',
        action="store_true",
        help="Custom options to obtain MPICH with compiler caches, to use generally")
    args, unknown = parser.parse_known_args()
    return args, unknown


def _detect_darwin():
    return sys.platform == 'darwin'


def process_args(options_in, args):
    """ Main logic to create a set of options for PETSc's configure script,
    along with a corresponding PETSC_ARCH string, if required """

    # NOTE: the order here is significant, as
    # 1. PETSC_ARCH names are constructed in order
    # 2. Processing of options depends on the processing of previous ones

    # A special case
    mpich_only_arch = 'arch-mpich-only'
    if args.mpich_only:
        return options_for_mpich_only(mpich_only_arch)

    # Initialize options and arch identifiers
    options = options_in[:]  #copy
    arch_identifiers = initialize_arch_identifiers(args)

    # Floating point precision
    precision = option_value(options, "--with-precision")
    if not precision:
        precision = 'double'
    if precision and precision != 'double':
        if precision == '__float128':
            arch_identifiers.append('quad')
        else:
            arch_identifiers.append(precision)

    # MPI
    # By default, we expect you to have $HOME/code/petsc/arch-mpich-only,
    # which you created with this script.
    with_mpi = option_value(options, "--with-mpi")
    with_mpi_dir = option_value(options, "--with-mpi-dir")
    download_mpich = option_value(options, "--download-mpich")
    if with_mpi is not False and not with_mpi_dir and not download_mpich:
        mpich_only_petsc_dir = os.path.join(os.environ['HOME'], 'code', 'petsc')
        mpich_only_dir = os.path.join(mpich_only_petsc_dir, mpich_only_arch)
        if not os.path.isdir(mpich_only_dir):
            print('Did not find expected', mpich_only_dir)
            print('Either run this script with --mpich-only from', mpich_only_petsc_dir)
            print('Or specify MPI some other way, e.g. --download-mpich')
            sys.exit(1)
        options.append('--with-mpi-dir=' + mpich_only_dir)

    # Fortran bindings
    with_fortran_bindings = option_value(options, "--with-fortran-bindings")
    if with_fortran_bindings is None:
        options.append('--with-fortran-bindings=0')

    # Integer precision
    if option_value(options, "--with-64-bit-indices"):
        arch_identifiers.append("int64")

    # Scalar type
    scalartype = option_value(options, "--with-scalar-type")
    if not scalartype:
        scalartype = 'real'
    if scalartype and scalartype != 'real':
        arch_identifiers.append(scalartype)
        options.append("--with-scalar-type=%s" % scalartype)

    # C language
    clanguage = option_value(options, "--with-clanguage")
    if not clanguage:
        clanguage = 'c'
    if clanguage and clanguage != 'c' and clanguage != 'C':
        if clanguage in ['cxx', 'Cxx', 'c++', 'C++']:
            arch_identifiers.append('cxx')

    # BLAS/LAPACK
    download_fblaslapack = option_value(options,
                                            "--download-fblaslapack")
    download_f2cblaslapack = option_value(options,
                                              "--download-f2cblaslapack")
    if not download_fblaslapack and not download_f2cblaslapack:
        if precision == '__float128':
            options.append('--download-f2cblaslapack')

    # X
    with_x = option_value(options, "--with-x")
    if with_x is None and _detect_darwin():
        options.append("--with-x=0")

    # Extra packages
    if args.extra:
        if args.extra >= 1:
            if scalartype == 'real' and precision == 'double':
                options.append('--download-suitesparse')
        if args.extra >= 2:
            options.append('--download-scalapack')
            options.append('--download-metis')
            download_cmake = option_value(options, '--download-cmake')
            if download_cmake is None:
                options.append('--download-cmake')  # for METIS
            options.append('--download-parmetis')
            options.append('--download-mumps')
        if args.extra >= 3:
            options.append('--download-hdf5')
            if with_fortran_bindings:
                options.append('--download-hdf5-fortran-bindings')
            options.append('--download-superlu_dist')
            with_cuda = option_value(options, "--with-cuda")
            if with_cuda:
                options.append('--with-openmp=1')  # for SuperLU_dist GPU
        if args.extra >= 4:
            options.append('--download-triangle')
            options.append('--download-sundials2')
        if args.extra >= 2:
            arch_identifiers.append('extra')

    # Debugging
    debugging = option_value(options, "--with-debugging")
    if debugging is None or debugging:
        arch_identifiers.append('debug')
    else:
        if not option_value(options, "--COPTFLAGS"):
            options.append("--COPTFLAGS=-g -O3 -march=native")
        if not option_value(options, "--CXXOPTFLAGS"):
            options.append("--CXXOPTFLAGS=-g -O3 -march=native")
        if not option_value(options, "--FOPTFLAGS"):
            options.append("--FOPTFLAGS=-g -O3 -march=native")
        if not option_value(options, "--CUDAOPTFLAGS"):
            options.append("--CUDAOPTFLAGS=-O3")
        arch_identifiers.append('opt')

    # C2HTML (for building docs locally)
    with_c2html = option_value(options, '--with-c2html')
    download_c2html = option_value(options, '--download-c2html')
    if not with_c2html is not False and download_c2html is not False:
        options.append("--download-c2html")

    # Prefix
    prefix = option_value(options, "--prefix")
    if prefix:
        arch_identifiers.append('prefix')

    # Auto-prefix
    # Define an install directory inside the PETSC_DIR (danger for older versions of PETSc?)
    if args.prefix_auto:
        if prefix:
            raise RuntimeError('Cannot use both --prefix and --prefix-auto')
        options.append(
            '--prefix=' +
            os.path.join(os.getcwd(), '-'.join(arch_identifiers) + '-install'))
        arch_identifiers.append('prefix')

    # Add PETSC_ARCH
    options.append('PETSC_ARCH=' + '-'.join(arch_identifiers))

    # Use the current directory as PETSC_DIR
    options.append('PETSC_DIR=' + os.getcwd())

    return options


def option_value(options, key):
    """ Get the value of a configure option """
    # match the key either:
    # - exactly (end of string, $), or
    # - followed by = and 1 or more non-whitespace characters (\S)
    regexp = re.compile(key + r'($|=\S+)')
    matches = list(filter(regexp.match, options))
    if len(matches) > 1:
        raise RuntimeError('More than one match for option', key)
    if matches:
        match = matches[0]
        if match == key:  # interpret exact key as True
            value = True
        else:
            spl = match.split("=", 1)
            if len(spl) != 2:
                raise RuntimeError('match %s does not seem to be --foo[=bar]' % match)
            value = spl[1]
    else:
        value = None
    if value in ['0', 'false', 'no']:
        value = False
    elif value in ['1', 'true', 'yes']:
        value = True
    elif value == '':
        raise RuntimeError("Don't know how to process match " + match)
    return value


def initialize_arch_identifiers(args):
    """ Create initial arch identifiers """
    arch_identifiers = ['arch']
    if args.archmod:
        arch_identifiers.append(args.archmod)
    return arch_identifiers


def options_for_mpich_only(mpich_only_arch):
    """ Return a custom set of arguments to simply download and build MPICH """

    MKL_DIR = os.getenv('MKLROOT')

    options = []
    options.append('--with-cc=mpicc')
    # options.append('--with-cxx=0')
    options.append('--with-fc=mpif90')
    options.append('--with-debugging=0')
    options.append("--COPTFLAGS=-g -O3 -march=native")
    options.append("--CXXOPTFLAGS=-g -O3 -march=native")
    # options.append("--CUDAOPTFLAGS=-O3")
    options.append("--FOPTFLAGS=-g -O3 -march=native")
    options.append("--with-blaslapack-dir=" + MKL_DIR)
    options.append("--with-mpiexec=srun")
    options.append("--with-shared-libraries=0")
    options.append("--with-x11=0")
    options.append("--with-x=0")
    options.append("--with-windows-graphics=0")
    # options.append('PETSC_ARCH=' + mpich_only_arch)
    # options.append('PETSC_DIR=' + os.getcwd())
    return options


def petsc_configure(options, args):
    """ Standard PETSc configuration script logic (from config/examples) """
    if args.dryrun:
        print("Dry Run. Would configure with these options:")
        print("\n".join(options))
    else:
        sys.path.insert(0, os.path.abspath('config'))
        # print(sys.version)
        try:
            import configure
        except ImportError:
            print(
                'PETSc configure module not found. Make sure you are executing from PETSC_DIR'
            )
            sys.exit(1)
        print('Configuring with these options:')
        print("\n".join(options))

        # Since petsc_configure looks directly at sys.argv, remove and replace arguments
        argv_temp = sys.argv
        sys.argv = sys.argv[:1]
        configure.petsc_configure(options)
        sys.argv = argv_temp


if __name__ == '__main__':
    main()
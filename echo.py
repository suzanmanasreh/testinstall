# echo.py

def echo(text: str, repetitions: int = 3) -> str:
    """Imitate a real-world echo."""
    echoed_text = ""
    for i in range(repetitions, 0, -1):
        echoed_text += f"{text[-i:]}\n"
    return f"{echoed_text.lower()}."

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.abspath('config'))
    import config
    MKL_DIR = os.getenv('MKLROOT')
    print(MKL_DIR)

    configure_options = [
        '--with-debugging=1',
        '--with-blaslapack-lib=-L%s/lib/intel64 -Wl,--no-as-needed -lmkl_intel_lp64 -lmkl_sequential -lmkl_core -lpthread -lm -ldl' % MKL_DIR,
        '--with-blaslapack-include=%s/include' % MKL_DIR,
        '--with-cc=mpicc',
        '--with-cxx=0',
        '--with-fc=mpif90',
        '--with-mpiexec=srun',
        '--with-scalapack-lib=-lmkl_scalapack_lp64 -lmkl_blacs_intelmpi_lp64', # we don't repeat what is already in --with-blaslapack-lib
        '--with-scalapack-include=%s/include' % MKL_DIR,
        'COPTFLAGS=\'-O3 -march=native -mtune=native\'',
        'CXXOPTFLAGS=\'-O3 -march=native -mtune=native\'',
        'FOPTFLAGS=\'-O3 -march=native -mtune=native\''
    ]
    print("HERE")
    config.petsc_configure(configure_options)

    text = input("Yell something at a mountain: ")
    print(echo(text))
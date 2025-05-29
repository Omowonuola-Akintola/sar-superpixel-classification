
from cffi import FFI
import os

def compile_sniclib():
    ffibuilder = FFI()
    
    # Get directory of this script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Absolute paths to files
    h_path = os.path.join(base_dir, "snic.h")
    c_path = os.path.join(base_dir, "snic.c")

    # Load the header
    ffibuilder.cdef(open(h_path).read())

    # Set the source using include
    ffibuilder.set_source(
        "_snic",
        '#include "snic.h"',
        sources=[c_path],
        library_dirs=[base_dir],
        extra_compile_args=['-O3', '-march=native', '-ffast-math'])

    ffibuilder.compile(verbose=True)
    

compile_sniclib()

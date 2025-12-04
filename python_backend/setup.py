from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import sys

# Get the C++ core directory
cpp_core_dir = os.path.join(os.path.dirname(__file__), '..', 'cpp_core')

# Define the extension
extensions = [
    Extension(
        "scheduler_wrapper",
        sources=[
            "scheduler_wrapper.pyx",
            os.path.join(cpp_core_dir, "graph.cpp"),
            os.path.join(cpp_core_dir, "constraints.cpp"),
            os.path.join(cpp_core_dir, "scheduler_core.cpp"),
        ],
        include_dirs=[cpp_core_dir],
        language="c++",
        extra_compile_args=['/std:c++17'] if sys.platform == 'win32' else ['-std=c++17', '-O3'],
        extra_link_args=[]
    )
]

setup(
    name="UTP Scheduler",
    version="1.0.0",
    description="University Timetable Planning Scheduler",
    ext_modules=cythonize(extensions, compiler_directives={'language_level': "3"}),
    zip_safe=False,
)

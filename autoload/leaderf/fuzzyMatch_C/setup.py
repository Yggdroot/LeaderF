# -*- coding: utf-8 -*-
import os
import platform
import subprocess
import sys

try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext
except ImportError:
    print("\nsetuptools is not installed. Attempting to install...")
    print(" ".join([sys.executable, "-m", "pip", "install", "setuptools"]))
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools"])
        from setuptools import setup, Extension
        from setuptools.command.build_ext import build_ext
    except Exception as e:
        print("\nFailed to install setuptools: {}".format(e))
        print("Please turn to https://stackoverflow.com/questions/69919970/no-module-named-distutils-util-but-distutils-is-installed/76691103#76691103 for help")
        sys.exit(1)

class BuildExt(build_ext):
    def build_extensions(self):
        if os.name == 'nt' and "MSC" in platform.python_compiler():
            pass
        elif os.name == 'posix':
            for ext in self.extensions:
                ext.extra_compile_args = ['-std=c99']
        build_ext.build_extensions(self)

if os.name == 'nt':
    module1 = Extension(
        "fuzzyMatchC",
        sources=["fuzzyMatch.cpp"],
    )

    module2 = Extension(
        "fuzzyEngine",
        sources=["fuzzyMatch.cpp", "fuzzyEngine.cpp"],
    )
else:
    module1 = Extension(
        "fuzzyMatchC",
        sources=["fuzzyMatch.c"],
    )

    module2 = Extension(
        "fuzzyEngine",
        sources=["fuzzyMatch.c", "fuzzyEngine.c"],
    )

setup(
    name="fuzzyEngine",
    version="2.0",
    description="Fuzzy match algorithm written in C.",
    author="Yggdroot",
    author_email="archofortune@gmail.com",
    url="https://github.com/Yggdroot/LeaderF",
    license="Apache License 2.0",
    ext_modules=[module1, module2],
    cmdclass={"build_ext": BuildExt},
)

# -*- coding: utf-8 -*-
import os
import platform
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class BuildExt(build_ext):
    def build_extensions(self):
        if os.name == 'nt' and "MSC" in platform.python_compiler():
            for ext in self.extensions:
                ext.extra_compile_args = ['/TP']
        elif os.name == 'posix':
            for ext in self.extensions:
                ext.extra_compile_args = ['-std=c99', '-O2']
        build_ext.build_extensions(self)

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

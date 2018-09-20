# -*- coding: utf-8 -*-
import os

try:
    from setuptools import setup
    from setuptools import Extension
except ImportError:
    from distutils.core import setup
    from distutils.extension import Extension

if os.name == 'nt':
    from distutils.msvccompiler import get_build_version

    if get_build_version() < 14.0: # Visual Studio 2015
        if get_build_version() >= 8.0:
            from distutils.msvc9compiler import MSVCCompiler
        else:
            from distutils.msvccompiler import MSVCCompiler

        # Because the msvc compiler does not support c99,
        # treat .c files as .cpp files
        MSVCCompiler._c_extensions = []
        MSVCCompiler._cpp_extensions = ['.c', '.cc', '.cpp', '.cxx']


module1 = Extension("fuzzyMatchC",
                    sources = ["fuzzyMatch.c"])

module2 = Extension("fuzzyEngine",
                    sources = ["fuzzyMatch.c", "fuzzyEngine.c"])


setup(name = "fuzzyEngine",
      version = "2.0",
      description = "fuzzy match algorithm written in C.",
      author = "Yggdroot",
      author_email = "archofortune@gmail.com",
      url = "https://github.com/Yggdroot/LeaderF",
      license = "Apache License 2.0",
      ext_modules = [module1, module2]
      )

# -*- coding: utf-8 -*-

from distutils.core import setup, Extension

module = Extension("fuzzyMatchC",
                    sources = ["fuzzyMatch.c"])

setup(name = "fuzzyMatchC",
      version = "1.0",
      description = "fuzzy match algorithm written in C.",
      author = "Yggdroot",
      author_email = "archofortune@gmail.com",
      url = "https://github.com/Yggdroot/LeaderF",
      license = "Apache License 2.0",
      ext_modules = [module]
      )

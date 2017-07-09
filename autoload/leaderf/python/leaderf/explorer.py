#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

if sys.version_info >= (3,0):
    from .explorer3 import Explorer
else:
    from .explorer2 import Explorer

__all__ = ['Explorer']

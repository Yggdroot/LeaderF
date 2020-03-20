#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from .utils import *

_icons = set(lfEval("values(get(g:, 'WebDevIconsUnicodeDecorateFileNodesPatternSymbols', {}))"))
_icons = _icons.union(set(lfEval("values(get(g:, 'WebDevIconsUnicodeDecorateFileNodesExactSymbols', {}))")))
_icons = _icons.union(set(lfEval("values(get(g:, 'WebDevIconsUnicodeDecorateFileNodesExtensionSymbols', {}))")))

_icons.add(lfEval("get(g:, 'WebDevIconsUnicodeDecorateFolderNodesDefaultSymbol', '')"))
_icons.add(lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesDefaultSymbol', '')"))

def getWebDevIconsGetFileTypeSymbol(file, isdir=False):
    isdir = 1 if isdir else 0
    return lfEval('WebDevIconsGetFileTypeSymbol("{}", {})'.format(file, isdir))

def removeDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        line = args[1]
        if isStartDevIcons(line):
            _args = list(args)
            _args[1] = line[1:].lstrip()
            args = tuple(_args)
        return func(*args, **kwargs)
    return deco

def isStartDevIcons(line):
    return any(map(lambda x: line.startswith(x), _icons))

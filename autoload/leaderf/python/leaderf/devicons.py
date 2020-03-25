#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from functools import wraps
from .utils import *

fileNodesDefaultSymbol = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesDefaultSymbol', '')")

fileNodesExactSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExactSymbols', {})")
fileNodesExtensionSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExtensionSymbols', {})")

_ambiwidth = lfEval('&ambiwidth')

_icons = set()
_icons = _icons.union(set(fileNodesExactSymbols.values()))
_icons = _icons.union(set(fileNodesExtensionSymbols.values()))
_icons.add(fileNodesDefaultSymbol)

_iconBytesLen = 0

def removeDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        is_list = isinstance(args[1], list)

        lines = args[1] if is_list else [args[1]]

        res_lines = []
        for line in lines:
            b_line = lfByteArray(line)
            if isStartDevIcons(lfBytes2Str(b_line, encoding="utf-8")):
                b_line = b_line[webDevIconsBytesLen():]
                line = lfBytes2Str(b_line, encoding="utf-8")
            res_lines.append(line)

        _args = list(args)
        _args[1] = res_lines if is_list else res_lines[0]

        args = tuple(_args)
        return func(*args, **kwargs)
    return deco

def isStartDevIcons(line):
    return line[0] in _icons

def _getExt(file):
    idx = file.rfind('.')
    return '' if idx == -1 else file[idx+1:]

def setAmbiwidth(val):
    global _ambiwidth
    _ambiwidth = val

# from vim-devicons
# To use asynchronously
def webDevIconsGetFileTypeSymbol(file):
    fileNode = getBasename(file).lower()
    fileNodeExt = _getExt(fileNode)

    symbol = fileNodesDefaultSymbol

    if fileNode in fileNodesExactSymbols:
        symbol = fileNodesExactSymbols[fileNode]
    elif fileNodeExt in fileNodesExtensionSymbols:
        symbol = fileNodesExtensionSymbols[fileNodeExt]

    if _ambiwidth == 'double':
        spaces = ' '
    else:
        # Required to display the font correctly.
        spaces = '  '

    return symbol + spaces

def webDevIconsBytesLen():
    global _iconBytesLen
    if _iconBytesLen == 0:
        _iconBytesLen = lfBytesLen(webDevIconsGetFileTypeSymbol('txt'))
    return _iconBytesLen

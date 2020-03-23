#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from functools import wraps
from .utils import *

appendArtifactFix = lfEval("get(g:, 'DevIconsAppendArtifactFix', 0)") == "1"
artifactFixChar = lfEval("get(g:, 'DevIconsArtifactFixChar', '')")

fileNodesDefaultSymbol = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesDefaultSymbol', '')")

fileNodesExactSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExactSymbols', {})")
fileNodesPatternSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesPatternSymbols', {})")
fileNodesExtensionSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExtensionSymbols', {})")

_icons = set()
_icons = _icons.union(set(fileNodesExactSymbols.values()))
_icons = _icons.union(set(fileNodesPatternSymbols.values()))
_icons = _icons.union(set(fileNodesExtensionSymbols.values()))
_icons.add(fileNodesDefaultSymbol)

_iconBytesLen = 0

# compile
compiledFileNodesPatternSymbols = {}
for [pattern, glyph] in fileNodesPatternSymbols.items():
    compiledFileNodesPatternSymbols[re.compile(pattern)] = glyph


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
    return '' if idx == -1 else file[idx+1:].lower()

# from vim-devicons
# To use asynchronously
def webDevIconsGetFileTypeSymbol(file):
    fileNode = getBasename(file).lower()
    fileNodeExt = _getExt(file)

    symbol = fileNodesDefaultSymbol

    for [pattern, glyph] in compiledFileNodesPatternSymbols.items():
        if pattern.search(fileNode):
            symbol = glyph
            break

    if symbol == fileNodesDefaultSymbol:
        if fileNode in fileNodesExactSymbols:
            symbol = fileNodesExactSymbols[fileNode]
        elif fileNodeExt in fileNodesExtensionSymbols:
            symbol = fileNodesExtensionSymbols[fileNodeExt]

    if appendArtifactFix:
        artifactFix = artifactFixChar
    else:
        artifactFix = ''

    return symbol + artifactFix

def webDevIconsBytesLen():
    global _iconBytesLen
    if _iconBytesLen == 0:
        _iconBytesLen = lfBytesLen(webDevIconsGetFileTypeSymbol('txt'))
    return _iconBytesLen

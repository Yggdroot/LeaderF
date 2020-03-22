#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from functools import wraps
from .utils import *

enableFolderPatternMatching = lfEval("get(g:, 'DevIconsEnableFolderPatternMatching', 0)") == "1"
enableFolderExtensionPatternMatching = lfEval("get(g:, 'DevIconsEnableFolderExtensionPatternMatching', 0)") == "1"
appendArtifactFix = lfEval("get(g:, 'DevIconsAppendArtifactFix', 0)") == "1"
artifactFixChar = lfEval("get(g:, 'DevIconsArtifactFixChar', '')")

folderNodesDefaultSymbol = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFolderNodesDefaultSymbol', '')")
fileNodesDefaultSymbol = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesDefaultSymbol', '')")

fileNodesExactSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExactSymbols', '{}')")
fileNodesPatternSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesPatternSymbols', '{}')")
fileNodesExtensionSymbols = lfEval("get(g:, 'WebDevIconsUnicodeDecorateFileNodesExtensionSymbols', '{}')")

_icons = set()
_icons = _icons.union(set(fileNodesExactSymbols.values()))
_icons = _icons.union(set(fileNodesPatternSymbols.values()))
_icons = _icons.union(set(fileNodesExtensionSymbols.values()))
_icons.add(fileNodesDefaultSymbol)
_icons.add(folderNodesDefaultSymbol)

_iconBytesLen = 0

_iconBytesLen = 0

def removeDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        is_list = isinstance(args[1], list)

        lines = args[1] if is_list else [args[1]]

        lines = [
            line if not isStartDevIcons(line) else line[1:].lstrip() for line in lines
        ]

        _args = list(args)
        _args[1] = lines if is_list else lines[0]

        args = tuple(_args)
        return func(*args, **kwargs)
    return deco

def isStartDevIcons(line):
    return any(map(lambda x: line.startswith(x), _icons))

# from vim-devicons
# To use asynchronously
def webDevIconsGetFileTypeSymbol(file, isdir=False):
    fileNode = getBasename(file).lower()
    fileNodeExt = os.path.splitext(file)[-1][1:].lower()

    if not isdir or enableFolderPatternMatching:
        symbol = fileNodesDefaultSymbol

        for [pattern, glyph] in fileNodesPatternSymbols.items():
            if re.search(pattern, fileNode):
                symbol = glyph
                break

        if symbol == fileNodesDefaultSymbol:
            if fileNode in fileNodesExactSymbols:
                symbol = fileNodesExactSymbols[fileNode]
            elif ((isdir and enableFolderExtensionPatternMatching) or not isdir) and fileNodeExt in fileNodesExtensionSymbols:
                symbol = fileNodesExtensionSymbols[fileNodeExt]
            elif isdir:
                symbol = folderNodesDefaultSymbol
    else:
        symbol = folderNodesDefaultSymbol

    if appendArtifactFix:
        artifactFix = artifactFixChar
    else:
        artifactFix = ''

    return symbol + artifactFix

def webDevIconsBytesLen():
    global _iconBytesLen
    if _iconBytesLen == 0:
        _iconBytesLen = lfBytesLen(webDevIconsGetFileTypeSymbol('', True))
    return _iconBytesLen

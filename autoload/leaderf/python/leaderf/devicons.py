#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import vim
from functools import wraps
from .utils import *

# thanks for the icons from https://github.com/ryanoasis/vim-devicons and https://github.com/LinArcX/mpi
fileNodesDefaultSymbol = ''
folderNodesDefaultSymbol = ''

fileNodesExactSymbols = {
        'exact-match-case-sensitive-1.txt' : '1',
        'exact-match-case-sensitive-2'     : '2',
        'gruntfile.coffee'                 : '',
        'gruntfile.js'                     : '',
        'gruntfile.ls'                     : '',
        'gulpfile.coffee'                  : '',
        'gulpfile.js'                      : '',
        'gulpfile.ls'                      : '',
        'mix.lock'                         : '',
        'dropbox'                          : '',
        '.ds_store'                        : '',
        '.gitconfig'                       : '',
        '.gitignore'                       : '',
        '.gitlab-ci.yml'                   : '',
        '.bashrc'                          : '',
        '.zshrc'                           : '',
        '.vimrc'                           : '',
        '.gvimrc'                          : '',
        '_vimrc'                           : '',
        '_gvimrc'                          : '',
        '.bashprofile'                     : '',
        'favicon.ico'                      : '',
        'license'                          : '',
        'node_modules'                     : '',
        'react.jsx'                        : '',
        'procfile'                         : '',
        'dockerfile'                       : '',
        'docker-compose.yml'               : '',
        }

fileNodesExtensionSymbols = {
        'L'          : '', 'erl'       : '', 'ksh'     : '',  'rbw'         : '',
        'Rmd'        : '', 'es'        : '', 'less'    : '',  'rej'         : '',
        'Smd'        : '', 'ex'        : '', 'lhs'     : '',  'rlib'        : '',
        'ai'         : '', 'exs'       : '', 'lisp'    : '',  'rmd'         : '',
        'awk'        : '', 'f#'        : '', 'lock'    : '',  'rmeta'       : '',
        'bash'       : '', 'fish'      : '', 'log'     : '',  'rs'          : '',
        'bat'        : '', 'fs'        : '', 'lsp'     : '',  'rss'         : '',
        'bin'        : '', 'fsi'       : '', 'lua'     : '',  'sass'        : '',
        'bmp'        : '', 'fsscript'  : '', 'markdown': '',  'scala'       : '',
        'c'          : '', 'fsx'       : '', 'md'      : '',  'scss'        : '',
        'c++'        : '', 'ft'        : '', 'mdown'   : '',  'sh'          : '',
        'cc'         : '', 'fth'       : '', 'mdwn'    : '',  'slim'        : '',
        'chs'        : '', 'gif'       : '', 'mjs'     : '',  'sln'         : '',
        'cl'         : '', 'go'        : '', 'mkd'     : '',  'smd'         : '',
        'clj'        : '', 'gz'        : '', 'mkdn'    : '',  'so'          : '',
        'cljc'       : '', 'h'         : '', 'ml'      : 'λ',  'sql'         : '',
        'cljs'       : '', 'h32'       : '', 'mli'     : 'λ',  'styl'        : '',
        'cljx'       : '', 'hbs'       : '', 'mll'     : 'λ',  'suo'         : '',
        'coffee'     : '', 'hex'       : '', 'mly'     : 'λ',  'swift'       : '',
        'conf'       : '', 'hh'        : '', 'msql'    : '',  'sys'         : '',
        'cp'         : '', 'hpp'       : '', 'mustache': '',  't'           : '',
        'cpp'        : '', 'hrl'       : '', 'mysql'   : '',  'timestamp'   : '﨟',
        'cs'         : '', 'hs'        : '', 'php'     : '',  'toml'        : '',
        'csh'        : '', 'hs-boot'   : '', 'phtml'   : '',  'ts'          : '',
        'csproj'     : '', 'htm'       : '', 'pl'      : '',  'tsx'         : '',
        'csproj.user': '', 'html'      : '', 'plist'   : '况', 'twig'        : '',
        'css'        : '', 'hxx'       : '', 'pm'      : '',  'txt'         : '',
        'ctp'        : '', 'icn'       : '', 'png'     : '',  'ui'          : '',
        'cxx'        : '', 'ico'       : '', 'pp'      : '',  'vim'         : '',
        'd'          : '', 'ini'       : '', 'ps1'     : '',  'vue'         : '﵂',
        'dart'       : '', 'jav'       : '', 'psb'     : '',  'wpl'         : '',
        'db'         : '', 'java'      : '', 'psd'     : '',  'wsdl'        : '',
        'diff'       : '', 'javascript': '', 'ptl'     : '',  'xcplayground': '',
        'dump'       : '', 'jl'        : '', 'py'      : '',  'xht'         : '',
        'dylib'      : '', 'jpeg'      : '', 'pyc'     : '',  'xhtml'       : '',
        'edn'        : '', 'jpg'       : '', 'pyd'     : '',  'xlf'         : '',
        'eex'        : '', 'js'        : '', 'pyi'     : '',  'xliff'       : '',
        'ejs'        : '', 'json'      : '', 'pyo'     : '',  'xmi'         : '',
        'el'         : '', 'jsonp'     : '', 'pyw'     : '',  'xml'         : '',
        'elm'        : '', 'jsx'       : '', 'rb'      : '',  'xul'         : '',
        'yaml'       : '', 'yaws'      : '', 'yml'     : '',  'zip'         : '',
        'zsh'        : '',
        }

_ambiwidth = lfEval('&ambiwidth')

_iconBytesLen = 0

_default_palette = {
    "gui": "NONE",
    "guifg": "NONE",
    "guibg": "NONE",
    "cterm": "NONE",
    "ctermfg": "NONE",
    "ctermbg": "NONE",
}

RE_CANNOT_USE_FOR_HIGHLIGHT = re.compile(r'[^a-zA-Z0-9_]+')

def _icons_setup():
    symbols = set()
    symbols = symbols.union(set(fileNodesExactSymbols.values()))
    symbols = symbols.union(set(fileNodesExtensionSymbols.values()))
    symbols.add(fileNodesDefaultSymbol)

    names = set()
    names = names.union(set(fileNodesExactSymbols.keys()))
    names = names.union(set(fileNodesExtensionSymbols.keys()))
    names.add('default')

    return {'names': names, 'symbols': symbols}


_icons = _icons_setup()

def webDevIconsString():
    if _ambiwidth == 'double':
        return ' ' + fileNodesDefaultSymbol
    else:
        return '  ' + fileNodesDefaultSymbol

def webDevIconsStrLen():
    return len(webDevIconsString())

def webDevIconsBytesLen():
    global _iconBytesLen
    if _iconBytesLen == 0:
        _iconBytesLen = lfBytesLen(webDevIconsString())
    return _iconBytesLen

def removeDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.vars.get('Lf_ShowDevIcons', True):
            is_list = isinstance(args[1], list)

            lines = args[1] if is_list else [args[1]]

            res_lines = []
            for line in lines:
                res_lines.append(line[webDevIconsStrLen():])

            _args = list(args)
            _args[1] = res_lines if is_list else res_lines[0]

            args = tuple(_args)
        return func(*args, **kwargs)
    return deco

def _getExt(file):
    idx = file.rfind('.')
    return '' if idx == -1 else file[idx+1:]

def setAmbiwidth(val):
    global _ambiwidth
    _ambiwidth = val
    _iconBytesLen = lfBytesLen(webDevIconsString())

# To use asynchronously
def webDevIconsGetFileTypeSymbol(file, isdir=False):
    if isdir:
        symbol = folderNodesDefaultSymbol
    else:
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

def _normalize_name(val):
    # Replace unavailable characters for highlights with __
    # [^a-zA-Z0-9_]
    return RE_CANNOT_USE_FOR_HIGHLIGHT.sub('__', val)

def _matchadd(icons, pattern, priority, winid):
    """
    Enable ignore case (\c flag)
    """
    ids = []
    pattern = r'\c' + pattern
    for [name, glyph] in icons.items():
        tmp_pattern = pattern.replace("__icon__", glyph)
        tmp_pattern = tmp_pattern.replace("__name__", name.replace(".", r"\."))

        group_name = "Lf_hl_devIcons_" + _normalize_name(name)

        if winid:
            lfCmd(
                """call win_execute({:d}, 'let matchid = matchadd(''{:s}'', ''{:s}'')')""".format(
                    winid, group_name, tmp_pattern
                )
            )
            id = int(lfEval("matchid"))
        else:
            id = int(lfEval("matchadd('{:s}', '{:s}')".format(group_name, tmp_pattern)))
        ids.append(id)
    return ids

def matchaddDevIconsDefault(pattern, winid=None):
    """
    pattern:
        It will be converted to the following
          __icon__ => icon

    e,g,.: "__icon__\ze\s\+\S\+\($\|\s\)"
           "\ze\s\+\S\+\($\|\s\)"
    """
    def convertor(pattern, _, glyph):
        return pattern.replace('__icon__', glyph)

    return _matchadd({'default': fileNodesDefaultSymbol}, pattern, 9, winid)

def matchaddDevIconsExact(pattern, winid=None):
    """
    pattern:
        It will be converted to the following
          __icon__  => icon
          __name__  => exact string

    e,g,.: r"__icon__\ze\s\+__name__\($\|\s\)"
           r"\ze\s\+\.vimrc\($\|\s\)"
    """
    return _matchadd(fileNodesExactSymbols, pattern, 8, winid)

def matchaddDevIconsExtension(pattern, winid=None):
    """
    pattern:
        It will be converted to the following
          __icon__  => icon
          __name__  => extension string

    e,g,.: r"__icon__\ze\s\+\S\+\.__name__\($\|\s\)"
           r"__icon__\ze\s\+\S\+\.vim\($\|\s\)"
    """
    return _matchadd(fileNodesExtensionSymbols, pattern, 7, winid)

def highlightDevIcons():
    icon_font = lfEval("get(g:, 'Lf_DevIconsFont', '')")

    devicons_palette = lfEval("get(g:, 'Lf_DevIconsPallete', {})")
    palette = devicons_palette.get(lfEval('&background'), {})

    for icon_name in _icons['names']:
        name = _normalize_name(icon_name)

        if icon_name in palette:
            plt = palette[icon_name]
        else:
            plt = palette.get("_", _default_palette)

        hi_cmd = "hi def Lf_hl_devIcons_{name} gui={gui} guifg={guifg} guibg={guibg} cterm={cterm} ctermfg={ctermfg} ctermbg={ctermbg}".format(
            name=name,
            gui=plt.get("gui", "NONE"),
            guifg=plt.get("guifg", "NONE"),
            guibg=plt.get("guibg", "NONE"),
            cterm=plt.get("cterm", "NONE"),
            ctermfg=plt.get("ctermfg", "NONE"),
            ctermbg=plt.get("ctermbg", "NONE"),
        )
        if 'font' in plt:
            hi_cmd += " font='{}'".format(plt.get('font'))
        elif icon_font != '':
            hi_cmd += " font='{}'".format(icon_font)

        lfCmd(hi_cmd)

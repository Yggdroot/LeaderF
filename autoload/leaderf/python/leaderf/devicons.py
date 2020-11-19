#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
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
fileNodesExactSymbols.update(lfEval("get(g:, 'Lf_DevIconsExactSymbols', {})"))

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
fileNodesExtensionSymbols.update(lfEval("get(g:, 'Lf_DevIconsExtensionSymbols', {})"))

devicons_palette = {
        'light': {
            '_':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'default':      { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            '.gvimrc':      { 'guifg': '#007F00', 'ctermfg': '28'   },
            '.vimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            '_gvimrc':      { 'guifg': '#007F00', 'ctermfg': '28'   },
            '_vimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            'ai':           { 'guifg': '#F37021', 'ctermfg': '202'  },
            'awk':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'bash':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'bat':          { 'guifg': '#7ab8b8', 'ctermfg': '109'  },
            'bmp':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'c':            { 'guifg': '#005f91', 'ctermfg': '24'   },
            'c++':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            'cc':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            'chs':          { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            'cl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'clj':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            'cljc':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            'cljs':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            'cljx':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            'coffee':       { 'guifg': '#6f4e37', 'ctermfg': '58'   },
            'conf':         { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            'cp':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            'cpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            'cs':           { 'guifg': '#368832', 'ctermfg': '28'   },
            'csh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'css':          { 'guifg': '#1572b6', 'ctermfg': '25'   },
            'cxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            'd':            { 'guifg': '#b03931', 'ctermfg': '124'  },
            'dart':         { 'guifg': '#66c3fa', 'ctermfg': '81'   },
            'db':           { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            'diff':         { 'guifg': '#dd4c35', 'ctermfg': '166'  },
            'dump':         { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            'edn':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            'eex':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            'ejs':          { 'guifg': '#90a93a', 'ctermfg': '106'  },
            'el':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'elm':          { 'guifg': '#5fb4cb', 'ctermfg': '74'   },
            'erl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            'es':           { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'ex':           { 'guifg': '#6f567e', 'ctermfg': '60'   },
            'exs':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            'f#':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            'fish':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'fs':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            'fsi':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            'fsscript':     { 'guifg': '#378bba', 'ctermfg': '31'   },
            'fsx':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            'gif':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'go':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'gvimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            'h':            { 'guifg': '#984c93', 'ctermfg': '96'   },
            'hbs':          { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'hh':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            'hpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            'hrl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            'hs':           { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            'hs-boot':      { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            'htm':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'html':         { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'hxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            'ico':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'ini':          { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            'java':         { 'guifg': '#5382a1', 'ctermfg': '67'   },
            'javascript':   { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'jl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'jpeg':         { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'jpg':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'js':           { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'json':         { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'jsx':          { 'guifg': '#00a6ff', 'ctermfg': '39'   },
            'ksh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'leex':         { 'guifg': '#6f567e', 'ctermfg': '60'   },
            'less':         { 'guifg': '#2a4f84', 'ctermfg': '24'   },
            'lhs':          { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            'lua':          { 'guifg': '#3e6dbf', 'ctermfg': '25'   },
            'markdown':     { 'guifg': '#755838', 'ctermfg': '94'   },
            'md':           { 'guifg': '#755838', 'ctermfg': '94'   },
            'mdx':          { 'guifg': '#755838', 'ctermfg': '94'   },
            'mjs':          { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'ml':           { 'guifg': '#a1a1a1', 'ctermfg': '246'  },
            'mli':          { 'guifg': '#a1a1a1', 'ctermfg': '246'  },
            'mustache':     { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'php':          { 'guifg': '#6280b6', 'ctermfg': '67'   },
            'pl':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'pm':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'png':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'pp':           { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'ps1':          { 'guifg': '#af4343', 'ctermfg': '124'  },
            'psb':          { 'guifg': '#00ade6', 'ctermfg': '38'   },
            'psd':          { 'guifg': '#00ade6', 'ctermfg': '38'   },
            'py':           { 'guifg': '#366994', 'ctermfg': '24'   },
            'pyc':          { 'guifg': '#366994', 'ctermfg': '24'   },
            'pyd':          { 'guifg': '#366994', 'ctermfg': '24'   },
            'pyi':          { 'guifg': '#366994', 'ctermfg': '24'   },
            'pyo':          { 'guifg': '#366994', 'ctermfg': '24'   },
            'pyw':          { 'guifg': '#366994', 'ctermfg': '24'   },
            'rb':           { 'guifg': '#871101', 'ctermfg': '88'   },
            'rbw':          { 'guifg': '#871101', 'ctermfg': '88'   },
            'rlib':         { 'guifg': '#817871', 'ctermfg': '101'  },
            'rmd':          { 'guifg': '#755838', 'ctermfg': '94'   },
            'rs':           { 'guifg': '#817871', 'ctermfg': '101'  },
            'rss':          { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'sass':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            'scala':        { 'guifg': '#33bbff', 'ctermfg': '39'   },
            'scss':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            'sh':           { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'slim':         { 'guifg': '#719E40', 'ctermfg': '70'   },
            'sln':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            'sql':          { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            'styl':         { 'guifg': '#1572b6', 'ctermfg': '25'   },
            'suo':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            'swift':        { 'guifg': '#f88535', 'ctermfg': '208'  },
            't':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'toml':         { 'guifg': '#7e7f7f', 'ctermfg': '243'  },
            'ts':           { 'guifg': '#007acc', 'ctermfg': '32'   },
            'tsx':          { 'guifg': '#00a6ff', 'ctermfg': '39'   },
            'twig':         { 'guifg': '#63bf6a', 'ctermfg': '71'   },
            'vim':          { 'guifg': '#007F00', 'ctermfg': '28'   },
            'vimrc':        { 'guifg': '#007F00', 'ctermfg': '28'   },
            'vue':          { 'guifg': '#41b883', 'ctermfg': '36'   },
            'webp':         { 'guifg': '#28b48f', 'ctermfg': '36'   },
            'xcplayground': { 'guifg': '#f88535', 'ctermfg': '208'  },
            'xul':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'yaml':         { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'yml':          { 'guifg': '#d7a723', 'ctermfg': '178'  },
            'zsh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
        },
        'dark': {
            '_':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'default':      { 'guifg': '#d8e698', 'ctermfg': '186' },
            '.gvimrc':      { 'guifg': '#00cc00', 'ctermfg': '40'   },
            '.vimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            '_gvimrc':      { 'guifg': '#00cc00', 'ctermfg': '40'   },
            '_vimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            'ai':           { 'guifg': '#F37021', 'ctermfg': '202'  },
            'awk':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'bash':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'bat':          { 'guifg': '#bedcdc', 'ctermfg': '152'  },
            'bmp':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'c':            { 'guifg': '#44cef6', 'ctermfg': '81'   },
            'c++':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'cc':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'chs':          { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            'cl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'clj':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            'cljc':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            'cljs':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            'cljx':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            'coffee':       { 'guifg': '#bc9372', 'ctermfg': '137'  },
            'conf':         { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            'cp':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'cpp':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'cs':           { 'guifg': '#57c153', 'ctermfg': '71'   },
            'csh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'css':          { 'guifg': '#3199e9', 'ctermfg': '32'   },
            'cxx':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'd':            { 'guifg': '#b03931', 'ctermfg': '124'  },
            'dart':         { 'guifg': '#66c3fa', 'ctermfg': '81'   },
            'db':           { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            'diff':         { 'guifg': '#dd4c35', 'ctermfg': '166'  },
            'dump':         { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            'edn':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            'eex':          { 'guifg': '#957aa5', 'ctermfg': '103'  },
            'ejs':          { 'guifg': '#bed27b', 'ctermfg': '150'  },
            'el':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'elm':          { 'guifg': '#5fb4cb', 'ctermfg': '74'   },
            'erl':          { 'guifg': '#eb0057', 'ctermfg': '197'  },
            'es':           { 'guifg': '#f5de19', 'ctermfg': '220'  },
            'ex':           { 'guifg': '#957aa5', 'ctermfg': '103'  },
            'exs':          { 'guifg': '#957aa5', 'ctermfg': '103'  },
            'f#':           { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            'fish':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'fs':           { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            'fsi':          { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            'fsscript':     { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            'fsx':          { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            'gif':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'go':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'gvimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            'h':            { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'hbs':          { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'hh':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'hpp':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'hrl':          { 'guifg': '#eb0057', 'ctermfg': '197'  },
            'hs':           { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            'hs-boot':      { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            'htm':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'html':         { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'hxx':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            'ico':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'ini':          { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            'java':         { 'guifg': '#abc3ee', 'ctermfg': '153'  },
            'javascript':   { 'guifg': '#f5de19', 'ctermfg': '220'  },
            'jl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            'jpeg':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'jpg':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'js':           { 'guifg': '#f5de19', 'ctermfg': '220'  },
            'json':         { 'guifg': '#f5de19', 'ctermfg': '220'  },
            'jsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            'ksh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'leex':         { 'guifg': '#957aa5', 'ctermfg': '103'  },
            'less':         { 'guifg': '#779dd6', 'ctermfg': '110'  },
            'lhs':          { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            'lua':          { 'guifg': '#658ace', 'ctermfg': '68'   },
            'markdown':     { 'guifg': '#b48d60', 'ctermfg': '137'  },
            'md':           { 'guifg': '#b48d60', 'ctermfg': '137'  },
            'mdx':          { 'guifg': '#b48d60', 'ctermfg': '137'  },
            'mjs':          { 'guifg': '#f5de19', 'ctermfg': '220'  },
            'ml':           { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            'mli':          { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            'mustache':     { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'php':          { 'guifg': '#859cc7', 'ctermfg': '110'  },
            'pl':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'pm':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'png':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'pp':           { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'ps1':          { 'guifg': '#af4343', 'ctermfg': '124'  },
            'psb':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            'psd':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            'py':           { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'pyc':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'pyd':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'pyi':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'pyo':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'pyw':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            'rb':           { 'guifg': '#e52002', 'ctermfg': '160'  },
            'rbw':          { 'guifg': '#e52002', 'ctermfg': '160'  },
            'rlib':         { 'guifg': '#bbb5b0', 'ctermfg': '145'  },
            'rmd':          { 'guifg': '#b48d60', 'ctermfg': '137'  },
            'rs':           { 'guifg': '#bbb5b0', 'ctermfg': '145'  },
            'rss':          { 'guifg': '#00acd7', 'ctermfg': '38'   },
            'sass':         { 'guifg': '#d287da', 'ctermfg': '176'  },
            'scala':        { 'guifg': '#7ce1ff', 'ctermfg': '117'  },
            'scss':         { 'guifg': '#d287da', 'ctermfg': '176'  },
            'sh':           { 'guifg': '#d9b400', 'ctermfg': '178'  },
            'slim':         { 'guifg': '#a0c875', 'ctermfg': '150'  },
            'sln':          { 'guifg': '#0078cc', 'ctermfg': '32'   },
            'sql':          { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            'styl':         { 'guifg': '#3199e9', 'ctermfg': '32'   },
            'suo':          { 'guifg': '#0078cc', 'ctermfg': '32'   },
            'swift':        { 'guifg': '#f88535', 'ctermfg': '208'  },
            't':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            'toml':         { 'guifg': '#9b9898', 'ctermfg': '138'  },
            'ts':           { 'guifg': '#33aaff', 'ctermfg': '39'   },
            'tsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            'twig':         { 'guifg': '#63bf6a', 'ctermfg': '71'   },
            'vim':          { 'guifg': '#00cc00', 'ctermfg': '40'   },
            'vimrc':        { 'guifg': '#00cc00', 'ctermfg': '40'   },
            'vue':          { 'guifg': '#41b883', 'ctermfg': '36'   },
            'webp':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            'xcplayground': { 'guifg': '#f88535', 'ctermfg': '208'  },
            'xul':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            'yaml':         { 'guifg': '#ffe885', 'ctermfg': '222'  },
            'yml':          { 'guifg': '#ffe885', 'ctermfg': '222'  },
            'zsh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
        }
    }

devicons_palette["dark"].update(lfEval("get(get(g:, 'Lf_DevIconsPalette', {}), 'dark', {})"))
devicons_palette["light"].update(lfEval("get(get(g:, 'Lf_DevIconsPalette', {}), 'light', {})"))

if  os.name == 'nt' or lfEval('&ambiwidth') == "double":
    _spaces = ' '
else:
    _spaces = '  '

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
    return fileNodesDefaultSymbol + _spaces

def webDevIconsStrLen():
    return len(webDevIconsString())

def webDevIconsBytesLen():
    return lfBytesLen(webDevIconsString())

def removeDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.vars.get('Lf_ShowDevIcons', True):
            is_list = isinstance(args[1], list)

            lines = args[1] if is_list else [args[1]]

            res_lines = []
            start = webDevIconsStrLen()
            for line in lines:
                res_lines.append(line[start:])

            _args = list(args)
            _args[1] = res_lines if is_list else res_lines[0]

            args = tuple(_args)
        return func(*args, **kwargs)
    return deco

def _getExt(file):
    idx = file.rfind('.')
    return '' if idx == -1 else file[idx+1:]

def setAmbiwidth(val):
    global _spaces
    if os.name == 'nt' or val == "double":
        _spaces = ' '
    else:
        _spaces = '  '

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

    return symbol + _spaces

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
    if not vim.vars.get('Lf_ShowDevIcons', True):
        return

    lfCmd("let g:Lf_highlightDevIconsLoad = 1")
    icon_font = lfEval("get(g:, 'Lf_DevIconsFont', '')")

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

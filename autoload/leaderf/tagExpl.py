#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import fnmatch
import time
from functools import wraps
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *

#*****************************************************
# TagExplorer
#*****************************************************
class TagExplorer(Explorer):
    def __init__(self):
        self._cur_dir = ''
        self._content = []
        self._duplicate_tags = {}

    def _getFileList(self, dir, tagfiles):
        dir = dir if dir.endswith(os.sep) else dir + os.sep
        tag_list = []
        self._content = []
        self._duplicate_tags = {}
        for tagfile in tagfiles:
            with lfOpen(dir + tagfile, 'r+', errors='ignore') as f:
                #read file
                # if the tag file is large , the loading will take a long time  
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("!_TAG_"):
                        continue
                    tag = line.split("\t")[0]
                    if tag not in self._duplicate_tags:
                        tag_list.append(tag)
                        self._duplicate_tags[tag] = 1;
                    else:
                        self._duplicate_tags[tag] = 2;
        return tag_list

    def getContent(self, *args, **kwargs):
        self._tagfiles = vim.eval("tagfiles()")
        dir = os.getcwd()
        if vim.eval("g:Lf_UseMemoryCache") == 0 or dir != self._cur_dir:
            self._cur_dir = dir
            self._content = self._getFileList(dir, self._tagfiles)
        return self._content

    def acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        if file in self._duplicate_tags:
            if self._duplicate_tags[file] == 1:
                vim.command("tag %s" % file)
            else:
                vim.command("tselect %s" % file)
        else:
            return

    def getFreshContent(self, *args, **kwargs):
        self._content = self._getFileList(self._cur_dir, self._tagfiles)
        return self._content

    def getStlFunction(self):
        return 'Tag'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.path.abspath(self._cur_dir)))

    def supportsMulti(self):
        return False 

    def supportsNameOnly(self):
        return False


#*****************************************************
# tagExplManager
#*****************************************************
class TagExplManager(Manager):
    def _getExplClass(self):
        return TagExplorer

    def _defineMaps(self):
        vim.command("call g:LfTagExplMaps()")

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" c : clear all selections')
        help.append('" q : quit')
        help.append('" <F5> : refresh the cache')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

#*****************************************************
# tagExplManager is a singleton
#*****************************************************
tagExplManager = TagExplManager()

__all__ = ['tagExplManager']

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import subprocess
import tempfile
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# FunctionExplorer
#*****************************************************
class FunctionExplorer(Explorer):
    def __init__(self):
        self._ctags = lfEval("g:Lf_Ctags")
        self._func_list = {}       # a dict with (key, value) = (buffer number, taglist)
        self._buf_changedtick = {} # a dict with (key, value) = (buffer number, changedtick)
        self._ctags_options = {
                b"aspvbs": "--asp-kinds=f",
                b"awk": "--awk-kinds=f",
                b"c": "--c-kinds=fp",
                b"cpp": "--c++-kinds=fp",
                b"cs": "--c#-kinds=m",
                b"erlang": "--erlang-kinds=f",
                b"fortran": "--fortran-kinds=f",
                b"java": "--java-kinds=m",
                b"javascript": "--javascript-kinds=f",
                b"lisp": "--lisp-kinds=f",
                b"lua": "--lua-kinds=f",
                b"matlab": "--matlab-kinds=f",
                b"pascal": "--pascal-kinds=f",
                b"php": "--php-kinds=f",
                b"python": "--python-kinds=fm",
                b"ruby": "--ruby-kinds=fF",
                b"scheme": "--scheme-kinds=f",
                b"sh": "--sh-kinds=f",
                b"sql": "--sql-kinds=f",
                b"tcl": "--tcl-kinds=m",
                b"verilog": "--verilog-kinds=f",
                b"vim": "--vim-kinds=f",
                b"go": "--go-kinds=f"   # universal ctags
                }
        for buf in vim.buffers:
            if buf.options["buflisted"]:
                changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buf.number))
                self._buf_changedtick[buf.number] = changedtick

    def getContent(self, *args, **kwargs):
        func_list = []
        if len(args) > 0: # all buffers
            cur_buffer = vim.current.buffer
            for b in vim.buffers:
                if b.options["buflisted"]:
                    if lfEval("bufloaded(%d)" % b.number) == '0':
                        lfCmd("silent hide buffer %d" % b.number)
                    func_list.extend(self._getFunctionList(b))
            if vim.current.buffer is not cur_buffer:
                vim.current.buffer = cur_buffer
        else:
            func_list = self._getFunctionList(vim.current.buffer)
        return func_list

    def _getFunctionList(self, buffer):
        changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buffer.number))
        # there is no change since last call
        if changedtick == self._buf_changedtick.get(buffer.number, -1):
            if buffer.number in self._func_list:
                return self._func_list[buffer.number]
        else:
            self._buf_changedtick[buffer.number] = changedtick

        extra_options = self._ctags_options.get(buffer.options["filetype"], "")

        # {tagname}<Tab>{tagfile}<Tab>{tagaddress};"<Tab>{kind}
        process = subprocess.Popen("{} -n -u --fields=k {} -f- -L- ".format(self._ctags, extra_options),
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        if buffer.options["modified"] == True:
            with tempfile.NamedTemporaryFile(mode='w+',
                                             suffix='_'+os.path.basename(buffer.name),
                                             delete=False) as f:
                for line in buffer[:]:
                    f.write(line + '\n')
                file_name = f.name
            out = process.communicate(lfDecode(file_name))
            os.remove(file_name)
        else:
            out = process.communicate(lfDecode(buffer.name))

        if out[1]:
            lfCmd("echoerr '%s'" % escQuote(out[1].rstrip()))

        if not out[0]:
            return []

        # a list of [tag, file, line, kind]
        output = [line.split('\t') for line in out[0].splitlines()]
        if len(output[0]) < 4:
            lfCmd("echoerr '%s'" % escQuote(out[0].rstrip()))
            return []

        func_list = []
        for _, item  in enumerate(output):
            bufname = buffer.name if vim.options["autochdir"] else lfRelpath(buffer.name)
            line = "{}\t{}\t[{}:{} {}]".format(item[3],
                                               buffer[int(item[2][:-2]) - 1].strip(),
                                               bufname,        # file
                                               item[2][:-2],   # line
                                               buffer.number
                                               )
            func_list.append(line)

        self._func_list[buffer.number] = func_list

        return func_list

    def getStlCategory(self):
        return 'Function'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def isFilePath(self):
        return False

    def removeCache(self, buf_number):
        if buf_number in self._func_list:
            del self._func_list[buf_number]

        if buf_number in self._buf_changedtick:
            del self._buf_changedtick[buf_number]


#*****************************************************
# FunctionExplManager
#*****************************************************
class FunctionExplManager(Manager):
    def __init__(self):
        super(FunctionExplManager, self).__init__()
        self._match_ids = []

    def _getExplClass(self):
        return FunctionExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#functionExplMaps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        # {kind} {code} {file} {line}
        line = line.rsplit("\t", 1)[1][1:-1]    # file:line buf_number
        line_nr, buf_number = line.rsplit(":", 1)[1].split()
        lfCmd("hide buffer +%s %s" % (line_nr, buf_number))
        lfCmd("norm! ^")
        lfCmd("norm! zz")

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the whole line
                  1, return the code
                  2, return the remaining part
        """
        if mode == 0:
            return line[2:]
        elif mode == 1:
            return line.rsplit("\t", 1)[0][2:]
        else:
            return line.rsplit("\t", 1)[1][1:-1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start position of the whole line
                  1, return the start position of code
                  2, return the start position remaining part
        """
        if mode == 0:
            return 2
        elif mode == 1:
            return 2
        else:
            return len(line.rsplit("\t", 1)[0]) + 2

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(FunctionExplManager, self)._afterEnter()
        id = int(lfEval('''matchadd('Lf_hl_funcKind', '^\w')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_funcReturnType', '^\w\t\zs.\{-}\ze\s*[~]\=\w\+\W\{-}[(\[]')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_funcScope', '\w*\(<[^>]*>\)\=::')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_funcName', '^\w\t.\{-}\s*\zs[~]\=\w\+\W\{-}\ze[(\[]')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_funcDirname', '\t\zs\[.*:\d\+ \d\+]$')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_funcLineNum', ':\zs\d\+\ze \d\+]$')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(FunctionExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _supportsRefine(self):
        return True

    def removeCache(self, buf_number):
        self._getExplorer().removeCache(buf_number)


#*****************************************************
# functionExplManager is a singleton
#*****************************************************
functionExplManager = FunctionExplManager()

__all__ = ['functionExplManager']

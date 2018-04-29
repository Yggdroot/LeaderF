#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import subprocess
import tempfile
import itertools
import multiprocessing
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor


#*****************************************************
# FunctionExplorer
#*****************************************************
class FunctionExplorer(Explorer):
    def __init__(self):
        self._ctags = lfEval("g:Lf_Ctags")
        self._func_list = {}       # a dict with (key, value) = (buffer number, taglist)
        self._buf_changedtick = {} # a dict with (key, value) = (buffer number, changedtick)
        self._executor = []
        self._ctags_options = {
                "aspvbs": "--asp-kinds=f",
                "awk": "--awk-kinds=f",
                "c": "--c-kinds=fp",
                "cpp": "--c++-kinds=fp",
                "cs": "--c#-kinds=m",
                "erlang": "--erlang-kinds=f",
                "fortran": "--fortran-kinds=f",
                "java": "--java-kinds=m",
                "javascript": "--javascript-kinds=f",
                "lisp": "--lisp-kinds=f",
                "lua": "--lua-kinds=f",
                "matla": "--matlab-kinds=f",
                "pascal": "--pascal-kinds=f",
                "php": "--php-kinds=f",
                "python": "--python-kinds=fm --language-force=Python",
                "ruby": "--ruby-kinds=fF",
                "scheme": "--scheme-kinds=f",
                "sh": "--sh-kinds=f",
                "sql": "--sql-kinds=f",
                "tcl": "--tcl-kinds=m",
                "verilog": "--verilog-kinds=f",
                "vim": "--vim-kinds=f",
                "go": "--go-kinds=f"   # universal ctags
                }

    def getContent(self, *args, **kwargs):
        if len(args) > 0: # all buffers
            cur_buffer = vim.current.buffer
            for b in vim.buffers:
                if b.options["buflisted"]:
                    if lfEval("bufloaded(%d)" % b.number) == '0':
                        vim.current.buffer = b
            if vim.current.buffer != cur_buffer:
                vim.current.buffer = cur_buffer

            for b in vim.buffers:
                if b.options["buflisted"] and b.name:
                    changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % b.number))
                    if changedtick != self._buf_changedtick.get(b.number, -1):
                        break
            else:
                return list(itertools.chain.from_iterable(self._func_list.values()))

            return itertools.chain.from_iterable(self._getFunctionList())
        else:
            result = self._getFunctionResult(vim.current.buffer)
            if isinstance(result, list):
                return result
            else:
                return self._formatResult(*result)

    def _getFunctionList(self):
        buffers = [b for b in vim.buffers]
        n = multiprocessing.cpu_count()
        for i in range(0, len(vim.buffers), n):
            func_list = []
            exe_result = []
            for b in buffers[i:i+n]:
                if b.options["buflisted"] and b.name:
                    result = self._getFunctionResult(b)
                    if isinstance(result, list):
                        func_list.extend(result)
                    else:
                        exe_result.append(result)
            if not exe_result:
                yield func_list
            else:
                exe_taglist = (self._formatResult(*r) for r in exe_result)
                # list can reduce the flash of screen
                yield list(itertools.chain(func_list, itertools.chain.from_iterable(exe_taglist)))

    def _getFunctionResult(self, buffer):
        if not buffer.name:
            return []
        changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buffer.number))
        # there is no change since last call
        if changedtick == self._buf_changedtick.get(buffer.number, -1):
            if buffer.number in self._func_list:
                return self._func_list[buffer.number]
            else:
                return []
        else:
            self._buf_changedtick[buffer.number] = changedtick

        extra_options = self._ctags_options.get(lfEval("getbufvar(%d, '&filetype')" % buffer.number), "")

        executor = AsyncExecutor()
        self._executor.append(executor)
        if buffer.options["modified"] == True:
            with tempfile.NamedTemporaryFile(mode='w+',
                                             suffix='_'+os.path.basename(buffer.name),
                                             delete=False) as f:
                for line in buffer[:]:
                    f.write(line + '\n')
                file_name = f.name
            # {tagname}<Tab>{tagfile}<Tab>{tagaddress};"<Tab>{kind}
            cmd = '{} -n -u --fields=k {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(file_name))
            result = executor.execute(cmd, cleanup=partial(os.remove, file_name))
        else:
            cmd = '{} -n -u --fields=k {} -f- "{}"'.format(self._ctags, extra_options, lfDecode(buffer.name))
            result = executor.execute(cmd)

        return (buffer, result)

    def _formatResult(self, buffer, result):
        if not buffer.name:
            return []

        # a list of [tag, file, line, kind]
        output = [line.split('\t') for line in result if line is not None]
        if not output:
            return []
        if len(output[0]) < 4:
            lfCmd("echoerr '%s'" % escQuote(str(output[0])))
            return []

        func_list = []
        sorted = True
        lastln = -1

        for _, item  in enumerate(output):
            bufname = buffer.name if vim.options["autochdir"] else lfRelpath(buffer.name)
            try:
                ln = int(item[2][:-2], 0)
            except:
                ln = -1
            if lastln > ln:
                sorted = False
            else:
                lastln = ln
            line = "{}\t{}\t[{}:{} {}]".format(item[3],
                                               buffer[int(item[2][:-2]) - 1].strip(),
                                               bufname,        # file
                                               item[2][:-2],   # line
                                               buffer.number
                                               )

            func_list.append((ln, line))

        if not sorted:
            func_list.sort()

        func_list = [ line for ln, line in func_list ]
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

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []


#*****************************************************
# FunctionExplManager
#*****************************************************
class FunctionExplManager(Manager):
    def __init__(self):
        super(FunctionExplManager, self).__init__()
        self._match_ids = []
        self._orig_line = ''

    def _getExplClass(self):
        return FunctionExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Function#Maps()")
        lfCmd("autocmd BufWipeout * call leaderf#Function#removeCache(expand('<abuf>'))")
        lfCmd("autocmd VimLeave * call leaderf#Function#cleanup()")

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
        lfCmd("setlocal cursorline! | redraw | sleep 100m | setlocal cursorline!")

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

    def startExplorer(self, win_pos, *args, **kwargs):
        super(FunctionExplManager, self).startExplorer(win_pos, *args, **kwargs)
        if (not self._launched) or (len(args) > 0):
            return
        # a postfix bang sign, skip input() and locate cursor
        if kwargs.get('bang', False):
            self._relocateCursor()

    def _pathEqual(self, p1, p2):
        p1 = os.path.normcase(os.path.abspath(p1))
        p2 = os.path.normcase(os.path.abspath(p2))
        return (p1 == p2)

    def _relocateCursor(self):
        inst = self._getInstance()
        orig_name = inst.getOriginalPos()[2].name
        orig_line = inst.getOriginalCursor()[0]
        tags = []
        index = 0
        for line in inst.buffer:
            index += 1
            line = line.rsplit("\t", 1)[1][1:-1]
            filename = line.rsplit(':', 1)[0]
            line_nr = int(line.rsplit(":", 1)[1].split()[0])
            if self._pathEqual(lfDecode(orig_name), filename):
                tags.append((index, filename, line_nr))
        orig_line = int(orig_line)
        last = len(tags) - 1
        while last >= 0:
            if tags[last][2] <= orig_line:
                break
            last -= 1
        if last >= 0:
            index = tags[last][0]
            lfCmd(str(index))

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

    def _previewResult(self, preview):
        if not self._needPreview(preview):
            return

        line = self._getInstance().currentLine
        orig_pos = self._getInstance().getOriginalPos()
        cur_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'BufLeave,WinEnter,BufEnter'
        try:
            vim.current.tabpage, vim.current.window, vim.current.buffer = orig_pos
            self._acceptSelection(line)
        finally:
            vim.current.tabpage, vim.current.window, vim.current.buffer = cur_pos
            vim.options['eventignore'] = saved_eventignore


#*****************************************************
# functionExplManager is a singleton
#*****************************************************
functionExplManager = FunctionExplManager()

__all__ = ['functionExplManager']

#  vim: set ts=4 sw=4 tw=0 et :

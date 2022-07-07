#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import os.path
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
                "cpp": "--c++-kinds=fp --language-force=C++",
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
                "go": "--go-kinds=f",  # universal ctags
                "rust": "--rust-kinds=fPM",  # universal ctags
                "ocaml": "--ocaml-kinds=mf",   # universal ctags
                }
        ctags_opts = lfEval('g:Lf_CtagsFuncOpts')
        for k, v in ctags_opts.items():
            self._ctags_options[k] = v

    def getContent(self, *args, **kwargs):
        if "--all" in kwargs.get("arguments", {}): # all buffers
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
                return itertools.chain.from_iterable(self._func_list.values())

            return itertools.chain.from_iterable(self._getFunctionList())
        else:
            result = self._getFunctionResult(vim.current.buffer)
            if not isinstance(result, list):
                result = self._formatResult(*result)
            func_list = []
            for line in result:
                first, second = line.rsplit("\t", 1)
                func_list.append("{}\t[:{}".format(first, second.rsplit(":", 1)[1]))
            return func_list

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
                yield itertools.chain(func_list, itertools.chain.from_iterable(exe_taglist))

    def _getFunctionResult(self, buffer):
        if not buffer.name or lfEval("bufloaded(%d)" % buffer.number) == '0':
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
            if sys.version_info >= (3, 0):
                tmp_file = partial(tempfile.NamedTemporaryFile, encoding=lfEval("&encoding"))
            else:
                tmp_file = tempfile.NamedTemporaryFile

            with tmp_file(mode='w+', suffix='_'+os.path.basename(buffer.name), delete=False) as f:
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
        if not buffer.name or lfEval("bufloaded(%d)" % buffer.number) == '0':
            return []

        # a list of [tag, file, line, kind]
        output = [line.split('\t') for line in result]
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
        return escQuote(lfEncode(lfGetCwd()))

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
        self._orig_line = ''

    def _getExplClass(self):
        return FunctionExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Function#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        # {kind} {code} {file} {line}
        line = line.rsplit("\t", 1)[1][1:-1]    # file:line buf_number
        line_nr, buf_number = line.rsplit(":", 1)[1].split()
        if kwargs.get("mode", '') == 't':
            buf_name = lfEval("bufname(%s)" % buf_number)
            lfDrop('tab', buf_name, line_nr)
        else:
            lfCmd("hide buffer +%s %s" % (line_nr, buf_number))
        lfCmd("norm! ^zv")
        lfCmd("norm! zz")

        if "preview" not in kwargs:
            lfCmd("setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!")

        if vim.current.window not in self._cursorline_dict:
            self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

        lfCmd("setlocal cursorline")

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
        help.append('" i/<Tab> : switch to input mode')
        help.append('" p : preview the result')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(FunctionExplManager, self)._afterEnter()
        lfCmd("augroup Lf_Function")
        lfCmd("autocmd!")
        lfCmd("autocmd BufWipeout * call leaderf#Function#removeCache(expand('<abuf>'))")
        lfCmd("autocmd VimLeavePre * call leaderf#Function#cleanup()")
        lfCmd("augroup END")
        if self._getInstance().getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcKind'', ''^\w'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcReturnType'', ''^\w\t\zs.\{-}\ze\s*[~]\=\(\w\|[#:]\)\+\W\{-}[(\[]'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcScope'', ''\w*\(<[^>]*>\)\=::'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcName'', ''^\w\t.\{-}\s*\zs[~]\=\(\w\|[#:]\)\+\W\{-}\ze[(\[]'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcDirname'', ''\t\zs\[.*:\d\+ \d\+]$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_funcLineNum'', '':\zs\d\+\ze \d\+]$'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
        else:
            id = int(lfEval('''matchadd('Lf_hl_funcKind', '^\w')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_funcReturnType', '^\w\t\zs.\{-}\ze\s*[~]\=\(\w\|[#:]\)\+\W\{-}[(\[]')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_funcScope', '\w*\(<[^>]*>\)\=::')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_funcName', '^\w\t.\{-}\s*\zs[~]\=\(\w\|[#:]\)\+\W\{-}\ze[(\[]')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_funcDirname', '\t\zs\[.*:\d\+ \d\+]$')'''))
            self._match_ids.append(id)
            id = int(lfEval('''matchadd('Lf_hl_funcLineNum', ':\zs\d\+\ze \d\+]$')'''))
            self._match_ids.append(id)

    def _beforeExit(self):
        super(FunctionExplManager, self)._beforeExit()
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _supportsRefine(self):
        return True

    def removeCache(self, buf_number):
        self._getExplorer().removeCache(buf_number)

    def _previewResult(self, preview):
        if self._getInstance().getWinPos() == 'floatwin':
            self._cli.buildPopupPrompt()

        if lfEval("get(g:, 'Lf_PreviewInPopup', 0)") == '1':
            if self._orig_line != self._getInstance().currentLine:
                self._closePreviewPopup()
            else:
                return

        if not self._needPreview(preview):
            return

        line = self._getInstance().currentLine
        if lfEval("get(g:, 'Lf_PreviewInPopup', 0)") == '1':
            self._previewInPopup(line)
            lfCmd("redraw")
            return

        orig_pos = self._getInstance().getOriginalPos()
        cur_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'BufLeave,WinEnter,BufEnter'
        try:
            vim.current.tabpage, vim.current.window, vim.current.buffer = orig_pos
            self._acceptSelection(line, preview=True)
        finally:
            vim.current.tabpage, vim.current.window, vim.current.buffer = cur_pos
            vim.options['eventignore'] = saved_eventignore

    def _bangEnter(self):
        super(FunctionExplManager, self)._bangEnter()
        if "--all" in self._arguments and not self._is_content_list:
            if lfEval("exists('*timer_start')") == '0':
                lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
                return
            self._callback(bang=True)
            if self._read_finished < 2:
                self._timer_id = lfEval("timer_start(1, 'leaderf#Function#TimerCallback', {'repeat': -1})")
        else:
            self._relocateCursor()

    def _bangReadFinished(self):
        super(FunctionExplManager, self)._bangReadFinished()
        self._relocateCursor()

    def _relocateCursor(self):
        remember_last_status = "--recall" in self._arguments \
                or lfEval("g:Lf_RememberLastSearch") == '1' and self._cli.pattern
        if remember_last_status:
            return

        inst = self._getInstance()
        if inst.empty():
            return
        orig_buf_nr = inst.getOriginalPos()[2].number
        orig_line = inst.getOriginalCursor()[0]
        tags = []
        for index, line in enumerate(inst.buffer, 1):
            line = line.rsplit("\t", 1)[1][1:-1]
            line_nr, buf_number = line.rsplit(":", 1)[1].split()
            line_nr, buf_number = int(line_nr), int(buf_number)
            if orig_buf_nr == buf_number:
                tags.append((index, buf_number, line_nr))

        if self._getInstance().isReverseOrder():
            tags = tags[::-1]

        last = len(tags) - 1
        while last >= 0:
            if tags[last][2] <= orig_line:
                break
            last -= 1
        if last >= 0:
            index = tags[last][0]
            if self._getInstance().getWinPos() == 'popup':
                lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', '%s')"
                        % (self._getInstance().getPopupWinId(), 'leaderf#PopupFilter'))
                lfCmd("""call win_execute(%d, "exec 'norm! %dG'")""" % (self._getInstance().getPopupWinId(), int(index)))

                if lfEval("exists('*leaderf#%s#NormalModeFilter')" % self._getExplorer().getStlCategory()) == '1':
                    lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', '%s')" % (self._getInstance().getPopupWinId(),
                            'leaderf#%s#NormalModeFilter' % self._getExplorer().getStlCategory()))
                else:
                    lfCmd("call leaderf#ResetPopupOptions(%d, 'filter', function('leaderf#NormalModeFilter', [%d]))"
                            % (self._getInstance().getPopupWinId(), id(self)))
            else:
                lfCmd(str(index))
                lfCmd("norm! zz")

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        # {kind} {code} {file} {line}
        line = line.rsplit("\t", 1)[1][1:-1]    # file:line buf_number
        line_nr, buf_number = line.rsplit(":", 1)[1].split()
        buf_number = int(buf_number)

        self._createPopupPreview("", buf_number, line_nr)


#*****************************************************
# functionExplManager is a singleton
#*****************************************************
functionExplManager = FunctionExplManager()

__all__ = ['functionExplManager']

#  vim: set ts=4 sw=4 tw=0 et :

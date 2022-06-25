#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import fnmatch
import time
import locale
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    removeDevIcons,
    matchaddDevIconsDefault,
    matchaddDevIconsExact,
    matchaddDevIconsExtension,
)

def showRelativePath(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if lfEval("g:Lf_ShowRelativePath") == '1':
            # os.path.relpath() is too slow!
            dir = lfGetCwd() if args[0]._cmd_work_dir == "" else args[1]
            cwd_length = len(lfEncode(dir))
            if not dir.endswith(os.sep):
                cwd_length += 1
            return [line[cwd_length:] for line in func(*args, **kwargs)]
        else:
            return func(*args, **kwargs)
    return deco

def showDevIcons(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1":
            content = func(*args, **kwargs)
            # In case of Windows, line feeds may be included when reading from the cache.
            return [format_line(line.rstrip()) for line in content or []]
        else:
            return func(*args, **kwargs)
    return deco

def format_line(line):
    return webDevIconsGetFileTypeSymbol(line) + line


#*****************************************************
# FileExplorer
#*****************************************************
class FileExplorer(Explorer):
    def __init__(self):
        self._cur_dir = ''
        self._content = []
        self._cache_dir = os.path.join(lfEval("g:Lf_CacheDirectory"),
                                       '.LfCache',
                                       'python' + lfEval("g:Lf_PythonVersion"),
                                       'file')
        self._cache_index = os.path.join(self._cache_dir, 'cacheIndex')
        self._external_cmd = None
        self._executor = []
        self._no_ignore = None
        self._cmd_work_dir = ""

    @showDevIcons
    def _readFromFileList(self, files):
        result = []
        for file in files:
            with lfOpen(file, 'r', errors='ignore') as f:
                result += f.readlines()
        return result

    def _exists(self, path, dir):
        """
        return True if `dir` exists in `path` or its ancestor path,
        otherwise return False
        """
        if os.name == 'nt':
            # e.g. C:\\
            root = os.path.splitdrive(os.path.abspath(path))[0] + os.sep
        else:
            root = '/'

        while os.path.abspath(path) != root:
            cur_dir = os.path.join(path, dir)
            if os.path.exists(cur_dir) and os.path.isdir(cur_dir):
                return True
            path = os.path.join(path, "..")

        cur_dir = os.path.join(path, dir)
        if os.path.exists(cur_dir) and os.path.isdir(cur_dir):
            return True

        return False

    def _expandGlob(self, type, glob):
        # is absolute path
        if os.name == 'nt' and re.match(r"^[a-zA-Z]:[/\\]", glob) or glob.startswith('/'):
            if type == "file":
                return glob
            elif type == "dir":
                return os.path.join(glob, '*')
            else:
                return glob
        else:
            if type == "file":
                return "**/" + glob
            elif type == "dir":
                return "**/" + os.path.join(glob, '*')
            else:
                return glob

    def _buildCmd(self, dir, **kwargs):
        if self._cmd_work_dir:
            if os.name == 'nt':
                cd_cmd = 'cd /d "{}" && '.format(dir)
            else:
                cd_cmd = 'cd "{}" && '.format(dir)
        else:
            cd_cmd = ""

        if lfEval("g:Lf_ShowRelativePath") == '1' and self._cmd_work_dir == "":
            dir = os.path.relpath(dir)

        if lfEval("exists('g:Lf_ExternalCommand')") == '1':
            if cd_cmd:
                cmd = cd_cmd + lfEval("g:Lf_ExternalCommand").replace('"%s"', '').replace('%s', '')
            else:
                cmd = lfEval("g:Lf_ExternalCommand") % dir.join('""')
            self._external_cmd = cmd
            return cmd

        if lfEval("g:Lf_UseVersionControlTool") == '1':
            if self._exists(dir, ".git") and lfEval("executable('git')") == '1':
                wildignore = lfEval("g:Lf_WildIgnore")
                if ".git" in wildignore.get("dir", []):
                    wildignore.get("dir", []).remove(".git")
                if ".git" in wildignore.get("file", []):
                    wildignore.get("file", []).remove(".git")
                ignore = ""
                for i in wildignore.get("dir", []):
                    ignore += ' -x "%s"' % i
                for i in wildignore.get("file", []):
                    ignore += ' -x "%s"' % i

                if "--no-ignore" in kwargs.get("arguments", {}):
                    no_ignore = ""
                else:
                    no_ignore = "--exclude-standard"

                if lfEval("get(g:, 'Lf_RecurseSubmodules', 0)") == '1':
                    recurse_submodules = "--recurse-submodules"
                else:
                    recurse_submodules = ""

                if cd_cmd:
                    cmd = cd_cmd + 'git ls-files %s && git ls-files --others %s %s' % (recurse_submodules, no_ignore, ignore)
                else:
                    cmd = 'git ls-files %s "%s" && git ls-files --others %s %s "%s"' % (recurse_submodules, dir, no_ignore, ignore, dir)
                self._external_cmd = cmd
                return cmd
            elif self._exists(dir, ".hg") and lfEval("executable('hg')") == '1':
                wildignore = lfEval("g:Lf_WildIgnore")
                if ".hg" in wildignore.get("dir", []):
                    wildignore.get("dir", []).remove(".hg")
                if ".hg" in wildignore["file"]:
                    wildignore.get("file", []).remove(".hg")
                ignore = ""
                for i in wildignore.get("dir", []):
                    ignore += ' -X "%s"' % self._expandGlob("dir", i)
                for i in wildignore.get("file", []):
                    ignore += ' -X "%s"' % self._expandGlob("file", i)

                if cd_cmd:
                    cmd = cd_cmd + 'hg files %s' % ignore
                else:
                    cmd = 'hg files %s "%s"' % (ignore, dir)
                self._external_cmd = cmd
                return cmd

        if lfEval("exists('g:Lf_DefaultExternalTool')") == '1':
            default_tool = {"rg": 0, "pt": 0, "ag": 0, "find": 0}
            tool = lfEval("g:Lf_DefaultExternalTool")
            if tool and lfEval("executable('%s')" % tool) == '0':
                raise Exception("executable '%s' can not be found!" % tool)
            default_tool[tool] = 1
        else:
            default_tool = {"rg": 1, "pt": 1, "ag": 1, "find": 1}

        if default_tool["rg"] and lfEval("executable('rg')") == '1':
            wildignore = lfEval("g:Lf_WildIgnore")
            if os.name == 'nt': # https://github.com/BurntSushi/ripgrep/issues/500
                color = ""
                ignore = ""
                for i in wildignore.get("dir", []):
                    if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'): # rg does not show hidden files by default
                        ignore += ' -g "!%s"' % i
                for i in wildignore.get("file", []):
                    if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'):
                        ignore += ' -g "!%s"' % i
            else:
                color = "--color never"
                ignore = ""
                for i in wildignore.get("dir", []):
                    if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'):
                        ignore += " -g '!%s'" % i
                for i in wildignore.get("file", []):
                    if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'):
                        ignore += " -g '!%s'" % i

            if lfEval("g:Lf_FollowLinks") == '1':
                followlinks = "-L"
            else:
                followlinks = ""

            if lfEval("g:Lf_ShowHidden") == '0':
                show_hidden = ""
            else:
                show_hidden = "--hidden"

            if "--no-ignore" in kwargs.get("arguments", {}):
                no_ignore = "--no-ignore"
            else:
                no_ignore = ""

            if dir == '.':
                cur_dir = ''
            else:
                cur_dir = '"%s"' % dir

            if cd_cmd:
                cmd = cd_cmd + 'rg --no-messages --files %s %s %s %s %s' % (color, ignore, followlinks, show_hidden, no_ignore)
            else:
                cmd = 'rg --no-messages --files %s %s %s %s %s %s' % (color, ignore, followlinks, show_hidden, no_ignore, cur_dir)
        elif default_tool["pt"] and lfEval("executable('pt')") == '1':
            wildignore = lfEval("g:Lf_WildIgnore")
            ignore = ""
            for i in wildignore.get("dir", []):
                if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'): # pt does not show hidden files by default
                    ignore += " --ignore=%s" % i
            for i in wildignore.get("file", []):
                if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'):
                    ignore += " --ignore=%s" % i

            if lfEval("g:Lf_FollowLinks") == '1':
                followlinks = "-f"
            else:
                followlinks = ""

            if lfEval("g:Lf_ShowHidden") == '0':
                show_hidden = ""
            else:
                show_hidden = "--hidden"

            if "--no-ignore" in kwargs.get("arguments", {}):
                no_ignore = "-U"
            else:
                no_ignore = ""

            if cd_cmd:
                cmd = cd_cmd + 'pt --nocolor %s %s %s %s -g=""' % (ignore, followlinks, show_hidden, no_ignore)
            else:
                cmd = 'pt --nocolor %s %s %s %s -g="" "%s"' % (ignore, followlinks, show_hidden, no_ignore, dir)
        elif default_tool["ag"] and lfEval("executable('ag')") == '1':
            wildignore = lfEval("g:Lf_WildIgnore")
            ignore = ""
            for i in wildignore.get("dir", []):
                if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'): # ag does not show hidden files by default
                    ignore += ' --ignore "%s"' % i
            for i in wildignore.get("file", []):
                if lfEval("g:Lf_ShowHidden") != '0' or not i.startswith('.'):
                    ignore += ' --ignore "%s"' % i

            if lfEval("g:Lf_FollowLinks") == '1':
                followlinks = "-f"
            else:
                followlinks = ""

            if lfEval("g:Lf_ShowHidden") == '0':
                show_hidden = ""
            else:
                show_hidden = "--hidden"

            if "--no-ignore" in kwargs.get("arguments", {}):
                no_ignore = "-U"
            else:
                no_ignore = ""

            if cd_cmd:
                cmd = cd_cmd + 'ag --nocolor --silent %s %s %s %s -g ""' % (ignore, followlinks, show_hidden, no_ignore)
            else:
                cmd = 'ag --nocolor --silent %s %s %s %s -g "" "%s"' % (ignore, followlinks, show_hidden, no_ignore, dir)
        elif default_tool["find"] and lfEval("executable('find')") == '1' \
                and lfEval("executable('sed')") == '1' and os.name != 'nt':
            wildignore = lfEval("g:Lf_WildIgnore")
            ignore_dir = ""
            for d in wildignore.get("dir", []):
                ignore_dir += '-type d -name "%s" -prune -o ' % d

            ignore_file = ""
            for f in wildignore.get("file", []):
                    ignore_file += '-type f -name "%s" -o ' % f

            if lfEval("g:Lf_FollowLinks") == '1':
                followlinks = "-L"
            else:
                followlinks = ""

            if lfEval("g:Lf_ShowRelativePath") == '1':
                strip = "| sed 's#^\./##'"
            else:
                strip = ""

            if os.name == 'nt':
                redir_err = ""
            else:
                redir_err = " 2>/dev/null"

            if lfEval("g:Lf_ShowHidden") == '0':
                show_hidden = '-name ".*" -prune -o'
            else:
                show_hidden = ""

            if cd_cmd:
                cmd = cd_cmd + 'find %s . -name "." -o %s %s %s -type f -print %s %s' % (followlinks,
                                                                                         ignore_dir,
                                                                                         ignore_file,
                                                                                         show_hidden,
                                                                                         redir_err,
                                                                                         strip)
            else:
                cmd = 'find %s "%s" -name "." -o %s %s %s -type f -print %s %s' % (followlinks,
                                                                                   dir,
                                                                                   ignore_dir,
                                                                                   ignore_file,
                                                                                   show_hidden,
                                                                                   redir_err,
                                                                                   strip)
        else:
            cmd = None

        self._external_cmd = cmd

        return cmd


    def getContentFromMultiDirs(self, dirs, **kwargs):
        no_ignore = kwargs.get("arguments", {}).get("--no-ignore")
        if no_ignore != self._no_ignore:
            self._no_ignore = no_ignore
            arg_changes = True
        else:
            arg_changes = False

        dirs = { os.path.abspath(os.path.expanduser(lfDecode(dir.strip('"').rstrip('\\/')))) for dir in dirs }
        if arg_changes or lfEval("g:Lf_UseMemoryCache") == '0' or dirs != self._cur_dir or \
                not self._content:
            self._cur_dir = dirs

            cmd = ''
            for dir in dirs:
                if not os.path.exists(dir):
                    lfCmd("echoe ' Unknown directory `%s`'" % dir)
                    return None

                command = self._buildCmd(dir, **kwargs)
                if command:
                    if cmd == '':
                        cmd = command
                    else:
                        cmd += ' && ' + command

            if cmd:
                executor = AsyncExecutor()
                self._executor.append(executor)
                if cmd.split(None, 1)[0] == "dir":
                    content = executor.execute(cmd, format_line)
                else:
                    if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1":
                        content = executor.execute(cmd, encoding=lfEval("&encoding"), format_line=format_line)
                    else:
                        content = executor.execute(cmd, encoding=lfEval("&encoding"))
                self._cmd_start_time = time.time()
                return content

        return self._content


    def getContent(self, *args, **kwargs):
        files = kwargs.get("arguments", {}).get("--file", [])
        if files:
            return self._readFromFileList(files)

        dir = lfGetCwd()

        self._cmd_work_dir = ""
        directory = kwargs.get("arguments", {}).get("directory")
        if directory and len(directory) > 1:
            return self.getContentFromMultiDirs(directory, **kwargs)

        if directory and directory[0] not in ['""', "''"]:
            dir = directory[0].strip('"').rstrip('\\/')
            if os.path.exists(os.path.expanduser(lfDecode(dir))):
                if lfEval("get(g:, 'Lf_NoChdir', 1)") == '0':
                    lfCmd("silent cd %s" % dir)
                    dir = lfGetCwd()
                else:
                    dir = os.path.abspath(os.path.expanduser(lfDecode(dir)))
                    self._cmd_work_dir = dir
            else:
                lfCmd("echoe ' Unknown directory `%s`'" % dir)
                return None

        no_ignore = kwargs.get("arguments", {}).get("--no-ignore")
        if no_ignore != self._no_ignore:
            self._no_ignore = no_ignore
            arg_changes = True
        else:
            arg_changes = False

        if arg_changes or lfEval("g:Lf_UseMemoryCache") == '0' or dir != self._cur_dir or \
                not self._content:
            self._cur_dir = dir

            cmd = self._buildCmd(dir, **kwargs)
            lfCmd("let g:Lf_Debug_Cmd = '%s'" % escQuote(cmd))

            lfCmd("let g:Lf_FilesFromCache = 0")
            if lfEval("g:Lf_UseCache") == '1' and kwargs.get("refresh", False) == False:
                lfCmd("let g:Lf_FilesFromCache = 1")
                self._content = self._getFilesFromCache()
                if self._content:
                    return self._content

            if cmd:
                executor = AsyncExecutor()
                self._executor.append(executor)
                if cmd.split(None, 1)[0] == "dir":
                    content = executor.execute(cmd, format_line)
                else:
                    if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1":
                        content = executor.execute(cmd, encoding=lfEval("&encoding"), format_line=format_line)
                    else:
                        content = executor.execute(cmd, encoding=lfEval("&encoding"))
                self._cmd_start_time = time.time()
                self._content = list(content)
            else:
                self._content = self._getFileList(dir)
        #f = open('/dev/shm/debug.txt','w')
        #f.write(str(self._content))
        #f.close()
        return self._content

    def getStlCategory(self):
        return 'File'

    def getStlCurDir(self):
        if self._cmd_work_dir:
            return escQuote(lfEncode(self._cmd_work_dir))
        else:
            return escQuote(lfEncode(lfGetCwd()))

    def supportsMulti(self):
        return True

    def supportsNameOnly(self):
        return True

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []


#*****************************************************
# FileExplManager
#*****************************************************
class FileExplManager(Manager):
    def _getExplClass(self):
        return FileExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#File#Maps()")

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" s : select multiple files')
        help.append('" a : select all files')
        help.append('" c : clear all selections')
        help.append('" p : preview the file')
        help.append('" q : quit')
        help.append('" <F5> : refresh the cache')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _nearestAncestor(self, markers, path):
        """
        return the nearest ancestor path(including itself) of `path` that contains
        one of files or directories in `markers`.
        `markers` is a list of file or directory names.
        """
        if os.name == 'nt':
            # e.g. C:\\
            root = os.path.splitdrive(os.path.abspath(path))[0] + os.sep
        else:
            root = '/'

        path = os.path.abspath(path)
        while path != root:
            for name in markers:
                if os.path.exists(os.path.join(path, name)):
                    return path
            path = os.path.abspath(os.path.join(path, ".."))

        for name in markers:
            if os.path.exists(os.path.join(path, name)):
                return path

        return ""

    def _afterEnter(self):
        super(FileExplManager, self)._afterEnter()
        lfCmd("augroup Lf_File")
        lfCmd("autocmd!")
        lfCmd("autocmd VimLeavePre * call leaderf#File#cleanup()")
        lfCmd("augroup END")

        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            winid = self._getInstance().getPopupWinId() if self._getInstance().getWinPos() == 'popup' else None
            icon_pattern = r'^__icon__'
            self._match_ids.extend(matchaddDevIconsExtension(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsExact(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsDefault(icon_pattern, winid))

    def _beforeExit(self):
        super(FileExplManager, self)._beforeExit()
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

    def _bangEnter(self):
        super(FileExplManager, self)._bangEnter()
        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return

        self._workInIdle(bang=True)
        if self._read_finished < 2:
            self._timer_id = lfEval("timer_start(1, 'leaderf#File#TimerCallback', {'repeat': -1})")

    def startExplorer(self, win_pos, *args, **kwargs):
        directory = kwargs.get("arguments", {}).get("directory")
        if directory and directory[0] not in ['""', "''"]: # behavior no change for `LeaderfFile <directory>`
            self._orig_cwd = None
            super(FileExplManager, self).startExplorer(win_pos, *args, **kwargs)
            return

        self._orig_cwd = lfGetCwd()
        root_markers = lfEval("g:Lf_RootMarkers")
        mode = lfEval("g:Lf_WorkingDirectoryMode")
        working_dir = lfEval("g:Lf_WorkingDirectory")

        # https://github.com/neovim/neovim/issues/8336
        if lfEval("has('nvim')") == '1':
            chdir = vim.chdir
        else:
            chdir = os.chdir

        if os.path.exists(working_dir) and os.path.isdir(working_dir):
            chdir(working_dir)
            super(FileExplManager, self).startExplorer(win_pos, *args, **kwargs)
            return

        cur_buf_name = lfDecode(vim.current.buffer.name)
        fall_back = False
        if 'a' in mode:
            working_dir = self._nearestAncestor(root_markers, self._orig_cwd)
            if working_dir: # there exists a root marker in nearest ancestor path
                chdir(working_dir)
            else:
                fall_back = True
        elif 'A' in mode:
            if cur_buf_name:
                working_dir = self._nearestAncestor(root_markers, os.path.dirname(cur_buf_name))
            else:
                working_dir = ""
            if working_dir: # there exists a root marker in nearest ancestor path
                chdir(working_dir)
            else:
                fall_back = True
        else:
            fall_back = True

        if fall_back:
            if 'f' in mode:
                if cur_buf_name:
                    chdir(os.path.dirname(cur_buf_name))
            elif 'F' in mode:
                if cur_buf_name and not os.path.dirname(cur_buf_name).startswith(self._orig_cwd):
                    chdir(os.path.dirname(cur_buf_name))

        super(FileExplManager, self).startExplorer(win_pos, *args, **kwargs)

    @removeDevIcons
    def _previewInPopup(self, *args, **kwargs):
        line = args[0]
        if not os.path.isabs(line):
            if self._getExplorer()._cmd_work_dir:
                line = os.path.join(self._getExplorer()._cmd_work_dir, lfDecode(line))
            else:
                line = os.path.join(self._getInstance().getCwd(), lfDecode(line))
            line = os.path.normpath(lfEncode(line))
        if lfEval("bufloaded('%s')" % escQuote(line)) == '1':
            source = int(lfEval("bufadd('%s')" % escQuote(line)))
        else:
            source = line
        self._createPopupPreview(line, source, 0)

    @removeDevIcons
    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        try:
            if not os.path.isabs(file):
                if self._getExplorer()._cmd_work_dir:
                    file = os.path.join(self._getExplorer()._cmd_work_dir, lfDecode(file))
                else:
                    file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
                file = os.path.normpath(lfEncode(file))

            if kwargs.get("mode", '') == 't':
                if (lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1' and vim.current.buffer.name == ''
                        and vim.current.buffer.number == 1
                        and len(vim.current.tabpage.windows) == 1 and len(vim.current.buffer) == 1
                        and vim.current.buffer[0] == '' and not vim.current.buffer.options["modified"]
                        and not (lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1'
                            and lfEval("bufloaded('%s')" % escQuote(file)) == '1'
                            and len([w for tp in vim.tabpages for w in tp.windows if w.buffer.name == file]) > 0)):
                    lfCmd("setlocal bufhidden=wipe")
                    lfCmd("hide edit %s" % escSpecial(file))
                elif lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('tab', file)
                else:
                    lfCmd("tabe %s" % escSpecial(file))
            else:
                if (lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' or kwargs.get("mode", 'dr')) and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    if (kwargs.get("mode", '') == '' and lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1'
                            and vim.current.buffer.name == ''
                            and vim.current.buffer.number == 1
                            and len(vim.current.buffer) == 1 and vim.current.buffer[0] == ''
                            and not vim.current.buffer.options["modified"]
                            and len([w for w in vim.windows if w.buffer.name == file]) == 0):
                        lfCmd("setlocal bufhidden=wipe")
                    lfDrop('', file)
                else:
                    if (kwargs.get("mode", '') == '' and lfEval("get(g:, 'Lf_DiscardEmptyBuffer', 1)") == '1'
                            and vim.current.buffer.name == ''
                            and vim.current.buffer.number == 1
                            and len(vim.current.buffer) == 1 and vim.current.buffer[0] == ''
                            and not vim.current.buffer.options["modified"]):
                        lfCmd("setlocal bufhidden=wipe")

                    lfCmd("hide edit %s" % escSpecial(file))
        except vim.error: # E37
            lfPrintTraceback()

#*****************************************************
# fileExplManager is a singleton
#*****************************************************
fileExplManager = FileExplManager()

__all__ = ['fileExplManager']

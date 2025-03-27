#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import os.path
import json
import bisect
import tempfile
import itertools
from pathlib import PurePath
from difflib import SequenceMatcher
from itertools import islice
from functools import partial
from enum import Enum
from collections import OrderedDict
from datetime import datetime
from .utils import *
from .explorer import *
from .manager import *
from .diff import LfDiffer
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    matchaddDevIconsDefault,
    matchaddDevIconsExact,
    matchaddDevIconsExtension,
)

def ensureWorkingDirectory(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        try:
            orig_cwd = lfGetCwd()
            changed = False
            if self._project_root != orig_cwd:
                changed = True
                lfChdir(self._project_root)

            return func(self, *args, **kwargs)
        finally:
            if changed:
                lfChdir(orig_cwd)

    return deco

def lfGetFilePath(source):
    """
    source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
    """
    return source[3] if source[4] == "" else source[4]

#*****************************************************
# GitExplorer
#*****************************************************
class GitExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._show_icon = lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1"

    def getContent(self, *args, **kwargs):
        commands = lfEval("leaderf#Git#Commands()")
        return [list(item)[0] for item in commands]

    def formatLine(self, line):
        pass

    def getStlCategory(self):
        return 'Git'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def supportsNameOnly(self):
        return False

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []


class GitDiffExplorer(GitExplorer):
    def __init__(self):
        super(GitDiffExplorer, self).__init__()
        self._source_info = {}

    def supportsNameOnly(self):
        return True

    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})

        if "content" in arguments_dict:
            return arguments_dict["content"]

        executor = AsyncExecutor()
        self._executor.append(executor)

        self._source_info = {}

        cmd = "git diff --no-color --raw --no-abbrev"
        if "--cached" in arguments_dict:
            cmd += " --cached"
        if "extra" in arguments_dict:
            cmd += " " + " ".join(arguments_dict["extra"])
        content = executor.execute(cmd, encoding=lfEval("&encoding"), format_line=self.formatLine)
        return content

    def formatLine(self, line):
        """
        :000000 100644 000000000 5b01d33aa A    runtime/syntax/json5.vim
        :100644 100644 671b269c0 ef52cddf4 M    runtime/syntax/nix.vim
        :100644 100644 69671c59c 084f8cdb4 M    runtime/syntax/zsh.vim
        :100644 100644 b90f76fc1 bad07e644 R099 src/version.c   src/version2.c
        :100644 000000 b5825eb19 000000000 D    src/testdir/dumps

        ':100644 100644 72943a1 dbee026 R050\thello world.txt\thello world2.txt'
        """
        tmp = line.split(sep='\t')
        file_names = (tmp[1], tmp[2] if len(tmp) == 3 else "")
        blob_status = tmp[0].split()
        self._source_info[file_names] = (blob_status[2], blob_status[3], blob_status[4],
                                         file_names[0], file_names[1])
        icon = webDevIconsGetFileTypeSymbol(file_names[0]) if self._show_icon else ""
        return "{:<4} {}{}{}".format(blob_status[4], icon, file_names[0],
                                     "" if file_names[1] == "" else "\t=>\t" + file_names[1] )

    def getStlCategory(self):
        return 'Git_diff'

    def getSourceInfo(self):
        return self._source_info


class GitLogExplorer(GitExplorer):
    def __init__(self):
        super(GitLogExplorer, self).__init__()
        self.orig_name = {}
        self.patches = {}

    def generateContent(self, content):
        for line1, line2, _ in itertools.zip_longest(content, content, content):
            commit_id = line1.split(None, 1)[0]
            self.orig_name[commit_id] = line2
            yield line1

    def generateContentPatches(self, content):
        result = []
        commit = None
        for line in content:
            if line.startswith("$"):
                result.append(line[1:])
                commit = line.split(None, 1)[0].lstrip("$")
                self.patches[commit] = []
            else:
                self.patches[commit].append(line)

        return result

    def getContent(self, *args, **kwargs):
        self.orig_name.clear()
        self.patches = {}

        arguments_dict = kwargs.get("arguments", {})

        executor = AsyncExecutor()
        self._executor.append(executor)

        options = GitLogExplorer.generateOptions(arguments_dict)
        cmd = 'git log {} --pretty=format:"%h%d %s"'.format(options)
        if "--current-file" in arguments_dict and "current_file" in arguments_dict:
            cmd += " --name-only --follow -- {}".format(arguments_dict["current_file"])
        elif "--current-line" in arguments_dict and "current_file" in arguments_dict:
            cmd = 'git log {} --pretty=format:"$%h%d %s"'.format(options)
            cmd += " -L{},{}:{}".format(arguments_dict["current_line_num"],
                                        arguments_dict["current_line_num"],
                                        arguments_dict["current_file"])
            content = executor.execute(cmd, encoding=lfEval("&encoding"))
            return self.generateContentPatches(content)

        if "extra" in arguments_dict:
            cmd += " " + " ".join(arguments_dict["extra"])

        content = executor.execute(cmd, encoding=lfEval("&encoding"))

        if "--current-file" in arguments_dict and "current_file" in arguments_dict:
            return AsyncExecutor.Result(self.generateContent(content))

        return content

    def getStlCategory(self):
        return 'Git_log'

    @staticmethod
    def generateOptions(arguments_dict):
        options = ""
        if "-n" in arguments_dict:
            options += "-n %s " % arguments_dict["-n"][0]

        if "--skip" in arguments_dict:
            options += "--skip %s " % arguments_dict["--skip"][0]

        if "--since" in arguments_dict:
            options += "--since %s " % arguments_dict["--since"][0]

        if "--until" in arguments_dict:
            options += "--until %s " % arguments_dict["--until"][0]

        if "--author" in arguments_dict:
            options += "--author %s " % arguments_dict["--author"][0]

        if "--committer" in arguments_dict:
            options += "--committer %s " % arguments_dict["--committer"][0]

        if "--no-merges" in arguments_dict:
            options += "--no-merges "

        if "--all" in arguments_dict:
            options += "--all "

        if "--graph" in arguments_dict:
            options += "--graph "

        if "--reverse-order" in arguments_dict:
            options += "--reverse "

        return options


class GitCommand(object):
    def __init__(self, arguments_dict, source):
        self._arguments = arguments_dict
        self._source = source
        self._cmd = ""
        self._file_type = ""
        self._file_type_cmd = ""
        self._buffer_name = ""
        self.buildCommandAndBufferName()

    def buildCommandAndBufferName(self):
        pass

    def getCommand(self):
        return self._cmd

    def getFileType(self):
        return self._file_type

    def getFileTypeCommand(self):
        return self._file_type_cmd

    def getBufferName(self):
        return self._buffer_name

    def getArguments(self):
        return self._arguments

    def getSource(self):
        return self._source


class GitDiffCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        """
        source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        super(GitDiffCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        self._cmd = "git diff --no-color"
        extra_options = ""
        if "--cached" in self._arguments:
            extra_options += " --cached"

        if "extra" in self._arguments:
            extra_options += " " + " ".join(self._arguments["extra"])

        if self._source is not None:
            if " -- " not in self._arguments["arg_line"]:
                file_name = lfGetFilePath(self._source)
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                extra_options += " -- {}".format(file_name)
        elif "--current-file" in self._arguments and "current_file" in self._arguments:
            extra_options += " -- {}".format(self._arguments["current_file"])

        self._cmd += extra_options
        self._buffer_name = "LeaderF://git diff" + extra_options
        self._file_type = "diff"
        if lfEval("has('nvim')") == '1':
            self._file_type_cmd = "setlocal filetype=diff"
        else:
            self._file_type_cmd = "silent! doautocmd filetypedetect BufNewFile *.diff"


class GitLogDiffCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        """
        source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        super(GitLogDiffCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        # fuzzy search in navigation panel
        if not self._arguments["parent"].startswith("0000000"):
            self._cmd = "git diff --follow --no-color {}..{} -- {}".format(self._arguments["parent"],
                                                                           self._arguments["commit_id"],
                                                                           lfGetFilePath(self._source)
                                                                           )
        else:
            self._cmd = "git show --pretty= --no-color {} -- {}".format(self._arguments["commit_id"],
                                                                        lfGetFilePath(self._source)
                                                                        )
        self._buffer_name = "LeaderF://" + self._cmd
        self._file_type = "diff"
        if lfEval("has('nvim')") == '1':
            self._file_type_cmd = "setlocal filetype=diff"
        else:
            self._file_type_cmd = "silent! doautocmd filetypedetect BufNewFile *.diff"


class GitCatFileCommand(GitCommand):
    def __init__(self, arguments_dict, source, commit_id):
        """
        source is a tuple like (b90f76fc1, R099, src/version.c)
        """
        self._commit_id = commit_id
        super(GitCatFileCommand, self).__init__(arguments_dict, source)

    @staticmethod
    def buildBufferName(commit_id, source):
        """
        source is a tuple like (b90f76fc1, R099, src/version.c)
        """
        if source[1].startswith("C"):
            return "{}:{}:{}:{}".format(commit_id[:7], source[0][:9], "C", source[2])

        return "{}:{}:{}".format(commit_id[:7], source[0][:9], source[2])

    def buildCommandAndBufferName(self):
        self._cmd = "git cat-file -p {}".format(self._source[0])
        if self._source[0].startswith("0000000"):
            if self._source[1] == "M":
                if os.name == 'nt':
                    self._cmd = "type {}".format(os.path.normpath(self._source[2]))
                else:
                    self._cmd = "cat {}".format(self._source[2])
            else:
                self._cmd = ""

        self._buffer_name = GitCatFileCommand.buildBufferName(self._commit_id, self._source)
        self._file_type_cmd = "silent! doautocmd filetypedetect BufNewFile {}".format(self._source[2])


class GitLogCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        """
        source is a commit id
        """
        super(GitLogCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        if "--directly" in self._arguments:
            options = GitLogExplorer.generateOptions(self._arguments)
            self._cmd = "git log {}".format(options)

            if "extra" in self._arguments:
                self._cmd += " " + " ".join(self._arguments["extra"])

            if "--current-file" in self._arguments and "current_file" in self._arguments:
                self._cmd += " --follow -- {}".format(self._arguments["current_file"])

            self._buffer_name = "LeaderF://" + self._cmd
        elif "--current-line" in self._arguments and "current_file" in self._arguments:
            self._buffer_name = "LeaderF://" + self._source
        else:
            sep = ' ' if os.name == 'nt' else ''
            if "--find-copies-harder" in self._arguments:
                find_copies_harder = " -C"
            else:
                find_copies_harder = ""

            self._cmd = ('git show {} -C{} --pretty=format:"commit %H%nparent %P%n'
                         'Author:     %an <%ae>%nAuthorDate: %ad%nCommitter:  %cn <%ce>%nCommitDate:'
                         ' %cd{}%n%n%s%n%n%b%n%x2d%x2d%x2d" --stat=70 --stat-graph-width=10 --no-color'
                         ' && git log -1 -p --pretty=format:"%x20" --no-color {}'
                         ).format(self._source, find_copies_harder, sep, self._source)

            if (("--recall" in self._arguments or "--current-file" in self._arguments)
                and "current_file" in self._arguments):
                self._cmd = ('git show {} -C{} --pretty=format:"commit %H%nparent %P%n'
                             'Author:     %an <%ae>%nAuthorDate: %ad%nCommitter:  %cn <%ce>%nCommitDate:'
                             ' %cd{}%n%n%s%n%n%b%n%x2d%x2d%x2d" --stat=70 --stat-graph-width=10 --no-color'
                             ' && git log -1 -p --follow --pretty=format:"%x20" --no-color {} -- {}'
                             ).format(self._source, find_copies_harder, sep, self._source,
                                      self._arguments["orig_name"].get(self._source,
                                                                       self._arguments["current_file"]))

            self._buffer_name = "LeaderF://" + self._source

        self._file_type = "git"
        self._file_type_cmd = "setlocal filetype=git"


class GitDiffExplCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        super(GitDiffExplCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        self._cmd = 'git diff --raw -C --numstat --shortstat --no-abbrev'
        extra_options = ""
        if "--cached" in self._arguments:
            extra_options += " --cached"

        if "extra" in self._arguments:
            extra_options += " " + " ".join(self._arguments["extra"])

        self._cmd += extra_options

        self._buffer_name = "LeaderF://navigation/" + self._source
        self._file_type_cmd = ""


class GitLogExplCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        """
        source is a commit id
        """
        super(GitLogExplCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        if "--find-copies-harder" in self._arguments:
            find_copies_harder = " -C"
        else:
            find_copies_harder = ""

        self._cmd = ('git show -m --raw -C{} --numstat --shortstat '
                     '--pretty=format:"# %P" --no-abbrev {}').format(find_copies_harder,
                                                                     self._source)

        self._buffer_name = "LeaderF://navigation/" + self._source
        self._file_type_cmd = ""


class GitBlameCommand(GitCommand):
    def __init__(self, arguments_dict, commit_id):
        super(GitBlameCommand, self).__init__(arguments_dict, commit_id)

    @staticmethod
    def buildCommand(arguments_dict, commit_id, file_name, use_contents=False):
        extra_options = ""
        if "-c" in arguments_dict:
            extra_options += " -c"

        if "-w" in arguments_dict:
            extra_options += " -w"

        if "--date" in arguments_dict:
            extra_options += " --date={}".format(arguments_dict["--date"][0])

        if use_contents and "--contents" in arguments_dict:
            extra_options += " --contents {}".format(arguments_dict["--contents"][0])

        return "git blame -f -n {} {} -- {}".format(extra_options, commit_id, file_name)

    def buildCommandAndBufferName(self):
        commit_id = ""
        if self._source is not None:
            commit_id = self._source

        file_name = vim.current.buffer.name
        if " " in file_name:
            file_name = file_name.replace(' ', r'\ ')
        file_name = PurePath(lfRelpath(file_name)).as_posix()

        self._cmd = GitBlameCommand.buildCommand(self._arguments, commit_id, file_name, True)
        self._buffer_name = "LeaderF://git blame {} {}".format(commit_id, file_name)
        self._file_type = ""
        self._file_type_cmd = ""


class GitShowCommand(GitCommand):
    def __init__(self, arguments_dict, commit_id, file_name):
        self._commit_id = commit_id
        self._file_name = file_name
        super(GitShowCommand, self).__init__(arguments_dict, None)

    def buildCommandAndBufferName(self):
        self._cmd = "git log -1 -p --follow {} -- {}".format(self._commit_id, self._file_name)
        self._file_type = "git"
        self._file_type_cmd = "setlocal filetype=git"


class GitCustomizeCommand(GitCommand):
    def __init__(self, arguments_dict, cmd, buf_name, file_type, file_type_cmd):
        super(GitCustomizeCommand, self).__init__(arguments_dict, None)
        self._cmd = cmd
        self._buffer_name = buf_name
        self._file_type = file_type
        self._file_type_cmd = file_type_cmd


class ParallelExecutor(object):
    @staticmethod
    def run(*cmds, format_line=None, directory=None, silent=False):
        outputs = [[] for _ in range(len(cmds))]
        stop_thread = False

        def readContent(content, output):
            try:
                for line in content:
                    output.append(line)
                    if stop_thread:
                        break
            except Exception:
                if silent == False:
                    traceback.print_exc()
                    traceback.print_stack()


        executors = [AsyncExecutor() for _ in range(len(cmds))]
        workers = []
        for i, (exe, cmd) in enumerate(zip(executors, cmds)):
            if isinstance(format_line, list):
                format_line_cb = format_line[i]
            else:
                format_line_cb = format_line
            content = exe.execute(cmd,
                                  encoding=lfEval("&encoding"),
                                  format_line=format_line_cb,
                                  cwd=directory)
            worker = threading.Thread(target=readContent, args=(content, outputs[i]))
            worker.daemon = True
            worker.start()
            workers.append(worker)

        for w in workers:
            w.join(5) # I think 5s is enough for git cat-file

        stop_thread = True

        for e in executors:
            e.killProcess()

        return outputs


class GitCommandView(object):
    def __init__(self, owner, cmd):
        self._owner = owner
        self._cmd = cmd
        self._executor = AsyncExecutor()
        self._buffer = None
        self._window_id = -1
        self._bufhidden = 'wipe'
        self._format_line = None
        self.init()
        owner.register(self)

    def init(self):
        self._content = []
        self._timer_id = None
        self._reader_thread = None
        self._offset_in_content = 0
        self._read_finished = 0
        self._stop_reader_thread = False

    def getBufferName(self):
        return self._cmd.getBufferName()

    def getBufferNum(self):
        if self._buffer is None:
            return -1
        else:
            return self._buffer.number

    def getWindowId(self):
        self._window_id = int(lfEval("bufwinid({})".format(self._buffer.number)))
        # window not exist in current tabpage
        if self._window_id == -1:
            ids = lfEval("win_findbuf({})".format(self._buffer.number))
            if len(ids) > 0:
                self._window_id = int(ids[0])

        return self._window_id

    def setWindowId(self, winid):
        self._window_id = winid

    def getContent(self):
        return self._content

    def setContent(self, content):
        try:
            self._buffer.options['modifiable'] = True
            self._buffer[:] = content
        finally:
            self._buffer.options['modifiable'] = False

    def getSource(self):
        return self._cmd.getSource()

    def start(self):
        # start a timer and thread
        self._timer_id = lfEval("timer_start(100, function('leaderf#Git#WriteBuffer', [%d]), {'repeat': -1})" % id(self))

        self._reader_thread = threading.Thread(target=self._readContent, args=(lfEval("&encoding"),))
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def setOptions(self, winid, bufhidden):
        lfCmd("call win_execute({}, 'setlocal nobuflisted')".format(winid))
        lfCmd("call win_execute({}, 'setlocal buftype=nofile')".format(winid))
        lfCmd("call win_execute({}, 'setlocal bufhidden={}')".format(winid, bufhidden))
        lfCmd("call win_execute({}, 'setlocal undolevels=-1')".format(winid))
        lfCmd("call win_execute({}, 'setlocal noswapfile')".format(winid))
        lfCmd("call win_execute({}, 'setlocal nospell')".format(winid))
        lfCmd("call win_execute({}, 'setlocal nomodifiable')".format(winid))
        if lfEval("getbufvar(winbufnr(%d), '&ft')" % winid) != self._cmd.getFileType():
            lfCmd("silent! call win_execute({}, '{}')".format(winid, self._cmd.getFileTypeCommand()))

    def initBuffer(self):
        pass

    def defineMaps(self, winid):
        pass

    def enableColor(self, winid):
        pass

    def create(self, winid, bufhidden='wipe', buf_content=None, format_line=None):
        self._bufhidden = bufhidden
        self._format_line = format_line

        if self._buffer is not None:
            self.cleanup()
            lfCmd("call win_gotoid({})".format(self.getWindowId()))

        self.init()

        if self._buffer is None:
            self.defineMaps(winid)
            self.setOptions(winid, bufhidden)
            lfCmd("augroup Lf_Git | augroup END")
            lfCmd("call win_execute({}, 'autocmd! Lf_Git BufWipeout <buffer> call leaderf#Git#Suicide({})')"
                  .format(winid, id(self)))
            lfCmd("call win_execute({}, 'autocmd! Lf_Git BufHidden <buffer> call leaderf#Git#Bufhidden({})')"
                  .format(winid, id(self)))

            self._buffer = vim.buffers[int(lfEval("winbufnr({})".format(winid)))]
            self._window_id = winid

        self.enableColor(self.getWindowId())

        if buf_content is not None:
            # cache the content if buf_content is the result of ParallelExecutor.run()
            self._content = buf_content
            self._owner.readFinished(self)

            self._read_finished = 2

            self._buffer.options['modifiable'] = True
            self._buffer[:] = buf_content
            self._buffer.options['modifiable'] = False

            self._owner.writeFinished(self.getWindowId())

            return

        if self._cmd.getCommand() == "":
            self._read_finished = 2
            self._owner.writeFinished(self.getWindowId())
            return

        self.initBuffer()
        self.start()

    def writeBuffer(self):
        if self._read_finished == 2:
            return

        if not self._buffer.valid:
            self.stopTimer()
            return

        self._buffer.options['modifiable'] = True
        try:
            cur_len = len(self._content)
            if cur_len > self._offset_in_content:
                if self._offset_in_content == 0:
                    self._buffer[:] = self._content[:cur_len]
                else:
                    self._buffer.append(self._content[self._offset_in_content:cur_len])

                self._offset_in_content = cur_len
                lfCmd("redraw")
        finally:
            self._buffer.options['modifiable'] = False

        if self._read_finished == 1 and self._offset_in_content == len(self._content):
            self._read_finished = 2
            self._owner.writeFinished(self.getWindowId())
            self.stopTimer()

    def _readContent(self, encoding):
        try:
            content = self._executor.execute(self._cmd.getCommand(),
                                             encoding=encoding,
                                             format_line=self._format_line,
                                             cwd=self._owner.getProjectRoot()
                                             )
            for line in content:
                self._content.append(line)
                if self._stop_reader_thread:
                    break
            else:
                self._read_finished = 1
                self._owner.readFinished(self)
        except Exception:
            traceback.print_exc()
            traceback.print_stack()
            self._read_finished = 1

    def stopThread(self):
        if self._reader_thread and self._reader_thread.is_alive():
            self._stop_reader_thread = True
            self._reader_thread.join(0.01)

    def stopTimer(self):
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

    def cleanup(self, wipe=True):
        self.stopTimer()
        self.stopThread()
        # must do this at last
        self._executor.killProcess()

        if self._bufhidden == "hide" and wipe == True:
            lfCmd("noautocmd bwipe! {}".format(self._buffer.number))

    def suicide(self):
        self._owner.deregister(self)

    def bufHidden(self):
        self._owner.bufHidden(self)

    def valid(self):
        return self._buffer is not None and self._buffer.valid


class GitBlameView(GitCommandView):
    def __init__(self, owner, cmd):
        super(GitBlameView, self).__init__(owner, cmd)
        self._alternate_winid = None
        self._alternate_buffer_num = None
        self._alternate_win_options = {}
        self._color_table = {
            '0':   '#000000', '1':   '#800000', '2':   '#008000', '3':   '#808000',
            '4':   '#000080', '5':   '#800080', '6':   '#008080', '7':   '#c0c0c0',
            '8':   '#808080', '9':   '#ff0000', '10':  '#00ff00', '11':  '#ffff00',
            '12':  '#0000ff', '13':  '#ff00ff', '14':  '#00ffff', '15':  '#ffffff',
            '16':  '#000000', '17':  '#00005f', '18':  '#000087', '19':  '#0000af',
            '20':  '#0000d7', '21':  '#0000ff', '22':  '#005f00', '23':  '#005f5f',
            '24':  '#005f87', '25':  '#005faf', '26':  '#005fd7', '27':  '#005fff',
            '28':  '#008700', '29':  '#00875f', '30':  '#008787', '31':  '#0087af',
            '32':  '#0087d7', '33':  '#0087ff', '34':  '#00af00', '35':  '#00af5f',
            '36':  '#00af87', '37':  '#00afaf', '38':  '#00afd7', '39':  '#00afff',
            '40':  '#00d700', '41':  '#00d75f', '42':  '#00d787', '43':  '#00d7af',
            '44':  '#00d7d7', '45':  '#00d7ff', '46':  '#00ff00', '47':  '#00ff5f',
            '48':  '#00ff87', '49':  '#00ffaf', '50':  '#00ffd7', '51':  '#00ffff',
            '52':  '#5f0000', '53':  '#5f005f', '54':  '#5f0087', '55':  '#5f00af',
            '56':  '#5f00d7', '57':  '#5f00ff', '58':  '#5f5f00', '59':  '#5f5f5f',
            '60':  '#5f5f87', '61':  '#5f5faf', '62':  '#5f5fd7', '63':  '#5f5fff',
            '64':  '#5f8700', '65':  '#5f875f', '66':  '#5f8787', '67':  '#5f87af',
            '68':  '#5f87d7', '69':  '#5f87ff', '70':  '#5faf00', '71':  '#5faf5f',
            '72':  '#5faf87', '73':  '#5fafaf', '74':  '#5fafd7', '75':  '#5fafff',
            '76':  '#5fd700', '77':  '#5fd75f', '78':  '#5fd787', '79':  '#5fd7af',
            '80':  '#5fd7d7', '81':  '#5fd7ff', '82':  '#5fff00', '83':  '#5fff5f',
            '84':  '#5fff87', '85':  '#5fffaf', '86':  '#5fffd7', '87':  '#5fffff',
            '88':  '#870000', '89':  '#87005f', '90':  '#870087', '91':  '#8700af',
            '92':  '#8700d7', '93':  '#8700ff', '94':  '#875f00', '95':  '#875f5f',
            '96':  '#875f87', '97':  '#875faf', '98':  '#875fd7', '99':  '#875fff',
            '100': '#878700', '101': '#87875f', '102': '#878787', '103': '#8787af',
            '104': '#8787d7', '105': '#8787ff', '106': '#87af00', '107': '#87af5f',
            '108': '#87af87', '109': '#87afaf', '110': '#87afd7', '111': '#87afff',
            '112': '#87d700', '113': '#87d75f', '114': '#87d787', '115': '#87d7af',
            '116': '#87d7d7', '117': '#87d7ff', '118': '#87ff00', '119': '#87ff5f',
            '120': '#87ff87', '121': '#87ffaf', '122': '#87ffd7', '123': '#87ffff',
            '124': '#af0000', '125': '#af005f', '126': '#af0087', '127': '#af00af',
            '128': '#af00d7', '129': '#af00ff', '130': '#af5f00', '131': '#af5f5f',
            '132': '#af5f87', '133': '#af5faf', '134': '#af5fd7', '135': '#af5fff',
            '136': '#af8700', '137': '#af875f', '138': '#af8787', '139': '#af87af',
            '140': '#af87d7', '141': '#af87ff', '142': '#afaf00', '143': '#afaf5f',
            '144': '#afaf87', '145': '#afafaf', '146': '#afafd7', '147': '#afafff',
            '148': '#afd700', '149': '#afd75f', '150': '#afd787', '151': '#afd7af',
            '152': '#afd7d7', '153': '#afd7ff', '154': '#afff00', '155': '#afff5f',
            '156': '#afff87', '157': '#afffaf', '158': '#afffd7', '159': '#afffff',
            '160': '#d70000', '161': '#d7005f', '162': '#d70087', '163': '#d700af',
            '164': '#d700d7', '165': '#d700ff', '166': '#d75f00', '167': '#d75f5f',
            '168': '#d75f87', '169': '#d75faf', '170': '#d75fd7', '171': '#d75fff',
            '172': '#d78700', '173': '#d7875f', '174': '#d78787', '175': '#d787af',
            '176': '#d787d7', '177': '#d787ff', '178': '#d7af00', '179': '#d7af5f',
            '180': '#d7af87', '181': '#d7afaf', '182': '#d7afd7', '183': '#d7afff',
            '184': '#d7d700', '185': '#d7d75f', '186': '#d7d787', '187': '#d7d7af',
            '188': '#d7d7d7', '189': '#d7d7ff', '190': '#d7ff00', '191': '#d7ff5f',
            '192': '#d7ff87', '193': '#d7ffaf', '194': '#d7ffd7', '195': '#d7ffff',
            '196': '#ff0000', '197': '#ff005f', '198': '#ff0087', '199': '#ff00af',
            '200': '#ff00d7', '201': '#ff00ff', '202': '#ff5f00', '203': '#ff5f5f',
            '204': '#ff5f87', '205': '#ff5faf', '206': '#ff5fd7', '207': '#ff5fff',
            '208': '#ff8700', '209': '#ff875f', '210': '#ff8787', '211': '#ff87af',
            '212': '#ff87d7', '213': '#ff87ff', '214': '#ffaf00', '215': '#ffaf5f',
            '216': '#ffaf87', '217': '#ffafaf', '218': '#ffafd7', '219': '#ffafff',
            '220': '#ffd700', '221': '#ffd75f', '222': '#ffd787', '223': '#ffd7af',
            '224': '#ffd7d7', '225': '#ffd7ff', '226': '#ffff00', '227': '#ffff5f',
            '228': '#ffff87', '229': '#ffffaf', '230': '#ffffd7', '231': '#ffffff',
            '232': '#080808', '233': '#121212', '234': '#1c1c1c', '235': '#262626',
            '236': '#303030', '237': '#3a3a3a', '238': '#444444', '239': '#4e4e4e',
            '240': '#585858', '241': '#626262', '242': '#6c6c6c', '243': '#767676',
            '244': '#808080', '245': '#8a8a8a', '246': '#949494', '247': '#9e9e9e',
            '248': '#a8a8a8', '249': '#b2b2b2', '250': '#bcbcbc', '251': '#c6c6c6',
            '252': '#d0d0d0', '253': '#dadada', '254': '#e4e4e4', '255': '#eeeeee'
        }

        self._heat_colors = {
            "dark":  ['160', '196', '202', '208', '214', '220', '226', '190', '154', '118', '46',
                      '47', '48', '49', '50', '51', '45', '39', '33', '27', '21', '244', '242', '240'
            ],
            "light": ['160', '196', '202', '208', '214', '178', '142', '106', '70', '34', '35',
                      '36', '37', '38', '39', '33', '32', '27', '26', '21', '232'
            ]
        }

        self._date_dict = {}
        self._heat_seconds = []

        self.blame_stack = []
        # key is commit id, value is (blame_buffer, alternate_buffer_num)
        self.blame_dict = {}
        # key is alternate buffer name, value is (blame_buffer, alternate_buffer_num)
        self.blame_buffer_dict = {}

    def setOptions(self, winid, bufhidden):
        super(GitBlameView, self).setOptions(winid, bufhidden)
        lfCmd("call win_execute({}, 'setlocal nowrap')".format(winid))
        lfCmd("call win_execute({}, 'setlocal winfixwidth')".format(winid))
        lfCmd("call win_execute({}, 'setlocal foldcolumn=0')".format(winid))
        lfCmd("call win_execute({}, 'setlocal number norelativenumber')".format(winid))
        lfCmd("call win_execute({}, 'setlocal nofoldenable')".format(winid))
        lfCmd("call win_execute({}, 'setlocal signcolumn=no')".format(winid))
        lfCmd("call win_execute({}, 'setlocal cursorline')".format(winid))
        lfCmd("call win_execute({}, 'setlocal scrolloff=0')".format(winid))

    def saveAlternateWinOptions(self, winid, buffer_num):
        self._alternate_winid = winid
        self._alternate_buffer_num = buffer_num

        self._alternate_win_options = {
                "foldenable": lfEval("getwinvar({}, '&foldenable')".format(winid)),
                "scrollbind": lfEval("getwinvar({}, '&scrollbind')".format(winid)),
                }

    def getAlternateWinid(self):
        return self._alternate_winid

    def enableColor(self, winid):
        if (lfEval("hlexists('Lf_hl_blame_255')") == '0'
            or lfEval("exists('*hlget')") == '0'
            or lfEval("hlget('Lf_hl_blame_255')[0]").get("cleared", False)):
            for cterm_color, gui_color in self._color_table.items():
                lfCmd("hi def Lf_hl_blame_{} guifg={} guibg=NONE gui=NONE ctermfg={} ctermbg=NONE cterm=NONE"
                      .format(cterm_color, gui_color, cterm_color))

            stl = ""
            for i, cterm_color in enumerate(self._heat_colors[lfEval("&bg")]):
                lfCmd("hi def Lf_hl_blame_heat_{} guifg={} guibg=NONE gui=NONE ctermfg={} ctermbg=NONE cterm=NONE"
                      .format(i, self._color_table[cterm_color], cterm_color))
                lfCmd("call leaderf#colorscheme#popup#link_two('Lf_hl_blame_stl_heat_{}', 'StatusLine', 'Lf_hl_blame_heat_{}', 1)"
                      .format(i, i))
                stl = "%#Lf_hl_blame_stl_heat_{}#>".format(i) + stl

            lfCmd("let g:Lf_GitStlHeatLine = '{}'".format(stl))

        if lfEval("hlexists('Lf_hl_gitBlameDate')") == '0':
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')"
                  .format("git", lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))

        lfCmd(r"""call win_execute(%d, 'syn match WarningMsg /\<Not Committed Yet\>/')""" % winid)

    def highlightCommitId(self, commit_id):
        n = int(commit_id.lstrip('^')[:2], 16)
        lfCmd(r"syn match Lf_hl_blame_{} /^\^\?{}\x\+/".format(n, commit_id[:2]))

    def suicide(self):
        super(GitBlameView, self).suicide()

        line_num = vim.current.window.cursor[0]
        top_line = lfEval("line('w0')")
        if len(self.blame_stack) > 0:
            line_num = self.blame_stack[0][3]
            top_line = self.blame_stack[0][4]

        lfCmd("call win_execute({}, 'buffer {} | norm! {}Gzt{}G0')".format(self._alternate_winid,
                                                                           self._alternate_buffer_num,
                                                                           top_line,
                                                                           line_num))

        if self._alternate_winid is not None:
            for k, v in self._alternate_win_options.items():
                lfCmd("call setwinvar({}, '&{}', {})".format(self._alternate_winid, k, v))

        for item in self.blame_dict.values():
            buffer_num = int(item[1])
            # buftype is not empty
            if (lfEval("bufexists({})".format(buffer_num)) == "1"
                and vim.buffers[buffer_num].options["buftype"]):
                lfCmd("bwipe {}".format(buffer_num))
        self.blame_dict = {}
        self.blame_stack = []
        self.blame_buffer_dict = {}

    def _helper(self, date_format):
        if date_format == "iso":
            # 6817817e (Yggdroot       2014-02-26 00:37:26 +0800) 1 autoload/leaderf/manager.py
            pattern = r"\b\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{4}\b"
            format_str = "%Y-%m-%d %H:%M:%S %z"
            to_timestamp = lambda date: int(datetime.strptime(date, format_str).timestamp())
        elif date_format == "iso-strict":
            # 6817817e (Yggdroot       2014-02-26T00:37:26+08:00) 1 autoload/leaderf/manager.py
            pattern = r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}\b"
            to_timestamp = lambda date: int(datetime.fromisoformat(date).timestamp())
        elif date_format == "short":
            # 6817817e (Yggdroot       2014-02-26) 1 autoload/leaderf/manager.py
            pattern = r"\b\d{4}-\d{2}-\d{2}\b"
            to_timestamp = lambda date: int(datetime.fromisoformat(date).timestamp())
        else:
            lfPrintError("Error. date_format = {}".format(date_format))

        return (pattern, to_timestamp)

    def highlightHeatDate1(self, date_format, blame_list):
        pattern, to_timestamp = self._helper(date_format)
        self._date_dict = {}
        for line in blame_list:
            commit_id, rest = line.split(None, 1)
            if commit_id not in self._date_dict:
                self.highlightCommitId(commit_id)
                match = re.search(pattern, rest)
                if match:
                    date = match.group(0)
                    timestamp = to_timestamp(date)
                else:
                    lfPrintError("Error. pattern '{}' can not be found in '{}'"
                                 .format(pattern, rest))

                self._date_dict[commit_id] = (date, timestamp)

        self._highlightHeatDate()

    def highlightHeatDate2(self, normal_blame_list, unix_blame_list):
        """
        normal_blame_list:
        ["6817817e\t(  Yggdroot\t10 years ago          \t1)#!/usr/bin/env python",
         ...
        ]

        unix_blame_list:
        ["6817817e\t(  Yggdroot\t1393346246\t1)#!/usr/bin/env python",
         ...
        ]
        """
        self._date_dict = {}
        for i, line in enumerate(normal_blame_list):
            commit_id, rest = line.split('\t', 1)
            if commit_id not in self._date_dict:
                self.highlightCommitId(commit_id)
                date = rest.split('\t')[1].strip()
                timestamp = int(unix_blame_list[i].split('\t')[2])
                self._date_dict[commit_id] = (date, timestamp)

        self._highlightHeatDate()

    def _highlightHeatDate(self):
        color_num = len(self._heat_colors[lfEval("&bg")])
        current_time = int(time.time())
        heat_seconds = sorted((current_time - timestamp
                               for date, timestamp in self._date_dict.values()))
        heat_seconds_len = len(heat_seconds)
        if heat_seconds_len > color_num:
            step, remainder = divmod(heat_seconds_len, color_num)
            if step > 0:
                tmp = heat_seconds[step - 1 : heat_seconds_len - remainder : step]
                if remainder > 0:
                    tmp[-1] = heat_seconds[-1]
                heat_seconds = tmp

        self._heat_seconds = heat_seconds
        self._highlight(current_time, self._date_dict)

    def highlightRestHeatDate1(self, date_format, blame_list):
        pattern, to_timestamp = self._helper(date_format)
        date_dict = {}
        for line in blame_list:
            commit_id, rest = line.split(None, 1)
            if commit_id not in self._date_dict:
                self.highlightCommitId(commit_id)
                match = re.search(pattern, rest)
                if match:
                    date = match.group(0)
                    timestamp = to_timestamp(date)
                else:
                    lfPrintError("Error. pattern '{}' can not be found in '{}'"
                                 .format(pattern, rest))

                date_dict[commit_id] = (date, timestamp)
                self._date_dict[commit_id] = date_dict[commit_id]

        current_time = int(time.time())
        self._highlight(current_time, date_dict)

    def highlightRestHeatDate2(self, normal_blame_list, unix_blame_list):
        """
        normal_blame_list:
        ["6817817e\t(  Yggdroot\t10 years ago          \t1)#!/usr/bin/env python",
         ...
        ]

        unix_blame_list:
        ["6817817e\t(  Yggdroot\t1393346246\t1)#!/usr/bin/env python",
         ...
        ]
        """
        date_dict = {}
        for i, line in enumerate(normal_blame_list):
            commit_id, rest = line.split('\t', 1)
            if commit_id not in self._date_dict:
                self.highlightCommitId(commit_id)
                date = rest.split('\t')[1].strip()
                timestamp = int(unix_blame_list[i].split('\t')[2])
                date_dict[commit_id] = (date, timestamp)
                self._date_dict[commit_id] = date_dict[commit_id]

        current_time = int(time.time())
        self._highlight(current_time, date_dict)

    def _highlight(self, current_time, date_dict):
        date_set = set()
        for date, timestamp in date_dict.values():
            if date not in date_set:
                date_set.add(date)
                index = Bisect.bisect_left(self._heat_seconds, current_time - timestamp)
                lfCmd(r"syn match Lf_hl_blame_heat_{} /\<{}\>/".format(index, date))

    def clearHeatSyntax(self):
        for i in range(len(self._heat_seconds)):
            lfCmd("silent! syn clear Lf_hl_blame_heat_{}".format(i))


class LfOrderedDict(OrderedDict):
    def last_key(self):
        return next(reversed(self.keys()))

    def last_value(self):
        return next(reversed(self.values()))

    def last_key_value(self):
        return next(reversed(self.items()))

    def first_key(self):
        return next(iter(self.keys()))

    def first_value(self):
        return next(iter(self.values()))

    def first_key_value(self):
        return next(iter(self.items()))


class FolderStatus(Enum):
    CLOSED = 0
    OPEN = 1


class TreeNode(object):
    def __init__(self, status=FolderStatus.OPEN):
        self.status = status
        # key is the directory name, value is a TreeNode
        self.dirs = LfOrderedDict()
        # key is the file name,
        # value is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        self.files = LfOrderedDict()


class MetaInfo(object):
    def __init__(self, level, is_dir, name, info, path):
        """
        info is TreeNode if is_dir is true or source otherwise.
        """
        self.level = level
        self.is_dir = is_dir
        self.name = name
        self.info = info
        self.path = path
        self.has_num_stat = False


class KeyWrapper(object):
    def __init__(self, iterable, key):
        self._list = iterable
        self._key = key

    def __getitem__(self, i):
        if self._key is None:
            return self._list[i]

        return self._key(self._list[i])

    def __len__(self):
        return len(self._list)


class Bisect(object):
    @staticmethod
    def bisect_left(a, x, lo=0, hi=None, *, key=None):
        if hi is None:
            hi = len(a)

        if sys.version_info >= (3, 10):
            pos = bisect.bisect_left(a, x, lo, hi, key=key)
        else:
            pos = bisect.bisect_left(KeyWrapper(a, key), x, lo, hi)
        return pos

    @staticmethod
    def bisect_right(a, x, lo=0, hi=None, *, key=None):
        if hi is None:
            hi = len(a)

        if sys.version_info >= (3, 10):
            pos = bisect.bisect_right(a, x, lo, hi, key=key)
        else:
            pos = bisect.bisect_right(KeyWrapper(a, key), x, lo, hi)
        return pos


class TreeView(GitCommandView):
    def __init__(self, owner, cmd, project_root, target_path, callback):
        super(TreeView, self).__init__(owner, cmd)
        self._project_root = project_root
        self._target_path = target_path
        # the argument is source, source is a tuple like
        # (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        self._callback = callback
        # key is the parent hash, value is a TreeNode
        self._trees = LfOrderedDict()
        # key is the parent hash, value is a list of MetaInfo
        self._file_structures = {}
        # to protect self._file_structures
        self._lock = threading.Lock()
        self._file_list = {}
        self._cur_parent = None
        self._short_stat = {}
        self._num_stat = {}
        self._first_source = {}
        self._show_icon = lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1"
        folder_icons = lfEval("g:Lf_GitFolderIcons")
        self._closed_folder_icon = folder_icons["closed"]
        self._open_folder_icon = folder_icons["open"]
        self._preopen_num = int(lfEval("get(g:, 'Lf_GitPreopenNum', 100)"))
        self._add_icon = lfEval("get(g:, 'Lf_GitAddIcon', '')")    #  
        self._copy_icon = lfEval("get(g:, 'Lf_GitCopyIcon', '')")
        self._del_icon = lfEval("get(g:, 'Lf_GitDelIcon', '')")    #  
        self._modification_icon = lfEval("get(g:, 'Lf_GitModifyIcon', '')")
        self._rename_icon = lfEval("get(g:, 'Lf_GitRenameIcon', '')")
        self._status_icons = {
                "A": self._add_icon,
                "C": self._copy_icon,
                "D": self._del_icon,
                "M": self._modification_icon,
                "R": self._rename_icon,
                }
        self._head = [
                self._project_root + os.sep,
                ]
        self._match_ids = []

    def startLine(self):
        return self._owner.startLine()

    def enableColor(self, winid):
        if lfEval("hlexists('Lf_hl_help')") == '0':
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')"
                  .format("git", lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))

        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitHelp'', ''^".*'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitFolder'', ''\S*[/\\]'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitFolderIcon'', ''^\s*\zs[{}{}]'', -100)')"""
              .format(winid, self._closed_folder_icon, self._open_folder_icon))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitAddIcon'', ''^\s*\zs{}'', -100)')"""
              .format(winid, self._add_icon))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitCopyIcon'', ''^\s*\zs{}'', -100)')"""
              .format(winid, self._copy_icon))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitDelIcon'', ''^\s*\zs{}'', -100)')"""
              .format(winid, self._del_icon))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitModifyIcon'', ''^\s*\zs{}'', -100)')"""
              .format(winid, self._modification_icon))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitRenameIcon'', ''^\s*\zs{}'', -100)')"""
              .format(winid, self._rename_icon))
        id = int(lfEval("matchid"))
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitRenameIcon'', '' \zs=>\ze '', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitNumStatAdd'', ''\t\zs+\d\+'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitNumStatDel'', ''\t+\d\+\s\+\zs-\d\+'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitNumStatBinary'', ''\t\zs(Bin)'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)

        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Identifier'', '''', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitSelectedOption'', ''\S\+ ◉\@='', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitDiffAddition'', ''\(\S\+ \)\@<=◉'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitNonSelectedOption'', ''\S\+ ○\@='', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitDiffDeletion'', ''\(\S\+ \)\@<=○'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitSelectedOption'', ''\( \)\@<=Ignore Whitespace 🗹\@='', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitDiffAddition'', ''\( Ignore Whitespace \)\@<=🗹 '', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitNonSelectedOption'', ''\( \)\@<=Ignore Whitespace 🗷\@='', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitDiffDeletion'', ''\( Ignore Whitespace \)\@<=🗷 '', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)

    def defineMaps(self, winid):
        lfCmd("call win_execute({}, 'call leaderf#Git#TreeViewMaps({})')"
              .format(winid, id(self)))

    def getCurrentParent(self):
        return self._cur_parent

    def getFileList(self):
        return self._file_list[self._cur_parent]

    @staticmethod
    def generateSource(line):
        """
        :000000 100644 000000000 5b01d33aa A    runtime/syntax/json5.vim
        :100644 100644 671b269c0 ef52cddf4 M    runtime/syntax/nix.vim
        :100644 100644 69671c59c 084f8cdb4 M    runtime/syntax/zsh.vim
        :100644 100644 b90f76fc1 bad07e644 R099 src/version.c   src/version2.c
        :100644 000000 b5825eb19 000000000 D    src/testdir/dumps

        ':100644 100644 72943a1 dbee026 R050\thello world.txt\thello world2.txt'

        return a tuple like (100644, (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c))
                            (100644, (69671c59c, 084f8cdb4, M,    runtime/syntax/zsh.vim, ""))
        """
        tmp = line.split(sep='\t')
        file_names = (tmp[1], tmp[2] if len(tmp) == 3 else "")
        blob_status = tmp[0].split()
        return (blob_status[1],
                (blob_status[2], blob_status[3], blob_status[4],
                file_names[0], file_names[1])
                )

    def buildFileStructure(self, parent, level, name, tree_node, path):
        if len(tree_node.dirs) == 1 and len(tree_node.files) == 0:
            if tree_node.status == FolderStatus.CLOSED:
                self._file_structures[parent].append(
                        MetaInfo(level, True, name, tree_node, path)
                        )
            else:
                dir_name, node = tree_node.dirs.last_key_value()
                self.buildFileStructure(parent, level, "{}/{}".format(name, dir_name),
                                        node, "{}{}/".format(path, dir_name)
                                        )
        else:
            self._file_structures[parent].append(
                    MetaInfo(level, True, name, tree_node, path)
                    )

            if tree_node.status == FolderStatus.OPEN:
                for dir_name, node in tree_node.dirs.items():
                    self.buildFileStructure(parent, level + 1, dir_name, node,
                                            "{}{}/".format(path, dir_name))

                self.appendFiles(parent, level + 1, tree_node)

    def appendRemainingFiles(self, parent, tree_node):
        if len(tree_node.dirs) == 0:
            return

        dir_name, node = tree_node.dirs.last_key_value()
        if len(node.dirs) > 1:
            if node.status == FolderStatus.OPEN:
                child_dir_name, child_node = node.dirs.last_key_value()
                self.buildFileStructure(parent, 1, child_dir_name, child_node,
                                        "{}/{}/".format(dir_name, child_dir_name))

                self.appendFiles(parent, 1, node)
        else:
            self.buildFileStructure(parent, 0, dir_name, node, dir_name + "/")

    def appendFiles(self, parent, level, tree_node):
        for k, v in tree_node.files.items():
            self._file_structures[parent].append(
                    MetaInfo(level, False, k, v, lfGetFilePath(v))
                    )

    def getLeftMostFile(self, tree_node):
        for node in tree_node.dirs.values():
            result = self.getLeftMostFile(node)
            if result is not None:
                return result

        for i in tree_node.files.values():
            return i

        return None

    def buildTree(self, line):
        """
        command output is something as follows:

        # 9d0ccb54c743424109751a82a742984699e365fe 63aa0c07bcd16ddac52d5275b9513712b780bc25
        :100644 100644 0cbabf4 d641678 M        src/a.txt
        2       0       src/a.txt
         1 file changed, 2 insertions(+)

        # 9d0ccb54c743424109751a82a742984699e365fe 63aa0c07bcd16ddac52d5275b9513712b780bc25
        :100644 100644 acc5824 d641678 M        src/a.txt
        3       0       src/a.txt
         1 file changed, 3 insertions(+)
        """
        if line.startswith("#"):
            size = len(self._trees)
            parents = line.split()
            if len(parents) == 1: # first commit
                parent = "0000000"
            else:
                parent = parents[size + 1]
            if self._cur_parent is None:
                self._cur_parent = parent
            self._trees[parent] = TreeNode()
            self._file_structures[parent] = []
            self._file_list[parent] = []
        elif line.startswith(":"):
            if self._cur_parent is None:
                parent = "0000000"
                self._cur_parent = parent
                self._trees[parent] = TreeNode()
                self._file_structures[parent] = []
                self._file_list[parent] = []

            parent, tree_node = self._trees.last_key_value()
            root_node = tree_node
            mode, source = TreeView.generateSource(line)
            file_path = lfGetFilePath(source)
            icon = webDevIconsGetFileTypeSymbol(file_path) if self._show_icon else ""
            self._file_list[parent].append("{:<4} {}{}{}"
                                           .format(source[2], icon, source[3],
                                                   "" if source[4] == ""
                                                   else "\t=>\t" + source[4])
                                           )
            if mode == "160000": # gitlink
                directories = file_path.split("/")
            else:
                *directories, file = file_path.split("/")
            with self._lock:
                for i, d in enumerate(directories, 0):
                    if i == 0:
                        level0_dir_name = d

                    if d not in tree_node.dirs:
                        # not first directory
                        if len(tree_node.dirs) > 0:
                            if i == 1:
                                if len(tree_node.dirs) == 1:
                                    self._file_structures[parent].append(
                                            MetaInfo(0, True, level0_dir_name,
                                                     tree_node, level0_dir_name + "/")
                                            )

                                if tree_node.status == FolderStatus.OPEN:
                                    dir_name, node = tree_node.dirs.last_key_value()
                                    self.buildFileStructure(parent, 1, dir_name, node,
                                                            "{}/{}/".format(level0_dir_name,
                                                                            dir_name)
                                                            )
                            elif i == 0:
                                self.appendRemainingFiles(parent, tree_node)

                        if len(self._file_structures[parent]) >= self._preopen_num:
                            status = FolderStatus.CLOSED
                        else:
                            status = FolderStatus.OPEN
                        tree_node.dirs[d] = TreeNode(status)

                    tree_node = tree_node.dirs[d]

                if self._target_path == file_path:
                    node = root_node
                    node.status = FolderStatus.OPEN
                    for d in directories:
                        node = node.dirs[d]
                        node.status = FolderStatus.OPEN

            if mode != "160000":
                tree_node.files[file] = source
        elif line.startswith(" "):
            parent, tree_node = self._trees.last_key_value()
            self._short_stat[parent] = line
            self.appendRemainingFiles(parent, tree_node)
            self.appendFiles(parent, 0, tree_node)
        elif line == "":
            pass
        else:
            parent = self._trees.last_key()
            if parent not in self._num_stat:
                self._num_stat[parent] = {}

            #'3\t1\tarch/{i386 => x86}/Makefile'
            added, deleted, pathname = line.split("\t")
            if "=>" in pathname:
                if "{" in pathname:
                    pathname = re.sub(r'{.*?=> (.*?)}', r'\1', pathname)
                else:
                    pathname = pathname.split(" => ")[1]
            if added == "-" and deleted == "-":
                self._num_stat[parent][pathname] = "(Bin)"
            else:
                self._num_stat[parent][pathname] = "+{:3} -{}".format(added, deleted)

    def metaInfoGenerator(self, meta_info, recursive, level):
        meta_info.info.status = FolderStatus.OPEN

        tree_node = meta_info.info
        if len(tree_node.dirs) == 1 and len(tree_node.files) == 0 and level != -1:
            node = tree_node
            while len(node.dirs) == 1 and len(node.files) == 0:
                dir_name, node = node.dirs.last_key_value()
                meta_info.name = "{}/{}".format(meta_info.name, dir_name)
                meta_info.path = "{}{}/".format(meta_info.path, dir_name)
                meta_info.info = node
                if level == 0:
                    node.status = FolderStatus.OPEN

            if recursive == True or node.status == FolderStatus.OPEN:
                yield from self.metaInfoGenerator(meta_info, recursive, level + 1)

            return

        for dir_name, node in tree_node.dirs.items():
            cur_path = "{}{}/".format(meta_info.path, dir_name)
            info = MetaInfo(meta_info.level + 1, True, dir_name, node, cur_path)
            yield info
            if recursive == True or node.status == FolderStatus.OPEN:
                yield from self.metaInfoGenerator(info, recursive, level + 1)

        for k, v in tree_node.files.items():
            yield MetaInfo(meta_info.level + 1, False, k, v, lfGetFilePath(v))

    def expandOrCollapseFolder(self, recursive=False):
        with self._lock:
            line_num = int(lfEval("getcurpos({})[1]".format(self.getWindowId())))
            index = line_num - self.startLine()
            # the root
            if index == -1 and recursive == True:
                self.expandRoot(line_num)
                return None

            structure = self._file_structures[self._cur_parent]
            if index < 0 or index >= len(structure):
                return None

            meta_info = structure[index]
            if meta_info.is_dir:
                if meta_info.info.status == FolderStatus.CLOSED:
                    self.expandFolder(line_num, index, meta_info, recursive)
                elif recursive == True:
                    self.collapseFolder(line_num, index, meta_info, recursive)
                    self.expandFolder(line_num, index, meta_info, recursive)
                else:
                    self.collapseFolder(line_num, index, meta_info, recursive)
                return None
            else:
                return meta_info.info

    def collapseChildren(self):
        with self._lock:
            line_num = vim.current.window.cursor[0]
            index = line_num - self.startLine()
            structure = self._file_structures[self._cur_parent]
            if index < -1 or index >= len(structure):
                return

            # the root
            if index == -1:
                level = -1
            else:
                meta_info = structure[index]
                if not meta_info.is_dir:
                    return

                level = meta_info.level

            index += 1
            line_num += 1
            while index < len(structure) and structure[index].level > level and structure[index].is_dir:
                if structure[index].info.status == FolderStatus.OPEN:
                    self.collapseFolder(line_num, index, structure[index], False)
                index += 1
                line_num += 1

    def expandRoot(self, line_num):
        meta_info = MetaInfo(-1, True, "", self._trees[self._cur_parent], "")
        self._file_structures[self._cur_parent] = list(self.metaInfoGenerator(meta_info, True, -1))
        self._buffer.options['modifiable'] = True
        structure = self._file_structures[self._cur_parent]
        try:
            increment = len(structure)
            self._buffer[line_num:] = [self.buildLine(info) for info in structure]
            self._offset_in_content = increment
        finally:
            self._buffer.options['modifiable'] = False

        return increment

    def expandFolder(self, line_num, index, meta_info, recursive):
        structure = self._file_structures[self._cur_parent]
        size = len(structure)
        structure[index + 1 : index + 1] = self.metaInfoGenerator(meta_info, recursive, 0)
        self._buffer.options['modifiable'] = True
        try:
            increment = len(structure) - size
            if index >= 0:
                self._buffer[line_num - 1] = self.buildLine(structure[index])
            self._buffer.append([self.buildLine(info)
                                 for info in structure[index + 1 : index + 1 + increment]],
                                line_num)
            self._offset_in_content += increment
        finally:
            self._buffer.options['modifiable'] = False

        return increment

    def collapseFolder(self, line_num, index, meta_info, recursive):
        meta_info.info.status = FolderStatus.CLOSED
        # # Should all the status be set as CLOSED ?
        # # No.
        # if "/" in meta_info.name:
        #     prefix = meta_info.path[:len(meta_info.path) - len(meta_info.name) - 2]
        #     tree_node = self._trees[self._cur_parent]
        #     for d in prefix.split("/"):
        #         tree_node = tree_node.dirs[d]

        #     for d in meta_info.name.split("/"):
        #         tree_node = tree_node.dirs[d]
        #         tree_node.status = FolderStatus.CLOSED

        structure = self._file_structures[self._cur_parent]
        cur_node = meta_info.info
        children_num = len(cur_node.dirs) + len(cur_node.files)
        if (index + children_num + 1 == len(structure)
            or not structure[index + children_num + 1].path.startswith(meta_info.path)):
            decrement = children_num
        else:
            pos = Bisect.bisect_right(structure, False, lo=index + children_num + 1,
                                      key=lambda info: not info.path.startswith(meta_info.path))
            decrement = pos - 1 - index

        del structure[index + 1 : index + 1 + decrement]
        self._buffer.options['modifiable'] = True
        try:
            self._buffer[line_num - 1] = self.buildLine(structure[index])
            del self._buffer[line_num:line_num + decrement]
            self._offset_in_content -= decrement
        finally:
            self._buffer.options['modifiable'] = False

    def inFileStructure(self, path):
        *directories, file = path.split("/")
        tree_node = self._trees[self._cur_parent]
        for d in directories:
            if d not in tree_node.dirs:
                return False
            tree_node = tree_node.dirs[d]

        return file in tree_node.files

    def locateFile(self, path):
        with self._lock:
            self._locateFile(PurePath(lfRelpath(path)).as_posix())

    @staticmethod
    def getDirName(path):
        if path.endswith("/"):
            return path
        else:
            path = os.path.dirname(path)
            if path != "":
                path += "/"
            return path

    def _locateFile(self, path):
        def getKey(info):
            if info.path == path:
                return 0
            else:
                info_path_dir = TreeView.getDirName(info.path)
                path_dir = TreeView.getDirName(path)
                if ((info.path > path
                     and not (info_path_dir.startswith(path_dir) and info_path_dir != path_dir)
                     )
                    or
                    (info.path < path and info.is_dir == False
                     and (path_dir.startswith(info_path_dir) and info_path_dir != path_dir)
                     )
                    ):
                    return 1
                else:
                    return -1

        structure = self._file_structures[self._cur_parent]
        index = Bisect.bisect_left(structure, 0, key=getKey)
        if index < len(structure) and structure[index].path == path:
            lfCmd("call win_execute({}, 'norm! {}G0zz')"
                  .format(self.getWindowId(), index + self.startLine()))
        else:
            if not self.inFileStructure(path):
                lfPrintError("File can't be found!")
                return

            meta_info = structure[index-1]
            prefix_len = len(meta_info.path)
            tree_node = meta_info.info
            *directories, file = path[prefix_len:].split("/")
            node = tree_node
            node.status = FolderStatus.OPEN
            for d in directories:
                node = node.dirs[d]
                node.status = FolderStatus.OPEN

            line_num = index + self.startLine() - 1
            increment = self.expandFolder(line_num, index - 1, meta_info, False)

            index = Bisect.bisect_left(structure, 0, index, index + increment, key=getKey)
            if index < len(structure) and structure[index].path == path:
                lfCmd("call win_execute({}, 'norm! {}G0zz')"
                      .format(self.getWindowId(), index + self.startLine()))
            else:
                lfPrintError("BUG: File can't be found!")

    def buildLine(self, meta_info):
        if meta_info.is_dir:
            if meta_info.info.status == FolderStatus.CLOSED:
                icon = self._closed_folder_icon
            else:
                icon = self._open_folder_icon
            return "{}{} {}/".format("  " * meta_info.level, icon, meta_info.name)
        else:
            num_stat = self._num_stat.get(self._cur_parent, {}).get(meta_info.path, "")
            if num_stat != "":
                meta_info.has_num_stat = True

            icon = self._status_icons.get(meta_info.info[2][0], self._modification_icon)

            orig_name = ""
            if meta_info.info[2][0] in ("R", "C"):
                orig_name = "{} => ".format(PurePath(lfRelpath(meta_info.info[3],
                                                               os.path.dirname(meta_info.info[4]))).as_posix())

            return "{}{} {}{}\t{}".format("  " * meta_info.level,
                                          icon,
                                          orig_name,
                                          meta_info.name,
                                          num_stat
                                          )

    def setOptions(self, winid, bufhidden):
        super(TreeView, self).setOptions(winid, bufhidden)
        lfCmd(r"""call win_execute({}, 'let &l:stl="%#Lf_hl_gitStlChangedNum# 0 %#Lf_hl_gitStlFileChanged#file changed, %#Lf_hl_gitStlAdd#0 (+), %#Lf_hl_gitStlDel#0 (-)"')"""
              .format(winid))
        if lfEval("has('nvim')") == '1':
            lfCmd("call nvim_win_set_option(%d, 'cursorline', v:false)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
        else:
            lfCmd("call win_execute({}, 'setlocal nocursorline')".format(winid))
            lfCmd("call win_execute({}, 'setlocal nonumber')".format(winid))
        lfCmd("call win_execute({}, 'noautocmd setlocal sw=2 tabstop=4')".format(winid))
        lfCmd("call win_execute({}, 'setlocal signcolumn=no')".format(winid))
        lfCmd("call win_execute({}, 'setlocal foldmethod=indent')".format(winid))
        lfCmd("call win_execute({}, 'setlocal foldcolumn=1')".format(winid))
        lfCmd("call win_execute({}, 'setlocal conceallevel=0')".format(winid))
        lfCmd("call win_execute({}, 'setlocal winfixwidth')".format(winid))
        lfCmd("call win_execute({}, 'setlocal winfixheight')".format(winid))
        try:
            lfCmd(r"call win_execute({}, 'setlocal list lcs=leadmultispace:¦\ ,tab:\ \ ')"
                  .format(winid))
        except vim.error:
            lfCmd("call win_execute({}, 'setlocal nolist')".format(winid))
        lfCmd("augroup Lf_Git_Colorscheme | augroup END")
        lfCmd("autocmd Lf_Git_Colorscheme ColorScheme * call leaderf#colorscheme#popup#load('Git', '{}')"
              .format(lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))

    def initBuffer(self):
        self._buffer.options['modifiable'] = True
        try:
            self._buffer.append(self._head)
        finally:
            self._buffer.options['modifiable'] = False

    def refreshNumStat(self):
        self._buffer.options['modifiable'] = True
        try:
            init_line = self.startLine() - 1
            structure = self._file_structures[self._cur_parent]
            for i, info in enumerate(structure, init_line):
                if info.has_num_stat == True:
                    return
                if not info.is_dir:
                    self._buffer[i] = self.buildLine(info)
        finally:
            self._buffer.options['modifiable'] = False

    def writeBuffer(self):
        if self._cur_parent is None:
            return

        if self._read_finished == 2:
            return

        if not self._buffer.valid:
            self.stopTimer()
            return

        with self._lock:
            self._buffer.options['modifiable'] = True
            try:
                structure = self._file_structures[self._cur_parent]
                cur_len = len(structure)
                if cur_len > self._offset_in_content:
                    cursor_line = int(lfEval("getcurpos({})[1]".format(self.getWindowId())))
                    init_line = self.startLine() - 1

                    if cursor_line <= init_line:
                        lfCmd("call win_execute({}, 'norm! {}G')"
                              .format(self.getWindowId(), init_line))
                        cursor_line = int(lfEval("getcurpos({})[1]".format(self.getWindowId())))

                    source = None
                    for info in structure[self._offset_in_content:cur_len]:
                        self._buffer.append(self.buildLine(info))
                        if cursor_line == init_line and not info.is_dir:
                            if self._target_path is None or info.path == self._target_path:
                                cursor_line = len(self._buffer)
                                source = info.info

                    if source is not None:
                        self._callback(source)
                        if lfEval("has('nvim')") == '1':
                            lfCmd("call nvim_win_set_option({}, 'cursorline', v:true)"
                                  .format(self.getWindowId()))
                        else:
                            lfCmd("call win_execute({}, 'setlocal cursorline')"
                                  .format(self.getWindowId()))
                        lfCmd("call win_execute({}, 'norm! {}G0zz')"
                              .format(self.getWindowId(), cursor_line))

                    if self._target_path is None:
                        lfCmd("call win_gotoid({})".format(self.getWindowId()))

                    self._offset_in_content = cur_len
                    lfCmd("redraw")
            finally:
                self._buffer.options['modifiable'] = False

        if self._read_finished == 1 and self._offset_in_content == len(structure):
            self.refreshNumStat()
            shortstat = re.sub(r"( \d+)( files? changed)",
                               r"%#Lf_hl_gitStlChangedNum#\1%#Lf_hl_gitStlFileChanged#\2",
                               self._short_stat[self._cur_parent])
            shortstat = re.sub(r"(\d+) insertions?", r"%#Lf_hl_gitStlAdd#\1 ",shortstat)
            shortstat = re.sub(r"(\d+) deletions?", r"%#Lf_hl_gitStlDel#\1 ", shortstat)
            lfCmd(r"""call win_execute({}, 'let &l:stl="{}"')"""
                  .format(self.getWindowId(), shortstat))
            self._read_finished = 2
            self._owner.writeFinished(self.getWindowId())
            self.stopTimer()

    def _readContent(self, encoding):
        try:
            content = self._executor.execute(self._cmd.getCommand(),
                                             encoding=encoding,
                                             cwd=self._project_root
                                             )
            for line in content:
                self.buildTree(line)
                if self._stop_reader_thread:
                    break
            else:
                self._read_finished = 1
                self._owner.readFinished(self)
        except Exception:
            traceback.print_exc()
            traceback.print_stack()
            self._read_finished = 1

    def cleanup(self):
        super(TreeView, self).cleanup()
        self._match_ids = []


class Panel(object):
    def __init__(self):
        self._project_root = None

    def getProjectRoot(self):
        return self._project_root

    def register(self, view):
        pass

    def deregister(self, view):
        pass

    def bufHidden(self, view):
        pass

    def cleanup(self):
        pass

    def writeBuffer(self):
        pass

    def readFinished(self, view):
        pass

    def writeFinished(self, winid):
        pass


class ResultPanel(Panel):
    def __init__(self):
        super(ResultPanel, self).__init__()
        self._views = {}
        self._sources = set()

    def register(self, view):
        self._views[view.getBufferName()] = view
        self._sources.add(view.getSource())

    def deregister(self, view):
        name = view.getBufferName()
        if name in self._views:
            self._sources.discard(self._views[name].getSource())
            self._views[name].cleanup()
            del self._views[name]

    def getSources(self):
        return self._sources

    def _createWindow(self, win_pos, buffer_name):
        if win_pos == 'tab':
            lfCmd("silent! keepa keepj hide edit {}".format(buffer_name))
        elif win_pos == 'top':
            lfCmd("silent! noa keepa keepj abo sp {}".format(buffer_name))
        elif win_pos == 'bottom':
            lfCmd("silent! noa keepa keepj bel sp {}".format(buffer_name))
        elif win_pos == 'left':
            lfCmd("silent! noa keepa keepj abo vsp {}".format(buffer_name))
        elif win_pos == 'right':
            lfCmd("silent! noa keepa keepj bel vsp {}".format(buffer_name))
        else:
            lfCmd("silent! keepa keepj hide edit {}".format(buffer_name))

        return int(lfEval("win_getid()"))

    def create(self, cmd, content=None):
        buffer_name = cmd.getBufferName()
        if buffer_name in self._views and self._views[buffer_name].valid():
            self._views[buffer_name].create(-1, buf_content=content)
        else:
            arguments = cmd.getArguments()
            if arguments.get("mode") == 't':
                win_pos = 'tab'
            else:
                win_pos = arguments.get("--position", ["top"])[0]
            winid = self._createWindow(win_pos, buffer_name)
            GitCommandView(self, cmd).create(winid, buf_content=content)
            if cmd.getFileType() in ("diff", "git"):
                key_map = lfEval("g:Lf_GitKeyMap")
                lfCmd("call win_execute({}, 'nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#PreviousChange(1)<CR>')"
                      .format(winid, key_map["previous_change"]))
                lfCmd("call win_execute({}, 'nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#NextChange(1)<CR>')"
                      .format(winid, key_map["next_change"]))
                lfCmd("call win_execute({}, 'nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#EditFile(1)<CR>')"
                      .format(winid, key_map["edit_file"]))

    def writeBuffer(self):
        for v in self._views.values():
            v.writeBuffer()


class PreviewPanel(Panel):
    def __init__(self):
        super(PreviewPanel, self).__init__()
        self._view = None
        self._buffer_contents = {}
        self._preview_winid = 0

    def register(self, view):
        if self._view is not None:
            self._view.cleanup()
        self._view = view

    def deregister(self, view):
        if self._view is view:
            self._view.cleanup()
            self._view = None

    def create(self, cmd, config, buf_content=None, project_root=None):
        self._project_root = project_root
        if lfEval("has('nvim')") == '1':
            lfCmd("noautocmd let scratch_buffer = nvim_create_buf(0, 1)")
            self._preview_winid = int(lfEval("nvim_open_win(scratch_buffer, 0, %s)"
                                             % json.dumps(config)))
        else:
            lfCmd("noautocmd silent! let winid = popup_create([], %s)" % json.dumps(config))
            self._preview_winid = int(lfEval("winid"))

        GitCommandView(self, cmd).create(self._preview_winid, buf_content=buf_content)

    def createView(self, cmd):
        if self._preview_winid > 0:
            GitCommandView(self, cmd).create(self._preview_winid)

    def writeBuffer(self):
        if self._view is not None:
            self._view.writeBuffer()

    def getPreviewWinId(self):
        return self._preview_winid

    def cleanup(self):
        if self._view is not None:
            # may never run here
            self._view.cleanup()
        self._view = None
        self._buffer_contents = {}
        self._preview_winid = 0

    def readFinished(self, view):
        self._buffer_contents[view.getSource()] = view.getContent()

    def getContent(self, source):
        return self._buffer_contents.get(source)

    def setContent(self, content):
        if self._view:
            self._view.setContent(content)

    def getViewContent(self):
        if self._view:
            return self._view.getContent()

        return []


class DiffViewPanel(Panel):
    def __init__(self, bufhidden_callback=None, commit_id=""):
        super(DiffViewPanel, self).__init__()
        self._commit_id = commit_id
        self._views = {}
        self._hidden_views = {}
        # key is current tabpage
        self._buffer_names = {}
        self._bufhidden_cb = bufhidden_callback

    def setCommitId(self, commit_id):
        self._commit_id = commit_id

    def register(self, view):
        self._views[view.getBufferName()] = view

    def deregister(self, view):
        # :bw
        name = view.getBufferName()
        if name in self._views:
            self._views[name].cleanup(wipe=False)
            del self._views[name]

        if name in self._hidden_views:
            self._hidden_views[name].cleanup(wipe=False)
            del self._hidden_views[name]

    def bufHidden(self, view):
        name = view.getBufferName()
        if name in self._views:
            del self._views[name]
        self._hidden_views[name] = view
        lfCmd("call win_execute({}, 'diffoff')".format(view.getWindowId()))

        if self._bufhidden_cb is not None:
            self._bufhidden_cb()

    def bufShown(self, buffer_name, winid):
        view = self._hidden_views[buffer_name]
        view.setWindowId(winid)
        del self._hidden_views[buffer_name]
        self._views[buffer_name] = view
        lfCmd("call win_execute({}, 'diffthis')".format(winid))

    def cleanup(self):
        for view in self._hidden_views.values():
            view.cleanup()
        self._hidden_views = {}

        self._buffer_names = {}

    def writeFinished(self, winid):
        lfCmd("call win_execute({}, 'diffthis')".format(winid))

    def getValidWinIDs(self, win_ids, win_pos):
        if win_ids == [-1, -1]:
            if win_pos in ["top", "left"]:
                lfCmd("wincmd w")
            else:
                lfCmd("wincmd W")
            lfCmd("leftabove new")
            win_ids[1] = int(lfEval("win_getid()"))
            lfCmd("noautocmd leftabove vertical new")
            win_ids[0] = int(lfEval("win_getid()"))
        elif win_ids[0] == -1:
            lfCmd("call win_gotoid({})".format(win_ids[1]))
            lfCmd("noautocmd leftabove vertical new")
            win_ids[0] = int(lfEval("win_getid()"))
        elif win_ids[1] == -1:
            lfCmd("call win_gotoid({})".format(win_ids[0]))
            lfCmd("noautocmd rightbelow vertical new")
            win_ids[1] = int(lfEval("win_getid()"))

        return win_ids

    def isAllHidden(self):
        return len(self._views) == 0

    def create(self, arguments_dict, source, **kwargs):
        """
        source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        self._project_root = kwargs.get("project_root", None)
        file_path = lfGetFilePath(source)
        sources = ((source[0], source[2], source[3]),
                   (source[1], source[2], file_path))
        buffer_names = (GitCatFileCommand.buildBufferName(self._commit_id, sources[0]),
                        GitCatFileCommand.buildBufferName(self._commit_id, sources[1]))
        target_winid = None
        if buffer_names[0] in self._views and buffer_names[1] in self._views:
            win_ids = (self._views[buffer_names[0]].getWindowId(),
                       self._views[buffer_names[1]].getWindowId())
            lfCmd("call win_gotoid({})".format(win_ids[1]))
            target_winid = win_ids[1]
        elif buffer_names[0] in self._views:
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[0]].getWindowId()))
            cmd = GitCatFileCommand(arguments_dict, sources[1], self._commit_id)
            lfCmd("rightbelow vsp {}".format(cmd.getBufferName()))
            if buffer_names[1] in self._hidden_views:
                self.bufShown(buffer_names[1], int(lfEval("win_getid()")))
            else:
                GitCommandView(self, cmd).create(int(lfEval("win_getid()")), bufhidden='hide')
            target_winid = int(lfEval("win_getid()"))
            lfCmd("call win_execute({}, 'setlocal cursorlineopt=number')".format(target_winid))
            lfCmd("call win_execute({}, 'setlocal cursorline')".format(target_winid))
        elif buffer_names[1] in self._views:
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[1]].getWindowId()))
            cmd = GitCatFileCommand(arguments_dict, sources[0], self._commit_id)
            lfCmd("leftabove vsp {}".format(cmd.getBufferName()))
            if buffer_names[0] in self._hidden_views:
                self.bufShown(buffer_names[0], int(lfEval("win_getid()")))
            else:
                GitCommandView(self, cmd).create(int(lfEval("win_getid()")), bufhidden='hide')
            lfCmd("call win_execute({}, 'setlocal cursorlineopt=number')"
                  .format(int(lfEval("win_getid()"))))
            lfCmd("call win_execute({}, 'setlocal cursorline')".format(int(lfEval("win_getid()"))))
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[1]].getWindowId()))
            target_winid = int(lfEval("win_getid()"))
        else:
            if kwargs.get("mode", '') == 't':
                lfCmd("noautocmd tabnew | vsp")
                tabmove()
                win_ids = [int(lfEval("win_getid({})".format(w.number)))
                           for w in vim.current.tabpage.windows]
            elif "winid" in kwargs: # --explorer create
                win_ids = [kwargs["winid"], 0]
                lfCmd("call win_gotoid({})".format(win_ids[0]))
                lfCmd("noautocmd bel vsp")
                win_ids[1] = int(lfEval("win_getid()"))
                lfCmd("call win_gotoid({})".format(win_ids[0]))
            elif vim.current.tabpage not in self._buffer_names: # Leaderf git diff -s
                lfCmd("noautocmd tabnew | vsp")
                tabmove()
                win_ids = [int(lfEval("win_getid({})".format(w.number)))
                           for w in vim.current.tabpage.windows]
            else: # open
                buffer_names = self._buffer_names[vim.current.tabpage]
                win_ids = [int(lfEval("bufwinid('{}')".format(escQuote(name))))
                           for name in buffer_names]
                win_pos = arguments_dict.get("--navigation-position", ["left"])[0]
                win_ids = self.getValidWinIDs(win_ids, win_pos)

            target_winid = win_ids[1]
            cat_file_cmds = [GitCatFileCommand(arguments_dict, s, self._commit_id) for s in sources]
            outputs = [None, None]
            if (cat_file_cmds[0].getBufferName() not in self._hidden_views
                and cat_file_cmds[1].getBufferName() not in self._hidden_views):
                outputs = ParallelExecutor.run(*[cmd.getCommand() for cmd in cat_file_cmds],
                                               directory=self._project_root)

            if vim.current.tabpage not in self._buffer_names:
                self._buffer_names[vim.current.tabpage] = [None, None]

            for i, (cmd, winid) in enumerate(zip(cat_file_cmds, win_ids)):
                if (lfEval("bufname(winbufnr({}))".format(winid)) == ""
                    and int(lfEval("bufnr('{}')".format(escQuote(cmd.getBufferName())))) != -1):
                    lfCmd("call win_execute({}, 'setlocal bufhidden=wipe')".format(winid))

                buffer_name = lfEval("bufname(winbufnr({}))".format(winid))
                lfCmd("call win_execute({}, 'diffoff | hide edit {}')"
                      .format(winid, cmd.getBufferName()))
                lfCmd("call win_execute({}, 'setlocal cursorlineopt=number')".format(winid))
                lfCmd("call win_execute({}, 'setlocal cursorline')".format(winid))
                lfCmd("call win_execute({}, 'let b:lf_explorer_page_id = {}')"
                      .format(winid, kwargs.get("explorer_page_id", 0)))
                lfCmd("call win_execute({}, 'let b:lf_git_diff_win_pos = {}')".format(winid, i))
                lfCmd("call win_execute({}, 'let b:lf_git_diff_win_id = {}')".format(winid, win_ids[1]))
                lfCmd("""call win_execute(%d, "let b:lf_git_buffer_name = '%s'")"""
                      % (winid, escQuote(os.path.abspath(lfGetFilePath(source)))))
                lfCmd("""call win_execute({}, 'let b:lf_diff_view_mode = "side-by-side"')"""
                      .format(winid))
                lfCmd("""call win_execute({}, "let b:lf_diff_view_source = {}")"""
                      .format(winid, str(list(source))))
                key_map = lfEval("g:Lf_GitKeyMap")
                lfCmd("""call win_execute({}, 'nnoremap <buffer> <silent> {} [c')"""
                      .format(winid, key_map["previous_change"]))
                lfCmd("""call win_execute({}, 'nnoremap <buffer> <silent> {} ]c')"""
                      .format(winid, key_map["next_change"]))
                lfCmd("""call win_execute({}, 'nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#EditFile(2)<CR>')"""
                      .format(winid, key_map["edit_file"]))

                # if the buffer also in another tabpage, BufHidden is not triggerd
                # should run this code
                if buffer_name in self._views:
                    self.bufHidden(self._views[buffer_name])

                self._buffer_names[vim.current.tabpage][i] = cmd.getBufferName()
                if cmd.getBufferName() in self._hidden_views:
                    self.bufShown(cmd.getBufferName(), winid)
                else:
                    GitCommandView(self, cmd).create(winid, bufhidden='hide',
                                                     buf_content=outputs[i])

            lfCmd("call win_gotoid({})".format(win_ids[1]))

        if kwargs.get("line_num", None) is not None:
            lfCmd("call win_execute({}, 'norm! {}G0zbzz')"
                  .format(target_winid, kwargs["line_num"]))
        else:
            lfCmd("call win_execute({}, 'norm! gg]c0')".format(target_winid))

        # sometimes the two sides don't align.
        lfCmd("call win_execute({}, 'norm! ztzz')".format(target_winid))


class UnifiedDiffViewPanel(Panel):
    def __init__(self, bufhidden_callback=None, commit_id=""):
        super(UnifiedDiffViewPanel, self).__init__()
        self._commit_id = commit_id
        self._views = {}
        self._hidden_views = {}
        self._bufhidden_cb = bufhidden_callback
        lfCmd("sign define Leaderf_diff_add linehl=Lf_hl_gitDiffAdd")
        lfCmd("sign define Leaderf_diff_delete linehl=Lf_hl_gitDiffDelete")
        lfCmd("sign define Leaderf_diff_change linehl=Lf_hl_gitDiffChange")

    def setCommitId(self, commit_id):
        self._commit_id = commit_id

    def register(self, view):
        self._views[view.getBufferName()] = view

    def deregister(self, view):
        # :bw
        name = view.getBufferName()
        if name in self._views:
            self._views[name].cleanup(wipe=False)
            del self._views[name]

        if name in self._hidden_views:
            self._hidden_views[name].cleanup(wipe=False)
            del self._hidden_views[name]

    def bufHidden(self, view):
        # window is closed if not equal
        if int(lfEval("win_getid()")) == view.getWindowId():
            lfCmd("silent! call leaderf#Git#ClearMatches()")

        name = view.getBufferName()
        if name in self._views:
            del self._views[name]
        self._hidden_views[name] = view

        if self._bufhidden_cb is not None:
            self._bufhidden_cb()

    def bufShown(self, buffer_name, winid):
        view = self._hidden_views[buffer_name]
        view.setWindowId(winid)
        del self._hidden_views[buffer_name]
        self._views[buffer_name] = view
        lfCmd("call setmatches(b:Leaderf_matches, {})".format(winid))

    def cleanup(self):
        for view in self._hidden_views.values():
            view.cleanup()
        self._hidden_views = {}

    def isAllHidden(self):
        return len(self._views) == 0

    def signPlace(self, added_line_nums, deleted_line_nums, buffer_num):
        lfCmd("call leaderf#Git#SignPlace({}, {}, {})"
              .format(str(added_line_nums), str(deleted_line_nums), buffer_num))

    def setLineNumberWin(self, line_num_content, buffer_num):
        if lfEval("has('nvim')") == '1':
            self.nvim_setLineNumberWin(line_num_content, buffer_num)
            return

        hi_line_num = int(lfEval("get(g:, 'Lf_GitHightlightLineNumber', 1)"))
        for i, line in enumerate(line_num_content, 1):
            if line[-2] == '-':
                if hi_line_num == 1:
                    property_type = "Lf_hl_gitDiffDelete"
                else:
                    property_type = "Lf_hl_LineNr"
                lfCmd("call prop_add(%d, 1, {'type': '%s', 'text': '%s', 'bufnr': %d})"
                      % (i, property_type, line[:-2], buffer_num))
                property_type = "Lf_hl_gitDiffDelete"
                lfCmd("call prop_add(%d, 1, {'type': '%s', 'text': '%s', 'bufnr': %d})"
                      % (i, property_type, line[-2:], buffer_num))
            elif line[-2] == '+':
                if hi_line_num == 1:
                    property_type = "Lf_hl_gitDiffAdd"
                else:
                    property_type = "Lf_hl_LineNr"
                lfCmd("call prop_add(%d, 1, {'type': '%s', 'text': '%s', 'bufnr': %d})"
                      % (i, property_type, line[:-2], buffer_num))
                property_type = "Lf_hl_gitDiffAdd"
                lfCmd("call prop_add(%d, 1, {'type': '%s', 'text': '%s', 'bufnr': %d})"
                      % (i, property_type, line[-2:], buffer_num))
            else:
                property_type = "Lf_hl_LineNr"
                lfCmd("call prop_add(%d, 1, {'type': '%s', 'text': '%s', 'bufnr': %d})"
                      % (i, property_type, line, buffer_num))

    def nvim_setLineNumberWin(self, line_num_content, buffer_num):
        lfCmd("call leaderf#Git#SetLineNumberWin({}, {})".format(str(line_num_content),
                                                                 buffer_num))

    def highlight(self, winid, status, content, line_num, line):
        i = 0
        while i < len(line):
            if line[i] == status or line[i] == '^':
                c = line[i]
                beg = i
                i += 1
                while i < len(line) and line[i] == c:
                    i += 1
                end = i
                col = lfBytesLen(content[line_num-1][:beg]) + 1
                length = lfBytesLen(content[line_num - 1][beg : end])
                if c == '^':
                    hl_group = "Lf_hl_gitDiffText"
                elif c == '-':
                    hl_group = "Lf_hl_gitDiffText"
                else:
                    hl_group = "Lf_hl_gitDiffText"
                lfCmd("""call win_execute({}, "let matchid = matchaddpos('{}', [{}], -100)")"""
                        .format(winid, hl_group, str([line_num, col, length])))
            else:
                i += 1

    def highlightOneline(self, winid, content, minus_beg, plus_beg):
        sm = SequenceMatcher(None, content[minus_beg-1], content[plus_beg-1])
        opcodes = sm.get_opcodes()
        if len(opcodes) == 1 and opcodes[0][0] == "replace":
            return

        hl_group = "Lf_hl_gitDiffChange"
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
              .format(winid, hl_group, minus_beg))
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
              .format(winid, hl_group, plus_beg))

        for tag, beg1, end1, beg2, end2 in sm.get_opcodes():
            if tag == "delete":
                col = lfBytesLen(content[minus_beg-1][:beg1]) + 1
                length = lfBytesLen(content[minus_beg - 1][beg1 : end1])
                hl_group = "Lf_hl_gitDiffText"
                lfCmd("""call win_execute({}, "let matchid = matchaddpos('{}', [{}], -100)")"""
                      .format(winid, hl_group, str([minus_beg, col, length])))
            elif tag == "insert":
                col = lfBytesLen(content[plus_beg-1][:beg2]) + 1
                length = lfBytesLen(content[plus_beg - 1][beg2 : end2])
                hl_group = "Lf_hl_gitDiffText"
                lfCmd("""call win_execute({}, "let matchid = matchaddpos('{}', [{}], -100)")"""
                      .format(winid, hl_group, str([plus_beg, col, length])))
            elif tag == "replace":
                col = lfBytesLen(content[minus_beg-1][:beg1]) + 1
                length = lfBytesLen(content[minus_beg - 1][beg1 : end1])
                hl_group = "Lf_hl_gitDiffText"
                lfCmd("""call win_execute({}, "let matchid = matchaddpos('{}', [{}], -100)")"""
                      .format(winid, hl_group, str([minus_beg, col, length])))

                col = lfBytesLen(content[plus_beg-1][:beg2]) + 1
                length = lfBytesLen(content[plus_beg - 1][beg2 : end2])
                hl_group = "Lf_hl_gitDiffText"
                lfCmd("""call win_execute({}, "let matchid = matchaddpos('{}', [{}], -100)")"""
                      .format(winid, hl_group, str([plus_beg, col, length])))

    def highlightDiff(self, winid, content, minus_plus_lines):
        for minus_beg, minus_end, plus_beg, plus_end in minus_plus_lines:
            if minus_beg == minus_end and plus_beg == plus_end:
                self.highlightOneline(winid, content, minus_beg, plus_beg)
                continue

            minus_text = content[minus_beg - 1 : minus_end]
            plus_text = content[plus_beg - 1 : plus_end]
            minus_line_num = minus_beg - 1
            plus_line_num = plus_beg - 1
            status = ' '
            changed_line_num = 0
            for line in LfDiffer().compare(minus_text, plus_text):
                if line.startswith('- '):
                    status = '-'
                    minus_line_num += 1
                elif line.startswith('+ '):
                    status = '+'
                    plus_line_num += 1
                elif line.startswith('? '):
                    if status == '-':
                        hl_group = "Lf_hl_gitDiffChange"
                        changed_line_num = plus_line_num + 1
                        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
                              .format(winid, hl_group, minus_line_num))
                        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
                              .format(winid, hl_group, plus_line_num + 1))
                        self.highlight(winid, status, content, minus_line_num, line[2:])
                    elif status == '+':
                        hl_group = "Lf_hl_gitDiffChange"
                        if changed_line_num != plus_line_num:
                            lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
                                  .format(winid, hl_group, minus_line_num))
                            lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''{}'', ''\%{}l'', -101)')"""
                                  .format(winid, hl_group, plus_line_num))
                        self.highlight(winid, status, content, plus_line_num, line[2:])
                elif line.startswith('  '):
                    status = ' '
                    minus_line_num += 1
                    plus_line_num += 1

    def setSomeOptions(self):
        lfCmd("setlocal foldcolumn=1")
        lfCmd("setlocal signcolumn=no")
        lfCmd("setlocal nonumber")
        lfCmd("setlocal conceallevel=0")
        lfCmd("setlocal nowrap")
        lfCmd("setlocal foldmethod=expr")
        lfCmd("setlocal foldexpr=leaderf#Git#FoldExpr()")
        lfCmd("setlocal foldlevel=0")

    def create(self, arguments_dict, source, **kwargs):
        """
        source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        self._project_root = kwargs.get("project_root", None)
        ignore_whitespace = kwargs.get("ignore_whitespace", False)
        diff_algorithm = kwargs.get("diff_algorithm", "myers")
        algo_dict = {
            "myers": 0,
            "minimal": 2,
            "patience": 4,
            "histogram": 6
        }
        uid = algo_dict[diff_algorithm] + int(ignore_whitespace)
        buf_name = "LeaderF://{}:{}:{}".format(self._commit_id,
                                               uid,
                                               lfGetFilePath(source))
        if buf_name in self._views:
            winid = self._views[buf_name].getWindowId()
            lfCmd("call win_gotoid({})".format(winid))
        else:
            if kwargs.get("mode", '') == 't':
                lfCmd("noautocmd tabnew")
                tabmove()
                winid = int(lfEval("win_getid()"))
            elif "winid" in kwargs: # --explorer
                winid = kwargs["winid"]
            else:
                win_pos = arguments_dict.get("--navigation-position", ["left"])[0]
                if win_pos in ["top", "left"]:
                    lfCmd("wincmd w")
                else:
                    lfCmd("wincmd W")
                winid = int(lfEval("win_getid()"))

            if buf_name not in self._hidden_views:
                fold_ranges = []
                minus_plus_lines = []
                line_num_dict = {}
                change_start_lines = []
                delimiter = lfEval("get(g:, 'Lf_GitDelimiter', '│')")
                if source[0].startswith("0000000"):
                    git_cmd = "git show {}".format(source[1])
                    outputs = ParallelExecutor.run(git_cmd, directory=self._project_root)
                    line_num_width = len(str(len(outputs[0])))
                    content = outputs[0]
                    line_num_content = ["{:>{}} +{}".format(i, line_num_width, delimiter)
                                        for i in range(1, len(content) + 1)]
                    deleted_line_nums = []
                    added_line_nums = range(1, len(outputs[0]) + 1)
                elif source[1].startswith("0000000") and source[2] != 'M':
                    git_cmd = "git show {}".format(source[0])
                    outputs = ParallelExecutor.run(git_cmd, directory=self._project_root)
                    line_num_width = len(str(len(outputs[0])))
                    content = outputs[0]
                    line_num_content = ["{:>{}} -{}".format(i, line_num_width, delimiter)
                                        for i in range(1, len(content) + 1)]
                    deleted_line_nums = range(1, len(outputs[0]) + 1)
                    added_line_nums = []
                else:
                    if source[1].startswith("0000000"):
                        extra_options = "--diff-algorithm=" + diff_algorithm
                        if "--cached" in arguments_dict:
                            extra_options += " --cached"

                        if "extra" in arguments_dict:
                            extra_options += " " + " ".join(arguments_dict["extra"])

                        if ignore_whitespace == True:
                            extra_options += " -w"

                        git_cmd = "git diff -U999999 --no-color {} -- {}".format(extra_options,
                                                                                 source[3])
                    else:
                        extra_options = "--diff-algorithm=" + diff_algorithm
                        if ignore_whitespace == True:
                            extra_options += " -w"

                        git_cmd = "git diff -U999999 --no-color {} {} {}".format(extra_options,
                                                                                 source[0],
                                                                                 source[1])

                    outputs = ParallelExecutor.run(git_cmd, directory=self._project_root)
                    start = 0
                    for i, line in enumerate(outputs[0], 1):
                        if line.startswith("@@"):
                            start = i
                            break

                    line_num_width = len(str(len(outputs[0]) - start))

                    content = []
                    line_num_content = []
                    orig_line_num = 0
                    line_num = 0

                    minus_beg = 0
                    minus_end = 0
                    plus_beg = 0
                    plus_end = 0

                    change_start = 0
                    deleted_line_nums = []
                    added_line_nums = []
                    context_num = int(lfEval("get(g:, 'Lf_GitContextNum', 6)"))
                    if context_num < 0:
                        context_num = 6
                    beg = 1
                    for i, line in enumerate(islice(outputs[0], start, None), 1):
                        content.append(line[1:])
                        if line.startswith("-"):
                            # for fold
                            if beg != 0:
                                end = i - context_num - 1
                                if end > beg:
                                    fold_ranges.append([beg, end])
                                beg = 0

                            # for highlight
                            if plus_beg != 0:
                                plus_end = i - 1
                                minus_plus_lines.append((minus_beg, minus_end, plus_beg, plus_end))
                                minus_beg = 0
                                plus_beg = 0

                            if minus_beg == 0:
                                minus_beg = i

                            if change_start == 0:
                                change_start = i

                            deleted_line_nums.append(i)
                            orig_line_num += 1
                            line_num_content.append("{:>{}} {:{}} -{}".format(orig_line_num,
                                                                              line_num_width,
                                                                              " ",
                                                                              line_num_width,
                                                                              delimiter))
                        elif line.startswith("+"):
                            # for fold
                            if beg != 0:
                                end = i - context_num - 1
                                if end > beg:
                                    fold_ranges.append([beg, end])
                                beg = 0

                            # for highlight
                            if minus_beg != 0 and plus_beg == 0:
                                minus_end = i - 1
                                plus_beg = i

                            if change_start == 0:
                                change_start = i

                            added_line_nums.append(i)
                            line_num += 1
                            line_num_dict[line_num] = i
                            line_num_content.append("{:{}} {:>{}} +{}".format(" ",
                                                                              line_num_width,
                                                                              line_num,
                                                                              line_num_width,
                                                                              delimiter))
                        else:
                            # for fold
                            if beg == 0:
                                beg = i + context_num

                            # for highlight
                            if plus_beg != 0:
                                plus_end = i - 1
                                minus_plus_lines.append((minus_beg, minus_end, plus_beg, plus_end))
                                plus_beg = 0

                            minus_beg = 0

                            if change_start != 0:
                                change_start_lines.append(change_start)
                                change_start = 0

                            orig_line_num += 1
                            line_num += 1
                            line_num_dict[line_num] = i
                            line_num_content.append("{:>{}} {:>{}}  {}".format(orig_line_num,
                                                                               line_num_width,
                                                                               line_num,
                                                                               line_num_width,
                                                                               delimiter))
                    else:
                        # for fold
                        end = len(outputs[0]) - start
                        if beg != 0 and end > beg:
                            fold_ranges.append([beg, end])

                        # for highlight
                        if plus_beg != 0:
                            plus_end = end
                            minus_plus_lines.append((minus_beg, minus_end, plus_beg, plus_end))

                        if change_start != 0:
                            change_start_lines.append(change_start)

                lfCmd("call win_gotoid({})".format(winid))
                if not vim.current.buffer.name: # buffer name is empty
                    lfCmd("setlocal bufhidden=wipe")
                lfCmd("silent hide edit {}".format(buf_name))
                lfCmd("let b:lf_git_buffer_name = '%s'" % escQuote(os.path.abspath(lfGetFilePath(source))))
                lfCmd("let b:lf_git_line_num_content = {}".format(str(line_num_content)))
                lfCmd("augroup Lf_Git_Log | augroup END")
                lfCmd("autocmd! Lf_Git_Log BufWinEnter <buffer> call leaderf#Git#SetMatches()")
                ranges = (range(sublist[0], sublist[1] + 1) for sublist in fold_ranges)
                fold_ranges_dict = {i: 0 for i in itertools.chain.from_iterable(ranges)}
                lfCmd("let b:Leaderf_fold_ranges_dict = {}".format(str(fold_ranges_dict)))
                lfCmd("silent! IndentLinesDisable")
                self.setSomeOptions()

                cmd = GitCustomizeCommand(arguments_dict, "", buf_name, "", "")
                view = GitCommandView(self, cmd)
                view.line_num_dict = line_num_dict
                view.change_start_lines = change_start_lines
                view.create(winid, bufhidden='hide', buf_content=content)

                buffer_num = int(lfEval("winbufnr({})".format(winid)))
                self.signPlace(added_line_nums, deleted_line_nums, buffer_num)

                self.setLineNumberWin(line_num_content, buffer_num)
                self.highlightDiff(winid, content, minus_plus_lines)
                lfCmd("let b:Leaderf_matches = getmatches()")
                lfCmd("let b:lf_change_start_lines = {}".format(str(change_start_lines)))
                lfCmd("let b:lf_explorer_page_id = {}".format(kwargs.get("explorer_page_id", 0)))
                lfCmd("let b:lf_diff_view_mode = 'unified'")
                lfCmd("let b:lf_diff_view_source = {}".format(str(list(source))))
                key_map = lfEval("g:Lf_GitKeyMap")
                lfCmd("nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#PreviousChange(0)<CR>"
                      .format(key_map["previous_change"]))
                lfCmd("nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#NextChange(0)<CR>"
                      .format(key_map["next_change"]))
                lfCmd("nnoremap <buffer> <silent> {} :<C-U>call leaderf#Git#EditFile(0)<CR>"
                      .format(key_map["edit_file"]))
            else:
                lfCmd("call win_gotoid({})".format(winid))
                if not vim.current.buffer.name: # buffer name is empty
                    lfCmd("setlocal bufhidden=wipe")
                lfCmd("silent hide edit {}".format(buf_name))
                self.bufShown(buf_name, winid)
                self.setSomeOptions()

        target_line_num = kwargs.get("line_num", None)
        if target_line_num is not None:
            target_line_num = int(target_line_num)
            line_num = self._views[buf_name].line_num_dict.get(target_line_num, target_line_num)
            lfCmd("call win_execute({}, 'norm! {}G0zbzz')".format(winid, line_num))
        else:
            change_start_lines = self._views[buf_name].change_start_lines
            if len(change_start_lines) == 0:
                first_change = 1
            else:
                first_change = change_start_lines[0]
            lfCmd("call win_execute({}, 'norm! {}G0zbzz')".format(winid, first_change))


class NavigationPanel(Panel):
    def __init__(self, owner, project_root, commit_id, bufhidden_callback=None):
        super(NavigationPanel, self).__init__()
        self._owner = owner
        self._project_root = project_root
        self._commit_id = commit_id
        self.tree_view = None
        self._bufhidden_cb = bufhidden_callback
        self._is_hidden = False
        self._arguments = {}
        self._diff_view_mode = None
        self._ignore_whitespace = False
        self._diff_algorithm = 'myers'
        self._git_diff_manager = None
        self._winid = None
        self._buffer = None
        self._head = [
                '" Press <F1> for help',
                ' Side-by-side ◉ Unified ○',
                ' Ignore Whitespace 🗷 ',
                ' Myers ◉ Minimal ○ Patience ○ Histogram ○',
                '',
                ]

    def startLine(self):
        return len(self._head) + 1 + 1

    def getDiffViewMode(self):
        return self._diff_view_mode

    def getIgnoreWhitespace(self):
        return self._ignore_whitespace

    def getDiffAlgorithm(self):
        return self._diff_algorithm

    def register(self, view):
        self.tree_view = view

    def bufHidden(self, view):
        self._is_hidden = True
        if self._bufhidden_cb is not None:
            self._bufhidden_cb()

    def isHidden(self):
        return self._is_hidden

    def cleanup(self):
        if self.tree_view is not None:
            self.tree_view.cleanup()
            self.tree_view = None

    def create(self, arguments_dict, cmd, winid, project_root, target_path, callback):
        if "-u" in arguments_dict:
            self._diff_view_mode = "unified"
        elif "-s" in arguments_dict:
            self._diff_view_mode = "side-by-side"
        else:
            self._diff_view_mode = lfEval("get(g:, 'Lf_GitDiffViewMode', 'unified')")

        self._winid = winid
        self._buffer = vim.buffers[int(lfEval("winbufnr({})".format(winid)))]
        self._buffer[:] = self._head
        self.setDiffViewMode(self._diff_view_mode)

        self._arguments = cmd.getArguments()
        TreeView(self, cmd, project_root, target_path, callback).create(winid, bufhidden="hide")
        lfCmd("call win_execute({}, 'let b:lf_navigation_matches = getmatches()')".format(winid))

        self.defineMaps(winid)

    def defineMaps(self, winid):
        lfCmd("call win_execute({}, 'call leaderf#Git#NavigationPanelMaps({})')"
              .format(winid, id(self)))

    def setDiffViewMode(self, mode):
        self._buffer.options['modifiable'] = True
        if mode == 'side-by-side':
            self._buffer[1] = ' Side-by-side ◉ Unified ○'

            diffopt = lfEval("&diffopt")
            if "iwhiteall" in diffopt:
                self._buffer[2] = ' Ignore Whitespace 🗹 '
            else:
                self._buffer[2] = ' Ignore Whitespace 🗷 '

            if "algorithm:" in diffopt:
                algo = re.sub(r".*algorithm:(\w+).*", r"\1", diffopt)
                self.setDiffAlgorithm(algo)
            else:
                self.setDiffAlgorithm("myers")
        else:
            self._buffer[1] = ' Side-by-side ○ Unified ◉'
        self._buffer.options['modifiable'] = False

    def setIgnoreWhitespace(self, diff_view_mode, ignore):
        self._buffer.options['modifiable'] = True
        if diff_view_mode == 'side-by-side':
            if "iwhiteall" in lfEval("&diffopt"):
                self._buffer[2] = ' Ignore Whitespace 🗹 '
            else:
                self._buffer[2] = ' Ignore Whitespace 🗷 '
        else:
            if ignore == True:
                self._buffer[2] = ' Ignore Whitespace 🗹 '
            else:
                self._buffer[2] = ' Ignore Whitespace 🗷 '
        self._buffer.options['modifiable'] = False

    def setDiffAlgorithm(self, algorithm):
        self._buffer.options['modifiable'] = True
        if algorithm == 'myers':
            self._buffer[3] = ' Myers ◉ Minimal ○ Patience ○ Histogram ○'
        elif algorithm == 'minimal':
            self._buffer[3] = ' Myers ○ Minimal ◉ Patience ○ Histogram ○'
        elif algorithm == 'patience':
            self._buffer[3] = ' Myers ○ Minimal ○ Patience ◉ Histogram ○'
        elif algorithm == 'histogram':
            self._buffer[3] = ' Myers ○ Minimal ○ Patience ○ Histogram ◉'
        self._buffer.options['modifiable'] = False

    def selectOption(self):
        mouse_pos = lfEval("getmousepos()")
        column = int(mouse_pos["column"])
        if mouse_pos["line"] == '2':
            if column >= 5 and column <= 18:
                mode = 'side-by-side'
            elif column >= 22 and column <= 30:
                mode = 'unified'
            else:
                mode = None

            if mode is not None and mode != self._diff_view_mode:
                self.toggleDiffViewMode()
        elif mouse_pos["line"] == '3':
            if column >= 5 and column <= 23:
                self.toggleIgnoreWhitespace()
        elif mouse_pos["line"] == '4':
            if column >= 5 and column <= 11:
                diff_algorithm = 'myers'
            elif column >= 15 and column <= 23:
                diff_algorithm = 'minimal'
            elif column >= 27 and column <= 36:
                diff_algorithm = 'patience'
            elif column >= 40 and column <= 50:
                diff_algorithm = 'histogram'
            else:
                diff_algorithm = self._diff_algorithm

            if self._diff_algorithm != diff_algorithm:
                self._diff_algorithm = diff_algorithm
                self.selectDiffAlgorithm()

    def selectDiffAlgorithm(self):
        self.setDiffAlgorithm(self._diff_algorithm)
        if self._diff_view_mode == 'side-by-side':
            lfCmd("set diffopt+=internal")
            diffopt = lfEval("&diffopt")
            if "algorithm:" in diffopt:
                diffopt = re.sub(r"(?<=algorithm:)\w+", self._diff_algorithm, diffopt)
                lfCmd("let &diffopt = '{}'".format(diffopt))
            else:
                lfCmd("set diffopt+=algorithm:{}".format(self._diff_algorithm))
        else:
            self.openDiffView(False, preview=True, diff_view_source=True)

    def toggleDiffViewMode(self):
        if self._diff_view_mode == 'side-by-side':
            self._diff_view_mode = 'unified'
            self._ignore_whitespace = "iwhiteall" in lfEval("&diffopt")
        else:
            self._diff_view_mode = 'side-by-side'
            if self._ignore_whitespace == True:
                lfCmd("set diffopt+=iwhiteall")
            else:
                lfCmd("set diffopt-=iwhiteall")

        self.setDiffViewMode(self._diff_view_mode)

        if self._diff_view_mode == 'side-by-side':
            diffopt = lfEval("&diffopt")
            if "algorithm:" in diffopt:
                algo = re.sub(r".*algorithm:(\w+).*", r"\1", diffopt)
                self._diff_algorithm = algo
            else:
                self._diff_algorithm = "myers"

        self.openDiffView(False, preview=True, diff_view_source=True)

    def toggleIgnoreWhitespace(self):
        if self._diff_view_mode == 'side-by-side':
            if "iwhiteall" in lfEval("&diffopt"):
                lfCmd("set diffopt-=iwhiteall")
            else:
                lfCmd("set diffopt+=iwhiteall")
            self.setIgnoreWhitespace(self._diff_view_mode, self._ignore_whitespace)
        else:
            self._ignore_whitespace = not self._ignore_whitespace
            self.setIgnoreWhitespace(self._diff_view_mode, self._ignore_whitespace)
            self.openDiffView(False, preview=True, diff_view_source=True)

    def openDiffView(self, recursive, **kwargs):
        return self._owner.openDiffView(recursive, **kwargs)

    def open(self):
        buffer_name = self.tree_view.getBufferName()
        navigation_winid = int(lfEval("bufwinid('{}')".format(escQuote(buffer_name))))
        if navigation_winid != -1:
            lfCmd("call win_gotoid({})".format(navigation_winid))
            return

        current_file_path = vim.current.buffer.name.rsplit(':', 1)[1]
        win_pos = self._arguments.get("--navigation-position", ["left"])[0]
        if win_pos == 'top':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj topleft {}sp {}".format(height, buffer_name))
        elif win_pos == 'bottom':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj botright {}sp {}".format(height, buffer_name))
        elif win_pos == 'left':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj topleft {}vsp {}".format(width, buffer_name))
        elif win_pos == 'right':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj botright {}vsp {}".format(width, buffer_name))
        else: # left
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj topleft {}vsp {}".format(width, buffer_name))

        lfCmd("call setmatches(b:lf_navigation_matches)")
        lfCmd("setlocal winfixwidth | wincmd =")
        self._is_hidden = False
        self.tree_view.locateFile(current_file_path)

    def getWindowId(self):
        return self.tree_view.getWindowId()

    def locateFile(self, path, line_num=None, preview=True):
        self.tree_view.locateFile(path)
        self.openDiffView(False, line_num=line_num, preview=preview)

    @ensureWorkingDirectory
    def fuzzySearch(self, recall=False):
        if self._git_diff_manager is None:
            self._git_diff_manager = GitDiffExplManager()

        kwargs = {}
        kwargs["arguments"] = {
                "owner": self._owner._owner,
                "commit_id": self._commit_id,
                "parent": self.tree_view.getCurrentParent(),
                "content": self.tree_view.getFileList(),
                "accept": self.locateFile
                }

        if recall == True:
            kwargs["arguments"]["--recall"] = []

        self._git_diff_manager.startExplorer("popup", **kwargs)

    @ensureWorkingDirectory
    def showCommitMessage(self):
        cmd = "git show {} -s --decorate --pretty=fuller".format(self._commit_id)
        lfCmd("""call leaderf#Git#ShowCommitMessage(systemlist('{}'))""".format(cmd))


class BlamePanel(Panel):
    def __init__(self, owner):
        super(BlamePanel, self).__init__()
        self._owner = owner
        self._views = {}

    def register(self, view):
        self._views[view.getBufferName()] = view

    def deregister(self, view):
        name = view.getBufferName()
        if name in self._views:
            self._views[name].cleanup()
            del self._views[name]
            if len(self._views) == 0:
                self._owner.discardPanel(self.getProjectRoot())

    def getBlameView(self, buffer_name):
        return self._views[buffer_name]

    def getAlternateWinid(self, buffer_name):
        return self._views[buffer_name].getAlternateWinid()

    def getBlameStack(self, buffer_name):
        return self._views[buffer_name].blame_stack

    def getBlameDict(self, buffer_name):
        return self._views[buffer_name].blame_dict

    def getBlameBufferDict(self, buffer_name):
        return self._views[buffer_name].blame_buffer_dict

    @staticmethod
    def formatLine(arguments_dict, line_num_width, line):
        if line.startswith("0000000"):
            line = line.replace("External file (--contents)", "Not Committed Yet         ")

        date_format = arguments_dict.get("--date", ["iso"])[0]
        if date_format in ["iso", "iso-strict", "short"]:
            # 6817817e autoload/leaderf/manager.py 1 (Yggdroot 2014-02-26 00:37:26 +0800 1) #!/usr/bin/env python
            return re.sub(r'(^\^?\w+)\s+(.*?)\s+(\d+)\s+(\(.*?\d\d)\s+\d+\).*',
                          r'\g<1> \g<4>)\t\g<3> \g<2>', line, 1)
        elif date_format == "relative":
            # c5c6d072 autoload/leaderf/python/leaderf/manager.py 63 (Yggdroot 4 years, 6 months ago    66) def catchException(func):
            line = re.sub(r'(^.*?\s\d+\)).*', r'\g<1>', line, 1)
            return re.sub(r'(^\^?\w+)\s+(.*?)\s+(\d+)\s+(\(.*)',
                          r'\g<1> \g<4>)\t\g<3> \g<2>',
                          line[:-(line_num_width + 1)], 1)
        elif date_format == "local":
            # 6817817e autoload/leaderf/manager.py 1 (Yggdroot Wed Feb 26 00:37:26 2014  1) #!/usr/bin/env python
            line = re.sub(r'(^.*?\s\d+\)).*', r'\g<1>', line, 1)
            return re.sub(r'(^\^?\w+)\s+(.*?)\s+(\d+)\s+(\(.*)',
                          r'\g<1> \g<4>)\t\g<3> \g<2>',
                          line[:-(line_num_width + 7)], 1)
        elif date_format in ("rfc", "default"):
            # 6817817e autoload/leaderf/manager.py 1 (Yggdroot Wed, 26 Feb 2014 00:37:26 +0800    1) #!/usr/bin/env python
            # 6817817e autoload/leaderf/manager.py 1 (Yggdroot Wed Feb 26 00:37:26 2014 +0800    1) #!/usr/bin/env python
            line = re.sub(r'(^.*?\s\d+\)).*', r'\g<1>', line, 1)
            return re.sub(r'(^\^?\w+)\s+(.*?)\s+(\d+)\s+(\(.*)',
                          r'\g<1> \g<4>)\t\g<3> \g<2>',
                          line[:-(line_num_width + 1)], 1)
        else:
            return line

    def create(self, arguments_dict, cmd, project_root=None):
        self._project_root = project_root
        buffer_name = cmd.getBufferName()
        line_num_width = len(str(len(vim.current.buffer))) + 1

        date_format = arguments_dict.get("--date", ["iso"])[0]
        if date_format in ["iso", "iso-strict", "short"]:
            outputs = ParallelExecutor.run(cmd.getCommand(),
                                           format_line=partial(BlamePanel.formatLine,
                                                               arguments_dict,
                                                               line_num_width),
                                           directory=self._project_root)
        else:
            arguments_dict2 = arguments_dict.copy()
            arguments_dict2["-c"] = []
            cmd2 = GitBlameCommand(arguments_dict2, None)

            arguments_dict3 = arguments_dict2.copy()
            arguments_dict3["--date"] = ["unix"]
            cmd3 = GitBlameCommand(arguments_dict3, None)

            outputs = ParallelExecutor.run(cmd.getCommand(),
                                           cmd2.getCommand(),
                                           cmd3.getCommand(),
                                           format_line=[partial(BlamePanel.formatLine,
                                                                arguments_dict,
                                                                line_num_width),
                                                        None,
                                                        None],
                                           directory=self._project_root)

        line_num_width = max(line_num_width, int(lfEval('&numberwidth')))
        if len(outputs[0]) > 0:
            if buffer_name in self._views and self._views[buffer_name].valid():
                top_line = lfEval("line('w0')")
                cursor_line = lfEval("line('.')")
                line_width = outputs[0][0].rfind('\t')
                self._views[buffer_name].create(-1, buf_content=outputs[0])
                lfCmd("vertical resize {}".format(line_width + line_num_width))
                lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, cursor_line))
                if date_format != lfEval("b:lf_blame_date_format"):
                    lfCmd("let b:lf_blame_date_format = '{}'".format(date_format))
                    blame_view = self._views[buffer_name]
                    blame_view.clearHeatSyntax()
                    if date_format in ["iso", "iso-strict", "short"]:
                        blame_view.highlightHeatDate1(date_format, outputs[0])
                    else:
                        blame_view.highlightHeatDate2(outputs[1], outputs[2])
            else:
                winid = int(lfEval("win_getid()"))
                blame_view = GitBlameView(self, cmd)
                blame_view.saveAlternateWinOptions(winid, vim.current.buffer.number)
                lfCmd("setlocal nofoldenable")
                top_line = lfEval("line('w0')")
                cursor_line = lfEval("line('.')")
                line_width = outputs[0][0].rfind('\t')
                lfCmd("silent! noa keepa keepj abo {}vsp {}".format(line_width + line_num_width,
                                                                    buffer_name))
                blame_winid = int(lfEval("win_getid()"))
                blame_view.create(blame_winid, buf_content=outputs[0])
                if date_format in ["iso", "iso-strict", "short"]:
                    blame_view.highlightHeatDate1(date_format, outputs[0])
                else:
                    blame_view.highlightHeatDate2(outputs[1], outputs[2])
                self._owner.defineMaps(blame_winid)
                lfCmd("let b:lf_blame_project_root = '{}'".format(self._project_root))
                lfCmd("let b:lf_blame_date_format = '{}'".format(date_format))
                lfCmd("let b:lf_blame_file_name = '{}'".format(escQuote(arguments_dict["blamed_file_name"])))
                lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, cursor_line))
                lfCmd("call win_execute({}, 'setlocal scrollbind')".format(winid))
                lfCmd("setlocal scrollbind")
                lfCmd(r"""call win_execute({}, 'let &l:stl=" Press <F1> for help.%=".g:Lf_GitStlHeatLine')"""
                      .format(blame_winid))
        else:
            lfPrintError("No need to blame!")


class ExplorerPage(object):
    def __init__(self, project_root, commit_id, owner):
        self._project_root = project_root
        self._navigation_panel = NavigationPanel(self, project_root, commit_id, self.afterBufhidden)
        self._diff_view_panel = DiffViewPanel(self.afterBufhidden, commit_id)
        self._unified_diff_view_panel = UnifiedDiffViewPanel(self.afterBufhidden, commit_id)
        self.commit_id = commit_id
        self._owner = owner
        self._arguments = {}
        self.tabpage = None

    def openNavigationPanel(self):
        self._navigation_panel.open()

    def _createWindow(self, win_pos, buffer_name):
        if win_pos == 'top':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj abo {}sp {}".format(height, buffer_name))
        elif win_pos == 'bottom':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj bel {}sp {}".format(height, buffer_name))
        elif win_pos == 'left':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj abo {}vsp {}".format(width, buffer_name))
        elif win_pos == 'right':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj bel {}vsp {}".format(width, buffer_name))
        else: # left
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            lfCmd("silent! noa keepa keepj abo {}vsp {}".format(width, buffer_name))

        return int(lfEval("win_getid()"))

    def splitWindow(self, win_pos):
        if win_pos == 'top':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            height = int(lfEval("&lines")) - height - 4
            lfCmd("silent! noa keepa keepj bel {}sp".format(height))
        elif win_pos == 'bottom':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            height = int(lfEval("&lines")) - height - 4
            lfCmd("silent! noa keepa keepj abo {}sp".format(height))
        elif win_pos == 'left':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            width = int(lfEval("&columns")) - width - 1
            lfCmd("silent! noa keepa keepj bel {}vsp".format(width))
        elif win_pos == 'right':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            width = int(lfEval("&columns")) - width - 1
            lfCmd("silent! noa keepa keepj abo {}vsp".format(width))
        else: # left
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', 44)")))
            width = int(lfEval("&columns")) - width - 1
            lfCmd("silent! noa keepa keepj bel {}vsp".format(width))

        return int(lfEval("win_getid()"))

    def getDiffViewPanel(self):
        if self._navigation_panel.getDiffViewMode() == "side-by-side":
            return self._diff_view_panel
        else:
            return self._unified_diff_view_panel

    def create(self, arguments_dict, cmd, target_path=None, line_num=None):
        self._arguments = arguments_dict
        lfCmd("noautocmd tabnew")

        self.tabpage = vim.current.tabpage
        diff_view_winid = int(lfEval("win_getid()"))

        win_pos = arguments_dict.get("--navigation-position", ["left"])[0]
        winid = self._createWindow(win_pos, cmd.getBufferName())

        callback = partial(self.getDiffViewPanel().create,
                           arguments_dict,
                           winid=diff_view_winid,
                           line_num=line_num,
                           project_root=self._project_root,
                           explorer_page_id=id(self))
        self._navigation_panel.create(arguments_dict,
                                      cmd,
                                      winid,
                                      self._project_root,
                                      target_path,
                                      callback)

    def afterBufhidden(self):
        if (self._navigation_panel.isHidden() and self._diff_view_panel.isAllHidden()
            and self._unified_diff_view_panel.isAllHidden()):
            lfCmd("call timer_start(1, function('leaderf#Git#Cleanup', [{}]))".format(id(self)))

    def cleanup(self):
        self._navigation_panel.cleanup()
        self._diff_view_panel.cleanup()
        self._unified_diff_view_panel.cleanup()
        self._owner.cleanupExplorerPage(self)

    def getExistingSource(self):
        for w in vim.current.tabpage.windows:
            source = lfEval("getbufvar({}, 'lf_diff_view_source', 0)".format(w.buffer.number))
            if source != '0':
                return source

        return None

    def makeOnly(self):
        diff_view_mode = self._navigation_panel.getDiffViewMode()
        for w in vim.current.tabpage.windows:
            if (lfEval("getbufvar({}, 'lf_diff_view_mode', '{}')".format(w.buffer.number,
                                                                         diff_view_mode))
                != diff_view_mode):
                lfCmd("only")
                break

    def openDiffView(self, recursive, **kwargs):
        kwargs["project_root"] = self._project_root
        kwargs["explorer_page_id"] = id(self)
        kwargs["ignore_whitespace"] = self._navigation_panel.getIgnoreWhitespace()
        kwargs["diff_algorithm"] = self._navigation_panel.getDiffAlgorithm()
        if "diff_view_source" in kwargs:
            source = self.getExistingSource()
        else:
            source = self._navigation_panel.tree_view.expandOrCollapseFolder(recursive)

        if source is not None:
            self.makeOnly()

            if kwargs.get("mode", '') == 't':
                tabpage_count = len(vim.tabpages)
                self.getDiffViewPanel().create(self._arguments, source, **kwargs)
                if len(vim.tabpages) > tabpage_count:
                    tabmove()
            elif len(vim.current.tabpage.windows) == 1:
                win_pos = self._arguments.get("--navigation-position", ["left"])[0]
                diff_view_winid = self.splitWindow(win_pos)
                kwargs["winid"] = diff_view_winid
                self.getDiffViewPanel().create(self._arguments, source, **kwargs)
            else:
                self.getDiffViewPanel().create(self._arguments, source, **kwargs)

            if kwargs.get("preview", False) == True:
                lfCmd("call win_gotoid({})".format(self._navigation_panel.getWindowId()))

    def locateFile(self, path, line_num=None, preview=True):
        self._navigation_panel.locateFile(path, line_num, preview)


#*****************************************************
# GitExplManager
#*****************************************************
class GitExplManager(Manager):
    def __init__(self):
        super(GitExplManager, self).__init__()
        self._show_icon = lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == "1"
        self._result_panel = ResultPanel()
        self._preview_panel = PreviewPanel()
        self._git_diff_manager = None
        self._git_log_manager = None
        self._git_blame_manager = None
        self._selected_content = None
        self._project_root = None

    def _getExplClass(self):
        return GitExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Git#Maps({})".format(id(self)))
        if type(self) is GitExplManager:
            lfCmd("call leaderf#Git#SpecificMaps({})".format(id(self)))

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : execute command under cursor')
        help.append('" i/<Tab> : switch to input mode')
        if type(self) is GitExplManager:
            help.append('" e : edit command under cursor')
        help.append('" p : preview the help information')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" <ESC> : close the preview window or quit')
        help.append('" ---------------------------------------------------------')
        return help

    def _workInIdle(self, content=None, bang=False):
        self._result_panel.writeBuffer()
        self._preview_panel.writeBuffer()

        super(GitExplManager, self)._workInIdle(content, bang)

    def _beforeExit(self):
        super(GitExplManager, self)._beforeExit()
        self._preview_panel.cleanup()

    def getExplManager(self, subcommand):
        if subcommand == "diff":
            if self._git_diff_manager is None:
                self._git_diff_manager = GitDiffExplManager()
            return self._git_diff_manager
        elif subcommand == "log":
            if self._git_log_manager is None:
                self._git_log_manager = GitLogExplManager()
            return self._git_log_manager
        elif subcommand == "blame":
            if self._git_blame_manager is None:
                self._git_blame_manager = GitBlameExplManager()
            return self._git_blame_manager
        else:
            return super(GitExplManager, self)

    def getWorkingDirectory(self, orig_cwd):
        wd_mode = lfEval("get(g:, 'Lf_GitWorkingDirectoryMode', 'f')")
        if wd_mode == 'f':
            cur_buf_name = lfDecode(vim.current.buffer.name)
            if cur_buf_name:
                return nearestAncestor([".git"], os.path.dirname(cur_buf_name))

        return nearestAncestor([".git"], orig_cwd)

    def checkWorkingDirectory(self):
        self._orig_cwd = lfGetCwd()
        self._project_root = self.getWorkingDirectory(self._orig_cwd)

        if self._project_root: # there exists a root marker in nearest ancestor path
            lfChdir(self._project_root)
        else:
            lfPrintError("Not a git repository (or any of the parent directories): .git")
            return False

        return True

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" in arguments_dict:
            self._arguments.update(arguments_dict)
        else:
            self.setArguments(arguments_dict)

        arg_list = self._arguments.get("arg_line", 'git').split()
        arg_list = [item for item in arg_list if not item.startswith('-')]
        if len(arg_list) == 1:
            subcommand = ""
        else:
            subcommand = arg_list[1]
        self.getExplManager(subcommand).startExplorer(win_pos, *args, **kwargs)

    def accept(self, mode=''):
        source = self.getSource(self._getInstance().currentLine)
        self._selected_content = self._preview_panel.getContent(source)

        return super(GitExplManager, self).accept(mode)

    def _accept(self, file, mode, *args, **kwargs):
        self._acceptSelection(file, *args, **kwargs)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        cmd = line
        try:
            lfCmd(cmd)
        except vim.error:
            lfPrintTraceback()

    def _bangEnter(self):
        super(GitExplManager, self)._bangEnter()

        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return

        self._callback(bang=True)
        if self._read_finished < 2:
            self._timer_id = lfEval("timer_start(10, function('leaderf#Git#TimerCallback', [%d]), {'repeat': -1})" % id(self))

    def getSource(self, line):
        commands = lfEval("leaderf#Git#Commands()")
        for cmd in commands:
            if line in cmd:
                return cmd[line]

        return None

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        line = args[0]
        source = self.getSource(line)

        self._createPopupPreview("", source, 0)

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        if lfEval("has('nvim')") == '1':
            lfCmd("noautocmd let scratch_buffer = nvim_create_buf(0, 1)")
            lfCmd("noautocmd call setbufline(scratch_buffer, 1, '{}')".format(escQuote(source)))
            lfCmd("noautocmd call nvim_buf_set_option(scratch_buffer, 'bufhidden', 'wipe')")
            lfCmd("noautocmd call nvim_buf_set_option(scratch_buffer, 'undolevels', -1)")

            self._preview_winid = int(lfEval("nvim_open_win(scratch_buffer, 0, {})"
                                             .format(json.dumps(config))))
        else:
            lfCmd("noautocmd let winid = popup_create('{}', {})"
                  .format(escQuote(source), json.dumps(config)))
            self._preview_winid = int(lfEval("winid"))

        self._setWinOptions(self._preview_winid)

    def createGitCommand(self, arguments_dict, source):
        pass

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        self.setOptionsForCursor()

        if lfEval("has('nvim')") == '1':
            lfCmd("""call win_execute({}, "call nvim_buf_set_lines(0, 0, -1, v:false, ['{}'])")"""
                  .format(self._preview_winid, escQuote(source)))
        else:
            lfCmd("noautocmd call popup_settext({}, '{}')"
                  .format(self._preview_winid, escQuote(source)))

    def _cmdExtension(self, cmd):
        if type(self) is GitExplManager:
            if equal(cmd, '<C-o>'):
                self.editCommand()
            return True

    def editCommand(self):
        instance = self._getInstance()
        line = instance.currentLine
        instance.exitBuffer()
        lfCmd("call feedkeys(':%s', 'n')" % escQuote(line))


class GitDiffExplManager(GitExplManager):
    def __init__(self):
        super(GitDiffExplManager, self).__init__()
        self._diff_view_panel = DiffViewPanel(self.afterBufhidden)
        self._pages = set()

    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = GitDiffExplorer()
        return self._explorer

    def _getDigest(self, line, mode):
        if mode == 0:
            return line[5:]
        elif mode == 1:
            return getBasename(line)
        else:
            return getDirname(line[5:])

    def _getDigestStartPos(self, line, mode):
        if mode == 0 or mode == 2:
            return 5
        else:
            return lfBytesLen(getDirname(line))

    def afterBufhidden(self):
        if self._diff_view_panel.isAllHidden():
            lfCmd("call timer_start(1, function('leaderf#Git#Cleanup', [{}]))".format(id(self)))

    def getSource(self, line):
        """
        return a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        if line == '':
            return None

        file_name2 = ""
        if "\t=>\t" in line:
            # 'R050 hello world.txt\t=>\thello world2.txt'
            # 'R050   hello world.txt\t=>\thello world2.txt'
            tmp = line.split("\t=>\t")
            file_name1 = tmp[0].split(None, 2 if self._show_icon else 1)[-1]
            file_name2 = tmp[1]
        else:
            # 'M      runtime/syntax/nix.vim'
            file_name1 = line.split()[-1]

        return self._getExplorer().getSourceInfo().get((file_name1, file_name2),
                                                       ("", "", "", file_name1, file_name2))

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        self._preview_panel.create(self.createGitCommand(self._arguments, source),
                                   config,
                                   project_root=self._project_root)
        self._preview_winid = self._preview_panel.getPreviewWinId()
        self._setWinOptions(self._preview_winid)

    def getPreviewCommand(self, arguments_dict, source):
        arguments_dict.update(self._arguments)
        return GitDiffCommand(arguments_dict, source)

    def createGitCommand(self, arguments_dict, source):
        if "owner" in arguments_dict:
            return arguments_dict["owner"].getPreviewCommand(arguments_dict, source)
        else:
            return GitDiffCommand(arguments_dict, source)

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        self.setOptionsForCursor()

        content = self._preview_panel.getContent(source)
        if content is None:
            self._preview_panel.createView(self.createGitCommand(self._arguments, source))
        else:
            self._preview_panel.setContent(content)

    def vsplitDiff(self):
        if "--cached" not in self._arguments:
            if "extra" in self._arguments:
                cmd = "git diff {} --raw -- {}".format(" ".join(self._arguments["extra"]),
                                                 self._arguments["current_file"])

                outputs = ParallelExecutor.run(cmd, directory=self._project_root)
                if len(outputs[0]) == 0:
                    lfPrintError("No diffs!")
                    return

                blob = outputs[0][0].split()[2]
                cmd = "git cat-file -p {}".format(blob)
                file_name = "LeaderF://{}:{}".format(blob, self._arguments["current_file"])
            else:
                cmd = "git show :{}".format(self._arguments["current_file"])
                file_name = "LeaderF://:{}".format(self._arguments["current_file"])

            win_ids = [int(lfEval("win_getid()")), 0]
            lfCmd("keepa keepj abo vsp {}".format(file_name))
            win_ids[1] = int(lfEval("win_getid()"))
            lfCmd("augroup Lf_Git_Diff | augroup END")
            lfCmd("autocmd! Lf_Git_Diff BufWipeout <buffer> call leaderf#Git#DiffOff({})"
                  .format(win_ids))
            lfCmd("call win_execute({}, 'autocmd! Lf_Git_Diff BufHidden,BufWipeout <buffer> call leaderf#Git#DiffOff({})')"
                  .format(win_ids[0], win_ids))
            lfCmd("setlocal nobuflisted")
            lfCmd("setlocal buftype=nofile")
            lfCmd("setlocal bufhidden=wipe")
            lfCmd("setlocal undolevels=-1")
            lfCmd("setlocal noswapfile")
            lfCmd("setlocal nospell")

            outputs = ParallelExecutor.run(cmd, directory=self._project_root)
            vim.current.buffer[:] = outputs[0]
            lfCmd("setlocal nomodifiable")

            for winid in win_ids:
                lfCmd("call win_execute({}, 'diffthis')".format(winid))
        else:
            if "extra" in self._arguments:
                extra = " ".join(self._arguments["extra"])
            else:
                extra = ""

            cmd = "git diff {} --cached --raw -- {}".format(extra,
                                                            self._arguments["current_file"])
            outputs = ParallelExecutor.run(cmd, directory=self._project_root)
            if len(outputs[0]) > 0:
                _, source = TreeView.generateSource(outputs[0][0])
                self._diff_view_panel.create(self._arguments, source, **{"mode": 't'})
            else:
                lfPrintError("No diffs!")

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" not in arguments_dict and self.checkWorkingDirectory() == False:
            return

        if "--recall" not in arguments_dict:
            self.setArguments(arguments_dict)
            if ("--current-file" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']
               ):
                file_name = vim.current.buffer.name
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                self._arguments["current_file"] = PurePath(lfRelpath(file_name)).as_posix()
                if "-s" in self._arguments:
                    self.vsplitDiff()
                else:
                    self._accept(self._arguments["current_file"], "")

                self._restoreOrigCwd()
                return

        if "--recall" in arguments_dict:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)
        elif "--directly" in self._arguments:
            self._result_panel.create(self.createGitCommand(self._arguments, None))
            self._restoreOrigCwd()
        elif "--explorer" in self._arguments:
            uid = str(int(time.time()))[-7:]
            page = ExplorerPage(self._project_root, uid, self)
            page.create(arguments_dict, GitDiffExplCommand(arguments_dict, uid))
            self._pages.add(page)
        else:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def _afterEnter(self):
        super(GitExplManager, self)._afterEnter()

        if lfEval("get(g:, 'Lf_ShowDevIcons', 1)") == '1':
            winid = self._getInstance().getPopupWinId() if self._getInstance().getWinPos() == 'popup' else None
            icon_pattern = r'^\S*\s*\zs__icon__'
            self._match_ids.extend(matchaddDevIconsExtension(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsExact(icon_pattern, winid))
            self._match_ids.extend(matchaddDevIconsDefault(icon_pattern, winid))

        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitDiffModification'', ''^[MRT]\S*'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitDiffAddition'', ''^[AC]\S*'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitDiffDeletion'', ''^[DU]'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_gitDiffModification', '^[MRT]\S*')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitDiffAddition', '^[AC]\S*')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitDiffDeletion', '^[DU]')'''))
            self._match_ids.append(id)

    def _accept(self, file, mode, *args, **kwargs):
        if "-s" in self._arguments:
            kwargs["mode"] = mode
            self._acceptSelection(file, *args, **kwargs)
        else:
            super(GitExplManager, self)._accept(file, mode, *args, **kwargs)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        source = self.getSource(line)

        if "accept" in self._arguments:
            self._arguments["accept"](lfGetFilePath(source))
        elif "-s" in self._arguments:
            kwargs["project_root"] = self._project_root
            self._diff_view_panel.create(self._arguments, source, **kwargs)
        else:
            if kwargs.get("mode", '') == 't' and source not in self._result_panel.getSources():
                self._arguments["mode"] = 't'
                lfCmd("tabnew")
            else:
                self._arguments["mode"] = ''

            tabpage_count = len(vim.tabpages)

            self._result_panel.create(self.createGitCommand(self._arguments, source),
                                      self._selected_content)

            if kwargs.get("mode", '') == 't' and len(vim.tabpages) > tabpage_count:
                tabmove()

    def cleanup(self):
        self._diff_view_panel.cleanup()

    def cleanupExplorerPage(self, page):
        self._pages.discard(page)


class GitLogExplManager(GitExplManager):
    def __init__(self):
        super(GitLogExplManager, self).__init__()
        lfCmd("augroup Lf_Git_Log | augroup END")
        lfCmd("autocmd! Lf_Git_Log FileType git call leaderf#Git#DefineSyntax()")
        self._diff_view_panel = None
        # key is commit id, value is ExplorerPage
        self._pages = {}

    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = GitLogExplorer()
        return self._explorer

    def _getDigest(self, line, mode):
        return line.lstrip(r"*\|_/ ")

    def _getDigestStartPos(self, line, mode):
        return len(line) - len(line.lstrip(r"*\|_/ "))

    def afterBufhidden(self):
        if self._diff_view_panel.isAllHidden():
            lfCmd("call timer_start(1, function('leaderf#Git#Cleanup', [{}]))".format(id(self)))

    def getSource(self, line):
        """
        return the hash
        """
        line = line.lstrip(r"*\|_/ ")
        if line == '':
            return None

        return line.split(None, 1)[0]

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        if source is None:
            return

        if "--current-line" in self._arguments and len(self._getExplorer().patches) > 0:
            self._preview_panel.create(self.createGitCommand(self._arguments, source),
                                       config,
                                       buf_content=self._getExplorer().patches[source],
                                       project_root=self._project_root)
        else:
            self._preview_panel.create(self.createGitCommand(self._arguments, source),
                                       config,
                                       project_root=self._project_root)
        self._preview_winid = self._preview_panel.getPreviewWinId()
        self._setWinOptions(self._preview_winid)

    def getPreviewCommand(self, arguments_dict, source):
        return GitLogDiffCommand(arguments_dict, source)

    def createGitCommand(self, arguments_dict, commit_id):
        return GitLogCommand(arguments_dict, commit_id)

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        if source is None:
            return

        self.setOptionsForCursor()

        content = self._preview_panel.getContent(source)
        if content is None:
            if "--current-line" in self._arguments and len(self._getExplorer().patches) > 0:
                self._preview_panel.setContent(self._getExplorer().patches[source])
            else:
                self._preview_panel.createView(self.createGitCommand(self._arguments, source))
        else:
            self._preview_panel.setContent(content)

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" not in arguments_dict and self.checkWorkingDirectory() == False:
            return

        if "--recall" not in arguments_dict:
            self.setArguments(arguments_dict)
            if ("--current-file" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']
               ):
                file_name = vim.current.buffer.name
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                self._arguments["current_file"] = PurePath(lfRelpath(file_name)).as_posix()
                self._arguments["orig_name"] = self._getExplorer().orig_name
            elif ("--current-line" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']
               ):
                file_name = vim.current.buffer.name
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                self._arguments["current_file"] = PurePath(lfRelpath(file_name)).as_posix()
                self._arguments["current_line_num"] = vim.current.window.cursor[0]

        if "--recall" in arguments_dict:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)
        elif "--directly" in self._arguments:
            self._result_panel.create(self.createGitCommand(self._arguments, None))
            self._restoreOrigCwd()
        else:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def _afterEnter(self):
        super(GitExplManager, self)._afterEnter()

        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph1'', ''^|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph2'', ''^[*\|_/ ]\{2}\zs|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph3'', ''^[*\|_/ ]\{4}\zs|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph4'', ''\(^[*\|_/ ]\{6,}\)\@<=|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraphSlash'', ''\(^[*\|_/ ]\{-}\)\@<=[\/]'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitHash'', ''\(^[*\|_/ ]*\)\@<=[0-9A-Fa-f]\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitRefNames'', ''^[*\|_/ ]*[0-9A-Fa-f]\+\s*\zs(.\{-})'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph1', '^|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph2', '^[*\|_/ ]\{2}\zs|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph3', '^[*\|_/ ]\{4}\zs|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph4', '\(^[*\|_/ ]\{6,}\)\@<=|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraphSlash', '\(^[*\|_/ ]\{-}\)\@<=[\/]')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitHash', '\(^[*\|_/ ]*\)\@<=[0-9A-Fa-f]\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitRefNames', '^[*\|_/ ]*[0-9A-Fa-f]\+\s*\zs(.\{-})')'''))
            self._match_ids.append(id)

    def _accept(self, file, mode, *args, **kwargs):
        super(GitExplManager, self)._accept(file, mode, *args, **kwargs)

    def _createExplorerPage(self, commit_id, target_path=None, line_num=None):
        if commit_id in self._pages:
            vim.current.tabpage = self._pages[commit_id].tabpage
        else:
            self._pages[commit_id] = ExplorerPage(self._project_root, commit_id, self)
            self._pages[commit_id].create(self._arguments,
                                          GitLogExplCommand(self._arguments, commit_id),
                                          target_path=target_path,
                                          line_num=line_num)

    def _getPathAndLineNum(self, commit_id):
        patch = self._getExplorer().patches[commit_id]
        file_path = patch[0].rsplit(None, 1)[1][2:]
        line_num = 1
        count = 0
        found = False
        for line in patch:
            if line.startswith("@@"):
                found = True
                line_numbers = line.split("+", 1)[1].split(None, 1)[0]
                if "," in line_numbers:
                    line_num, _ = line_numbers.split(",")
                    line_num = int(line_num)
                else:
                    # @@ -1886 +1893 @@
                    line_num = int(line_numbers)
            elif found:
                if line.startswith("-"):
                    pass
                elif line.startswith("+"):
                    line_num += count
                    break
                else:
                    count += 1

        return (file_path, line_num)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        commit_id = self.getSource(line)
        if commit_id is None:
            return

        if "--current-file" in self._arguments and "current_file" in self._arguments:
            file_name = self._getExplorer().orig_name[commit_id]
            if "--explorer" in self._arguments:
                self._createExplorerPage(commit_id, file_name)
            else:
                if self._diff_view_panel is None:
                    self._diff_view_panel = DiffViewPanel(self.afterBufhidden)

                self._diff_view_panel.setCommitId(commit_id)
                cmd = "git log -1 --follow --pretty= --no-color --raw {} -- {}".format(commit_id,
                                                                                       file_name)
                outputs = ParallelExecutor.run(cmd, directory=self._project_root)
                if len(outputs[0]) > 0:
                    _, source = TreeView.generateSource(outputs[0][0])
                    self._diff_view_panel.create(self._arguments, source, **kwargs)
        elif "--current-line" in self._arguments and len(self._getExplorer().patches) > 0:
            if "--explorer" in self._arguments:
                file_path, line_num = self._getPathAndLineNum(commit_id)
                self._createExplorerPage(commit_id, file_path, line_num)
            else:
                if kwargs.get("mode", '') == 't' and commit_id not in self._result_panel.getSources():
                    self._arguments["mode"] = 't'
                    lfCmd("tabnew")

                tabpage_count = len(vim.tabpages)

                self._result_panel.create(self.createGitCommand(self._arguments, commit_id),
                                          self._getExplorer().patches[commit_id])

                if kwargs.get("mode", '') == 't' and len(vim.tabpages) > tabpage_count:
                    tabmove()
        elif "--explorer" in self._arguments:
            self._createExplorerPage(commit_id)
        else:
            if kwargs.get("mode", '') == 't' and commit_id not in self._result_panel.getSources():
                self._arguments["mode"] = 't'
                lfCmd("tabnew")

            tabpage_count = len(vim.tabpages)

            self._result_panel.create(self.createGitCommand(self._arguments, commit_id),
                                      self._selected_content)

            if kwargs.get("mode", '') == 't' and len(vim.tabpages) > tabpage_count:
                tabmove()

    def cleanup(self):
        if self._diff_view_panel is not None:
            self._diff_view_panel.cleanup()

    def cleanupExplorerPage(self, page):
        del self._pages[page.commit_id]


class GitBlameExplManager(GitExplManager):
    def __init__(self):
        super(GitBlameExplManager, self).__init__()
        self._blame_panels = {}
        # key is commit_id, value is ExplorerPage
        self._pages = {}
        # key is buffer number
        self._blame_infos = {}
        # key is buffer number
        self._initial_changedtick = {}
        lfCmd("let g:lf_blame_manager_id = {}".format(id(self)))
        if lfEval("hlexists('Lf_hl_gitInlineBlame')") == '0':
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')"
                  .format("git", lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))

    def discardPanel(self, project_root):
        del self._blame_panels[project_root]

    def createGitCommand(self, arguments_dict, commit_id):
        return GitBlameCommand(arguments_dict, commit_id)

    def getPreviewCommand(self, arguments_dict, source):
        return GitLogDiffCommand(arguments_dict, source)

    def defineMaps(self, winid):
        lfCmd("call win_execute({}, 'call leaderf#Git#BlameMaps({})')"
              .format(winid, id(self)))

    def setOptions(self, winid):
        lfCmd("call win_execute({}, 'setlocal nobuflisted')".format(winid))
        lfCmd("call win_execute({}, 'setlocal buftype=nofile')".format(winid))
        lfCmd("call win_execute({}, 'setlocal bufhidden=hide')".format(winid))
        lfCmd("call win_execute({}, 'setlocal undolevels=-1')".format(winid))
        lfCmd("call win_execute({}, 'setlocal noswapfile')".format(winid))
        lfCmd("call win_execute({}, 'setlocal nospell')".format(winid))

    def getLineNumber(self, commit_id, file_name, line_num, text, project_root):
        cmd = 'git log -1 -p --pretty= -U0 --follow {} -- {}'.format(commit_id, file_name)
        outputs = ParallelExecutor.run(cmd, directory=project_root)
        found = False
        for i, line in enumerate(outputs[0]):
            # @@ -2,11 +2,21 @@
            if line.startswith("@@"):
                line_numbers = line.split("+", 1)[1].split(None, 1)[0]
                if "," in line_numbers:
                    start, count = line_numbers.split(",")
                    start = int(start)
                    count = int(count)
                else:
                    # @@ -1886 +1893 @@
                    start = int(line_numbers)
                    count = 1

                if start + count > line_num:
                    found = True
                    orig_line_numbers = line.split(None, 2)[1].lstrip("-")
                    if "," in orig_line_numbers:
                        orig_start, orig_count = orig_line_numbers.split(",")
                        orig_start = int(orig_start)
                        orig_count = int(orig_count)
                    else:
                        orig_start = int(orig_line_numbers)
                        orig_count = 1

                    if orig_count == 1 or orig_count == 0:
                        return orig_start
                    elif orig_count == count:
                        return orig_start + line_num - start
                    else:
                        ratio = 0
                        index = i + 1
                        for j, line in enumerate(outputs[0][index: index + orig_count], index):
                            r = SequenceMatcher(None, text, line).ratio()
                            if r > ratio:
                                ratio = r
                                index = j

                        return orig_start + index - i - 1

        return line_num

    def blamePrevious(self):
        if vim.current.line == "":
            return

        if vim.current.line.startswith('^'):
            lfPrintError("First commit!")
            return

        commit_id = vim.current.line.lstrip('^').split(None, 1)[0]
        if commit_id.startswith('0000000'):
            lfPrintError("Not Committed Yet!")
            return

        line_num, file_name = vim.current.line.rsplit('\t', 1)[1].split(None, 1)
        line_num = int(line_num)
        project_root = lfEval("b:lf_blame_project_root")
        blame_panel = self._blame_panels[project_root]
        blame_buffer_name = vim.current.buffer.name
        alternate_winid = blame_panel.getAlternateWinid(blame_buffer_name)
        blame_winid = lfEval("win_getid()")

        alternate_buffer_num = int(lfEval("winbufnr({})".format(alternate_winid)))
        text = vim.buffers[alternate_buffer_num][vim.current.window.cursor[0] - 1]
        line_num = self.getLineNumber(commit_id, file_name, line_num, text, project_root)
        top_line_delta = vim.current.window.cursor[0] - int(lfEval("line('w0')"))

        if commit_id not in blame_panel.getBlameDict(blame_buffer_name):
            cmd = 'git log -2 --pretty="%H" --name-status --follow {} -- {}'.format(commit_id,
                                                                                    file_name)
            # output is as below:

            # a7cdd68e0f9e891e6f5def7b2b657d07d92a3675
            #
            # R064    tui.py  src/tui.py
            # 5a0cd5103deba164a6fb33a5a3f67fb3a5dcf378
            #
            # M       tui.py
            outputs = ParallelExecutor.run(cmd, directory=project_root)
            name_stat = outputs[0][2]
            if name_stat.startswith("A") or name_stat.startswith("C"):
                lfPrintError("First commit of current file!")
                return
            else:
                if name_stat.startswith("R"):
                    orig_name = name_stat.split()[1]
                else:
                    orig_name = file_name

            parent_commit_id = outputs[0][3]

            blame_win_width = vim.current.window.width
            blame_panel.getBlameStack(blame_buffer_name).append(
                    (
                        vim.current.buffer[:],
                        lfEval("winbufnr({})".format(alternate_winid)),
                        blame_win_width,
                        vim.current.window.cursor[0],
                        int(lfEval("line('w0')"))
                    )
                )

            alternate_buffer_name = "LeaderF://{}:{}".format(parent_commit_id[:7], orig_name)
            blame_buffer_dict = blame_panel.getBlameBufferDict(blame_buffer_name)

            lfCmd("noautocmd call win_gotoid({})".format(alternate_winid))
            if alternate_buffer_name in blame_buffer_dict:
                blame_buffer, alternate_buffer_num = blame_buffer_dict[alternate_buffer_name]
                lfCmd("buffer {}".format(alternate_buffer_num))
                lfCmd("noautocmd norm! {}Gzt{}G0".format(line_num-top_line_delta, line_num))
                top_line = lfEval("line('w0')")

                lfCmd("noautocmd call win_gotoid({})".format(blame_winid))
            else:
                date_format = self._arguments.get("--date", ["iso"])[0]
                if date_format in ["iso", "iso-strict", "short"]:
                    cmd = [GitBlameCommand.buildCommand(self._arguments, parent_commit_id, orig_name),
                           "git show {}:{}".format(parent_commit_id, orig_name),
                           ]
                else:
                    arguments_dict2 = self._arguments.copy()
                    arguments_dict2["-c"] = []

                    arguments_dict3 = arguments_dict2.copy()
                    arguments_dict3["--date"] = ["unix"]

                    cmd = [GitBlameCommand.buildCommand(self._arguments, parent_commit_id, orig_name),
                           "git show {}:{}".format(parent_commit_id, orig_name),
                           GitBlameCommand.buildCommand(arguments_dict2, parent_commit_id, orig_name),
                           GitBlameCommand.buildCommand(arguments_dict3, parent_commit_id, orig_name),
                           ]

                outputs = ParallelExecutor.run(*cmd, directory=project_root)
                line_num_width = len(str(len(outputs[1]))) + 1
                blame_buffer = [BlamePanel.formatLine(self._arguments, line_num_width, line)
                                for line in outputs[0]
                                ]

                lfCmd("noautocmd enew")
                self.setOptions(alternate_winid)

                vim.current.buffer[:] = outputs[1]
                vim.current.buffer.name = alternate_buffer_name
                lfCmd("doautocmd filetypedetect BufNewFile {}".format(orig_name))
                lfCmd("setlocal nomodifiable")
                alternate_buffer_num = vim.current.buffer.number

                lfCmd("noautocmd norm! {}Gzt{}G0".format(line_num-top_line_delta, line_num))
                top_line = lfEval("line('w0')")

                lfCmd("noautocmd call win_gotoid({})".format(blame_winid))
                blame_view = blame_panel.getBlameView(blame_buffer_name)
                if date_format in ["iso", "iso-strict", "short"]:
                    blame_view.highlightRestHeatDate1(date_format, outputs[0])
                else:
                    blame_view.highlightRestHeatDate2(outputs[2], outputs[3])

            # here we are in the blame window
            lfCmd("setlocal modifiable")
            vim.current.buffer[:] = blame_buffer
            lfCmd("setlocal nomodifiable")
            if len(blame_buffer) > 0:
                line_width = blame_buffer[0].rfind('\t')
                line_num_width = max(len(str(len(vim.current.buffer))) + 1,
                                     int(lfEval('&numberwidth')))
                lfCmd("vertical resize {}".format(line_width + line_num_width))
                lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, line_num))
                lfCmd("call win_execute({}, 'setlocal scrollbind')".format(alternate_winid))

            blame_win_width = vim.current.window.width
            blame_panel.getBlameDict(blame_buffer_name)[commit_id] = (
                    blame_buffer,
                    alternate_buffer_num,
                    blame_win_width
                    )
            blame_buffer_dict[alternate_buffer_name] = (blame_buffer, alternate_buffer_num)
        else:
            blame_panel.getBlameStack(blame_buffer_name).append(
                    (
                        vim.current.buffer[:],
                        lfEval("winbufnr({})".format(alternate_winid)),
                        vim.current.window.width,
                        vim.current.window.cursor[0],
                        int(lfEval("line('w0')"))
                    )
                )
            (blame_buffer,
             alternate_buffer_num,
             blame_win_width
             ) = blame_panel.getBlameDict(blame_buffer_name)[commit_id]
            lfCmd("noautocmd call win_gotoid({})".format(alternate_winid))
            lfCmd("buffer {}".format(alternate_buffer_num))
            lfCmd("noautocmd norm! {}Gzt{}G0".format(line_num-top_line_delta, line_num))
            top_line = lfEval("line('w0')")

            lfCmd("noautocmd call win_gotoid({})".format(blame_winid))
            lfCmd("setlocal modifiable")
            vim.current.buffer[:] = blame_buffer
            lfCmd("setlocal nomodifiable")
            lfCmd("vertical resize {}".format(blame_win_width))
            lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, line_num))

        if lfEval("exists('b:lf_preview_winid') && winbufnr(b:lf_preview_winid) != -1") == '1':
            if lfEval("has('nvim')") == '1':
                lfCmd("call nvim_win_close(b:lf_preview_winid, 1)")
            else:
                lfCmd("call popup_close(b:lf_preview_winid)")
            self.preview()

    def blameNext(self):
        project_root = lfEval("b:lf_blame_project_root")
        blame_panel = self._blame_panels[project_root]
        blame_stack = blame_panel.getBlameStack(vim.current.buffer.name)
        if len(blame_stack) == 0:
            return

        blame_buffer, alternate_buffer_num, blame_win_width, cursor_line, top_line = blame_stack.pop()
        blame_winid = lfEval("win_getid()")
        alternate_winid = blame_panel.getAlternateWinid(vim.current.buffer.name)

        lfCmd("noautocmd call win_gotoid({})".format(alternate_winid))
        lfCmd("buffer {}".format(alternate_buffer_num))
        lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, cursor_line))

        lfCmd("noautocmd call win_gotoid({})".format(blame_winid))
        lfCmd("setlocal modifiable")
        vim.current.buffer[:] = blame_buffer
        lfCmd("setlocal nomodifiable")
        lfCmd("vertical resize {}".format(blame_win_width))
        lfCmd("noautocmd norm! {}Gzt{}G0".format(top_line, cursor_line))

        if lfEval("exists('b:lf_preview_winid') && winbufnr(b:lf_preview_winid) != -1") == '1':
            if lfEval("has('nvim')") == '1':
                lfCmd("call nvim_win_close(b:lf_preview_winid, 1)")
            else:
                lfCmd("call popup_close(b:lf_preview_winid)")
            self.preview()

    def showCommitMessage(self):
        if vim.current.line == "":
            return

        commit_id = vim.current.line.lstrip('^').split(None, 1)[0]
        if commit_id.startswith('0000000'):
            lfPrintError("Not Committed Yet!")
            return

        project_root = lfEval("b:lf_blame_project_root")
        cmd = "cd {} && git show {} -s --decorate --pretty=fuller".format(project_root, commit_id)
        lfCmd("""call leaderf#Git#ShowCommitMessage(systemlist('{}'))""".format(cmd))

    def open(self):
        if vim.current.line == "":
            return

        commit_id = vim.current.line.lstrip('^').split(None, 1)[0]
        if commit_id.startswith('0000000'):
            lfPrintError("Not Committed Yet!")
            return

        line_num, file_name = vim.current.line.rsplit('\t', 1)[1].split(None, 1)

        if commit_id in self._pages:
            vim.current.tabpage = self._pages[commit_id].tabpage
            self._pages[commit_id].locateFile(file_name, line_num, False)
        else:
            project_root = lfEval("b:lf_blame_project_root")
            self._pages[commit_id] = ExplorerPage(project_root, commit_id, self)
            self._pages[commit_id].create(self._arguments,
                                          GitLogExplCommand(self._arguments, commit_id),
                                          target_path=file_name,
                                          line_num=line_num)

    def generateConfig(self, project_root):
        maxheight = int(lfEval("get(g:, 'Lf_GitBlamePreviewHeight', {})"
                               .format(vim.current.window.height // 3)))
        if maxheight < 5:
            maxheight = 5

        blame_panel = self._blame_panels[project_root]
        alternate_winid = blame_panel.getAlternateWinid(vim.current.buffer.name)
        screenpos = lfEval("screenpos({}, {}, {})".format(alternate_winid,
                                                          vim.current.window.cursor[0],
                                                          1))
        col = int(screenpos["col"])
        maxwidth = int(lfEval("&columns")) - col

        if lfEval("has('nvim')") == '1':
            row = int(screenpos["row"])

            popup_borders = lfEval("g:Lf_PopupBorders")
            borderchars = [
                    [popup_borders[4],  "Lf_hl_popupBorder"],
                    [popup_borders[0],  "Lf_hl_popupBorder"],
                    [popup_borders[5],  "Lf_hl_popupBorder"],
                    [popup_borders[1],  "Lf_hl_popupBorder"],
                    [popup_borders[6],  "Lf_hl_popupBorder"],
                    [popup_borders[2],  "Lf_hl_popupBorder"],
                    [popup_borders[7],  "Lf_hl_popupBorder"],
                    [popup_borders[3],  "Lf_hl_popupBorder"]
                    ]

            if row > maxheight + 2:
                anchor = "SW"
                row -= 1
            else:
                anchor = "NW"

            config = {
                    "title":           " Preview ",
                    "title_pos":       "center",
                    "relative":        "editor",
                    "anchor":           anchor,
                    "row":             row,
                    "col":             col - 1,
                    "width":           maxwidth,
                    "height":          maxheight,
                    "zindex":          20482,
                    "noautocmd":       1,
                    "border":          borderchars,
                    "style":           "minimal",
                    }
        else:
            config = {
                "title":           " Preview ",
                "maxwidth":        maxwidth,
                "minwidth":        maxwidth,
                "maxheight":       maxheight,
                "minheight":       maxheight,
                "zindex":          20482,
                "pos":             "botleft",
                "line":            "cursor-1",
                "col":             col,
                "scrollbar":       0,
                "padding":         [0, 0, 0, 0],
                "border":          [1, 1, 1, 1],
                "borderchars":     lfEval("g:Lf_PopupBorders"),
                "borderhighlight": ["Lf_hl_popupBorder"],
                "filter":          "leaderf#Git#PreviewFilter",
                "mapping":         0,
                }

        return config

    def preview(self):
        if vim.current.line == "":
            return

        commit_id = vim.current.line.lstrip('^').split(None, 1)[0]

        line_num, file_name = vim.current.line.rsplit('\t', 1)[1].split(None, 1)
        line_num = int(line_num)

        if lfEval("has('nvim')") == '1':
            lfCmd("let b:lf_blame_preview_cursorline = line('.')")
            lfCmd("let b:lf_blame_winid = win_getid()")
            if lfEval("exists('b:lf_preview_winid') && winbufnr(b:lf_preview_winid) != -1") == '1':
                lfCmd("call nvim_win_close(b:lf_preview_winid, 1)")

        project_root = lfEval("b:lf_blame_project_root")
        if commit_id.startswith('0000000'):
            cmd = GitCustomizeCommand(self._arguments, "git diff @ -- {}".format(file_name),
                                      None, "git", "setlocal filetype=git")
        else:
            cmd = GitShowCommand(self._arguments, commit_id, file_name)
        outputs = ParallelExecutor.run(cmd.getCommand(), directory=project_root)
        self._preview_panel.create(cmd, self.generateConfig(project_root), outputs[0])
        preview_winid = self._preview_panel.getPreviewWinId()
        self._setWinOptions(preview_winid)
        lfCmd("let b:lf_preview_winid = {}".format(preview_winid))
        if lfEval("has('nvim')") == '1':
            lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % preview_winid)
        else:
            lfCmd("call win_execute({}, 'setlocal nonumber')".format(preview_winid))
            lfCmd("call win_execute({}, 'let b:lf_blame_manager_id = {}')".format(preview_winid,
                                                                                  id(self)))

        self.gotoLine(preview_winid, line_num)
        lfCmd("call win_execute({}, 'setlocal filetype=diff')".format(preview_winid))

    def quit(self):
        if lfEval("has('nvim')") == '1':
            if lfEval("exists('b:lf_preview_winid') && winbufnr(b:lf_preview_winid) != -1") == '1':
                lfCmd("call nvim_win_close(b:lf_preview_winid, 1)")

        lfCmd("bwipe")

    def gotoLine(self, winid, line_num):
        found = False
        current_line = 0
        view_content = self._preview_panel.getViewContent()
        for i, line in enumerate(view_content, 1):
            if found:
                if not line.startswith("-"):
                    current_line += 1
                    if current_line == line_num:
                        lfCmd("call win_execute({}, 'norm! {}Gzz')".format(winid, i))
                        break
            # @@ -2,11 +2,21 @@
            elif line.startswith("@@"):
                line_numbers = line.split("+", 1)[1].split(None, 1)[0]
                if "," in line_numbers:
                    start, count = line_numbers.split(",")
                    start = int(start)
                    count = int(count)
                else:
                    # @@ -1886 +1893 @@
                    start = int(line_numbers)
                    count = 1

                if start + count > line_num:
                    found = True
                    current_line = start - 1

    def startInlineBlame(self, tmp_file_name):
        if lfEval("exists('b:lf_blame_changedtick')") == "1":
            return

        lfCmd("let g:Lf_git_inline_blame_enabled = 1")

        lfCmd("augroup Lf_Git_Blame | augroup END")
        lfCmd("autocmd! Lf_Git_Blame BufRead * silent call leaderf#Git#StartInlineBlame()")
        lfCmd("autocmd! Lf_Git_Blame BufWinEnter * silent call leaderf#Git#StartInlineBlame()")

        file_name = vim.current.buffer.name
        self._initial_changedtick[vim.current.buffer.number] = vim.current.buffer.vars["changedtick"]

        if " " in file_name:
            file_name = file_name.replace(' ', r'\ ')

        if tmp_file_name is None:
            git_cmd = (r'git blame --line-porcelain -- {} | grep "^author \|^author-time\|^summary"'
                       .format(file_name))
        else:
            git_cmd = (r'git blame --line-porcelain --contents {} -- {} | grep "^author \|^author-time\|^summary"'
                       .format(tmp_file_name, file_name))

        outputs = ParallelExecutor.run(git_cmd, directory=self._project_root, silent=True)
        if len(outputs[0]) == 0:
            return

        lfCmd("let b:lf_blame_line_number = line('.')")
        lfCmd("let b:lf_blame_changedtick = b:changedtick")
        blame_list = iter(outputs[0])
        i = 0
        self._blame_infos[vim.current.buffer.number] = {}
        blame_infos = self._blame_infos[vim.current.buffer.number]
        if lfEval("has('nvim')") == '1':
            lfCmd("let ns_id = nvim_create_namespace('LeaderF_Git_Blame_0')")
            for i, (author, author_time, summary) in enumerate(itertools.zip_longest(blame_list,
                                                                                     blame_list,
                                                                                     blame_list)):
                author = author.split(None, 1)[1].replace("External file (--contents)", "Not Committed Yet")
                author_time = int(author_time.split(None, 1)[1])
                summary = summary.split(None, 1)[1]
                mark_id = i + 1
                blame_infos[mark_id] = (vim.current.buffer[i], author, author_time, summary)
                lfCmd("call nvim_buf_set_extmark(0, ns_id, %d, 0, {'id': %d})" % (i, mark_id))
        else:
            for i, (author, author_time, summary) in enumerate(itertools.zip_longest(blame_list,
                                                                                     blame_list,
                                                                                     blame_list)):
                author = author.split(None, 1)[1].replace("External file (--contents)", "Not Committed Yet")
                author_time = int(author_time.split(None, 1)[1])
                summary = summary.split(None, 1)[1]
                prop_id = i + 1
                blame_infos[prop_id] = (vim.current.buffer[i], author, author_time, summary)
                lfCmd('call prop_add(%d, 1, {"type": "Lf_hl_gitTransparent", "length": 0, "id": %d})'
                      % (i+1, prop_id))

        line_number = vim.current.window.cursor[0]
        _, author, author_time, summary = blame_infos[line_number]
        author_time = self.formated_time(author_time)
        blame_info = "{} • {} • {}".format(author, author_time, summary)
        if lfEval("has('nvim')") == '1':
            lfCmd("let ns_id = nvim_create_namespace('LeaderF_Git_Blame_1')")
            lfCmd("call nvim_buf_set_extmark(0, ns_id, line('.') - 1, 0, {'id': 1, 'virt_text': [['    %s', 'Lf_hl_gitInlineBlame']]})"
                  % (escQuote(blame_info)))
        else:
            lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    %s'})"
                  % (escQuote(blame_info)))

        lfCmd("autocmd! Lf_Git_Blame CursorMoved <buffer> call leaderf#Git#UpdateInlineBlame({})"
              .format(id(self)))
        lfCmd("autocmd! Lf_Git_Blame InsertEnter <buffer> call leaderf#Git#HideInlineBlame({})"
              .format(id(self)))
        lfCmd("autocmd! Lf_Git_Blame InsertLeave <buffer> call leaderf#Git#ShowInlineBlame({})"
              .format(id(self)))

    def formated_time(self, timestamp):
        time_format = lfEval("get(g:, 'Lf_GitBlameTimeFormat', '')")
        if time_format == "":
            return self.relative_time(timestamp)
        else:
            return datetime.fromtimestamp(timestamp).strftime(time_format)

    def relative_time(self, timestamp):
        def format_time_unit(value, unit):
            if value == 1:
                return "{} {}".format(value, unit)
            else:
                return "{} {}s".format(value, unit)

        current_time = datetime.now()
        past_time = datetime.fromtimestamp(timestamp)

        delta = current_time - past_time

        years = delta.days // 365
        months = (delta.days % 365) // 30
        if years >= 1:
            if months == 0:
                return "{} ago".format(format_time_unit(years, "year"))
            else:
                return "{}, {} ago".format(format_time_unit(years, "year"),
                                           format_time_unit(months, "month"))
        elif months >= 1:
            return "{} ago".format(format_time_unit(months, "month"))
        else:
            days = delta.days
            if days >= 7:
                weeks = days // 7
                return "{} ago".format(format_time_unit(weeks, "week"))
            elif days >= 1:
                return "{} ago".format(format_time_unit(days, "day"))
            else:
                hours = delta.seconds // 3600
                if hours >= 1:
                    return "{} ago".format(format_time_unit(hours, "hour"))
                else:
                    minutes = delta.seconds // 60
                    if minutes >= 1:
                        return "{} ago".format(format_time_unit(minutes, "minute"))
                    else:
                        return "{} ago".format(format_time_unit(delta.seconds, "second"))

    def updateInlineBlame(self):
        if (lfEval("b:lf_blame_line_number == line('.')") == '1'
            and lfEval("b:lf_blame_changedtick == b:changedtick") == '1'):
            return

        self.showInlineBlame()

    def showInlineBlame(self):
        if lfEval("has('nvim')") == '1':
            self.nvim_showInlineBlame()
            return

        lfCmd("let b:lf_blame_line_number = line('.')")
        lfCmd("let b:lf_blame_changedtick = b:changedtick")

        lfCmd("call prop_remove({'type': 'Lf_hl_gitInlineBlame'})")
        prop_list = lfEval("prop_list(line('.'), {'types':['Lf_hl_gitTransparent']})")
        if len(prop_list) > 0:
            prop_id = int(prop_list[0]["id"])
            line, author, author_time, summary = self._blame_infos[vim.current.buffer.number][prop_id]
            if (vim.current.buffer.vars["changedtick"] == self._initial_changedtick[vim.current.buffer.number]
                or vim.current.line == line):
                author_time = self.formated_time(author_time)
                blame_info = "{} • {} • {}".format(author, author_time, summary)
                lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    %s'})"
                      % (escQuote(blame_info)))
            else:
                lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    Not Committed Yet'})")
        else:
            lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    Not Committed Yet'})")

    def nvim_showInlineBlame(self):
        lfCmd("let b:lf_blame_line_number = line('.')")
        lfCmd("let b:lf_blame_changedtick = b:changedtick")

        lfCmd("let ns_id_1 = nvim_create_namespace('LeaderF_Git_Blame_1')")
        lfCmd("call nvim_buf_del_extmark(0, ns_id_1, 1)")

        lfCmd("let ns_id_0 = nvim_create_namespace('LeaderF_Git_Blame_0')")
        mark_list = lfEval("nvim_buf_get_extmarks(0, ns_id_0, [line('.')-1, 0], [line('.')-1, -1], {})")
        if len(mark_list) > 0:
            mark_id = int(mark_list[0][0])
            line, author, author_time, summary = self._blame_infos[vim.current.buffer.number][mark_id]
            if (vim.current.buffer.vars["changedtick"] == self._initial_changedtick[vim.current.buffer.number]
                or vim.current.line == line):
                author_time = self.formated_time(author_time)
                blame_info = "{} • {} • {}".format(author, author_time, summary)
                if lfEval("has('nvim')") == '1':
                    lfCmd("call nvim_buf_set_extmark(0, ns_id_1, line('.') - 1, 0, {'id': 1, 'virt_text': [['    %s', 'Lf_hl_gitInlineBlame']]})"
                          % (escQuote(blame_info)))
                else:
                    lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    %s'})"
                          % (escQuote(blame_info)))
            else:
                if lfEval("has('nvim')") == '1':
                    lfCmd("call nvim_buf_set_extmark(0, ns_id_1, line('.') - 1, 0, {'id': 1, 'virt_text': [[ '    Not Committed Yet', 'Lf_hl_gitInlineBlame']]})")
                else:
                    lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    Not Committed Yet'})")
        else:
            if lfEval("has('nvim')") == '1':
                lfCmd("call nvim_buf_set_extmark(0, ns_id_1, line('.') - 1, 0, {'id': 1, 'virt_text': [[ '    Not Committed Yet', 'Lf_hl_gitInlineBlame']]})")
            else:
                lfCmd("call prop_add(line('.'), 0, {'type': 'Lf_hl_gitInlineBlame', 'text': '    Not Committed Yet'})")

    def hideInlineBlame(self):
        if lfEval("has('nvim')") == '1':
            lfCmd("let ns_id_1 = nvim_create_namespace('LeaderF_Git_Blame_1')")
            lfCmd("call nvim_buf_del_extmark(0, ns_id_1, 1)")
        else:
            lfCmd("call prop_remove({'type': 'Lf_hl_gitInlineBlame'})")

    def disableInlineBlame(self):
        lfCmd("let g:Lf_git_inline_blame_enabled = 0")
        lfCmd("augroup Lf_Git_Blame | au! | augroup END")
        buffers = {b.number for b in vim.buffers}
        if lfEval("has('nvim')") == '1':
            for buffer_num in self._blame_infos:
                if buffer_num not in buffers:
                    continue

                lfCmd("call leaderf#Git#RemoveExtmarks(%d)" % buffer_num)
                del vim.buffers[buffer_num].vars["lf_blame_changedtick"]
        else:
            for buffer_num in self._blame_infos:
                if buffer_num not in buffers:
                    continue

                lfCmd("call prop_remove({'type': 'Lf_hl_gitInlineBlame', 'bufnr': %d})"
                      % buffer_num)
                lfCmd("call prop_remove({'type': 'Lf_hl_gitTransparent', 'bufnr': %d})"
                      % buffer_num)
                del vim.buffers[buffer_num].vars["lf_blame_changedtick"]

        self._blame_infos = {}
        self._initial_changedtick = {}

    def startExplorer(self, win_pos, *args, **kwargs):
        if self.checkWorkingDirectory() == False:
            return

        arguments_dict = kwargs.get("arguments", {})
        self.setArguments(arguments_dict)

        if lfEval("exists('b:lf_blame_file_name')") == "1":
            buf_winid = int(lfEval("bufwinid(b:lf_blame_file_name)"))
            if buf_winid != -1:
                lfCmd("call win_gotoid({})".format(buf_winid))
            else:
                lfCmd("bel vsp {}".format(lfEval("b:lf_blame_file_name")))

        if vim.current.buffer.name and not vim.current.buffer.options['bt']:
            if not vim.current.buffer.name.startswith(self._project_root):
                lfPrintError("fatal: '{}' is outside repository at '{}'"
                             .format(lfRelpath(vim.current.buffer.name), self._project_root))
            else:
                self._arguments["blamed_file_name"] = vim.current.buffer.name
                tmp_file_name = None
                if vim.current.buffer.options["modified"]:
                    if sys.version_info >= (3, 0):
                        tmp_file = partial(tempfile.NamedTemporaryFile,
                                           encoding=lfEval("&encoding"))
                    else:
                        tmp_file = tempfile.NamedTemporaryFile

                    with tmp_file(mode='w+', delete=False) as f:
                        for line in vim.current.buffer:
                            f.write(line + '\n')
                        tmp_file_name = f.name
                    self._arguments["--contents"] = [tmp_file_name]

                if "--inline" in self._arguments:
                    self.startInlineBlame(tmp_file_name)
                else:
                    if self._project_root not in self._blame_panels:
                        self._blame_panels[self._project_root] = BlamePanel(self)

                    self._blame_panels[self._project_root].create(arguments_dict,
                                                                  self.createGitCommand(self._arguments,
                                                                                        None),
                                                                  project_root=self._project_root)
                if tmp_file_name is not None:
                    os.remove(tmp_file_name)
        else:
            lfPrintError("fatal: no such path '{}' in HEAD".format(vim.current.buffer.name))

        self._restoreOrigCwd()

    def cleanupExplorerPage(self, page):
        del self._pages[page.commit_id]


#*****************************************************
# gitExplManager is a singleton
#*****************************************************
gitExplManager = GitExplManager()

__all__ = ['gitExplManager']

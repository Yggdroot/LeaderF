#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import sys
import os.path
import json
import bisect
import itertools
if sys.version_info >= (3, 0):
    import queue as Queue
else:
    import Queue
from enum import Enum
from collections import OrderedDict
from .utils import *
from .explorer import *
from .manager import *
from .devicons import (
    webDevIconsGetFileTypeSymbol,
    removeDevIcons,
    matchaddDevIconsDefault,
    matchaddDevIconsExact,
    matchaddDevIconsExtension,
)

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
        self._display_multi = False
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

    def getPatternRegex(self):
        return self._pattern_regex

    def getContextSeparator(self):
        return self._context_separator

    def displayMulti(self):
        return self._display_multi


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
    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})

        executor = AsyncExecutor()
        self._executor.append(executor)

        options = GitLogExplorer.generateOptions(arguments_dict)
        cmd = 'git log {} --pretty=format:"%h%d %s"'.format(options)
        if "--current-file" in arguments_dict and "current_file" in arguments_dict:
            cmd += " -- {}".format(arguments_dict["current_file"])

        if "extra" in arguments_dict:
            cmd += " " + " ".join(arguments_dict["extra"])
        content = executor.execute(cmd, encoding=lfEval("&encoding"), format_line=self.formatLine)
        return content

    def formatLine(self, line):
        return line

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
        super(GitDiffCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        self._cmd = "git diff --no-color"
        extra_options = ""
        if "--cached" in self._arguments:
            extra_options += " --cached"

        if "extra" in self._arguments:
            extra_options += " " + " ".join(self._arguments["extra"])

        if self._source is not None:
            file_name = lfGetFilePath(self._source)
            if " " in file_name:
                file_name = file_name.replace(' ', r'\ ')
            extra_options += " -- {}".format(file_name)
        elif "--current-file" in self._arguments and "current_file" in self._arguments:
            extra_options += " -- {}".format(self._arguments["current_file"])

        self._cmd += extra_options
        self._buffer_name = "LeaderF://git diff" + extra_options
        self._file_type = "diff"
        self._file_type_cmd = "silent! doautocmd filetypedetect BufNewFile *.diff"


class GitLogDiffCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        super(GitLogDiffCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        # fuzzy search in navigation panel
        if not self._arguments["parent"].startswith("0000000"):
            self._cmd = "git diff --no-color {}..{} -- {}".format(self._arguments["parent"],
                                                                  self._arguments["commit_id"],
                                                                  lfGetFilePath(self._source)
                                                                  )
        else:
            self._cmd = "git show --pretty= --no-color {} -- {}".format(self._arguments["commit_id"],
                                                                        lfGetFilePath(self._source)
                                                                        )
        self._buffer_name = "LeaderF://" + self._cmd
        self._file_type = "diff"
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
        return "{}:{}:{}".format(commit_id[:7], source[0][:9], source[2])

    def buildCommandAndBufferName(self):
        self._cmd = "git cat-file -p {}".format(self._source[0])
        if self._source[0].startswith("0000000"):
            if self._source[1] == "M":
                if os.name == 'nt':
                    self._cmd = "type {}".format(self._source[2])
                else:
                    self._cmd = "cat {}".format(self._source[2])
            else:
                self._cmd = ""

        self._buffer_name = GitCatFileCommand.buildBufferName(self._commit_id, self._source)
        self._file_type_cmd = "silent! doautocmd filetypedetect BufNewFile {}".format(self._source[2])


class GitLogCommand(GitCommand):
    def __init__(self, arguments_dict, source):
        super(GitLogCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        if "--directly" in self._arguments:
            options = GitLogExplorer.generateOptions(self._arguments)
            self._cmd = "git log {}".format(options)

            if "extra" in self._arguments:
                self._cmd += " " + " ".join(self._arguments["extra"])

            if "--current-file" in self._arguments and "current_file" in self._arguments:
                self._cmd += " -- {}".format(self._arguments["current_file"])

            self._buffer_name = "LeaderF://" + self._cmd
        else:
            sep = ' ' if os.name == 'nt' else ''
            self._cmd = ('git show {} --pretty=format:"commit %H%nparent %P%n'
                         'Author:     %an <%ae>%nAuthorDate: %ad%nCommitter:  %cn <%ce>%nCommitDate:'
                         ' %cd{}%n%n%s%n%n%b%n" --stat=70 --stat-graph-width=10 -p --no-color'
                         ).format(self._source, sep)

            if "--recall" in self._arguments and "current_file" in self._arguments:
                self._cmd += " -- {}".format(self._arguments["current_file"])
            elif "--current-file" in self._arguments and "current_file" in self._arguments:
                self._cmd += " -- {}".format(self._arguments["current_file"])

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
        super(GitLogExplCommand, self).__init__(arguments_dict, source)

    def buildCommandAndBufferName(self):
        self._cmd = ('git show -m --raw -C --numstat --shortstat '
                     '--pretty=format:"# %P" --no-abbrev {}').format(self._source)

        self._buffer_name = "LeaderF://navigation/" + self._source
        self._file_type_cmd = ""


class ParallelExecutor(object):
    @staticmethod
    def run(*cmds):
        outputs = [[] for _ in range(len(cmds))]
        stop_thread = False

        def readContent(content, output):
            try:
                for line in content:
                    output.append(line)
                    if stop_thread:
                        break
            except Exception:
                traceback.print_exc()
                traceback.print_stack()


        executors = [AsyncExecutor() for _ in range(len(cmds))]
        workers = []
        for i, (exe, cmd) in enumerate(zip(executors, cmds)):
            content = exe.execute(cmd, encoding=lfEval("&encoding"))
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

    def getWindowId(self):
        if lfEval("win_id2tabwin({})".format(self._window_id)) == ['0', '0']:
            self._window_id = int(lfEval("bufwinid('{}')".format(escQuote(self._buffer.name))))
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
            lfCmd("call win_execute({}, '{}')".format(winid, self._cmd.getFileTypeCommand()))

    def initBuffer(self):
        pass

    def defineMaps(self, winid):
        pass

    def enableColor(self, winid):
        pass

    def create(self, winid, bufhidden='wipe', buf_content=None):
        self._bufhidden = bufhidden

        if self._buffer is not None:
            self._buffer.options['modifiable'] = True
            del self._buffer[:]
            self._buffer.options['modifiable'] = False
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
            content = self._executor.execute(self._cmd.getCommand(), encoding=encoding)
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


class KeyWrapper(object):
    def __init__(self, iterable, key):
        self._list = iterable
        self._key = key

    def __getitem__(self, i):
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
    def __init__(self, owner, cmd, project_root):
        super(TreeView, self).__init__(owner, cmd)
        self._project_root = project_root
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
        self._left_most_file = set()
        self._source_queue = Queue.Queue()
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
                '" Press <F1> for help',
                '',
                self._project_root + "/",
                ]
        self._match_ids = []

    def enableColor(self, winid):
        if lfEval("hlexists('Lf_hl_help')") == '0':
            lfCmd("call leaderf#colorscheme#popup#load('{}', '{}')".format("git",
                    lfEval("get(g:, 'Lf_PopupColorscheme', 'default')")))

        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitHelp'', ''^".*'', -100)')"""
              .format(winid))
        id = int(lfEval("matchid"))
        self._match_ids.append(id)
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitFolder'', ''\S*/'', -100)')"""
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
        lfCmd(r"""call win_execute({}, 'let matchid = matchadd(''Lf_hl_gitModificationIcon'', ''^\s*\zs{}'', -100)')"""
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

    def defineMaps(self, winid):
        lfCmd("call win_execute({}, 'call leaderf#Git#TreeViewMaps({})')"
              .format(winid, id(self)))

    def getFirstSource(self):
        if self._cur_parent in self._first_source:
            return self._first_source[self._cur_parent]
        else:
            parent = ""
            while(parent != self._cur_parent):
                parent, source = self._source_queue.get()
                self._first_source[parent] = source

            return source

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

    def enqueueLeftMostFile(self, parent):
        self._left_most_file.add(parent)

        tree_node = self._trees[parent]
        self._source_queue.put((parent, self.getLeftMostFile(tree_node)))

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

                                if parent not in self._left_most_file:
                                    self.enqueueLeftMostFile(parent)
                            elif i == 0:
                                self.appendRemainingFiles(parent, tree_node)

                        if len(self._file_structures[parent]) >= self._preopen_num:
                            status = FolderStatus.CLOSED
                        else:
                            status = FolderStatus.OPEN
                        tree_node.dirs[d] = TreeNode(status)

                    tree_node = tree_node.dirs[d]

            if mode != "160000":
                tree_node.files[file] = source
        elif line.startswith(" "):
            parent, tree_node = self._trees.last_key_value()
            self._short_stat[parent] = line
            self.appendRemainingFiles(parent, tree_node)
            self.appendFiles(parent, 0, tree_node)
            if parent not in self._left_most_file:
                self.enqueueLeftMostFile(parent)
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
            line_num = vim.current.window.cursor[0]
            index = line_num - len(self._head) - 1
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
            index = line_num - len(self._head) - 1
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
            self._locateFile(lfRelpath(path))

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
            # lfCmd("call win_gotoid({})" .format(self.getWindowId()))
            # lfCmd("{} | norm! 0zz" .format(index + 1 + len(self._head)))
            lfCmd("call win_execute({}, 'norm! {}Gzz')"
                  .format(self.getWindowId(), index + 1 + len(self._head)))
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

            line_num = index + len(self._head)
            increment = self.expandFolder(line_num, index - 1, meta_info, False)

            index = Bisect.bisect_left(structure, 0, index, index + increment, key=getKey)
            if index < len(structure) and structure[index].path == path:
                lfCmd("call win_execute({}, 'norm! {}Gzz')"
                      .format(self.getWindowId(), index + 1 + len(self._head)))
                # lfCmd("call win_gotoid({})" .format(self.getWindowId()))
                # lfCmd("{} | norm! 0zz" .format(index + 1 + len(self._head)))
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
            icon = self._status_icons.get(meta_info.info[2][0], self._modification_icon)

            orig_name = ""
            if meta_info.info[2][0] in ("R", "C"):
                head, tail = os.path.split(meta_info.info[3])
                orig_name = "{} => ".format(lfRelpath(meta_info.info[3],
                                                      os.path.dirname(meta_info.info[4])))

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
            lfCmd("call nvim_win_set_option(%d, 'cursorline', v:true)" % winid)
            lfCmd("call nvim_win_set_option(%d, 'number', v:false)" % winid)
        else:
            lfCmd("call win_execute({}, 'setlocal cursorline')".format(winid))
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
            self._buffer[:] = self._head
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
                    init_line = len(self._head)

                    if cursor_line <= init_line:
                        lfCmd("call win_execute({}, 'norm! {}G')".format(self.getWindowId(), init_line))
                        cursor_line = int(lfEval("getcurpos({})[1]".format(self.getWindowId())))

                    for info in structure[self._offset_in_content:cur_len]:
                        self._buffer.append(self.buildLine(info))
                        if cursor_line == init_line and not info.is_dir:
                            cursor_line = len(self._buffer)
                            lfCmd("call win_execute({}, 'norm! {}G')".format(self.getWindowId(), cursor_line))

                    self._offset_in_content = cur_len
                    lfCmd("redraw")
            finally:
                self._buffer.options['modifiable'] = False

        if self._read_finished == 1 and self._offset_in_content == len(structure):
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
            content = self._executor.execute(self._cmd.getCommand(), encoding=encoding)
            for line in content:
                self.buildTree(line)
                if self._stop_reader_thread:
                    break
            else:
                self._read_finished = 1
                self._owner.readFinished(self)

            # if content is empty, getFirstSource() will hang
            if self._cur_parent is None:
                self._first_source[self._cur_parent] = None
                self._source_queue.put((None, None))
        except Exception:
            traceback.print_exc()
            traceback.print_stack()
            self._read_finished = 1

    def cleanup(self):
        super(TreeView, self).cleanup()

        self._match_ids = []


class Panel(object):
    def __init__(self):
        pass

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

    def writeBuffer(self):
        for v in self._views.values():
            v.writeBuffer()


class PreviewPanel(Panel):
    def __init__(self):
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

    def create(self, cmd, config):
        if lfEval("has('nvim')") == '1':
            lfCmd("noautocmd let scratch_buffer = nvim_create_buf(0, 1)")
            self._preview_winid = int(lfEval("nvim_open_win(scratch_buffer, 0, %s)"
                                             % json.dumps(config)))
        else:
            lfCmd("noautocmd silent! let winid = popup_create([], %s)" % json.dumps(config))
            self._preview_winid = int(lfEval("winid"))

        GitCommandView(self, cmd).create(self._preview_winid)

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


class DiffViewPanel(Panel):
    def __init__(self, bufhidden_callback=None, commit_id=""):
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

    def getValidWinIDs(self, win_ids):
        if win_ids == [-1, -1]:
            lfCmd("wincmd w | leftabove new")
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

    def hasView(self):
        return vim.current.tabpage in self._buffer_names

    def isAllHidden(self):
        return len(self._views) == 0

    def create(self, arguments_dict, source, **kwargs):
        """
        source is a tuple like (b90f76fc1, bad07e644, R099, src/version.c, src/version2.c)
        """
        file_path = lfGetFilePath(source)
        sources = ((source[0], source[2], source[3]),
                   (source[1], source[2], file_path))
        buffer_names = (GitCatFileCommand.buildBufferName(self._commit_id, sources[0]),
                        GitCatFileCommand.buildBufferName(self._commit_id, sources[1]))
        if buffer_names[0] in self._views and buffer_names[1] in self._views:
            win_ids = (self._views[buffer_names[0]].getWindowId(),
                       self._views[buffer_names[1]].getWindowId())
            lfCmd("call win_gotoid({})".format(win_ids[0]))
        elif buffer_names[0] in self._views:
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[0]].getWindowId()))
            cmd = GitCatFileCommand(arguments_dict, sources[1], self._commit_id)
            lfCmd("rightbelow vsp {}".format(cmd.getBufferName()))
            if buffer_names[1] in self._hidden_views:
                self.bufShown(buffer_names[1], int(lfEval("win_getid()")))
            else:
                GitCommandView(self, cmd).create(int(lfEval("win_getid()")), bufhidden='hide')
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[0]].getWindowId()))
        elif buffer_names[1] in self._views:
            lfCmd("call win_gotoid({})".format(self._views[buffer_names[1]].getWindowId()))
            cmd = GitCatFileCommand(arguments_dict, sources[0], self._commit_id)
            lfCmd("leftabove vsp {}".format(cmd.getBufferName()))
            if buffer_names[0] in self._hidden_views:
                self.bufShown(buffer_names[0], int(lfEval("win_getid()")))
            else:
                GitCommandView(self, cmd).create(int(lfEval("win_getid()")), bufhidden='hide')
        else:
            if kwargs.get("mode", '') == 't':
                lfCmd("noautocmd tabnew | vsp")
                tabmove()
                win_ids = [int(lfEval("win_getid({})".format(w.number)))
                           for w in vim.current.tabpage.windows]
            elif "winid" in kwargs: # --explorer
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
            else:
                buffer_names = self._buffer_names[vim.current.tabpage]
                win_ids = [int(lfEval("bufwinid('{}')".format(escQuote(name)))) for name in buffer_names]
                win_ids = self.getValidWinIDs(win_ids)

            cat_file_cmds = [GitCatFileCommand(arguments_dict, s, self._commit_id) for s in sources]
            outputs = [None, None]
            if (cat_file_cmds[0].getBufferName() not in self._hidden_views
                and cat_file_cmds[1].getBufferName() not in self._hidden_views):
                outputs = ParallelExecutor.run(*[cmd.getCommand() for cmd in cat_file_cmds])

            if vim.current.tabpage not in self._buffer_names:
                self._buffer_names[vim.current.tabpage] = [None, None]

            for i, (cmd, winid) in enumerate(zip(cat_file_cmds, win_ids)):
                if (lfEval("bufname(winbufnr({}))".format(winid)) == ""
                    and int(lfEval("bufnr('{}')".format(escQuote(cmd.getBufferName())))) != -1):
                    lfCmd("call win_execute({}, 'setlocal bufhidden=wipe')".format(winid))

                buffer_name = lfEval("bufname(winbufnr({}))".format(winid))
                lfCmd("call win_execute({}, 'diffoff | hide edit {}')".format(winid, cmd.getBufferName()))

                # if the buffer also in another tabpage, BufHidden is not triggerd
                # should run this code
                if buffer_name in self._views:
                    self.bufHidden(self._views[buffer_name])

                self._buffer_names[vim.current.tabpage][i] = cmd.getBufferName()
                if cmd.getBufferName() in self._hidden_views:
                    self.bufShown(cmd.getBufferName(), winid)
                else:
                    GitCommandView(self, cmd).create(winid, bufhidden='hide', buf_content=outputs[i])

            lfCmd("call win_gotoid({})".format(win_ids[0]))


class NavigationPanel(Panel):
    def __init__(self, bufhidden_callback=None):
        self.tree_view = None
        self._bufhidden_cb = bufhidden_callback
        self._is_hidden = False

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

    def create(self, cmd, winid, project_root):
        TreeView(self, cmd, project_root).create(winid, bufhidden="hide")

    def writeBuffer(self):
        # called in idle
        if self.tree_view is not None:
            self.tree_view.writeBuffer()

    def getFirstSource(self):
        return self.tree_view.getFirstSource()

    def getWindowId(self):
        return self.tree_view.getWindowId()


class ExplorerPage(object):
    def __init__(self, project_root, commit_id, owner):
        self._project_root = project_root
        self._navigation_panel = NavigationPanel(self.afterBufhidden)
        self._diff_view_panel = DiffViewPanel(self.afterBufhidden, commit_id)
        self._commit_id = commit_id
        self._owner = owner
        self._arguments = {}
        self._win_pos = None
        self.tabpage = None
        self._git_diff_manager = None

    def _createWindow(self, win_pos, buffer_name):
        self._win_pos = win_pos
        if win_pos == 'top':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj abo {}sp {}".format(height, buffer_name))
        elif win_pos == 'bottom':
            height = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelHeight', &lines * 0.3)")))
            lfCmd("silent! noa keepa keepj bel {}sp {}".format(height, buffer_name))
        elif win_pos == 'left':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
            lfCmd("silent! noa keepa keepj abo {}vsp {}".format(width, buffer_name))
        elif win_pos == 'right':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
            lfCmd("silent! noa keepa keepj bel {}vsp {}".format(width, buffer_name))
        else: # left
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
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
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
            width = int(lfEval("&columns")) - width + 1
            lfCmd("silent! noa keepa keepj bel {}vsp".format(width))
        elif win_pos == 'right':
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
            width = int(lfEval("&columns")) - width - 1
            lfCmd("silent! noa keepa keepj abo {}vsp".format(width))
        else: # left
            width = int(float(lfEval("get(g:, 'Lf_GitNavigationPanelWidth', &columns * 0.2)")))
            width = int(lfEval("&columns")) - width + 1
            lfCmd("silent! noa keepa keepj bel {}vsp".format(width))

        return int(lfEval("win_getid()"))

    def defineMaps(self, winid):
        lfCmd("call win_execute({}, 'call leaderf#Git#ExplorerMaps({})')"
              .format(winid, id(self)))

    def create(self, arguments_dict, cmd):
        self._arguments = arguments_dict
        lfCmd("noautocmd tabnew")

        self.tabpage = vim.current.tabpage
        diff_view_winid = int(lfEval("win_getid()"))

        win_pos = arguments_dict.get("--navigation-position", ["left"])[0]
        winid = self._createWindow(win_pos, cmd.getBufferName())

        self._navigation_panel.create(cmd, winid, self._project_root)
        self.defineMaps(self._navigation_panel.getWindowId())

        source = self._navigation_panel.getFirstSource()
        if source is not None:
            self._diff_view_panel.create(arguments_dict, source, winid=diff_view_winid)
            lfCmd("call win_gotoid({})".format(self._navigation_panel.getWindowId()))

    def afterBufhidden(self):
        if self._navigation_panel.isHidden() and self._diff_view_panel.isAllHidden():
            lfCmd("call timer_start(1, function('leaderf#Git#Cleanup', [{}]))".format(id(self)))

    def cleanup(self):
        self._navigation_panel.cleanup()
        self._diff_view_panel.cleanup()

    def open(self, recursive, **kwargs):
        source = self._navigation_panel.tree_view.expandOrCollapseFolder(recursive)
        if source is not None:
            if kwargs.get("mode", '') == 't':
                tabpage_count = len(vim.tabpages)
                self._diff_view_panel.create(self._arguments, source, mode='t')
                if len(vim.tabpages) > tabpage_count:
                    tabmove()
            elif len(vim.current.tabpage.windows) == 1:
                win_pos = self._arguments.get("--navigation-position", ["left"])[0]
                diff_view_winid = self.splitWindow(win_pos)
                self._diff_view_panel.create(self._arguments, source, winid=diff_view_winid)
            elif not self._diff_view_panel.hasView():
                if self._win_pos in ["top", "left"]:
                    lfCmd("wincmd w")
                else:
                    lfCmd("wincmd W")
                lfCmd("noautocmd leftabove sp")
                diff_view_winid = int(lfEval("win_getid()"))
                self._diff_view_panel.create(self._arguments, source, winid=diff_view_winid)
            else:
                self._diff_view_panel.create(self._arguments, source)

            if kwargs.get("preview", False) == True:
                lfCmd("call win_gotoid({})".format(self._navigation_panel.getWindowId()))

    def locateFile(self, path):
        self._navigation_panel.tree_view.locateFile(path)
        self.open(False, preview=True)

    def fuzzySearch(self, recall=False):
        if self._git_diff_manager is None:
            self._git_diff_manager = GitDiffExplManager()

        kwargs = {}
        kwargs["arguments"] = {
                "owner": self._owner,
                "commit_id": self._commit_id,
                "parent": self._navigation_panel.tree_view.getCurrentParent(),
                "content": self._navigation_panel.tree_view.getFileList(),
                "accept": self.locateFile
                }

        if recall == True:
            kwargs["arguments"]["--recall"] = []

        self._git_diff_manager.startExplorer("popup", **kwargs)


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
        self._selected_content = None
        self._project_root = ""

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
        else:
            return super(GitExplManager, self)

    def checkWorkingDirectory(self):
        self._orig_cwd = lfGetCwd()
        self._project_root = nearestAncestor([".git"], self._orig_cwd)
        if self._project_root: # there exists a root marker in nearest ancestor path
            # https://github.com/neovim/neovim/issues/8336
            if lfEval("has('nvim')") == '1':
                chdir = vim.chdir
            else:
                chdir = os.chdir
            chdir(self._project_root)
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
        self._preview_panel.create(self.createGitCommand(self._arguments, source), config)
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

                outputs = ParallelExecutor.run(cmd)
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
            lfCmd("augroup Lf_Git | augroup END")
            lfCmd("autocmd! Lf_Git BufWipeout <buffer> call leaderf#Git#DiffOff({})".format(win_ids))
            lfCmd("call win_execute({}, 'autocmd! Lf_Git BufHidden,BufWipeout <buffer> call leaderf#Git#DiffOff({})')"
                  .format(win_ids[0], win_ids))
            lfCmd("setlocal nobuflisted")
            lfCmd("setlocal buftype=nofile")
            lfCmd("setlocal bufhidden=wipe")
            lfCmd("setlocal undolevels=-1")
            lfCmd("setlocal noswapfile")
            lfCmd("setlocal nospell")

            outputs = ParallelExecutor.run(cmd)
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
            outputs = ParallelExecutor.run(cmd)
            if len(outputs[0]) > 0:
                _, source = TreeView.generateSource(outputs[0][0])
                self._diff_view_panel.create(self._arguments, source, **{"mode": 't'})
            else:
                lfPrintError("No diffs!")

    def startExplorer(self, win_pos, *args, **kwargs):
        if self.checkWorkingDirectory() == False:
            return

        arguments_dict = kwargs.get("arguments", {})
        if "--recall" not in arguments_dict:
            self.setArguments(arguments_dict)
            if ("--current-file" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']
               ):
                file_name = vim.current.buffer.name
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                self._arguments["current_file"] = lfRelpath(file_name)
                if "-s" in self._arguments:
                    self.vsplitDiff()
                else:
                    self._accept(self._arguments["current_file"], "")
                return

        if "--recall" in arguments_dict:
            super(GitExplManager, self).startExplorer(win_pos, *args, **kwargs)
        elif "--directly" in self._arguments:
            self._result_panel.create(self.createGitCommand(self._arguments, None))
            self._restoreOrigCwd()
        elif "--explorer" in self._arguments:
            lfCmd("augroup Lf_Git | augroup END")
            lfCmd("autocmd! Lf_Git TabClosed * call leaderf#Git#CleanupExplorerPage({})"
                  .format(id(self)))

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

        if "-s" in self._arguments:
            self._diff_view_panel.create(self._arguments, source, **kwargs)
        elif "accept" in self._arguments:
            self._arguments["accept"](lfGetFilePath(source))
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

    def cleanupExplorerPage(self):
        for page in self._pages:
            if page.tabpage not in vim.tabpages:
                self._pages.discard(page)
                return


class GitLogExplManager(GitExplManager):
    def __init__(self):
        super(GitLogExplManager, self).__init__()
        lfCmd("augroup Lf_Git | augroup END")
        lfCmd("autocmd! Lf_Git FileType git call leaderf#Git#DefineSyntax()")
        self._diff_view_panel = None
        # key is source, value is ExplorerPage
        self._pages = {}

    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = GitLogExplorer()
        return self._explorer

    def _getDigest(self, line, mode):
        return line.lstrip(r"*\|/ ")

    def _getDigestStartPos(self, line, mode):
        return len(line) - len(line.lstrip(r"*\|/ "))

    def afterBufhidden(self):
        if self._diff_view_panel.isAllHidden():
            lfCmd("call timer_start(1, function('leaderf#Git#Cleanup', [{}]))".format(id(self)))

    def getSource(self, line):
        """
        return the hash
        """
        line = line.lstrip(r"*\|/ ")
        if line == '':
            return None

        return line.split(None, 1)[0]

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        if source is None:
            return

        self._preview_panel.create(self.createGitCommand(self._arguments, source), config)
        self._preview_winid = self._preview_panel.getPreviewWinId()
        self._setWinOptions(self._preview_winid)

    def getPreviewCommand(self, arguments_dict, source):
        return GitLogDiffCommand(arguments_dict, source)

    def createGitCommand(self, arguments_dict, source):
        return GitLogCommand(arguments_dict, source)

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        if source is None:
            return

        self.setOptionsForCursor()

        content = self._preview_panel.getContent(source)
        if content is None:
            self._preview_panel.createView(self.createGitCommand(self._arguments, source))
        else:
            self._preview_panel.setContent(content)

    def startExplorer(self, win_pos, *args, **kwargs):
        if self.checkWorkingDirectory() == False:
            return

        arguments_dict = kwargs.get("arguments", {})
        if "--recall" not in arguments_dict:
            self.setArguments(arguments_dict)
            if ("--current-file" in arguments_dict
                and vim.current.buffer.name
                and not vim.current.buffer.options['bt']
               ):
                file_name = vim.current.buffer.name
                if " " in file_name:
                    file_name = file_name.replace(' ', r'\ ')
                self._arguments["current_file"] = lfRelpath(file_name)

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
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph2'', ''^[*\|/ ]\{2}\zs|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph3'', ''^[*\|/ ]\{4}\zs|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraph4'', ''\(^[*\|/ ]\{6,}\)\@<=|'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitGraphSlash'', ''\(^[*\|/ ]\{-}\)\@<=[\/]'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitHash'', ''\(^[*\|/ ]*\)\@<=[0-9A-Fa-f]\+'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_gitRefNames'', ''^[*\|/ ]*[0-9A-Fa-f]\+\s*\zs(.\{-})'')')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
        else:
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph1', '^|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph2', '^[*\|/ ]\{2}\zs|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph3', '^[*\|/ ]\{4}\zs|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraph4', '\(^[*\|/ ]\{6,}\)\@<=|')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitGraphSlash', '\(^[*\|/ ]\{-}\)\@<=[\/]')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitHash', '\(^[*\|/ ]*\)\@<=[0-9A-Fa-f]\+')'''))
            self._match_ids.append(id)
            id = int(lfEval(r'''matchadd('Lf_hl_gitRefNames', '^[*\|/ ]*[0-9A-Fa-f]\+\s*\zs(.\{-})')'''))
            self._match_ids.append(id)

    def _accept(self, file, mode, *args, **kwargs):
        super(GitExplManager, self)._accept(file, mode, *args, **kwargs)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        source = self.getSource(line)
        if source is None:
            return

        if "--current-file" in self._arguments and "current_file" in self._arguments:
            if self._diff_view_panel is None:
                self._diff_view_panel = DiffViewPanel(self.afterBufhidden)

            self._diff_view_panel.setCommitId(source)
            cmd = "git show --pretty= --no-color --raw {} -- {}".format(source,
                                                                        self._arguments["current_file"])
            outputs = ParallelExecutor.run(cmd)
            if len(outputs[0]) > 0:
                _, source = TreeView.generateSource(outputs[0][0])
                self._diff_view_panel.create(self._arguments, source, **kwargs)
        elif "--explorer" in self._arguments:
            if source in self._pages:
                vim.current.tabpage = self._pages[source].tabpage
            else:
                lfCmd("augroup Lf_Git | augroup END")
                lfCmd("autocmd! Lf_Git TabClosed * call leaderf#Git#CleanupExplorerPage({})"
                      .format(id(self)))

                self._pages[source] = ExplorerPage(self._project_root, source, self)
                self._pages[source].create(self._arguments,
                                           GitLogExplCommand(self._arguments, source))
        else:
            if kwargs.get("mode", '') == 't' and source not in self._result_panel.getSources():
                self._arguments["mode"] = 't'
                lfCmd("tabnew")

            tabpage_count = len(vim.tabpages)

            self._result_panel.create(self.createGitCommand(self._arguments, source),
                                      self._selected_content)

            if kwargs.get("mode", '') == 't' and len(vim.tabpages) > tabpage_count:
                tabmove()

    def cleanup(self):
        if self._diff_view_panel is not None:
            self._diff_view_panel.cleanup()

    def cleanupExplorerPage(self):
        for k, v in self._pages.items():
            if v.tabpage not in vim.tabpages:
                del self._pages[k]
                return


#*****************************************************
# gitExplManager is a singleton
#*****************************************************
gitExplManager = GitExplManager()

__all__ = ['gitExplManager']

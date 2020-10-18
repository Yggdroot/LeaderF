#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from .utils import *
from .explorer import *
from .manager import *

# :command result line
# "!|  LeaderfBufTag     0      Leaderf<bang> bufTag"
#      ^^^^^^^^^^^^^
RE_USER_DEFINED_COMMAND = re.compile(r"^.{4}(\w+)")

# index.txt line
# "|:silent|	:sil[ent]	..."
#    ^^^^^^
RE_BUILT_IN_COMMAND = re.compile(r"^\|:([^|]+)\|")

#*****************************************************
# CommandExplorer
#*****************************************************
class CommandExplorer(Explorer):
    def __init__(self):
        self._content = []

    def getContent(self, *args, **kwargs):
        if self._content:
            return self._content
        else:
            return self.getFreshContent()

    def getFreshContent(self, *args, **kwargs):
        result_list = []

        # user-defined Ex commands
        result = lfEval("execute('command')")

        for line in result.splitlines()[2:]:
            match = RE_USER_DEFINED_COMMAND.match(line)
            if match:
                result_list.append(match.group(1))

        # built-in Ex commands
        index_file = lfEval("expand('$VIMRUNTIME/doc/index.txt')")
        with lfOpen(index_file, 'r', errors="ignore") as f:
            for line in f:
                match = RE_BUILT_IN_COMMAND.search(line)
                if match:
                    result_list.append(match.group(1))

        return result_list

    def getStlCategory(self):
        return "Command"

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))


# *****************************************************
# CommandExplManager
# *****************************************************
class CommandExplManager(Manager):
    def __init__(self):
        super(CommandExplManager, self).__init__()

    def _getExplClass(self):
        return CommandExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Command#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        """"""
        cmd = args[0]

        if "--run-immediately" in self.getArguments():
            try:
                lfCmd(cmd)
                lfCmd("call histadd(':', '%s')" % escQuote(cmd))
            except vim.error as e:
                error = lfEncode(str(repr(e)))
                if "E471" in error:
                    # Arguments mandatory
                    lfCmd("call feedkeys(':%s', 'n')" % escQuote(cmd))
                else:
                    lfPrintError(e)
        else:
            lfCmd("call feedkeys(':%s', 'n')" % escQuote(cmd))

    def _getDigest(self, line, mode):
        return line

    def _getDegestStartPos(self, line, mode):
        return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/o : execute command under cursor')
        help.append('" q : quit')
        help.append('" i : switch to input mode')
        help.append('" e : edit command under cursor')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _cmdExtension(self, cmd):
        if equal(cmd, '<C-o>'):
            self.editCommand()
        return True

    def editCommand(self):
        instance = self._getInstance()
        line = instance.currentLine
        instance.exitBuffer()
        lfCmd("call feedkeys(':%s', 'n')" % escQuote(line))


# *****************************************************
# commandExplManager is a singleton
# *****************************************************
commandExplManager = CommandExplManager()

__all__ = ["commandExplManager"]

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import argparse
from functools import partial
from .utils import *
from .explorer import *
from .manager import *
from .asyncExecutor import AsyncExecutor


"""
let g:Lf_Extensions = {
    \ "apple": {
    \       "source": [], "grep -r '%s' *", funcref (arguments), {"command": "ls" or funcref(arguments)}
    \       "arguments": [
    \           { "name": ["--foo", "-f"], "nargs": n or "?" or "*" or "+", help: "hehe"},
    \           { "name": ["bar"], "nargs": n or "?" or "*" or "+" }
    \       ],
    \       "format_line": funcref (line, arguments),
    \       "format_list": funcref ([], arguments),
    \       "accept": funcref (line, arguments),
    \       "preview": funcref (orig_buf_nr, orig_cursor, arguments),
    \       "supports_name_only": 0,
    \       "get_digest": funcref (line, mode),
    \       "before_enter": funcref (arguments),
    \       "after_enter": funcref (orig_buf_nr, orig_cursor, arguments),
    \       "bang_enter": funcref (orig_buf_nr, orig_cursor, arguments),
    \       "before_exit": funcref (orig_buf_nr, orig_cursor, arguments),
    \       "after_exit": funcref (arguments),
    \       "highlights_def": {
    \               "Lf_hl_apple": '^\s*\zs\d\+',
    \               "Lf_hl_appleId": '\d\+$',
    \       },
    \       "highlights_cmd": [
    \               "hi Lf_hl_apple guifg=red",
    \               "hi Lf_hl_appleId guifg=green",
    \       ],
    \       "highlight": funcref (arguments),
    \       "supports_multi": 0,
    \       "supports_refine": 0,
    \ },
    \ "orange": {}
\}
"""
#*****************************************************
# AnyExplorer
#*****************************************************
class AnyExplorer(Explorer):
    def __init__(self):
        self._executor = []

    def setConfig(self, category, config):
        self._category, self._config = category, config

    def getContent(self, *args, **kwargs):
        source = self._config.get("source")
        if not source:
            return None

        if isinstance(source, list):
            result = source
        elif isinstance(source, vim.Function):
            try:
                result = list(line for line in list(source(kwargs["arguments"])))
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(source), err))
        elif isinstance(source, dict):
            if isinstance(source["command"], vim.Function):
                try:
                    source_cmd = lfBytes2Str(source["command"](kwargs.get("arguments", {})))
                except vim.error as err:
                    raise Exception("Error occurred in user defined %s: %s" % (str(source["command"]), err))
            elif type(source["command"]) == type("string"):
                source_cmd = source["command"]

                positional_args = kwargs["positional_args"]
                if source_cmd.count("%s") != len(positional_args):
                    raise Exception("Number of positional arguments does not match!\n"
                                    "source_cmd = '{}', positional_args = {}".format(source_cmd,
                                                                                     str(positional_args)))
                else:
                    arguments = kwargs["arguments"]
                    source_cmd = source_cmd % tuple(arguments[name][0] for name in positional_args)
            else:
                raise Exception("Invalid source command `{}`, should be a string or a Funcref!".format(str(source["command"])))

            lfCmd("let g:Lf_Debug_SourceCmd = '%s'" % escQuote(source_cmd))
            executor = AsyncExecutor()
            self._executor.append(executor)
            if re.search(r'\brg\b|\bag\b|\bpt\b|\bfd\b|\bgit\b', source_cmd): # encoding of output is utf-8
                result = executor.execute(source_cmd, encoding=lfEval("&encoding"))
            else: # buildin command such as dir, grep arguments
                result = executor.execute(source_cmd)
        else:
            raise Exception("Invalid source `{}`!".format(str(source)))

        format_line = self._config.get("format_line")
        if format_line:
            try:
                # Note: If outQueue is empty, AsyncExecutor may yield None in read()
                result = (format_line(line, kwargs["arguments"]) for line in result if line is not None)
                if isinstance(result, list):
                    result = list(result)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(format_line), err))

        format_list = self._config.get("format_list")
        if format_list:
            try:
                result = list(format_list(list(result), kwargs["arguments"]))
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(format_list), err))

        return result

    def getStlCategory(self):
        return self._category

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return bool(int(self._config.get("supports_name_only", False)))

    def supportsMulti(self):
        return bool(int(self._config.get("supports_multi", False)))


#*****************************************************
# AnyExplManager
#*****************************************************
class AnyExplManager(Manager):
    def __init__(self, category, config):
        super(AnyExplManager, self).__init__()
        self._getExplorer().setConfig(category, config)
        self._category = category
        self._config = config
        self._match_ids = []

    def _getExplClass(self):
        return AnyExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Any#Maps('%s')" % self._category)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        accept = self._config.get("accept")
        if accept:
            try:
                accept(line, self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(accept), err))

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ""

        get_digest = self._config.get("get_digest")
        if get_digest:
            try:
                return lfBytes2Str(get_digest(line, mode)[0])
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(get_digest), err))
        else:
            return super(AnyExplManager, self)._getDigest(line, mode)

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if not line:
            return 0

        get_digest = self._config.get("get_digest")
        if get_digest:
            try:
                return int(get_digest(line, mode)[1])
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(get_digest), err))
        else:
            return super(AnyExplManager, self)._getDigestStartPos(line, mode)

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q/<Esc> : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _beforeEnter(self):
        super(AnyExplManager, self)._beforeEnter()
        before_enter = self._config.get("before_enter")
        if before_enter:
            try:
                before_enter(self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(before_enter), err))

    def _afterEnter(self):
        super(AnyExplManager, self)._afterEnter()
        after_enter = self._config.get("after_enter")
        if after_enter:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            try:
                after_enter(orig_buf_nr, [line, col+1], self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(after_enter), err))

        highlights_cmd = self._config.get("highlights_cmd", [])
        for cmd in highlights_cmd:
            lfCmd(cmd)

        highlights_def = self._config.get("highlights_def", {})
        for group, pattern in highlights_def.items():
            id = int(lfEval("matchadd('%s', '%s')" % (group, escQuote(pattern))))
            self._match_ids.append(id)

        highlight = self._config.get("highlight")
        if highlight:
            try:
                self._match_ids += highlight(self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(highlight), err))

    def _bangEnter(self):
        bang_enter = self._config.get("bang_enter")
        if bang_enter:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            try:
                bang_enter(orig_buf_nr, [line, col+1], self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(bang_enter), err))

    def _beforeExit(self):
        super(AnyExplManager, self)._beforeExit()
        before_exit = self._config.get("before_exit")
        if before_exit:
            orig_buf_nr = self._getInstance().getOriginalPos()[2].number
            line, col = self._getInstance().getOriginalCursor()
            try:
                before_exit(orig_buf_nr, [line, col+1], self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(before_exit), err))

        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _afterExit(self):
        super(AnyExplManager, self)._afterExit()
        after_exit = self._config.get("after_exit")
        if after_exit:
            try:
                after_exit(self._arguments)
            except vim.error as err:
                raise Exception("Error occurred in user defined %s: %s" % (str(after_exit), err))

    def _previewResult(self, preview):
        if not self._needPreview(preview):
            return

        cur_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'BufLeave,WinEnter,BufEnter'
        try:
            preview = self._config.get("preview")
            if preview:
                orig_buf_nr = self._getInstance().getOriginalPos()[2].number
                line, col = self._getInstance().getOriginalCursor()
                try:
                    preview(orig_buf_nr, [line, col+1], self._arguments)
                except vim.error as err:
                    raise Exception("Error occurred in user defined %s: %s" % (str(preview), err))
        finally:
            vim.current.tabpage, vim.current.window, vim.current.buffer = cur_pos
            vim.options['eventignore'] = saved_eventignore

    def _supportsRefine(self):
        return bool(int(self._config.get("supports_refine", False)))

    def startExplorer(self, win_pos, *args, **kwargs):
        self._arguments = kwargs["arguments"]
        super(AnyExplManager, self).startExplorer(win_pos, *args, **kwargs)


class OptionalAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(OptionalAction, self).__init__(option_strings=option_strings,
                                             dest=dest,
                                             nargs=nargs,
                                             const=const,
                                             default=default,
                                             type=type,
                                             choices=choices,
                                             required=required,
                                             help=help,
                                             metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, [] if values is None else [values])


class AnyHub(object):
    def __init__(self):
        self._managers = {}

    def _add_argument(self, parser, arg_list, positional_args):
        """
        Args:
            parser:
                an argparse object
            arg_list:
                a list of argument definition, e.g.,
                [
                    # "--big" and "--small" are mutually exclusive
                    [
                        {"name": ["--big"], "nargs": 0, "help": "big help"},
                        {"name": ["--small"], "nargs": 0, "help": "small help"},
                    ],
                    {"name": ["--tabpage"], "nargs": 1},
                ]
            positional_args[output]:
                a list of positional arguments
        """
        for arg in arg_list:
            if isinstance(arg, list):
                group = parser.add_mutually_exclusive_group()
                self._add_argument(group, arg, positional_args)
            else:
                arg_name = arg["name"][0]
                if arg_name.startswith("-"):
                    metavar = arg_name.lstrip("-").upper().replace("-", "_")
                    add_argument = partial(parser.add_argument, metavar=metavar, dest=arg_name)
                else:
                    positional_args.append(arg["name"][0])
                    add_argument = partial(parser.add_argument)

                try:
                    nargs = int(arg["nargs"])
                except: # ? * +
                    nargs = arg["nargs"]

                if nargs == 0:
                    add_argument(*arg["name"], action='store_const', const=[],
                                 default=argparse.SUPPRESS, help=arg.get("help", ""))
                elif nargs == "?":
                    add_argument(*arg["name"], action=OptionalAction, nargs=nargs,
                                 default=argparse.SUPPRESS, help=arg.get("help", ""))
                else:
                    add_argument(*arg["name"], nargs=nargs, default=argparse.SUPPRESS,
                                 help=arg.get("help", ""))

    def _arg_line_to_args(self, line):
        """
        e.g.,
        `Leaderf file --foo hello --bar="hello world" --aaa "111 222" bbb` can be converted into
        ['Leaderf', 'file', '--foo', 'hello', '--bar', 'hello world', '--aaa', '111 222', 'bbb']
        """
        args = []
        start = i = 0
        end = len(line)
        in_quotes = False
        while i < end:
            if not in_quotes and line[i] in " =":
                if start < i:
                    args.append(line[start:i])
                start = i + 1
            elif not in_quotes and line[i] in ('"', "'"):
                left_quote = line[i]
                if i + 1 < end and left_quote in line[i+1:]:
                    start = i + 1
                    in_quotes = True
            elif in_quotes and line[i] == left_quote:
                args.append(line[start:i])
                in_quotes = False
                start = i + 1

            i += 1

        if start < end:
            args.append(line[start:])

        return args

    def start(self, category, arg_line, *args, **kwargs):
        parser = argparse.ArgumentParser(prog="Leaderf " + category)
        positional_args = []
        if lfEval("has_key(g:Lf_Extensions, '%s')" % category) == '1':
            if category not in self._managers:
                # In python3, string in g:Lf_Extensions is converted to bytes by vim.bindeval(),
                # so using vim.eval() instead.
                # But Funcref object will be converted to None by vim.eval()
                config = lfEval("g:Lf_Extensions['%s']" % category)
                for k in config:
                    if config[k] is None:
                        config[k] = vim.bindeval("g:Lf_Extensions['%s']['%s']" % (category, k))

                if "source" in config and isinstance(config["source"], dict) \
                        and config["source"].get("command", "") is None:
                    config["source"]["command"] = vim.bindeval("g:Lf_Extensions['%s']['source']['command']" % category)
                self._managers[category] = AnyExplManager(category, config)

            manager = self._managers[category]

            arg_def = lfEval("get(g:Lf_Extensions['%s'], 'arguments', [])" % category)
            self._add_argument(parser, arg_def, positional_args)
        else:
            if category == "file":
                from .fileExpl import fileExplManager
                manager = fileExplManager
            elif category == "buffer":
                from .bufExpl import bufExplManager
                manager = bufExplManager
            elif category == "mru":
                from .mruExpl import mruExplManager
                manager = mruExplManager
                kwargs["cb_name"] = vim.current.buffer.name
            elif category == "tag":
                from .tagExpl import tagExplManager
                manager = tagExplManager
            elif category == "bufTag":
                from .bufTagExpl import bufTagExplManager
                manager = bufTagExplManager
            elif category == "function":
                from .functionExpl import functionExplManager
                manager = functionExplManager
            elif category == "line":
                from .lineExpl import lineExplManager
                manager = lineExplManager
            elif category == "cmdHistory":
                from .historyExpl import historyExplManager
                manager = historyExplManager
                kwargs["history"] = "cmd"
            elif category == "searchHistory":
                from .historyExpl import historyExplManager
                manager = historyExplManager
                kwargs["history"] = "search"
            elif category == "help":
                from .helpExpl import helpExplManager
                manager = helpExplManager
            elif category == "colorscheme":
                from .colorschemeExpl import colorschemeExplManager
                manager = colorschemeExplManager
            else:
                raise Exception("Unrecognized argument %s!" % category)

            self._add_argument(parser, lfEval("g:Lf_Arguments")[category], positional_args)

        self._add_argument(parser, lfEval("g:Lf_CommonArguments"), positional_args)

        arg_list = self._arg_line_to_args(arg_line)

        try:
            # do not produce an error when extra arguments are present
            arguments = vars(parser.parse_known_args(arg_list[1:])[0])
        except SystemExit:
            return

        positions = {"--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"}
        win_pos = "--" + lfEval("g:Lf_WindowPosition")
        for i in arguments:
            if i in positions:
                win_pos = i
                break

        if "--cword" in arguments:
            kwargs["pattern"] = lfEval("expand('<cword>')")

        kwargs["arguments"] = arguments
        kwargs["positional_args"] = positional_args

        manager.startExplorer(win_pos[2:], *args, **kwargs)


#*****************************************************
# anyHub is a singleton
#*****************************************************
anyHub = AnyHub()

__all__ = ['anyHub']

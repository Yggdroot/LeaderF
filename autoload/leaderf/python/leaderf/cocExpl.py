#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import urllib.parse
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *


def workingDirectory(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        if self._getExplorer()._cmd_work_dir == lfGetCwd():
            return func(self, *args, **kwargs)

        # https://github.com/neovim/neovim/issues/8336
        if lfEval("has('nvim')") == '1':
            chdir = vim.chdir
        else:
            chdir = os.chdir
        orig_cwd = lfGetCwd()
        chdir(self._getExplorer()._cmd_work_dir)
        try:
            return func(self, *args, **kwargs)
        finally:
            chdir(orig_cwd)

    return deco

#*****************************************************
# CocExplorer
#*****************************************************
class CocExplorer(Explorer):
    def __init__(self):
        self._pattern_regex = []
        self._cmd_work_dir = ""

    def getContent(self, *args, **kwargs):
        self._cmd_work_dir = lfGetCwd()
        commands = lfEval("leaderf#Coc#Commands()")
        return [list(item)[0] for item in commands]

    def getStlCategory(self):
        return 'Coc'

    def getStlCurDir(self):
        return escQuote(lfEncode(self._cmd_work_dir))

    def supportsNameOnly(self):
        return False

    def getPatternRegex(self):
        return self._pattern_regex

    def getFileLine(self, file_name, line_num, file_contents):
        if lfEval("bufloaded('%s')" % escQuote(file_name)) == '1':
            return lfEval("getbufline('{}', {}, {})[0]".format(file_name, line_num, line_num))
        else:
            if file_name not in file_contents:
                with lfOpen(file_name, 'r', errors='ignore') as f:
                    file_contents[file_name] = f.readlines()

            return file_contents[file_name][line_num-1].rstrip("\r\n")

    def generateContent(self, items):
        self._pattern_regex = []
        content = []
        file_contents = {}
        for item in items:
            file_path = lfRelpath(urllib.parse.unquote(item["uri"][7:]))
            line_num = int(item["range"]["start"]["line"])
            col_num = int(item["range"]["start"]["character"])
            line = self.getFileLine(file_path, line_num + 1, file_contents)
            if len(self._pattern_regex) == 0:
                end_line_num = int(item["range"]["end"]["line"])
                end_col_num = int(item["range"]["end"]["character"])
                if end_line_num == line_num:
                    self._pattern_regex.append(line[col_num: end_col_num])

            content.append("{}:{}:{}:{}".format(file_path, line_num+1, col_num+1, line))

        return content


class DefinitionsExplorer(CocExplorer):
    def getContent(self, *args, **kwargs):
        try:
            self._cmd_work_dir = lfGetCwd()
            definitions = lfEval("CocAction('definitions')")
            return self.generateContent(definitions)
        except vim.error as e:
            lfPrintError(str(e).split('\n')[-1])
            return None

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return 'definitions'


class DeclarationsExplorer(CocExplorer):
    def getContent(self, *args, **kwargs):
        try:
            self._cmd_work_dir = lfGetCwd()
            declarations = lfEval("CocAction('declarations')")
            return self.generateContent(declarations)
        except vim.error as e:
            lfPrintError(str(e).split('\n')[-1])
            return None

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return 'declarations'


class ImplementationsExplorer(CocExplorer):
    def getContent(self, *args, **kwargs):
        try:
            self._cmd_work_dir = lfGetCwd()
            implementations = lfEval("CocAction('implementations')")
            return self.generateContent(implementations)
        except vim.error as e:
            lfPrintError(str(e).split('\n')[-1])
            return None

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return 'implementations'


class TypeDefinitionsExplorer(CocExplorer):
    def getContent(self, *args, **kwargs):
        try:
            self._cmd_work_dir = lfGetCwd()
            typeDefinitions = lfEval("CocAction('typeDefinitions')")
            return self.generateContent(typeDefinitions)
        except vim.error as e:
            lfPrintError(str(e).split('\n')[-1])
            return None

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return 'typeDefinitions'


class ReferencesExplorer(CocExplorer):
    def getContent(self, *args, **kwargs):
        try:
            self._cmd_work_dir = lfGetCwd()

            arguments_dict = kwargs.get("arguments", {})
            if "--exclude-declaration" in arguments_dict:
                references = lfEval("CocAction('references', 1)")
            else:
                references = lfEval("CocAction('references')")

            return self.generateContent(references)
        except vim.error as e:
            lfPrintError(str(e).split('\n')[-1])
            return None

    def supportsNameOnly(self):
        return True

    def getStlCategory(self):
        return 'references'


#*****************************************************
# CocExplManager
#*****************************************************
class CocExplManager(Manager):
    def __init__(self):
        super(CocExplManager, self).__init__()
        self._managers = {}

    def _getExplClass(self):
        return CocExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Coc#Maps({})".format(id(self)))

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" p : preview the file')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" <ESC> : close the preview window or quit')
        help.append('" ---------------------------------------------------------')
        return help

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        return line

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        return 0

    def createManager(self, subcommand):
        if subcommand == "definitions":
            return DefinitionsExplManager()
        elif subcommand == "declarations":
            return DeclarationsExplManager()
        elif subcommand == "implementations":
            return ImplementationsExplManager()
        elif subcommand == "typeDefinitions":
            return TypeDefinitionsExplManager()
        elif subcommand == "references":
            return ReferencesExplManager()
        else:
            return super(CocExplManager, self)

    def getExplManager(self, subcommand):
        if subcommand not in self._managers:
            self._managers[subcommand] = self.createManager(subcommand)
        return self._managers[subcommand]

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" in arguments_dict:
            self._arguments.update(arguments_dict)
        else:
            self.setArguments(arguments_dict)

        arg_list = self._arguments.get("arg_line", 'coc').split()
        arg_list = [item for item in arg_list if not item.startswith('-')]
        if len(arg_list) == 1:
            subcommand = ""
        else:
            subcommand = arg_list[1]
        self.getExplManager(subcommand).startExplorer(win_pos, *args, **kwargs)

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        cmd = line
        try:
            lfCmd(cmd)
        except vim.error:
            lfPrintTraceback()

    def getSource(self, line):
        commands = lfEval("leaderf#Coc#Commands()")
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

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        self.setOptionsForCursor()

        if lfEval("has('nvim')") == '1':
            lfCmd("""call win_execute({}, "call nvim_buf_set_lines(0, 0, -1, v:false, ['{}'])")"""
                  .format(self._preview_winid, escQuote(source)))
        else:
            lfCmd("noautocmd call popup_settext({}, '{}')"
                  .format(self._preview_winid, escQuote(source)))

    def _beforeExit(self):
        super(CocExplManager, self)._beforeExit()
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()


class CommonExplManager(CocExplManager):
    def _afterEnter(self):
        super(CocExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgFileName'', ''^.\{-}\ze\:\d\+:'', 10)')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgLineNumber'', ''^.\{-}\zs:\d\+:'', 10)')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd(r"""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgColumnNumber'', ''^.\{-}:\d\+:\zs\d\+:'', 10)')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            try:
                for i in self._getExplorer().getPatternRegex():
                    i = r'\<{}\>'.format(i)
                    lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_rgHighlight', '%s', 9)")"""
                            % (self._getInstance().getPopupWinId(), re.sub(r'\\(?!")', r'\\\\', escQuote(i))))
                    id = int(lfEval("matchid"))
                    self._match_ids.append(id)
            except vim.error:
                pass
        else:
            id = int(lfEval(r"matchadd('Lf_hl_rgFileName', '^.\{-}\ze\:\d\+:', 10)"))
            self._match_ids.append(id)
            id = int(lfEval(r"matchadd('Lf_hl_rgLineNumber', '^.\{-}\zs:\d\+:', 10)"))
            self._match_ids.append(id)
            id = int(lfEval(r"matchadd('Lf_hl_rgColumnNumber', '^.\{-}:\d\+:\zs\d\+:', 10)"))
            self._match_ids.append(id)

            try:
                for i in self._getExplorer().getPatternRegex():
                    i = r'\<{}\>'.format(i)
                    id = int(lfEval("matchadd('Lf_hl_rgHighlight', '%s', 9)" % escQuote(i)))
                    self._match_ids.append(id)
            except vim.error:
                pass

    def setStlMode(self, mode):
        if mode == "FullPath":
            mode = "WholeLine"
        elif mode == "NameOnly":
            mode = "Contents"
        super(CocExplManager, self).setStlMode(mode)

    def _getFileInfo(self, args):
        line = args[0]

        m = re.match(r'^(.+?):(\d+):(\d+):', line)
        if m is None:
            return (None, None, None)

        file, line_num, col_num = m.group(1, 2, 3)
        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
        i = 1
        while not os.path.exists(lfDecode(file)):
            m = re.match(r'^(.+?(?::\d+.*?){%d}):(\d+):(\d+):' % i, line)
            i += 1
            file, line_num, col_num = m.group(1, 2, 3)
            if not os.path.isabs(file):
                file = os.path.join(self._getInstance().getCwd(), lfDecode(file))

        file = os.path.normpath(lfEncode(file))

        return (file, line_num, col_num)

    @workingDirectory
    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        file, line_num, col_num = self._getFileInfo(args)
        if file is None:
            return

        try:
            is_shown = False
            if kwargs.get("mode", '') == 't':
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' \
                        and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    winid = int(lfEval("bufwinid('%s')" % escQuote(file)))
                    start_line = int(lfEval("line('w0', %d)" % winid))
                    end_line = int(lfEval("line('w$', %d)" % winid))
                    lfDrop('tab', file, line_num)
                    if start_line <= int(line_num) <= end_line:
                        is_shown = True
                else:
                    lfCmd("tabe %s | %s" % (escSpecial(file), line_num))
            else:
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' \
                        and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    winid = int(lfEval("bufwinid('%s')" % escQuote(file)))
                    start_line = int(lfEval("line('w0', %d)" % winid))
                    end_line = int(lfEval("line('w$', %d)" % winid))
                    lfDrop('', file, line_num)
                    if start_line <= int(line_num) <= end_line:
                        is_shown = True
                else:
                    lfCmd("hide edit +%s %s" % (line_num, escSpecial(file)))

            lfCmd("norm! ^zv")
            lfCmd("norm! {}|".format(col_num))

            if is_shown == False:
                lfCmd("norm! zz")

            if "preview" not in kwargs:
                lfCmd("setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!")

            if vim.current.window not in self._cursorline_dict:
                self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

            lfCmd("setlocal cursorline")
        except vim.error as e: # E37
            if 'E325' not in str(e).split(':'):
                lfPrintTraceback()

    def _highlightInPreview(self):
        if lfEval("has('nvim')") != '1':
            try:
                for i in self._getExplorer().getPatternRegex():
                    i = r'\<{}\>'.format(i)
                    lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_rgHighlight', '%s', 9)")"""
                            % (self._preview_winid, re.sub(r'\\(?!")', r'\\\\', escQuote(i))))
                    id = int(lfEval("matchid"))
                    self._match_ids.append(id)
            except vim.error:
                pass
        else:
            cur_winid = lfEval("win_getid()")
            lfCmd("noautocmd call win_gotoid(%d)" % self._preview_winid)
            if lfEval("win_getid()") != cur_winid:
                try:
                    for i in self._getExplorer().getPatternRegex():
                        i = r'\<{}\>'.format(i)
                        id = int(lfEval("matchadd('Lf_hl_rgHighlight', '%s', 9)" % escQuote(i)))
                        self._match_ids.append(id)
                except vim.error:
                    pass
                lfCmd("noautocmd call win_gotoid(%s)" % cur_winid)

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0 or args[0] == '':
            return

        file, line_num, col_num = self._getFileInfo(args)
        if file is None:
            return

        if lfEval("bufloaded('%s')" % escQuote(file)) == '1':
            source = int(lfEval("bufadd('%s')" % escQuote(file)))
        else:
            source = file

        self._createPopupPreview("", source, line_num)
        self._highlightInPreview()

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if mode == 0:
            return line
        elif mode == 1:
            return line.split(":", 3)[-1]
        else:
            return line.split(":", 1)[0]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if mode == 0 or mode == 2:
            return 0
        else:
            file_path, line_num, column, content = line.split(":", 3)
            return lfBytesLen(file_path + line_num + column) + 3

    def _createPreviewWindow(self, config, source, line_num, jump_cmd):
        return super(CocExplManager, self)._createPreviewWindow(config, source, line_num, jump_cmd)

    def _useExistingWindow(self, title, source, line_num, jump_cmd):
        return super(CocExplManager, self)._useExistingWindow(title, source, line_num, jump_cmd)

    def startExplorer(self, win_pos, *args, **kwargs):
        return super(CocExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def autoJump(self, content):
        if "--auto-jump" in self._arguments and isinstance(content, list) and len(content) == 1:
            mode = self._arguments["--auto-jump"][0] if len(self._arguments["--auto-jump"]) else ""
            self._accept(content[0], mode)
            return True

        return False


class DefinitionsExplManager(CommonExplManager):
    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = DefinitionsExplorer()
        return self._explorer


class DeclarationsExplManager(CommonExplManager):
    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = DeclarationsExplorer()
        return self._explorer


class ImplementationsExplManager(CommonExplManager):
    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = ImplementationsExplorer()
        return self._explorer


class TypeDefinitionsExplManager(CommonExplManager):
    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = TypeDefinitionsExplorer()
        return self._explorer


class ReferencesExplManager(CommonExplManager):
    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = ReferencesExplorer()
        return self._explorer


#*****************************************************
# cocExplManager is a singleton
#*****************************************************
cocExplManager = CocExplManager()

__all__ = ['cocExplManager']

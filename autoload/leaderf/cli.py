#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
from datetime import datetime
from functools import wraps
from leaderf.utils import *


def ctrlCursor(func):
    @wraps(func)
    def deco(*args, **kwargs):
        vim.command("let g:lf_old_gcr = &gcr")
        vim.command("let g:lf_old_t_ve = &t_ve")
        vim.command("set gcr=a:invisible")
        vim.command("set t_ve=")
        try:
            for i in func(*args, **kwargs):
                yield i
        finally:
            try:
                vim.command("let &gcr = g:lf_old_gcr")
                vim.command("let &t_ve = g:lf_old_t_ve")
            except: # there is a bug here, fixed by Patch 7.4.084.
                try:
                    vim.command("let &gcr = g:lf_old_gcr")
                    vim.command("let &t_ve = g:lf_old_t_ve")
                except:
                    pass
    return deco


#*****************************************************
# LfCli
#*****************************************************
class LfCli(object):
    def __init__(self):
        self._cmdline = []
        self._pattern = ''
        self._cursor_pos = 0
        self._start_time = datetime.now()
        self._idle = False
        self._blinkon = True
        self._cmd_map = vim.eval("g:Lf_CommandMap")
        self._refine = False
        self._delimiter = vim.eval("g:Lf_DelimiterChar")
        self._supports_nameonly = False
        self._setDefaultMode()

    def _setDefaultMode(self):
        mode = int(vim.eval("g:Lf_DefaultMode"))
        if mode == 0:       # nameOnly mode
            self._is_fuzzy = True
            self._is_full_path = False
        elif mode == 1:     # fullPath mode
            self._is_fuzzy = True
            self._is_full_path = True
        else:               # regex mode
            self._is_fuzzy = False
            self._is_full_path = True

    def _insert(self, ch):
        self._cmdline.insert(self._cursor_pos, ch)
        self._cursor_pos += 1

    def _paste(self):
        for ch in vim.eval("@*"):
            self._insert(ch)

    def _backspace(self):
        if self._cursor_pos > 0:
            self._cmdline.pop(self._cursor_pos-1)
            self._cursor_pos -= 1

    def _delete(self):
        if self._cursor_pos < len(self._cmdline):
            self._cmdline.pop(self._cursor_pos)
        else:
            self._backspace()

    def _clearLeft(self):
        self._cmdline[0:self._cursor_pos] = []
        self._cursor_pos = 0

    def _clearWord(self):
        for i in range(self._cursor_pos):
            if self._cmdline[self._cursor_pos - i - 1] == ' ':
                self._cmdline = self._cmdline[0:self._cursor_pos - i - 1]
                self._cursor_pos = self._cursor_pos - i - 1
                return
        self._clearLeft()

    def clear(self):
        self._cmdline[:] = []
        self._cursor_pos = 0

    def _toLeft(self):
        if self._cursor_pos > 0:
            self._cursor_pos -= 1

    def _toRight(self):
        if self._cursor_pos < len(self._cmdline):
            self._cursor_pos += 1

    def _toBegin(self):
        self._cursor_pos = 0

    def _toEnd(self):
        self._cursor_pos = len(self._cmdline)

    def _buildPrompt(self):
        delta_time = datetime.now() - self._start_time
        delta_ms = delta_time.microseconds + (delta_time.seconds +
                   delta_time.days * 24 * 3600) * 10**6
        if self._idle and delta_ms < 500000: # 500ms
            return
        else:
            if self._blinkon:
                vim.command("hi! default link Lf_hl_cursor Cursor")
            else:
                vim.command("hi! default link Lf_hl_cursor NONE")
            self._start_time = datetime.now()
            self._blinkon = not self._blinkon

        if self._is_fuzzy:
            if self._is_full_path:
                vim.command("echohl Constant | redraw | echon '>F> ' |"
                            "echohl NONE")
            else:
                vim.command("echohl Constant | redraw | echon '>>> ' |"
                            "echohl NONE")
        else:
            vim.command("echohl Constant | redraw | echon 'R>> ' |"
                        "echohl NONE")

        vim.command("echohl Normal | echon '%s' | echohl NONE" %
                    escQuote(''.join(self._cmdline[:self._cursor_pos])))
        if self._cursor_pos < len(self._cmdline):
            vim.command("echohl Lf_hl_cursor | echon '%s' | echohl NONE" %
                        escQuote(''.join(self._cmdline[self._cursor_pos])))
            vim.command("echohl Normal | echon '%s' | echohl NONE" %
                        escQuote(''.join(self._cmdline[self._cursor_pos+1:])))
        else:
            vim.command("echohl Lf_hl_cursor | echon ' ' | echohl NONE")

    def _buildPattern(self):
        if self._is_fuzzy:
            # supports refinement only in nameOnly mode
            if (self._supports_nameonly and not self._is_full_path and
                    self._delimiter in self._cmdline):
                self._refine = True
                idx = self._cmdline.index(self._delimiter)
                self._pattern = (''.join(self._cmdline[:idx]),
                                 ''.join(self._cmdline[idx+1:]))
                if self._pattern == ('', ''):
                    self._pattern = None
            else:
                self._refine = False
                self._pattern = ''.join(self._cmdline)
        else:
            self._pattern = ''.join(self._cmdline)

    def _join(self, cmdline):
        if not cmdline:
            return ''
        cmd = ['%s\[^%s]\{-}' % (c, c) for c in cmdline[0:-1]]
        cmd.append(cmdline[-1])
        regex = ''.join(cmd)
        return regex

    def highlightMatches(self):
        vim.command("silent! syn clear Lf_hl_match")
        vim.command("silent! syn clear Lf_hl_match_1")
        if not self._cmdline:
            return
        if self._is_fuzzy:
            cmdline = [r'\/' if c == '/' else r'\\' if c == '\\' else c
                       for c in self._cmdline] # \/ for syn match
            if self._is_full_path:
                regex = '\c\V' + self._join(cmdline)
                vim.command("syn match Lf_hl_match display /%s/ containedin="
                            "Lf_hl_nonHelp, Lf_hl_dirname, Lf_hl_filename contained" % regex)
            else:
                if self._refine:
                    idx = self._cmdline.index(self._delimiter)
                    regex = ('\c\V' + self._join(cmdline[:idx]),
                             '\c\V' + self._join(cmdline[idx+1:]))
                    if regex[0] == '\c\V' and regex[1] == '\c\V':
                        pass
                    elif regex[0] == '\c\V':
                        vim.command("syn match Lf_hl_match display /%s/ "
                                    "containedin=Lf_hl_dirname, Lf_hl_filename "
                                    "contained" % regex[1])
                    elif regex[1] == '\c\V':
                        vim.command("syn match Lf_hl_match display /%s/ "
                                    "containedin=Lf_hl_filename contained" %
                                    regex[0])
                    else:
                        vim.command("syn match Lf_hl_match display /%s/ "
                                    "containedin=Lf_hl_filename contained" %
                                    regex[0])
                        vim.command("syn match Lf_hl_match_1 display "
                                    "/%s\(\.\*\[\/]\)\@=/ containedin="
                                    "Lf_hl_dirname contained" % regex[1])
                else:
                    regex = '\c\V' + self._join(cmdline)
                    vim.command("syn match Lf_hl_match display /%s/ "
                                "containedin=Lf_hl_filename contained" % regex)
        else:
            if self._pattern:
                # e.g. if self._pattern is 'aa\', change it to 'aa\\';
                # else keep it as it is
                # syn match Lf_hl_match 'aa\' will raise an error without this line.
                regex = (self._pattern + '\\') if len(re.search(r'\\*$',
                        self._pattern).group(0)) % 2 == 1 else self._pattern
                # also for syn match, because we use ' to surround the syn-pattern
                regex = regex.replace("'", r"\'")
                # e.g. syn match Lf_hl_match '[' will raise an error,
                # change unmatched '[' to '\['
                if '[' in regex:
                    tmpRe = [i for i in regex]
                    i = 0
                    lenRegex = len(regex)
                    while i < lenRegex:
                        if tmpRe[i] == '\\':
                            i += 2
                        elif tmpRe[i] == '[':
                            j = i + 1
                            while j < lenRegex:
                                if tmpRe[j] == ']' and tmpRe[j-1] != '[':
                                    i = j + 1
                                    break
                                elif tmpRe[j] == '\\':
                                    j += 2
                                else:
                                    j += 1
                            else:
                                tmpRe[i] = r'\['
                                i += 1
                        else:
                            i += 1
                    regex = ''.join(tmpRe)

                if vim.eval("&ignorecase") == '1':
                    regex = r'\c' + regex

                try:
                    if int(vim.eval("v:version")) > 703:
                        vim.command("syn match Lf_hl_match '%s' containedin="
                                    "Lf_hl_dirname, Lf_hl_filename contained" %
                                    regex)
                    else:
                        regex = re.sub(r'\\', r'\\\\', regex)
                        vim.eval("""g:LfNoErrMsgCmd("syn match Lf_hl_match '%s' """
                                 """containedin=Lf_hl_dirname, Lf_hl_filename contained")""" % regex)
                except vim.error:
                    pass

    def hideCursor(self):
        self._blinkon = False
        self._buildPrompt()

    def setNameOnlyFeature(self, state):
        self._supports_nameonly = state

    @property
    def isPrefix(self): #assume that there are no \%23l, \%23c, \%23v, \%...
        pos = self._cursor_pos
        regex = self.pattern
        if pos > 1:
            if regex[pos - 2] != '\\' and (regex[pos - 1].isalnum() or
                    regex[pos - 1] in r'`$%*(-_+[\;:,. /?'):
                if regex[pos - 2] == '_':
                    if pos > 2 and regex[pos - 3] == '\\': #\_x
                        return False
                    else:
                        return True
                if regex.endswith(r'\zs') or regex.endswith(r'\ze'):
                    return False
                return True
        return False

    @property
    def pattern(self):
        return self._pattern

    @property
    def isFullPath(self):
        return self._is_full_path

    @property
    def isRefinement(self):
        return self._refine

    @property
    def isFuzzy(self):
        return self._is_fuzzy

    @ctrlCursor
    def input(self):
        try:
            self._blinkon = True
            while 1:
                self._buildPrompt()
                self._idle = False

                vim.command("let nr = getchar(%s)"
                            % vim.eval("g:Lf_CursorBlink == 1 ? 0 : ''"))
                vim.command("sleep 1m")
                vim.command("let str = strtrans(nr)")
                vim.command("let ch = !type(nr) ? nr2char(nr) : nr")
                # https://groups.google.com/forum/#!topic/vim_dev/gg-l-kaCz_M
                # '<80><fc>^B' is <Shift>, '<80><fc>^D' is <Ctrl>,
                # '<80><fc>^H' is <Alt>, '<80><fc>^L' is <Ctrl + Alt>
                if vim.eval("!type(nr) && nr == 0") == '1' or vim.eval(
                        "str == '<80><fc>^B' || str == '<80><fc>^D' || "
                        "str == '<80><fc>^H' || str == '<80><fc>^L' || "
                        "str == '<80><fc>$' || str == '<80><fc>\"' || "
                        "str == '<80><fc>('") == '1':
                    self._idle = True
                    continue
                else:
                    self._blinkon = True

                if vim.eval("!type(nr) && nr >= 0x20") == '1':
                    self._insert(vim.eval("ch"))
                    self._buildPattern()
                    yield '<Update>'
                else:
                    cmd = ''
                    for (key, value) in self._cmd_map.items():
                        for i in value:
                            if vim.eval('ch ==# "\%s"' % i) == '1':
                                cmd = key
                                break
                        if cmd != '':
                            break
                    if equal(cmd, '<CR>'):
                        yield '<CR>'
                    elif equal(cmd, '<2-LeftMouse>'):
                        yield '<2-LeftMouse>'
                    elif equal(cmd, '<Esc>'):
                        yield '<Esc>'
                    elif equal(cmd, '<C-F>'):
                        if self._supports_nameonly:
                            self._is_fuzzy = True
                            self._is_full_path = not self._is_full_path
                            self._buildPattern()
                            yield '<Mode>'
                    elif equal(cmd, '<C-R>'):
                        self._is_fuzzy = not self._is_fuzzy
                        self._buildPattern()
                        yield '<Mode>'
                    elif equal(cmd, '<BS>'):
                        self._backspace()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-U>'):
                        self._clearLeft()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-W>'):
                        self._clearWord()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<Del>'):
                        self._delete()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-V>'):
                        self._paste()
                        self._buildPattern()
                        yield '<Update>'
                    elif equal(cmd, '<Home>'):
                        self._toBegin()
                    elif equal(cmd, '<End>'):
                        self._toEnd()
                    elif equal(cmd, '<Left>'):
                        self._toLeft()
                    elif equal(cmd, '<Right>'):
                        self._toRight()
                    elif equal(cmd, '<C-C>'):
                        yield '<Quit>'
                    else:
                        yield cmd
        except KeyboardInterrupt: # <C-C>
            if int(vim.eval("v:version")) > 703:
                yield '<Quit>'
            else:
                pass


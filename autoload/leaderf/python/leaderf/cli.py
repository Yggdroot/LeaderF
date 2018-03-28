#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import time
from datetime import datetime
from functools import wraps
from .utils import *


def cursorController(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if lfEval("exists('g:lf_gcr_stack')") == '0':
            lfCmd("let g:lf_gcr_stack = []")
        lfCmd("call add(g:lf_gcr_stack, &gcr)")
        lfCmd("set gcr=a:invisible")
        if lfEval("exists('g:lf_t_ve_stack')") == '0':
            lfCmd("let g:lf_t_ve_stack = []")
        lfCmd("call add(g:lf_t_ve_stack, &t_ve)")
        lfCmd("set t_ve=")
        lfCmd("let g:Lf_ttimeoutlen_orig = &ttimeoutlen")
        lfCmd("set ttimeoutlen=0")
        try:
            for i in func(*args, **kwargs):
                yield i
        finally:
            lfCmd("let &ttimeoutlen = g:Lf_ttimeoutlen_orig")
            lfCmd("set gcr&")
            lfCmd("let &gcr = remove(g:lf_gcr_stack, -1)")
            lfCmd("set t_ve&")
            lfCmd("let &t_ve = remove(g:lf_t_ve_stack, -1)")
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
        self._cmd_map = lfEval("g:Lf_CommandMap")
        self._refine = False
        self._delimiter = lfEval("g:Lf_DelimiterChar")
        self._supports_nameonly = False
        self._supports_refine = False
        self._setDefaultMode()

    def _setDefaultMode(self):
        mode = lfEval("g:Lf_DefaultMode")
        if mode == 'NameOnly':       # nameOnly mode
            self._is_fuzzy = True
            self._is_full_path = False
        elif mode == 'FullPath':     # fullPath mode
            self._is_fuzzy = True
            self._is_full_path = True
        elif mode == 'Fuzzy':     # fuzzy mode
            self._is_fuzzy = True
            self._is_full_path = False
        else:               # regex mode
            self._is_fuzzy = False
            self._is_full_path = True

    def setCurrentMode(self, mode):
        if mode == 'NameOnly':       # nameOnly mode
            self._is_fuzzy = True
            self._is_full_path = False
        elif mode == 'FullPath':     # fullPath mode
            self._is_fuzzy = True
            self._is_full_path = True
        elif mode == 'Fuzzy':     # fuzzy mode
            self._is_fuzzy = True
            self._is_full_path = False
        else:               # regex mode
            self._is_fuzzy = False

    def _insert(self, ch):
        self._cmdline.insert(self._cursor_pos, ch)
        self._cursor_pos += 1

    def _paste(self):
        for ch in lfEval("@*"):
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

    def clear(self):
        self._cmdline[:] = []
        self._cursor_pos = 0
        self._pattern = ''

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

    def setPattern(self, pattern):
        if pattern:
            self.clear()
        for ch in pattern:
            self._insert(ch)
        self._buildPattern()

    def _buildPrompt(self):
        delta_time = datetime.now() - self._start_time
        delta_ms = delta_time.microseconds + (delta_time.seconds +
                   delta_time.days * 24 * 3600) * 10**6
        if self._idle and delta_ms < 500000: # 500ms
            return
        else:
            if self._blinkon:
                lfCmd("hi! default link Lf_hl_cursor Cursor")
            else:
                lfCmd("hi! default link Lf_hl_cursor NONE")
            if lfEval("g:Lf_CursorBlink") == '1':
                self._start_time = datetime.now()
                self._blinkon = not self._blinkon

        if self._is_fuzzy:
            if self._is_full_path:
                lfCmd("echohl Constant | echon '>F> ' | echohl NONE")
            else:
                lfCmd("echohl Constant | echon '>>> ' | echohl NONE")
        else:
            lfCmd("echohl Constant | echon 'R>> ' | echohl NONE")

        lfCmd("echohl Normal | echon '%s' | echohl NONE" %
              escQuote(''.join(self._cmdline[:self._cursor_pos])))
        if self._cursor_pos < len(self._cmdline):
            lfCmd("echohl Lf_hl_cursor | echon '%s' | echohl NONE" %
                  escQuote(''.join(self._cmdline[self._cursor_pos])))
            lfCmd("echohl Normal | echon '%s' | echohl NONE" %
                  escQuote(''.join(self._cmdline[self._cursor_pos+1:])))
        else:
            lfCmd("echohl Lf_hl_cursor | echon ' ' | echohl NONE")
        lfCmd("redraw")

    def _buildPattern(self):
        if self._is_fuzzy:
            # supports refinement only in nameOnly mode
            if (((self._supports_nameonly and not self._is_full_path) or
                    self._supports_refine) and self._delimiter in self._cmdline):
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
        lfCmd("silent! syn clear Lf_hl_match")
        lfCmd("silent! syn clear Lf_hl_match_refine")
        if not self._cmdline:
            return
        if self._is_fuzzy:
            # matchaddpos() is introduced by Patch 7.4.330
            if (lfEval("exists('*matchaddpos')") == '1' and
                    lfEval("g:Lf_HighlightIndividual") == '1'):
                return
            cmdline = [r'\/' if c == '/' else r'\\' if c == '\\' else c
                       for c in self._cmdline] # \/ for syn match
            if self._is_full_path:
                regex = '\c\V' + self._join(cmdline)
                lfCmd("syn match Lf_hl_match display /%s/ containedin="
                      "Lf_hl_nonHelp, Lf_hl_dirname, Lf_hl_filename contained" % regex)
            else:
                if self._refine:
                    idx = self._cmdline.index(self._delimiter)
                    regex = ('\c\V' + self._join(cmdline[:idx]),
                             '\c\V' + self._join(cmdline[idx+1:]))
                    if regex[0] == '\c\V' and regex[1] == '\c\V':
                        pass
                    elif regex[0] == '\c\V':
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_dirname, Lf_hl_filename "
                              "contained" % regex[1])
                    elif regex[1] == '\c\V':
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_filename contained" % regex[0])
                    else:
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_filename contained" % regex[0])
                        lfCmd("syn match Lf_hl_match_refine display "
                              "/%s\(\.\*\[\/]\)\@=/ containedin="
                              "Lf_hl_dirname contained" % regex[1])
                else:
                    regex = '\c\V' + self._join(cmdline)
                    lfCmd("syn match Lf_hl_match display /%s/ "
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

                if lfEval("&ignorecase") == '1':
                    regex = r'\c' + regex

                try:
                    lfCmd("syn match Lf_hl_match '%s' containedin="
                          "Lf_hl_dirname, Lf_hl_filename contained" % regex)
                except vim.error:
                    pass

    def hideCursor(self):
        self._blinkon = False
        self._buildPrompt()

    def setNameOnlyFeature(self, state):
        self._supports_nameonly = state

    def setRefineFeature(self, state):
        self._supports_refine = state

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

    @cursorController
    def input(self, callback):
        try:
            self._blinkon = True
            while 1:
                self._buildPrompt()
                self._idle = False

                if lfEval("g:Lf_CursorBlink") == '1' and callback() == False:
                    time.sleep(0.002)

                if lfEval("g:Lf_CursorBlink") == '1':
                    lfCmd("let nr = getchar(1)")
                    if lfEval("!type(nr) && nr == 0") == '1':
                        self._idle = True
                        continue
                    # https://groups.google.com/forum/#!topic/vim_dev/gg-l-kaCz_M
                    # '<80><fc>^B' is <Shift>, '<80><fc>^D' is <Ctrl>,
                    # '<80><fc>^H' is <Alt>, '<80><fc>^L' is <Ctrl + Alt>
                    elif lfEval("type(nr) != 0") == '1':
                        lfCmd("call getchar(0)")
                        lfCmd("call feedkeys('a') | call getchar()")
                        self._idle = True
                        continue
                    else:
                        lfCmd("let nr = getchar()")
                        lfCmd("let ch = !type(nr) ? nr2char(nr) : nr")
                        self._blinkon = True
                else:
                    lfCmd("let nr = getchar()")
                    lfCmd("let ch = !type(nr) ? nr2char(nr) : nr")

                if lfEval("!type(nr) && nr >= 0x20") == '1':
                    self._insert(lfEval("ch"))
                    self._buildPattern()
                    yield '<Update>'
                else:
                    cmd = ''
                    for (key, value) in self._cmd_map.items():
                        for i in value:
                            if lfEval('ch ==# "\%s"' % i) == '1':
                                cmd = key
                                break
                        if cmd != '':
                            break
                    if equal(cmd, '<CR>'):
                        yield '<CR>'
                    elif equal(cmd, '<2-LeftMouse>'):
                        yield '<2-LeftMouse>'
                    elif equal(cmd, '<Esc>'):
                        yield '<Quit>'
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
                    elif equal(cmd, '<BS>') or equal(cmd, '<C-H>'):
                        self._backspace()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-U>'):
                        self._clearLeft()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<Del>'):
                        self._delete()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-V>') or equal(cmd, '<S-Insert>'):
                        self._paste()
                        self._buildPattern()
                        yield '<Update>'
                    elif equal(cmd, '<Home>') or equal(cmd, '<C-B>'):
                        self._toBegin()
                    elif equal(cmd, '<End>') or equal(cmd, '<C-E>'):
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
            yield '<Quit>'
        except vim.error: # for neovim
            lfCmd("call getchar(0)")
            yield '<Quit>'


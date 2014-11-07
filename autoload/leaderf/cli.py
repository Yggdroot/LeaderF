#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
from datetime import datetime
from functools import wraps
from leaderf.util import *


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
            except: #due to vim's bug, I have to do like this
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
        self._regex = None
        self._cursorPos = 0
        self._startTime = datetime.now()
        self._idle = False
        self._blinkon = True
        self._cmdMap = vim.eval("g:Lf_CommandMap")
        self._isMixed = False
        self._supportFullPath = False
        self._setDefaultMode()

    def _setDefaultMode(self):
        mode = int(vim.eval("g:Lf_DefaultMode"))
        if mode == 0:       # nameOnly mode
            self._isFuzzy = True
            self._fullPath = False
        elif mode == 1:     # fullPath mode
            self._isFuzzy = True
            self._fullPath = True
        else:               # regex mode
            self._isFuzzy = False
            self._fullPath = False

    def _insert(self, ch):
        self._cmdline.insert(self._cursorPos, ch)
        self._cursorPos += 1

    def _paste(self):
        for ch in vim.eval("@*"):
            self._insert(ch)

    def _backspace(self):
        if self._cursorPos > 0:
            self._cmdline.pop(self._cursorPos-1)
            self._cursorPos -= 1

    def _delete(self):
        if self._cursorPos < len(self._cmdline):
            self._cmdline.pop(self._cursorPos)
        else:
            self._backspace()

    def _clearLeft(self):
        self._cmdline[0:self._cursorPos] = []
        self._cursorPos = 0

    def clear(self):
        self._cmdline[:] = []
        self._regex = None
        self._cursorPos = 0

    def _toLeft(self):
        if self._cursorPos > 0:
            self._cursorPos -= 1

    def _toRight(self):
        if self._cursorPos < len(self._cmdline):
            self._cursorPos += 1

    def _toBegin(self):
        self._cursorPos = 0

    def _toEnd(self):
        self._cursorPos = len(self._cmdline)

    def _buildPrompt(self):
        deltaTime = datetime.now() - self._startTime
        deltaMs = deltaTime.microseconds + (deltaTime.seconds + deltaTime.days * 24 * 3600) * 10**6
        if self._idle and deltaMs < 500000: #500ms
            return
        else:
            if self._blinkon:
                vim.command("hi! default link Lf_hl_cursor Cursor")
            else:
                vim.command("hi! default link Lf_hl_cursor NONE")
            self._startTime = datetime.now()
            self._blinkon = not self._blinkon

        if self._isFuzzy:
            if self.isFileNameOnly:
                vim.command("echohl Constant | redraw | echon '>>> ' | echohl NONE")
            else:
                vim.command("echohl Constant | redraw | echon '>F> ' | echohl NONE")
        else:
            vim.command("echohl Constant | redraw | echon 'R>> ' | echohl NONE")

        vim.command("echohl Normal | echon '%s' | echohl NONE" % escQuote(''.join(self._cmdline[:self._cursorPos])))
        if self._cursorPos < len(self._cmdline):
            vim.command("echohl Lf_hl_cursor | echon '%s' | echohl NONE" % escQuote(''.join(self._cmdline[self._cursorPos])))
            vim.command("echohl Normal | echon '%s' | echohl NONE" % escQuote(''.join(self._cmdline[self._cursorPos+1:])))
        else:
            vim.command("echohl Lf_hl_cursor | echon ' ' | echohl NONE")

    def _buildRegex(self):
        if self._cmdline:
            if self._isFuzzy:
                if os.name == 'nt':
                    # treat '/' and '\' the same
                    func = lambda c: r'[\\/].*?' if c == '\\' or c == '/' else re.escape(c)
                    nonSlash = r'[^\\/]*?'
                else:
                    func = lambda c: '/.*?' if c == '/' else re.escape(c)
                    nonSlash = r'[^/]*?'
                delimiter = vim.eval("g:Lf_DelimiterChar")
                if self.isFileNameOnly and delimiter in self._cmdline:
                    self._isMixed = True
                    idx = self._cmdline.index(delimiter)
                    self._regex = ('.*?'.join(map(func, self._cmdline[:idx])), nonSlash.join(map(func, self._cmdline[idx+1:])))
                    if self._regex == ('', ''):
                        self._regex == ()
                elif self.isFileNameOnly:
                    self._isMixed = False
                    self._regex = '.*?'.join(map(func, self._cmdline))
                else:
                    self._isMixed = False
                    self._regex = nonSlash.join(map(func, self._cmdline))
            else:
                self._regex = ''.join(self._cmdline)
        else:
            self._regex = ''

    def _join(self, cmdline):
        cmd = ['%s\[^%s]\{-}' % (c, c) for c in cmdline[0:-1]]
        cmd.append(cmdline[-1])
        regex = ''.join(cmd)
        return regex

    def highlightMatches(self):
        vim.command("silent! syn clear Lf_hl_match")
        if not self._cmdline:
            return
        if self._isFuzzy:
            if os.name == 'nt':
                cmdline = [r'\[\/]\.\{-}' if c == '\\' or c == '/' else c for c in self._cmdline] #\/ for syn match
                nonSlash = '\[^\\/]\{-}'
            else:
                cmdline = [r'\/\.\{-}' if c == '/' else ('\\' + c) if c == '\\' else c for c in self._cmdline] #\/ for syn match
                nonSlash = '\[^/]\{-}'
            if self.isFileNameOnly:
                if self.isMixed:
                    idx = self._cmdline.index(vim.eval("g:Lf_DelimiterChar"))
                    regex = ('\c\V' + self._join(cmdline[:idx]), '\c\V' + nonSlash.join(cmdline[idx+1:]))
                    if regex[0] == '\c\V' and regex[1] == '\c\V':
                        pass
                    elif regex[0] == '\c\V':
                        vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_nonHelp, Lf_hl_filename contained" % regex[1])
                    elif regex[1] == '\c\V':
                        vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_filename contained" % regex[0])
                    else:
                        vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_nonHelp, Lf_hl_filename contained" % regex[1])
                        vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_filename contained" % regex[0])
                else:
                    regex = '\c\V' + self._join(cmdline)
                    vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_filename contained" % regex)
            else:
                regex = '\c\V' + nonSlash.join(cmdline)
                vim.command("syn match Lf_hl_match /%s/ containedin=Lf_hl_nonHelp, Lf_hl_filename contained" % regex)
        else:
            if self.regex:
                regex = (self.regex + '\\') if len(re.search(r'\\*$', self.regex).group(0)) % 2 == 1 else self.regex
                regex = re.sub("'", r"\'", regex)
                if '[' in regex:
                    tmpRe = [i for i in regex]
                    i = 0
                    while i < len(regex):
                        if tmpRe[i] == '\\':
                            i += 2
                        elif tmpRe[i] == '[':
                            j = i + 1
                            while j < len(regex):
                                if tmpRe[j] == ']':
                                    i = j + 1
                                    break
                                elif tmpRe[j] == '\\':
                                    j += 2
                                else:
                                    j += 1
                            if j >= len(regex):
                                tmpRe[i] = r'\['
                                i += 1
                        else:
                            i += 1
                    regex = ''.join(tmpRe)

                if vim.eval("&ignorecase") == '1':
                    regex = r'\c' + regex

                try:
                    if int(vim.eval("v:version")) > 703:
                        vim.command("syn match Lf_hl_match '%s' containedin=Lf_hl_nonHelp, Lf_hl_filename contained" % regex)
                    else:
                        regex = re.sub(r'\\', r'\\\\', regex)
                        vim.eval("""g:LfNoErrMsgCmd("syn match Lf_hl_match '%s' containedin=Lf_hl_nonHelp, Lf_hl_filename contained")""" % regex)
                except vim.error:
                    pass

    def hideCursor(self):
        self._blinkon = False
        self._buildPrompt()

    def setFullPathFeature(self, state):
        self._supportFullPath = state

    @property
    def regex(self):
        return self._regex

    @property
    def cmdline(self):
        return self._cmdline

    @property
    def cursorPos(self):
        return self._cursorPos

    @property
    def isFileNameOnly(self):
        return not self._fullPath

    @property
    def isMixed(self):
        return self._isMixed

    @property
    def isFuzzy(self):
        return self._isFuzzy

    @ctrlCursor
    def input(self):
        try:
            self._blinkon = True
            while 1:
                self._buildPrompt()
                self._idle = False

                vim.command("let nr = getchar(%s)" % vim.eval("g:Lf_CursorBlink == 1 ? 0 : ''"))
                vim.command("sleep 1m")
                vim.command("let ch = !type(nr) ? nr2char(nr) : nr")
                if vim.eval("!type(nr) && nr == 0") == '1':
                    self._idle = True
                    continue
                else:
                    self._blinkon = True

                if vim.eval("!type(nr) && nr >= 0x20") == '1':
                    self._insert(vim.eval("ch"))
                    self._buildRegex()
                    yield '<Update>'
                else:
                    cmd = ''
                    for (key, value) in self._cmdMap.items():
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
                        break
                    elif equal(cmd, '<C-F>'):
                        if self._supportFullPath:
                            self._isFuzzy = True
                            self._fullPath = not self._fullPath
                            self._buildRegex()
                            yield '<Mode>'
                    elif equal(cmd, '<C-R>'):
                        self._isFuzzy = not self._isFuzzy
                        self._buildRegex()
                        yield '<Mode>'
                    elif equal(cmd, '<BS>'):
                        self._backspace()
                        self._buildRegex()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-U>'):
                        self._clearLeft()
                        self._buildRegex()
                        yield '<Shorten>'
                    elif equal(cmd, '<Del>'):
                        self._delete()
                        self._buildRegex()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-V>'):
                        self._paste()
                        self._buildRegex()
                        yield '<Update>'
                    elif equal(cmd, '<Home>'):
                        self._toBegin()
                    elif equal(cmd, '<End>'):
                        self._toEnd()
                    elif equal(cmd, '<Left>'):
                        self._toLeft()
                    elif equal(cmd, '<Right>'):
                        self._toRight()
                    elif equal(cmd, '<C-Q>'):
                        yield '<Quit>'
                    else:
                        yield cmd
        except KeyboardInterrupt: #<C-C>
            if int(vim.eval("v:version")) > 703:
                yield '<Quit>'
            else:
                pass


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import heapq
from leaderf.cli import LfCli
from leaderf.util import *


#*****************************************************
# Manager
#*****************************************************
class Manager(object):
    def __init__(self):
        self._bufName = vim.eval("expand('$VIMRUNTIME/[LeaderF]')")
        self._winPos = int(vim.eval("g:Lf_WindowPosition"))
        self._maxLines = int(vim.eval("g:Lf_MaxLines"))
        self._autochdir = 0
        self._cli = LfCli()
        self._explorer = None
        self._index = 0
        self._helpLength = 0
        self._showHelp = False
        self._selections = {}
        self._initStlVar()
        self._setStlMode()
        self._getExplClass()

    #*****************************************************
    # abstract methods, in fact all the functions can be overridden
    #*****************************************************
    def _getExplClass(self):
        '''
        this function MUST be overridden
        return the name of Explorer class
        '''
        raise NotImplementedError("Can't instantiate abstract class Manager with abstract methods _getExplClass")

    def _defineMaps(self):
        pass

    def _cmdExtension(self, cmd):
        '''
        this function can be overridden to add new cmd
        if return true, exit the input loop
        '''
        pass

    def _getDigest(self, line):
        '''
        this function can be overridden
        specify what part to match regex for a line in the match window
        '''
        return line

    def _createHelp(self):
        return []

    #*****************************************************
    # private methods
    #*****************************************************
    def _createHelpHint(self):
        help = []
        if not self._showHelp:
            help.append('" Press <F1> for help')
            help.append('" ---------------------------------------------------')
        else:
            help += self._createHelp()
        self._helpLength = len(help)
        vim.command("setlocal modifiable")
        vim.current.buffer.append(help, 0)
        vim.current.window.cursor = (self._helpLength + 1, 0)
        vim.command("setlocal nomodifiable")

    def _hideHelp(self):
        for i in range(self._helpLength):
            del vim.current.buffer[0]
        self._helpLength = 0

    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = self._getExplClass()()
        return self._explorer

    def _initStlVar(self):
        vim.command("let g:Lf_statusline_function = '-'")
        vim.command("let g:Lf_statusline_curDir = '-'")
        vim.command("let g:Lf_statusline_total = '0'")

    def _setStlMode(self):
        if self._cli.isFuzzy:
            if self._cli.isFileNameOnly:
                vim.command("let g:Lf_statusline_mode = 'NameOnly'")
            else:
                vim.command("let g:Lf_statusline_mode = 'FullPath'")
        else:
            vim.command("let g:Lf_statusline_mode = 'Regexp'")

    def _bufwinnr(self, name):
        nr = 1
        for w in vim.windows:
            if w.buffer.name is not None and os.path.abspath(w.buffer.name) == os.path.abspath(name):
                return nr
            nr += 1
        return 0

    def _gotoBuffer(self):
        if int(vim.eval("&autochdir")) == 1:
            self._autochdir = 1
            vim.command("set noautochdir")
        else:
            self._autochdir = 0

        self._origBuf = vim.current.buffer.name
        self._origWinNr = int(vim.eval("winnr()"))
        nr = self._bufwinnr(self._bufName)
        if nr == 0:
            self._createBufWindow()
        else:
            vim.command("exec '%d wincmd w'" % nr)
        self._setAttributes()
        self._setStatusline()
        self._defineMaps()

    def _createBufWindow(self):
        if self._winPos == 0:
            vim.command("silent! noa keepj hide edit %s" % self._bufName)
        elif self._winPos == 1:
            vim.command("silent! noa keepj bo sp %s" % self._bufName)
        elif self._winPos == 2:
            vim.command("silent! noa keepj to sp %s" % self._bufName)
        else:
            vim.command("silent! noa keepj to vsp %s" % self._bufName)

    def _setAttributes(self):
        vim.command("setlocal nobuflisted")
        vim.command("setlocal buftype=nofile")
        vim.command("setlocal bufhidden=hide")
        vim.command("setlocal noswapfile")
        vim.command("setlocal nolist")
        vim.command("setlocal nonumber")
        vim.command("setlocal nospell")
        vim.command("setlocal nowrap")
        vim.command("setlocal nofoldenable")
        vim.command("setlocal foldcolumn=1")
        vim.command("setlocal cursorline")
        vim.command("setlocal filetype=LeaderF")

    def _setStatusline(self):
        vim.command("setlocal statusline=LeaderF:\ [%#Lf_hl_stlFunction#%{g:Lf_statusline_function}%#Lf_hl_none#,")
        vim.command("setlocal statusline+=\ %#Lf_hl_stlMode#%-9(%{g:Lf_statusline_mode}%#Lf_hl_none#]%)")
        vim.command("setlocal statusline+=\ \ %<%#Lf_hl_stlCurDir#%{g:Lf_statusline_curDir}%#Lf_hl_none#")
        vim.command("setlocal statusline+=%=%lL/%-5L\ \ Total:%{g:Lf_statusline_total}\ ")
        vim.command("redraw!")

    def _toUp(self):
        vim.command("norm! k")

    def _toDown(self):
        vim.command("norm! j")

    def _leftClick(self):
        nr = self._bufwinnr(self._bufName)
        if nr == int(vim.eval("v:mouse_win")):
            vim.command("exec v:mouse_lnum")
            vim.command("exec 'norm!'.v:mouse_col.'|'")
            self.clearSelections()
        else:
            self.quit()
            self._exitLoop = True

    def _filter(self, iterable, regex):
        if self._cli.isFuzzy:
            if self._cli.isFileNameOnly:
                if self._cli.isMixed:
                    if regex[0] == '':
                        return [line for line in iterable if re.search(regex[1], self._getDigest(line), re.I)]
                    elif regex[1] == '':
                        return [line for line in iterable if re.search(regex[0], os.path.basename(self._getDigest(line)), re.I)]
                    else:
                        iterable = [line for line in iterable if re.search(regex[0], os.path.basename(self._getDigest(line)), re.I)]
                        return [line for line in iterable if re.search(regex[1], os.path.dirname(self._getDigest(line)), re.I)]
                else:
                    return [line for line in iterable if re.search(regex, os.path.basename(self._getDigest(line)), re.I)]
            else:
                return [line for line in iterable if re.search(regex, self._getDigest(line), re.I)]
        else:
            try:
                if '-2' == vim.eval("g:LfNoErrMsgMatch('', '%s')" % escQuote(regex)):
                    return []
                else:
                    return [line for line in iterable if '-1' != vim.eval("g:LfNoErrMsgMatch('%s', '%s')" % (escQuote(self._getDigest(line).strip()), escQuote(regex)))]
            except vim.error:
                pass

    def _isPrefix(self, regex): #assume that there are no \%23l, \%23c, \%23v, \%...
        pos = self._cli.cursorPos
        if pos > 1:
            if regex[pos - 2] != '\\' and (regex[pos - 1].isalnum() or regex[pos - 1] in r'`$%*(-_+[\;:,. /?'):
                if regex[pos - 2] == '_':
                    if pos > 2 and regex[pos - 3] == '\\': #\_x
                        return False
                    else:
                        return True
                if regex.endswith(r'\zs') or regex.endswith(r'\ze'):
                    return False
                return True
        return False

    def _search(self, content, regex):
        self.clearSelections()
        self._cli.highlightMatches()
        cb = vim.current.buffer
        if not regex:
            if self._maxLines > 0:
                setBuffer(cb, content[:self._maxLines])
            else:
                setBuffer(cb, content)
            return

        if not self._cli.isFuzzy:
            if not self._isPrefix(regex):
                self._index = 0

        step = int(vim.eval("g:Lf_SearchStep"))
        length = len(content)
        if self._index == 0:
            self._index = step
            if self._index < length:
                setBuffer(cb, self._filter(content[:self._index], regex))
            else:
                setBuffer(cb, self._filter(content, regex))
        else:
            setBuffer(cb, self._filter(cb[:], regex))

        while len(cb) < 1000 and self._index < length:
            end = self._index + step
            startLine = 0 if cb[0] == '' else len(cb)
            if end < length:
                appendBuffer(cb, self._filter(content[self._index:end], regex), startLine)
            else:
                appendBuffer(cb, self._filter(content[self._index:], regex), startLine)
            self._index = end
            if len(cb) > vim.current.window.height * 2:
                break

        if self._getExplorer().supportsSort():
            num = int(vim.eval("g:Lf_NumberOfSort"))
            if num == -1:
                self._sortResult(len(cb))
            elif num == 0:
                pass
            elif num == 1:
                self._sortResult(vim.current.window.height)
            else:
                self._sortResult(num)
            vim.current.window.cursor = (self._helpLength + 1, 0)

    def _getWeight(self, str, t):
        '''
        this function can be overridden to get the weight of the line,
        so that it can be applied in the sort algorithm
        '''
        pre = str.lower().index(t[0].lower())
        s = str[pre:]
        sl = len(s)
        tl = len(t)
        val = [[0 for col in range(tl)] for row in range(sl)]
        val[0][0] = 1
        JJ = 2
        for i in range(1, sl):
            J = JJ
            for j in range(min(J, tl)):
                if s[i].lower() != t[j].lower():
                    val[i][j] = val[i-1][j]
                else:
                    if j == JJ-1:
                        JJ += 1
                    if val[i-1][j] == (j+1)*(j+1):              # prune
                        val[i][j] = (j+1)*(j+1)
                        continue
                    val[i][j] = val[i-1][j]
                    ii = i
                    jj = j
                    k = 0
                    while ii >= 0 and jj >= 0:
                        if s[ii].lower() == t[jj].lower():
                            if i == j and val[i-1][j-1] == i*i: # prune
                                val[i][j] = (i+1)*(i+1)
                                break
                            k += 1
                            if j-k >= 0:
                                if val[i-k][j-k] + k*k > val[i][j]:
                                    val[i][j] = val[i-k][j-k] + k*k
                            else:
                                val[i][j] = k*k
                            ii -= 1
                            jj -= 1
                        else:
                            break
                if val[i][j] == tl*tl:                          # prune
                    return val[i][j] + 1.0/(2*pre + len(str))
        return val[sl-1][tl-1] + 1.0/(2*pre + len(str))

    def _sortResult(self, num):
        '''
        this function can be overridden to customize the sort algorithm
        '''
        cb = vim.current.buffer
        if len(cb) == 1 and cb[0] == '' or num == 0:
            return
        if self._cli.isFuzzy:
            if self._cli.isFileNameOnly:
                if self._cli.isMixed:
                    pass
                else:
                    pairs = [(i, self._getWeight(os.path.basename(self._getDigest(cb[i])), self._cli.cmdline)) for i in range(len(cb))]
                    pairs = heapq.nlargest(num, pairs, key = lambda x: x[1])
                    lines = [cb[i[0]] for i in pairs]
                    append(cb, lines, 0)
                    pairs.sort(key = lambda x: x[0], reverse = True)
                    for i in pairs:
                        del cb[i[0] + len(pairs)]
            else:
                pass

    def _accept(self, file, mode):
        try:
            if file:
                if mode == '':
                    pass
                elif mode == 'h':
                    vim.command("split")
                elif mode == 'v':
                    vim.command("vsplit")
                elif mode == 't':
                    vim.command("tabedit")
                    tabPos = int(vim.eval("g:Lf_TabpagePosition"))
                    if tabPos == 0:
                        vim.command("tabm 0")
                    elif tabPos == 1:
                        vim.command("tabm -1")
                    elif tabPos == 3:
                        vim.command("tabm")
                self._getExplorer().acceptSelection(file)
        except (KeyboardInterrupt, vim.error):
            pass

    def clearSelections(self):
        for i in self._selections.values():
            vim.command("call matchdelete(%d)" % i)
        self._selections.clear()


    #*****************************************************
    # public methods
    #*****************************************************
    def toggleHelp(self):
        vim.command("setlocal modifiable")
        self._showHelp = not self._showHelp
        for i in range(self._helpLength):
            del vim.current.buffer[0]
        self._createHelpHint()
        self.clearSelections()
        vim.command("setlocal nomodifiable")

    def accept(self, mode = ''):
        if vim.current.window.cursor[0] <= self._helpLength:
            vim.command("norm! j")
            return
        if len(self._selections) > 0:
            files = []
            for i in self._selections.keys():
                files.append(os.path.abspath(vim.current.buffer[i-1]))
            self.quit()
            if mode == '':
                vim.command("argdelete *")
                for file in files:
                    vim.command("argadd %s" % escSpecial(file))
                self._accept(files[0], mode)
            else:
                for file in files:
                    self._accept(file, mode)
        else:
            file = os.path.abspath(vim.current.line)
            self.quit()
            self._accept(file, mode)

    def quit(self):
        self._cli.clear()
        self.clearSelections()
        if self._winPos != 0 and len(vim.windows) > 1:
            vim.command("hide")
            vim.command("exec '%d wincmd w'" % self._origWinNr)
        else:
            if self._origBuf is None or vim.eval("bufexists('%s')" % escQuote(self._origBuf)) == '0':
                vim.command("bd")
            else:
                vim.command("hide edit %s" % escSpecial(self._origBuf))
        if self._winPos != 0:
            vim.command("call getchar(0) | redraw | echo")
        else:
            vim.command("call getchar(0)")
        if self._autochdir == 1:
            cwd = os.getcwd()
            vim.command("set autochdir")    # I think vim has a bug here
            os.chdir(cwd)

    def refresh(self, content = None):
        rContent = self._getExplorer().getFreshContent()
        if rContent is None:
            return
        if content is None:
            vim.command("setlocal modifiable")
            setBuffer(vim.current.buffer, rContent)
            self._content = rContent
            if self._cli.regex:
                self._index = 0
                self._search(rContent, self._cli.regex)
            vim.command("setlocal nomodifiable")
        else:
            setBuffer(vim.current.buffer, rContent)
            content[:] = rContent      #use slice to change content
            if self._cli.regex:
                self._index = 0
                self._search(rContent, self._cli.regex)

    def addSelections(self):
        nr = self._bufwinnr(self._bufName)
        if int(vim.eval("v:mouse_win")) != 0 and nr != int(vim.eval("v:mouse_win")):
            return
        elif nr == int(vim.eval("v:mouse_win")):
            vim.command("exec v:mouse_lnum")
            vim.command("exec 'norm!'.v:mouse_col.'|'")
        lineNr = vim.current.window.cursor[0]
        if lineNr <= self._helpLength:
            vim.command("norm! j")
            return
        
        if lineNr in self._selections:
            vim.command("call matchdelete(%d)" % self._selections[lineNr])
            del self._selections[lineNr]
        else:
            id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % lineNr))
            self._selections[lineNr] = id

        if int(vim.eval("v:mouse_win")) != 0:
            vim.command('call feedkeys("\<C-@>")')  #vim has bug, so add this line

    def selectMulti(self):
        origLine = vim.current.window.cursor[0]
        nr = self._bufwinnr(self._bufName)
        if int(vim.eval("v:mouse_win")) != 0 and nr != int(vim.eval("v:mouse_win")):
            return
        elif nr == int(vim.eval("v:mouse_win")):
            vim.command("exec v:mouse_lnum")
            vim.command("exec 'norm!'.v:mouse_col.'|'")
        self.clearSelections()
        curLine = vim.current.window.cursor[0]
        for i in range(min(origLine, curLine), max(origLine, curLine)+1):
            if i > self._helpLength and i not in self._selections:
                id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i)))
                self._selections[i] = id
        vim.command('call feedkeys("\<C-@>")')  #vim has bug, so add this line

    def selectAll(self):
        for i in range(len(vim.current.buffer)):
            if i >= self._helpLength and i+1 not in self._selections:
                id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i+1)))
                self._selections[i+1] = id

    def startExplorer(self, *args, **kwargs):
        self._cli.setFullPathFeature(self._getExplorer().supportsFullPath())
        vim.command("let g:Lf_statusline_function = '%s'" % self._getExplorer().getStlFunction())
        vim.command("echohl WarningMsg | redraw | echo ' searching ...' | echohl NONE")
        content = self._getExplorer().getContent(*args, **kwargs)
        if content is None:
            return
        self._gotoBuffer()
        vim.command("let g:Lf_statusline_curDir = '%s'" % self._getExplorer().getStlCurDir())
        vim.command("let g:Lf_statusline_total = '%d'" % len(content))
        self.startExplAction(content)

    def startExplAction(self, content = None):
        vim.command("setlocal modifiable")
        self._hideHelp()
        if content is None:
            content = self._content
        else:
            if self._maxLines > 0:
                setBuffer(vim.current.buffer, content[:self._maxLines])
            else:
                setBuffer(vim.current.buffer, content)
            self._index = 0
        quit = False
        for cmd in self._cli.input():
            if equal(cmd, '<Update>'):
                self._search(content, self._cli.regex)
            elif equal(cmd, '<Shorten>'):
                self._index = 0
                self._search(content, self._cli.regex)
            elif equal(cmd, '<Mode>'):
                self._setStlMode()
                self._index = 0
                if self._cli.regex:
                    self._search(content, self._cli.regex)
            elif equal(cmd, '<Up>'):
                self._toUp()
            elif equal(cmd, '<Down>'):
                self._toDown()
            elif equal(cmd, '<LeftMouse>'):
                self._exitLoop = False
                self._leftClick()
                if self._exitLoop:
                    break
            elif equal(cmd, '<2-LeftMouse>'):
                self._leftClick()
                self.accept()
                break
            elif equal(cmd, '<CR>'):
                self.accept()
                break
            elif equal(cmd, '<C-X>'):
                self.accept('h')
                break
            elif equal(cmd, '<C-]>'):
                self.accept('v')
                break
            elif equal(cmd, '<C-T>'):
                self.accept('t')
                break
            elif equal(cmd, '<Quit>'):
                quit = True
                break
            elif equal(cmd, '<Esc>'):
                self.clearSelections()
                self._cli.hideCursor()
                vim.command("setlocal nomodifiable")
                self._content = content
                self._createHelpHint()
            elif equal(cmd, '<F5>'):
                self.refresh(content)
            elif equal(cmd, '<C-LeftMouse>'):
                if self._getExplorer().supportsMulti():
                    self.addSelections()
            elif equal(cmd, '<S-LeftMouse>'):
                if self._getExplorer().supportsMulti():
                    self.selectMulti()
            elif equal(cmd, '<C-A>'):
                if self._getExplorer().supportsMulti():
                    self.selectAll()
            elif equal(cmd, '<C-L>'):
                self.clearSelections()
            else:
                if self._cmdExtension(cmd):
                    break
        if quit: #due to a bug, I have to write this ugly code
            self.quit()


#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import operator
from functools import partial
from leaderf.cli import LfCli
from leaderf.utils import *
from leaderf.fuzzyMatch import FuzzyMatch


#*****************************************************
# Manager
#*****************************************************
class Manager(object):
    def __init__(self):
        self._buffer_name = vim.eval("expand('$VIMRUNTIME/LeaderF')")
        self._win_pos = int(vim.eval("g:Lf_WindowPosition"))
        self._win_height = float(vim.eval("g:Lf_WindowHeight"))
        self._show_tabline = int(vim.eval("&showtabline"))
        self._tabpage_nr = 0
        self._autochdir = 0
        self._cli = LfCli()
        self._explorer = None
        self._content = []
        self._index = 0
        self._help_length = 0
        self._show_help = False
        self._selections = {}
        self._highlight_pos = []
        self._highlight_refine_pos = []
        self._highlight_ids = []
        self._initStlVar()
        self._setStlMode()
        self._getExplClass()

    #**************************************************************
    # abstract methods, in fact all the functions can be overridden
    #**************************************************************
    def _getExplClass(self):
        """
        this function MUST be overridden
        return the name of Explorer class
        """
        raise NotImplementedError("Can't instantiate abstract class Manager "
                                  "with abstract methods _getExplClass")

    def _defineMaps(self):
        pass

    def _cmdExtension(self, cmd):
        """
        this function can be overridden to add new cmd
        if return true, exit the input loop
        """
        pass

    def _getDigest(self, line, mode):
        """
        this function can be overridden
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if mode == 0:
            return line
        elif mode == 1:
            return getBasename(line)
        else:
            return getDirname(line)

    def _getDigestStartPos(self, line, mode):
        """
        this function can be overridden
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if mode == 0 or mode == 2:
            return 0
        else:
            return lfBytesLen(getDirname(line))

    def _createHelp(self):
        return []

    #**************************************************************

    def _createHelpHint(self):
        help = []
        if not self._show_help:
            help.append('" Press <F1> for help')
            help.append('" -------------------------------------------------'
                        '--------')
        else:
            help += self._createHelp()
        self._help_length = len(help)
        vim.current.buffer.append(help, 0)
        vim.current.window.cursor = (self._help_length + 1, 0)

    def _hideHelp(self):
        # should be 'del vim.current.buffer[:self._help_length]',
        # but there is bug in vim7.3
        for i in range(self._help_length):
            del vim.current.buffer[0]
        self._help_length = 0

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
            if self._cli.isFullPath:
                vim.command("let g:Lf_statusline_mode = 'FullPath'")
            else:
                vim.command("let g:Lf_statusline_mode = 'NameOnly'")
        else:
            vim.command("let g:Lf_statusline_mode = 'Regexp'")

    def _bufwinnr(self, name):
        nr = 1
        for w in vim.windows:
            if (w.buffer.name is not None and
                    os.path.abspath(w.buffer.name) == os.path.abspath(name)):
                return nr
            nr += 1
        return 0

    def _resetAutochdir(self):
        if int(vim.eval("&autochdir")) == 1:
            self._autochdir = 1
            vim.command("set noautochdir")
        else:
            self._autochdir = 0

    def _setAutochdir(self):
        if self._autochdir == 1:
            # When autochdir is set, Vim will change the current working directory
            # to the directory containing the file which was opened or selected.
            vim.command("set autochdir")

    def _gotoBuffer(self):
        self._resetAutochdir()
        if self._win_pos == 0:
            self._orig_tabpage = int(vim.eval("tabpagenr()"))
            if int(vim.eval("tabpagenr('$')")) < 2:
                vim.command("set showtabline=0")
            if self._tabpage_nr > 0:
                vim.command("tabnext %d" % self._tabpage_nr)
            else:
                self._createBufWindow()
        else:
            self._orig_win_nr = int(vim.eval("winnr()"))
            nr = self._bufwinnr(self._buffer_name)
            if nr == 0:
                self._createBufWindow()
            else:
                vim.command("exec '%d wincmd w'" % nr)
        self._setAttributes()
        self._setStatusline()
        self._defineMaps()
        self._cli.clear()
        self.clearSelections()
        self._clearHighlights()
        self._highlight_pos = []
        self._highlight_refine_pos = []

    def _createBufWindow(self):
        if self._win_pos != 0:
            self._restore_sizes = vim.eval("winrestcmd()")
        if self._win_pos == 0:
            vim.command("silent! noa keepj $tabedit %s" % self._buffer_name)
            self._tabpage_nr = int(vim.eval("tabpagenr()"))
        elif self._win_pos == 1:
            vim.command("silent! noa keepj bo sp %s" % self._buffer_name)
            if self._win_height >= 1:
                vim.command("resize %d" % self._win_height)
            elif self._win_height > 0:
                vim.command("resize %d" % (int(vim.eval("&lines")) * self._win_height))
        elif self._win_pos == 2:
            vim.command("silent! noa keepj to sp %s" % self._buffer_name)
            if self._win_height >= 1:
                vim.command("resize %d" % self._win_height)
            elif self._win_height > 0:
                vim.command("resize %d" % (int(vim.eval("&lines")) * self._win_height))
        else:
            vim.command("silent! noa keepj to vsp %s" % self._buffer_name)

    def _setAttributes(self):
        vim.command("setlocal nobuflisted")
        vim.command("setlocal buftype=nofile")
        vim.command("setlocal bufhidden=hide")
        vim.command("setlocal noswapfile")
        vim.command("setlocal nolist")
        vim.command("setlocal number")
        vim.command("setlocal norelativenumber")
        vim.command("setlocal nospell")
        vim.command("setlocal nowrap")
        vim.command("setlocal nofoldenable")
        vim.command("setlocal foldcolumn=0")
        vim.command("setlocal cursorline")
        vim.command("setlocal filetype=leaderf")

    def _setStatusline(self):
        vim.command("setlocal statusline=LeaderF:\ [%#Lf_hl_stlFunction#"
                    "%{g:Lf_statusline_function}%#Lf_hl_none#,")
        vim.command("setlocal statusline+=\ %#Lf_hl_stlMode#%-9("
                    "%{g:Lf_statusline_mode}%#Lf_hl_none#]%)")
        vim.command("setlocal statusline+=\ \ %<%#Lf_hl_stlCurDir#"
                    "%{g:Lf_statusline_curDir}%#Lf_hl_none#")
        vim.command("setlocal statusline+=%=%lL/%-5L\ \ Total:"
                    "%{g:Lf_statusline_total}\ ")
        vim.command("redraw!")

    def _toUp(self):
        vim.command("norm! k")

    def _toDown(self):
        vim.command("norm! j")

    def _leftClick(self):
        nr = self._bufwinnr(self._buffer_name)
        if nr == int(vim.eval("v:mouse_win")):
            vim.command("exec v:mouse_lnum")
            vim.command("exec 'norm!'.v:mouse_col.'|'")
            self.clearSelections()
        else:
            self.quit()
            self._exit_loop = True

    def _search(self, content):
        self.clearSelections()
        self._cli.highlightMatches()
        cb = vim.current.buffer
        if not self._cli.pattern:   # e.g., when <BS> or <Del> is typed
            setBuffer(cb, content)
            self._clearHighlights()
            return

        if self._cli.isFuzzy:
            self._fuzzySearch(content)
        else:
            self._regexSearch(content)

    def _filter(self, step, filter_method, content):
        """ Construct a list from result of filter_method(content).

        Args:
            step: An integer to indicate the number of lines to filter one time.
            filter_method: A function to apply `content` as parameter and
                return an iterable.
            content: The list to be filtered.
        """
        length = len(content)
        cb = vim.current.buffer
        result = []
        if self._index == 0:
            self._index = step
            if self._index < length:
                result.extend(filter_method(content[:self._index]))
            else:
                result.extend(filter_method(content))
        else:
            result.extend(filter_method(cb[:]))
            if self._index < length:
                end = self._index + step - len(cb)
                result.extend(filter_method(content[self._index:end]))
                self._index = end

        while len(result) < 200 and self._index < length:
            end = self._index + 5000
            result.extend(filter_method(content[self._index:end]))
            self._index = end

        return result

    def _fuzzyFilter(self, is_full_path, get_weight, iterable):
        """
        return a list, each item is a pair (weight, line)
        """
        getDigest = partial(self._getDigest, mode=0 if is_full_path else 1)
        pairs = ((get_weight(getDigest(line)), line) for line in iterable)
        return (p for p in pairs if p[0])

    def _refineFilter(self, first_get_weight, get_weight, iterable):
        getDigest = self._getDigest
        triples = ((first_get_weight(getDigest(line, 1)),
                    get_weight(getDigest(line, 2)), line)
                    for line in iterable)
        return ((i[0] + i[1], i[2]) for i in triples if i[0] and i[1])

    def _fuzzySearch(self, content):
        encoding = vim.eval("&encoding")
        if self._cli.isRefinement:
            if self._cli.pattern[1] == '':      # e.g. abc;
                fuzzy_match = FuzzyMatch(self._cli.pattern[0], encoding)
                filter_method = partial(self._fuzzyFilter,
                                        False,
                                        fuzzy_match.getWeight)
                highlight_method = partial(self._highlight,
                                           False,
                                           fuzzy_match.getHighlights)
            elif self._cli.pattern[0] == '':    # e.g. ;abc
                fuzzy_match = FuzzyMatch(self._cli.pattern[1], encoding)
                filter_method = partial(self._fuzzyFilter,
                                        True,
                                        fuzzy_match.getWeight)
                highlight_method = partial(self._highlight,
                                           True,
                                           fuzzy_match.getHighlights)
            else:
                fuzzy_match0 = FuzzyMatch(self._cli.pattern[0], encoding)
                fuzzy_match1 = FuzzyMatch(self._cli.pattern[1], encoding)
                filter_method = partial(self._refineFilter,
                                        fuzzy_match0.getWeight,
                                        fuzzy_match1.getWeight)
                highlight_method = partial(self._highlightRefine,
                                           fuzzy_match0.getHighlights,
                                           fuzzy_match1.getHighlights)
        else:
            fuzzy_match = FuzzyMatch(self._cli.pattern, encoding)
            filter_method = partial(self._fuzzyFilter,
                                    self._cli.isFullPath,
                                    fuzzy_match.getWeight)
            highlight_method = partial(self._highlight,
                                       self._cli.isFullPath,
                                       fuzzy_match.getHighlights)

        pairs = self._filter(30000, filter_method, content)
        pairs.sort(key=operator.itemgetter(0), reverse=True)
        setBuffer(vim.current.buffer, [p[1] for p in pairs])
        highlight_method()

    def _clearHighlights(self):
        for i in self._highlight_ids:
            vim.command("silent! call matchdelete(%d)" % i)
        self._highlight_ids = []

    def _resetHighlights(self):
        self._clearHighlights()
        for i, pos in enumerate(self._highlight_pos, self._help_length + 1):
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(vim.eval("matchaddpos('Lf_hl_match', %s)"
                         % str(pos[j:j+8])))
                self._highlight_ids.append(id)

        for i, pos in enumerate(self._highlight_refine_pos, self._help_length + 1):
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(vim.eval("matchaddpos('Lf_hl_match_refine', %s)"
                         % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _highlight(self, is_full_path, get_highlights):
        # matchaddpos() is introduced by Patch 7.4.330
        if (vim.eval("exists('*matchaddpos')") == '0' or
                vim.eval("g:Lf_HighlightIndividual") == '0'):
            return
        cb = vim.current.buffer
        if len(cb) == 1 and cb[0] == '': # buffer is empty.
            return

        highlight_number = int(vim.eval("g:Lf_NumberOfHighlight"))
        self._clearHighlights()

        getDigest = partial(self._getDigest, mode=0 if is_full_path else 1)

        # e.g., self._highlight_pos = [ [ [2,3], [6,2] ], [ [1,4], [7,6], ... ], ... ]
        # where [2, 3] indicates the highlight starts at the 2nd column with the
        # length of 3 in bytes
        self._highlight_pos = [get_highlights(getDigest(line))
                               for line in cb[:highlight_number]]
        for i, pos in enumerate(self._highlight_pos, 1):
            start_pos = self._getDigestStartPos(cb[i-1], 0 if is_full_path else 1)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(vim.eval("matchaddpos('Lf_hl_match', %s)"
                         % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _highlightRefine(self, first_get_highlights, get_highlights):
        # matchaddpos() is introduced by Patch 7.4.330
        if (vim.eval("exists('*matchaddpos')") == '0' or
                vim.eval("g:Lf_HighlightIndividual") == '0'):
            return
        cb = vim.current.buffer
        if len(cb) == 1 and cb[0] == '': # buffer is empty.
            return

        highlight_number = int(vim.eval("g:Lf_NumberOfHighlight"))
        self._clearHighlights()

        getDigest = self._getDigest
        self._highlight_pos = [first_get_highlights(getDigest(line, 1))
                               for line in cb[:highlight_number]]
        for i, pos in enumerate(self._highlight_pos, 1):
            start_pos = self._getDigestStartPos(cb[i-1], 1)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(vim.eval("matchaddpos('Lf_hl_match', %s)"
                         % str(pos[j:j+8])))
                self._highlight_ids.append(id)

        self._highlight_refine_pos = [get_highlights(getDigest(line, 2))
                                      for line in cb[:highlight_number]]
        for i, pos in enumerate(self._highlight_refine_pos, 1):
            start_pos = self._getDigestStartPos(cb[i-1], 2)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(vim.eval("matchaddpos('Lf_hl_match_refine', %s)"
                         % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _regexFilter(self, iterable):
        try:
            if ('-2' == vim.eval("g:LfNoErrMsgMatch('', '%s')" %
                    escQuote(self._cli.pattern))):
                return iter([])
            else:
                return (line for line in iterable
                        if '-1' != vim.eval("g:LfNoErrMsgMatch('%s', '%s')" %
                        (escQuote(self._getDigest(line, 0).strip()),
                        escQuote(self._cli.pattern))))
        except vim.error:
            return iter([])

    def _regexSearch(self, content):
        if not self._cli.isPrefix:
            self._index = 0
        lines = self._filter(8000, self._regexFilter, content)
        setBuffer(vim.current.buffer, lines)

    def clearSelections(self):
        for i in self._selections.values():
            vim.command("call matchdelete(%d)" % i)
        self._selections.clear()

    def toggleHelp(self):
        vim.command("setlocal modifiable")
        self._show_help = not self._show_help
        for i in range(self._help_length):
            del vim.current.buffer[0]
        self._createHelpHint()
        self.clearSelections()
        self._resetHighlights()
        vim.command("setlocal nomodifiable")

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
                    tab_pos = int(vim.eval("g:Lf_TabpagePosition"))
                    if tab_pos == 0:
                        vim.command("tabm 0")
                    elif tab_pos == 1:
                        vim.command("tabm -1")
                    elif tab_pos == 3:
                        vim.command("tabm")
                self._getExplorer().acceptSelection(file)
        except (KeyboardInterrupt, vim.error):
            pass

    def accept(self, mode=''):
        if vim.current.window.cursor[0] <= self._help_length:
            vim.command("norm! j")
            return
        if len(self._selections) > 0:
            files = []
            for i in sorted(self._selections.keys()):
                files.append(vim.current.buffer[i-1])
            self._quit()
            if mode == '':
                # It will raise E480 without 'silent!'
                vim.command("silent! argdelete *")
                for file in files:
                    vim.command("argadd %s" % escSpecial(file))
                self._accept(files[0], mode)
            else:
                for file in files:
                    self._accept(file, mode)
        else:
            file = '' if vim.current.line == '' else vim.current.line
            self._quit()
            self._accept(file, mode)
        self._setAutochdir()

    def _quit(self):
        self._cli.clear()
        self.clearSelections()
        self._clearHighlights()
        if self._win_pos == 0:
            try:
                vim.command("tabclose! | tabnext %d" % self._orig_tabpage)
            except: #E85, vim7.3 still reports the error
                vim.command("new | only")

            vim.command("set showtabline=%d" % self._show_tabline)
            self._tabpage_nr = 0
        else:
            if len(vim.windows) > 1:
                vim.command("hide")
                # 'silent!' is used to skip error E16.
                vim.command("silent! exec '%d wincmd w'" % self._orig_win_nr)
                vim.command(self._restore_sizes)
            else:
                vim.command("bd")

        if self._win_pos != 0:
            vim.command("call getchar(0) | redraw | echo")
        else:
            vim.command("call getchar(0)")

    def quit(self):
        self._quit()
        self._setAutochdir()

    def refresh(self, normal_mode=True):
        self._content = self._getExplorer().getFreshContent()
        if self._content is None:
            return

        if normal_mode: # when called in Normal mode
            vim.command("setlocal modifiable")

        setBuffer(vim.current.buffer, self._content)
        if self._cli.pattern:
            self._index = 0
            self._search(self._content)

        if normal_mode: # when called in Normal mode
            self._createHelpHint()
            self._resetHighlights()
            vim.command("setlocal nomodifiable")

    def addSelections(self):
        nr = self._bufwinnr(self._buffer_name)
        if (int(vim.eval("v:mouse_win")) != 0 and
                nr != int(vim.eval("v:mouse_win"))):
            return
        elif nr == int(vim.eval("v:mouse_win")):
            vim.command("exec v:mouse_lnum")
            vim.command("exec 'norm!'.v:mouse_col.'|'")
        line_nr = vim.current.window.cursor[0]
        if line_nr <= self._help_length:
            vim.command("norm! j")
            return

        if line_nr in self._selections:
            vim.command("call matchdelete(%d)" % self._selections[line_nr])
            del self._selections[line_nr]
        else:
            id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % line_nr))
            self._selections[line_nr] = id

    def selectMulti(self):
        orig_line = vim.current.window.cursor[0]
        nr = self._bufwinnr(self._buffer_name)
        if (int(vim.eval("v:mouse_win")) != 0 and
                nr != int(vim.eval("v:mouse_win"))):
            return
        elif nr == int(vim.eval("v:mouse_win")):
            cur_line = int(vim.eval("v:mouse_lnum"))
        self.clearSelections()
        for i in range(min(orig_line, cur_line), max(orig_line, cur_line)+1):
            if i > self._help_length and i not in self._selections:
                id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i)))
                self._selections[i] = id

    def selectAll(self):
        for i in range(len(vim.current.buffer)):
            if i >= self._help_length and i+1 not in self._selections:
                id = int(vim.eval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i+1)))
                self._selections[i+1] = id

    def startExplorer(self, *args, **kwargs):
        self._cli.setNameOnlyFeature(self._getExplorer().supportsNameOnly())
        vim.command("let g:Lf_statusline_function = '%s'" %
                    self._getExplorer().getStlFunction())
        vim.command("echohl WarningMsg | redraw |"
                    "echo ' searching ...' | echohl NONE")
        
        self._content = self._getExplorer().getContent(*args, **kwargs)
        if not self._content:
            vim.command("echohl Error | redraw | echo ' No content!' | echohl NONE")
            return
        self._gotoBuffer()
        vim.command("let g:Lf_statusline_curDir = '%s'" %
                    self._getExplorer().getStlCurDir())
        vim.command("let g:Lf_statusline_total = '%d'" % len(self._content))
        self.input(False)

    def input(self, normal_mode=True):
        vim.command("setlocal modifiable")
        self._hideHelp()
        self._resetHighlights()

        if not normal_mode:
            setBuffer(vim.current.buffer, self._content)
            vim.command("normal! gg")
            self._index = 0

        quit = False
        for cmd in self._cli.input():
            if equal(cmd, '<Update>'):
                self._search(self._content)
            elif equal(cmd, '<Shorten>'):
                self._index = 0 # search from beginning
                self._search(self._content)
            elif equal(cmd, '<Mode>'):
                self._setStlMode()
                self._index = 0 # search from beginning
                if self._cli.pattern:
                    self._search(self._content)
            elif equal(cmd, '<Up>'):
                self._toUp()
            elif equal(cmd, '<Down>'):
                self._toDown()
            elif equal(cmd, '<LeftMouse>'):
                self._exit_loop = False
                self._leftClick()
                if self._exit_loop:
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
            elif equal(cmd, '<Esc>'):   # switch to Normal mode
                self.clearSelections()
                self._cli.hideCursor()
                self._createHelpHint()
                self._resetHighlights()
                vim.command("setlocal nomodifiable")
                break
            elif equal(cmd, '<F5>'):
                self.refresh(False)
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
        if quit: # due to a bug which is fixed by Patch 7.4.084, I have to write this ugly code
            self.quit()


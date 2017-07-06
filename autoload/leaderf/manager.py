#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import time
import operator
import itertools
from functools import partial
from functools import wraps
from leaderf.instance import LfInstance
from leaderf.cli import LfCli
from leaderf.utils import *
from leaderf.fuzzyMatch import FuzzyMatch


def modifiableController(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        self._getInstance().buffer.options['modifiable'] = True
        func(self, *args, **kwargs)
        self._getInstance().buffer.options['modifiable'] = False
    return deco

#*****************************************************
# Manager
#*****************************************************
class Manager(object):
    def __init__(self):
        self._autochdir = 0
        self._instance = None
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

    def _argaddFiles(self, files):
        # It will raise E480 without 'silent!'
        lfCmd("silent! argdelete *")
        for file in files:
            lfCmd("argadd %s" % escSpecial(file))

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        file = args[0]
        try:
            lfCmd("hide edit %s" % escSpecial(file))
        except vim.error as e: # E37
            print(e)

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
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if mode == 0 or mode == 2:
            return 0
        else:
            return lfBytesLen(getDirname(line))

    def _createHelp(self):
        return []

    def _setStlMode(self):
        if self._cli.isFuzzy:
            if self._getExplorer().isFilePath():
                if self._cli.isFullPath:
                    mode = 'FullPath'
                else:
                    mode = 'NameOnly'
            else:
                mode = 'Fuzzy'
        else:
            mode = 'Regex'
        self._getInstance().setStlMode(mode)
        self._cli.setCurrentMode(mode)

    def _beforeEnter(self):
        self._resetAutochdir()

    def _afterEnter(self):
        self._cleanup()
        self._defineMaps()

    def _beforeExit(self):
        self._cleanup()
        self._getExplorer().cleanup()

    def _afterExit(self):
        pass

    def _getList(self, pairs):
        """
        this function can be overridden
        return a list constructed from pairs
        Args:
            pairs: a list of tuple(weight, line, ...)
        """
        return [p[1] for p in pairs]

    def _getUnit(self):
        """
        indicates how many lines are considered as a unit
        """
        return 1

    def _supportsRefine(self):
        return False

    def _previewResult(self):
        pass

    #**************************************************************

    def _getInstance(self):
        if self._instance is None:
            self._instance = LfInstance(self._getExplorer().getStlCategory(),
                                        self._beforeEnter,
                                        self._afterEnter,
                                        self._beforeExit,
                                        self._afterExit)
        return self._instance

    def _createHelpHint(self):
        help = []
        if not self._show_help:
            help.append('" Press <F1> for help')
            help.append('" ---------------------------------------------------------')
        else:
            help += self._createHelp()
        self._help_length = len(help)
        self._getInstance().buffer.append(help, 0)
        self._getInstance().window.cursor = (self._help_length + 1, 0)

    def _hideHelp(self):
        del self._getInstance().buffer[:self._help_length]
        self._help_length = 0

    def _getExplorer(self):
        if self._explorer is None:
            self._explorer = self._getExplClass()()
        return self._explorer

    def _resetAutochdir(self):
        if int(lfEval("&autochdir")) == 1:
            self._autochdir = 1
            lfCmd("set noautochdir")
        else:
            self._autochdir = 0

    def _setAutochdir(self):
        if self._autochdir == 1:
            # When autochdir is set, Vim will change the current working directory
            # to the directory containing the file which was opened or selected.
            lfCmd("set autochdir")

    def _toUp(self):
        lfCmd("norm! k")

    def _toDown(self):
        lfCmd("norm! j")

    def _leftClick(self):
        if self._getInstance().window.number == int(lfEval("v:mouse_win")):
            lfCmd("exec v:mouse_lnum")
            lfCmd("exec 'norm!'.v:mouse_col.'|'")
            self.clearSelections()
            exit_loop = False
        else:
            self.quit()
            exit_loop = True
        return exit_loop

    def _search(self, content, is_continue=False, step=30000):
        self.clearSelections()
        self._cli.highlightMatches()
        if not self._cli.pattern:   # e.g., when <BS> or <Del> is typed
            self._getInstance().setBuffer(content)
            self._clearHighlights()
            self._clearHighlightsPos()
            return

        if self._cli.isFuzzy:
            self._fuzzySearch(content, is_continue, step)
        else:
            self._regexSearch(content, is_continue, step)

        self._previewResult()

    def _filter(self, step, filter_method, content, is_continue):
        """ Construct a list from result of filter_method(content).

        Args:
            step: An integer to indicate the number of lines to filter one time.
            filter_method: A function to apply `content` as parameter and
                return an iterable.
            content: The list to be filtered.
        """
        unit = self._getUnit()
        step = step // unit * unit
        length = len(content)
        cb = self._getInstance().buffer
        result = []
        if self._index == 0:
            self._previous_result = []
            self._cb_content = []
            self._index = min(step, length)
            result.extend(filter_method(content[:self._index]))
        elif is_continue:
            end = min(self._index + step, length)
            result.extend(filter_method(content[self._index:end]))
            self._index = end
        else:
            if len(cb) >= step:
                result.extend(filter_method(cb[:step]))
                self._cb_content += cb[step:]
            else:
                result.extend(filter_method(cb[:]))
                left = step - len(cb)
                if len(self._cb_content) >= left:
                    result.extend(filter_method(self._cb_content[:left]))
                    self._cb_content = self._cb_content[left:]
                else:
                    result.extend(filter_method(self._cb_content))
                    left -= len(self._cb_content)
                    self._cb_content = []
                    if self._index < length:
                        end = min(self._index + left, length)
                        result.extend(filter_method(content[self._index:end]))
                        self._index = end

        if is_continue:
            self._previous_result += result
            result = self._previous_result
        else:
            self._previous_result = result

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

    def _fuzzySearch(self, content, is_continue, step):
        encoding = lfEval("&encoding")
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
            if self._getExplorer().getStlCategory() == "File" and self._cli.isFullPath:
                filter_method = partial(self._fuzzyFilter,
                                        self._cli.isFullPath,
                                        fuzzy_match.getWeight2)
            else:
                filter_method = partial(self._fuzzyFilter,
                                        self._cli.isFullPath,
                                        fuzzy_match.getWeight)

            highlight_method = partial(self._highlight,
                                       self._cli.isFullPath,
                                       fuzzy_match.getHighlights)

        if self._getExplorer().isFilePath() and self._cli.isFullPath and step == 30000:
            step = 8000

        pairs = self._filter(step, filter_method, content, is_continue)
        pairs.sort(key=operator.itemgetter(0), reverse=True)
        self._getInstance().setBuffer(self._getList(pairs))
        highlight_method()

    def _clearHighlights(self):
        for i in self._highlight_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._highlight_ids = []

    def _clearHighlightsPos(self):
        self._highlight_pos = []
        self._highlight_refine_pos = []

    def _resetHighlights(self):
        self._clearHighlights()
        for i, pos in enumerate(self._highlight_pos, self._help_length + 1):
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(lfEval("matchaddpos('Lf_hl_match', %s)" % str(pos[j:j+8])))
                self._highlight_ids.append(id)

        for i, pos in enumerate(self._highlight_refine_pos, self._help_length + 1):
            pos = [[i] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(lfEval("matchaddpos('Lf_hl_matchRefine', %s)" % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _highlight(self, is_full_path, get_highlights):
        # matchaddpos() is introduced by Patch 7.4.330
        if (lfEval("exists('*matchaddpos')") == '0' or
                lfEval("g:Lf_HighlightIndividual") == '0'):
            return
        cb = self._getInstance().buffer
        if len(cb) == 1 and cb[0] == '': # buffer is empty.
            return

        highlight_number = int(lfEval("g:Lf_NumberOfHighlight"))
        self._clearHighlights()

        getDigest = partial(self._getDigest, mode=0 if is_full_path else 1)

        unit = self._getUnit()

        # e.g., self._highlight_pos = [ [ [2,3], [6,2] ], [ [1,4], [7,6], ... ], ... ]
        # where [2, 3] indicates the highlight starts at the 2nd column with the
        # length of 3 in bytes
        self._highlight_pos = [get_highlights(getDigest(line))
                               for line in cb[:][:highlight_number:unit]]
        for i, pos in enumerate(self._highlight_pos):
            start_pos = self._getDigestStartPos(cb[unit*i], 0 if is_full_path else 1)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[unit*i+1] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(lfEval("matchaddpos('Lf_hl_match', %s)" % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _highlightRefine(self, first_get_highlights, get_highlights):
        # matchaddpos() is introduced by Patch 7.4.330
        if (lfEval("exists('*matchaddpos')") == '0' or
                lfEval("g:Lf_HighlightIndividual") == '0'):
            return
        cb = self._getInstance().buffer
        if len(cb) == 1 and cb[0] == '': # buffer is empty.
            return

        highlight_number = int(lfEval("g:Lf_NumberOfHighlight"))
        self._clearHighlights()

        getDigest = self._getDigest
        unit = self._getUnit()
        self._highlight_pos = [first_get_highlights(getDigest(line, 1))
                               for line in cb[:][:highlight_number:unit]]
        for i, pos in enumerate(self._highlight_pos):
            start_pos = self._getDigestStartPos(cb[unit*i], 1)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[unit*i+1] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(lfEval("matchaddpos('Lf_hl_match', %s)" % str(pos[j:j+8])))
                self._highlight_ids.append(id)

        self._highlight_refine_pos = [get_highlights(getDigest(line, 2))
                                      for line in cb[:][:highlight_number:unit]]
        for i, pos in enumerate(self._highlight_refine_pos):
            start_pos = self._getDigestStartPos(cb[unit*i], 2)
            if start_pos > 0:
                for j in range(len(pos)):
                    pos[j][0] += start_pos
            pos = [[unit*i+1] + p for p in pos]
            # The maximum number of positions is 8 in matchaddpos().
            for j in range(0, len(pos), 8):
                id = int(lfEval("matchaddpos('Lf_hl_matchRefine', %s)" % str(pos[j:j+8])))
                self._highlight_ids.append(id)

    def _regexFilter(self, iterable):
        try:
            if ('-2' == lfEval("g:LfNoErrMsgMatch('', '%s')" % escQuote(self._cli.pattern))):
                return iter([])
            else:
                return (line for line in iterable
                        if '-1' != lfEval("g:LfNoErrMsgMatch('%s', '%s')" %
                        (escQuote(self._getDigest(line, 0).strip()),
                         escQuote(self._cli.pattern))))
        except vim.error:
            return iter([])

    def _regexSearch(self, content, is_continue, step):
        if not self._cli.isPrefix:
            self._index = 0
        lines = self._filter(8000, self._regexFilter, content, is_continue)
        self._getInstance().setBuffer(lines)

    def clearSelections(self):
        for i in self._selections.values():
            lfCmd("call matchdelete(%d)" % i)
        self._selections.clear()

    def _cleanup(self):
        self._cli.clear()
        self.clearSelections()
        self._clearHighlights()
        self._clearHighlightsPos()
        self._help_length = 0

    @modifiableController
    def toggleHelp(self):
        self._show_help = not self._show_help
        del self._getInstance().buffer[:self._help_length]
        self._createHelpHint()
        self.clearSelections()
        self._resetHighlights()

    def _accept(self, file, mode, *args, **kwargs):
        if file:
            if mode == '':
                pass
            elif mode == 'h':
                lfCmd("split")
            elif mode == 'v':
                lfCmd("vsplit")
            elif mode == 't':
                lfCmd("tabedit")
                tab_pos = int(lfEval("g:Lf_TabpagePosition"))
                if tab_pos == 0:
                    lfCmd("tabm 0")
                elif tab_pos == 1:
                    lfCmd("tabm -1")
                elif tab_pos == 3:
                    lfCmd("tabm")
            self._acceptSelection(file, *args, **kwargs)

    def accept(self, mode=''):
        if self._getInstance().window.cursor[0] <= self._help_length:
            lfCmd("norm! j")
            return
        if len(self._selections) > 0:
            files = []
            for i in sorted(self._selections.keys()):
                files.append(self._getInstance().buffer[i-1])
            self._getInstance().exitBuffer()
            if mode == '':
                self._argaddFiles(files)
                self._accept(files[0], mode)
            else:
                for file in files:
                    self._accept(file, mode)
        else:
            file = self._getInstance().currentLine
            line_nr = self._getInstance().window.cursor[0]
            self._getInstance().exitBuffer()
            self._accept(file, mode, self._getInstance().buffer, line_nr) # for bugTag

        self._setAutochdir()

    def quit(self):
        self._getInstance().exitBuffer()
        self._setAutochdir()

    def refresh(self, normal_mode=True):
        content = self._getExplorer().getFreshContent()
        if not content:
            lfCmd("echohl Error | redraw | echo ' No content!' | echohl NONE")
            return

        if normal_mode: # when called in Normal mode
            self._getInstance().buffer.options['modifiable'] = True

        self._clearHighlights()
        self._clearHighlightsPos()
        self.clearSelections()

        self._getInstance().initBuffer(content, self._getUnit(), self._getExplorer().setContent)
        self._content = self._getInstance().buffer[:]
        self._iteration_end = True

        if self._cli.pattern:
            self._index = 0
            self._search(self._content)

        if normal_mode: # when called in Normal mode
            self._createHelpHint()
            self._resetHighlights()
            self._getInstance().buffer.options['modifiable'] = False

    def addSelections(self):
        nr = self._getInstance().window.number
        if (int(lfEval("v:mouse_win")) != 0 and
                nr != int(lfEval("v:mouse_win"))):
            return
        elif nr == int(lfEval("v:mouse_win")):
            lfCmd("exec v:mouse_lnum")
            lfCmd("exec 'norm!'.v:mouse_col.'|'")
        line_nr = self._getInstance().window.cursor[0]
        if line_nr <= self._help_length:
            lfCmd("norm! j")
            return

        if line_nr in self._selections:
            lfCmd("call matchdelete(%d)" % self._selections[line_nr])
            del self._selections[line_nr]
        else:
            id = int(lfEval("matchadd('Lf_hl_selection', '\%%%dl.')" % line_nr))
            self._selections[line_nr] = id

    def selectMulti(self):
        orig_line = self._getInstance().window.cursor[0]
        nr = self._getInstance().window.number
        if (int(lfEval("v:mouse_win")) != 0 and
                nr != int(lfEval("v:mouse_win"))):
            return
        elif nr == int(lfEval("v:mouse_win")):
            cur_line = int(lfEval("v:mouse_lnum"))
        self.clearSelections()
        for i in range(min(orig_line, cur_line), max(orig_line, cur_line)+1):
            if i > self._help_length and i not in self._selections:
                id = int(lfEval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i)))
                self._selections[i] = id

    def selectAll(self):
        line_num = len(self._getInstance().buffer)
        if line_num > 300:
            lfCmd("echohl Error | redraw | echo ' Too many files selected!' | echohl NONE")
            lfCmd("sleep 1")
            return
        for i in range(line_num):
            if i >= self._help_length and i+1 not in self._selections:
                id = int(lfEval("matchadd('Lf_hl_selection', '\%%%dl.')" % (i+1)))
                self._selections[i+1] = id

    def startExplorer(self, win_pos, *args, **kwargs):
        self._cli.setNameOnlyFeature(self._getExplorer().supportsNameOnly())
        self._cli.setRefineFeature(self._supportsRefine())
        lfCmd("echohl WarningMsg | redraw |"
              "echo ' searching ...' | echohl NONE")
        content = self._getExplorer().getContent(*args, **kwargs)
        if not content:
            lfCmd("echohl Error | redraw | echo ' No content!' | echohl NONE")
            return
        self._getInstance().enterBuffer(win_pos)

        self._getInstance().setStlCategory(self._getExplorer().getStlCategory())
        self._setStlMode()
        self._getInstance().setStlCwd(self._getExplorer().getStlCurDir())

        lfCmd("normal! gg")
        self._index = 0
        self._start_time = time.time()

        if isinstance(content, list):
            self._content = content
            self._iteration_end = True
            self._getInstance().setStlTotal(len(content)//self._getUnit())
            self._getInstance().setBuffer(content)
            self.input()
        else:
            if lfEval("g:Lf_CursorBlink") == '0':
                self._getInstance().initBuffer(content, self._getUnit(), self._getExplorer().setContent)
                self._content = self._getInstance().buffer[:]
                self._iteration_end = True
                self.input()
            else:
                self._content = []
                self._iteration_end = False
                self._backup = None
                self.input(content)

    def setContent(self, content):
        if not content or self._iteration_end == True:
            if time.time() - self._start_time > 0.1:
                self._start_time = time.time()
                if self._cli.pattern and self._index < len(self._content):
                    self._search(self._content, True, 1000)
                    return True
            return False

        i = -1
        for i, line in enumerate(itertools.islice(content, 10)):
            self._content.append(line)
            if self._index == 0:
                if i == 0 and len(self._getInstance().buffer[0]) == 0: # the buffer is empty
                    self._getInstance().buffer[0] = line
                else:
                    self._getInstance().appendLine(line)

        if i == -1:
            self._iteration_end = True
            self._getExplorer().setContent(self._content)
            self._getInstance().setStlTotal(len(self._content)//self._getUnit())
            lfCmd("redrawstatus")
            if self._index < len(self._content):
                self._search(self._content, True, 1000)
            return False
        else:
            if time.time() - self._start_time > 0.1:
                self._start_time = time.time()
                self._getInstance().setStlTotal(len(self._content)//self._getUnit())
                lfCmd("redrawstatus")
                if self._index < len(self._content):
                    self._search(self._content, True, 1000)
            return True

    @modifiableController
    def input(self, content=None):
        self._hideHelp()
        self._resetHighlights()

        if self._iteration_end == False and self._backup:
            content = self._backup

        for cmd in self._cli.input(partial(self.setContent, content)):
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
                self._previewResult()
            elif equal(cmd, '<Down>'):
                self._toDown()
                self._previewResult()
            elif equal(cmd, '<LeftMouse>'):
                if self._leftClick():
                    break
                self._previewResult()
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
                self.quit()
                break
            elif equal(cmd, '<Esc>'):   # switch to Normal mode
                self.clearSelections()
                self._cli.hideCursor()
                self._createHelpHint()
                self._resetHighlights()
                self._backup = content
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


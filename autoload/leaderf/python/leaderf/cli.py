#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import sys
import time
import platform
from datetime import datetime
from datetime import timedelta
from functools import wraps
from collections import OrderedDict
from .utils import *

def cursorController(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if lfEval("exists('g:lf_gcr_stack')") == '0':
            lfCmd("let g:lf_gcr_stack = []")
        lfCmd("call add(g:lf_gcr_stack, &gcr)")
        if lfEval("has('nvim')") == '1':
            lfCmd("hi Cursor blend=100")
            lfCmd("set gcr+=a:ver1-Cursor/lCursor")
        else:
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
            if lfEval("has('nvim')") == '1':
                lfCmd("hi Cursor blend=0")
            else:
                lfCmd("set t_ve&")
                lfCmd("let &t_ve = remove(g:lf_t_ve_stack, -1)")
    return deco


#*****************************************************
# LfCli
#*****************************************************
class LfCli(object):
    def __init__(self):
        self._instance = None
        self._cmdline = []
        self._pattern = ''
        self._cursor_pos = 0
        self._start_time = datetime.now()
        self._idle = False
        self._blinkon = True
        self._key_dict = lfEval("g:Lf_KeyDict")
        self._refine = False
        self._delimiter = lfEval("g:Lf_DelimiterChar")
        self._and_delimiter = lfEval("get(g:, 'Lf_AndDelimiter', ' ')")
        self._supports_nameonly = False
        self._supports_refine = False
        self._is_and_mode = False
        self._running_status = 0
        self._input_buf_namespace = None
        self._setDefaultMode()
        self._is_live = False
        self._additional_prompt_string = ''
        self._quick_select = False
        self.last_char = ''
        self._spin_symbols = lfEval("get(g:, 'Lf_SpinSymbols', [])")
        if not self._spin_symbols:
            if platform.system() == "Linux":
                self._spin_symbols = ['✵', '⋆', '✶','✷','✸','✹', '✺']
            else:
                self._spin_symbols = ['🌘', '🌗', '🌖', '🌕', '🌔', '🌓', '🌒', '🌑']

    def setInstance(self, instance):
        self._instance = instance

    def setArguments(self, arguments):
        self._arguments = arguments
        quick_select = self._arguments.get("--quick-select", [0])
        if len(quick_select) == 0:
            quick_select_value = 1
        else:
            quick_select_value = int(quick_select[0])

        if "--quick-select" in self._arguments:
            self._quick_select = not self._instance.isReverseOrder() and bool(quick_select_value)
        else:
            self._quick_select = (not self._instance.isReverseOrder()
                                  and bool(int(lfEval("get(g:, 'Lf_QuickSelect', 0)"))))

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
        self._is_live = False
        if mode == 'NameOnly':       # nameOnly mode
            self._is_fuzzy = True
            self._is_full_path = False
        elif mode == 'FullPath':     # fullPath mode
            self._is_fuzzy = True
            self._is_full_path = True
        elif mode == 'Fuzzy':     # fuzzy mode
            self._is_fuzzy = True
            self._is_full_path = False
        elif mode == 'Live':     # live mode
            self._is_fuzzy = False
            self._is_live = True
        else:               # regex mode
            self._is_fuzzy = False

    def _insert(self, ch):
        self._cmdline.insert(self._cursor_pos, ch)
        self._cursor_pos += 1

    def _paste(self):
        for ch in lfEval("@*"):
            if ch == '\n':
                break
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

    def _delLeftWord(self):
        orig_cursor_pos = self._cursor_pos
        # clear trailing spaces
        while self._cursor_pos > 0 and self._cmdline[self._cursor_pos-1] == ' ':
            self._cursor_pos -= 1
        while self._cursor_pos > 0 and self._cmdline[self._cursor_pos-1] != ' ':
            self._cursor_pos -= 1

        self._cmdline[self._cursor_pos:orig_cursor_pos] = []

    def clear(self):
        self._cmdline[:] = []
        self._cursor_pos = 0
        self._pattern = ''
        if self._instance and self._instance.getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'silent! syn clear Lf_hl_match')""" % self._instance.getPopupWinId())
            lfCmd("""call win_execute(%d, 'silent! syn clear Lf_hl_match_refine')""" % self._instance.getPopupWinId())
        else:
            lfCmd("silent! syn clear Lf_hl_match")
            lfCmd("silent! syn clear Lf_hl_match_refine")

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
        self._cmdline = list(pattern)
        self._cursor_pos = len(self._cmdline)
        self._buildPattern()

    def _buildPopupPrompt(self):
        self._instance.mimicCursor()

        if self._is_fuzzy:
            if self._is_full_path:
                prompt = ' >F> {}'.format(self._additional_prompt_string)
            else:
                prompt = ' >>> {}'.format(self._additional_prompt_string)
        elif self._is_live:
            prompt = ' >>> {}'.format(self._additional_prompt_string)
        else:
            prompt = ' R>> {}'.format(self._additional_prompt_string)

        pattern = ''.join(self._cmdline)
        input_window = self._instance.getPopupInstance().input_win
        content_winid = self._instance.getPopupInstance().content_win.id
        input_win_width = input_window.width
        if lfEval("get(g:, 'Lf_PopupShowBorder', 1)") == '1' and lfEval("has('nvim')") == '0':
            input_win_width -= 2
        if self._instance.getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'let line_num = line(".")')""" % content_winid)
            line_num = lfEval("line_num")
        else:
            line_num = lfEval("line('.')")
        result_count = lfEval("g:Lf_{}_StlResultsCount".format(self._instance._category))
        total = lfEval("g:Lf_{}_StlTotal".format(self._instance._category))

        part1 = prompt + pattern
        part2 = "{}/{}".format(line_num, result_count)
        part3 = total
        sep = lfEval("g:Lf_StlSeparator.right")
        if lfEval("g:Lf_{}_IsRunning".format(self._instance._category)) == '1':
            spin = "{}".format(self._spin_symbols[self._running_status])
            self._running_status = (self._running_status + 1) % len(self._spin_symbols)
        else:
            spin = ""
            self._running_status = 0

        input_win_width += 2 * (len(sep) - int(lfEval("strdisplaywidth('%s')" % escQuote(sep))))
        input_win_width += len(pattern) - int(lfEval("strdisplaywidth('%s')" % escQuote(pattern)))
        input_win_width += len(spin) - int(lfEval("strdisplaywidth('%s')" % spin))

        part3_start = input_win_width - len(part3) - 2
        sep2_start = part3_start - len(sep)
        part2_start = sep2_start - 2 - len(part2)
        sep1_start = part2_start - len(sep)
        spin_start = sep1_start - 1 - len(spin)
        part1_width = spin_start - 1
        text = "{:<{part1_width}} {} {:>{sep_width}} {:>{part2_width}} {:>{sep_width}} {:>{part3_width}} ".format(part1,
                                                                               spin,
                                                                               sep,
                                                                               part2,
                                                                               sep,
                                                                               part3,
                                                                               sep_width=len(sep),
                                                                               part1_width=max(0, part1_width),
                                                                               part2_width=len(part2),
                                                                               part3_width=len(part3))
        if self._instance.getWinPos() == 'popup':
            lfCmd("""call popup_settext(%d, '%s')""" % (input_window.id, escQuote(text)))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_prompt'})")""" % input_window.id)
            lfCmd("""call win_execute(%d, "call prop_add(1, 1, {'length': %d, 'type': 'Lf_hl_popup_prompt'})")"""
                    % (input_window.id, lfBytesLen(prompt)))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_cursor'})")""" % input_window.id)
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': 1, 'type': 'Lf_hl_popup_cursor'})")"""
                    % (input_window.id, lfBytesLen(prompt) + lfBytesLen(''.join(self._cmdline[:self._cursor_pos])) + 1))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_total'})")""" % (input_window.id))
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_total'})")"""
                    % (input_window.id, lfBytesLen(text[:part3_start]) + 1, len(part3) + 2))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep5'})")"""
                        % (input_window.id, self._instance._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep5'})")"""
                        % (input_window.id, lfBytesLen(text[:sep2_start]) + 1, lfBytesLen(sep), self._instance._category))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_lineInfo'})")""" % (input_window.id))
            lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_lineInfo'})")"""
                    % (input_window.id, lfBytesLen(text[:part2_start]) + 1, len(part2) + 2))

            if sep != "":
                lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_%s_sep4'})")"""
                        % (input_window.id, self._instance._category))
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_%s_sep4'})")"""
                        % (input_window.id, lfBytesLen(text[:sep1_start]) + 1, lfBytesLen(sep), self._instance._category))

            lfCmd("""call win_execute(%d, "call prop_remove({'type': 'Lf_hl_popup_spin'})")""" % (input_window.id))
            if spin != "":
                lfCmd("""call win_execute(%d, "call prop_add(1, %d, {'length': %d, 'type': 'Lf_hl_popup_spin'})")"""
                        % (input_window.id, lfBytesLen(text[:spin_start]) + 1, lfBytesLen(spin)))
        else:
            input_window.buffer[0] = text

            if self._input_buf_namespace is None:
                self._input_buf_namespace = int(lfEval("nvim_create_namespace('')"))
            else:
                lfCmd("call nvim_buf_clear_namespace(%d, %d, 0, -1)"
                        % (input_window.buffer.number, self._input_buf_namespace))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_prompt', 0, 0, %d)"
                    % (input_window.buffer.number, self._input_buf_namespace, lfBytesLen(prompt)))
            cursor_pos = lfBytesLen(prompt) + lfBytesLen(''.join(self._cmdline[:self._cursor_pos]))
            if self._cursor_pos == len(self._cmdline):
                cursor_pos_end = cursor_pos + 1
            else:
                cursor_pos_end = cursor_pos + lfBytesLen(self._cmdline[self._cursor_pos])
            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_cursor', 0, %d, %d)"
                    % (input_window.buffer.number, self._input_buf_namespace, cursor_pos, cursor_pos_end))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_total', 0, %d, %d)"
                    % (input_window.buffer.number, self._input_buf_namespace,
                        lfBytesLen(text[:part3_start]), lfBytesLen(text[:part3_start]) + len(part3) + 2))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep5', 0, %d, %d)"
                        % (input_window.buffer.number, self._input_buf_namespace, self._instance._category,
                            lfBytesLen(text[:sep2_start]), lfBytesLen(text[:sep2_start]) + lfBytesLen(sep)))

            lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_lineInfo', 0, %d, %d)"
                    % (input_window.buffer.number, self._input_buf_namespace,
                        lfBytesLen(text[:part2_start]), lfBytesLen(text[:part2_start]) + len(part2) + 2))

            if sep != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_%s_sep4', 0, %d, %d)"
                        % (input_window.buffer.number, self._input_buf_namespace, self._instance._category,
                            lfBytesLen(text[:sep1_start]), lfBytesLen(text[:sep1_start]) + lfBytesLen(sep)))

            if spin != "":
                lfCmd("call nvim_buf_add_highlight(%d, %d, 'Lf_hl_popup_spin', 0, %d, %d)"
                        % (input_window.buffer.number, self._input_buf_namespace,
                            lfBytesLen(text[:spin_start]), lfBytesLen(text[:spin_start]) + lfBytesLen(spin)))

    def buildPopupPrompt(self):
        self._buildPopupPrompt()
        lfCmd("silent! redraw")

    def _buildPrompt(self):
        if self._idle and datetime.now() - self._start_time < timedelta(milliseconds=500): # 500ms
            return
        else:
            self._start_time = datetime.now()
            if self._blinkon:
                lfCmd("hi! default link Lf_hl_cursor Lf_hl_popup_cursor")
            else:
                lfCmd("hi! default link Lf_hl_cursor NONE")

            if lfEval("g:Lf_CursorBlink") == '1':
                self._blinkon = not self._blinkon
            elif self._idle:
                lfCmd("silent! redraw")
                return

        if self._instance.getWinPos() in ('popup', 'floatwin'):
            self.buildPopupPrompt()
            return

        if self._is_fuzzy:
            if self._is_full_path:
                lfCmd("echohl Constant | echon '>F> {}' | echohl NONE".format(self._additional_prompt_string))
            else:
                lfCmd("echohl Constant | echon '>>> {}' | echohl NONE".format(self._additional_prompt_string))
        elif self._is_live:
            lfCmd("echohl Constant | echon '>>> {}' | echohl NONE".format(self._additional_prompt_string))
        else:
            lfCmd("echohl Constant | echon 'R>> {}' | echohl NONE".format(self._additional_prompt_string))

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
        case_insensitive = "--case-insensitive" in self._arguments
        if self._is_fuzzy:
            if self._and_delimiter in ''.join(self._cmdline).lstrip(self._and_delimiter) \
                    and self._delimiter not in self._cmdline:
                self._is_and_mode = True
                if case_insensitive:
                    patterns = re.split(r'['+self._and_delimiter+']+',
                                        ''.join(self._cmdline).strip(self._and_delimiter).lower())
                else:
                    patterns = re.split(r'['+self._and_delimiter+']+',
                                        ''.join(self._cmdline).strip(self._and_delimiter))
                pattern_dict = OrderedDict([])
                for p in patterns:
                    if p in pattern_dict:
                        pattern_dict[p] += 1
                    else:
                        pattern_dict[p] = 1
                self._pattern = tuple([i * pattern_dict[i] for i in pattern_dict])
                if self._pattern == ('',):
                    self._pattern = None
            else:
                self._is_and_mode = False

                # supports refinement only in nameOnly mode
                if (((self._supports_nameonly and not self._is_full_path) or
                        self._supports_refine) and self._delimiter in self._cmdline):
                    self._refine = True
                    idx = self._cmdline.index(self._delimiter)
                    if case_insensitive:
                        self._pattern = (''.join(self._cmdline[:idx]).lower(),
                                         ''.join(self._cmdline[idx+1:]).lower())
                    else:
                        self._pattern = (''.join(self._cmdline[:idx]),
                                         ''.join(self._cmdline[idx+1:]))
                    if self._pattern == ('', ''):
                        self._pattern = None
                else:
                    self._refine = False
                    if case_insensitive:
                        self._pattern = ''.join(self._cmdline).lower()
                    else:
                        self._pattern = ''.join(self._cmdline)
        else:
            self._is_and_mode = False
            self._pattern = ''.join(self._cmdline)

    def _join(self, cmdline):
        if not cmdline:
            return ''
        cmd = [r'%s\[^%s]\{-}' % (c, c) for c in cmdline[0:-1]]
        cmd.append(cmdline[-1])
        regex = ''.join(cmd)
        return regex

    def highlightMatches(self):
        if self._instance.getWinPos() == 'popup':
            lfCmd("""call win_execute(%d, 'silent! syn clear Lf_hl_match')""" % self._instance.getPopupWinId())
            lfCmd("""call win_execute(%d, 'silent! syn clear Lf_hl_match_refine')""" % self._instance.getPopupWinId())
        else:
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
                regex = r'\c\V' + self._join(cmdline)
                lfCmd("syn match Lf_hl_match display /%s/ containedin="
                      "Lf_hl_nonHelp, Lf_hl_dirname, Lf_hl_filename contained" % regex)
            else:
                if self._refine:
                    idx = self._cmdline.index(self._delimiter)
                    regex = (r'\c\V' + self._join(cmdline[:idx]),
                             r'\c\V' + self._join(cmdline[idx+1:]))
                    if regex[0] == r'\c\V' and regex[1] == r'\c\V':
                        pass
                    elif regex[0] == r'\c\V':
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_dirname, Lf_hl_filename "
                              "contained" % regex[1])
                    elif regex[1] == r'\c\V':
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_filename contained" % regex[0])
                    else:
                        lfCmd("syn match Lf_hl_match display /%s/ "
                              "containedin=Lf_hl_filename contained" % regex[0])
                        lfCmd("syn match Lf_hl_match_refine display "
                              r"/%s\(\.\*\[\/]\)\@=/ containedin="
                              "Lf_hl_dirname contained" % regex[1])
                else:
                    regex = r'\c\V' + self._join(cmdline)
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
                    if self._instance.getWinPos() == 'popup':
                        lfCmd("""call win_execute(%d, 'syn match Lf_hl_match /%s/ containedin=Lf_hl_dirname, Lf_hl_filename contained')"""
                                % (self._instance.getPopupWinId(), regex))
                    else:
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

    def writeHistory(self, category):
        if not self._pattern:
            return

        if self._is_and_mode:
            pattern = self._and_delimiter.join(self._pattern)
        elif self._refine:
            pattern = self._delimiter.join(self._pattern)
        else:
            pattern = self._pattern

        history_dir = os.path.join(lfEval("g:Lf_CacheDirectory"), 'LeaderF', 'history', category)
        if self._is_fuzzy:
            history_file = os.path.join(history_dir, 'fuzzy.txt')
        else:
            history_file = os.path.join(history_dir, 'regex.txt')

        if not os.path.exists(history_dir):
            os.makedirs(history_dir)

        if not os.path.exists(history_file):
            with lfOpen(history_file, 'w', errors='ignore'):
                pass

        with lfOpen(history_file, 'r+', errors='ignore') as f:
            lines = f.readlines()

            pattern += '\n'
            if pattern in lines:
                lines.remove(pattern)

            if len(lines) >= int(lfEval("get(g:, 'Lf_HistoryNumber', '100')")):
                del lines[0]

            lines.append(pattern)

            f.seek(0)
            f.truncate(0)
            f.writelines(lines)

    def previousHistory(self, category):
        history_dir = os.path.join(lfEval("g:Lf_CacheDirectory"), 'LeaderF', 'history', category)
        if self._is_fuzzy:
            history_file = os.path.join(history_dir, 'fuzzy.txt')
        else:
            history_file = os.path.join(history_dir, 'regex.txt')

        if not os.path.exists(history_file):
            return False

        with lfOpen(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            if self._history_index == 0:
                self._pattern_backup = self._pattern

            if -self._history_index < len(lines):
                self._history_index -= 1
                self.setPattern(lines[self._history_index].rstrip())
            else:
                return False

        return True

    def nextHistory(self, category):
        history_dir = os.path.join(lfEval("g:Lf_CacheDirectory"), 'LeaderF', 'history', category)
        if self._is_fuzzy:
            history_file = os.path.join(history_dir, 'fuzzy.txt')
        else:
            history_file = os.path.join(history_dir, 'regex.txt')

        if not os.path.exists(history_file):
            return False

        with lfOpen(history_file, 'r', errors='ignore') as f:
            lines = f.readlines()
            if self._history_index < 0:
                self._history_index += 1
                if self._history_index == 0:
                    self.setPattern(self._pattern_backup)
                else:
                    self.setPattern(lines[self._history_index].rstrip())
            else:
                return False

        return True

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
    def isAndMode(self):
        return self._is_and_mode

    @property
    def isFuzzy(self):
        return self._is_fuzzy

    @cursorController
    def input(self, callback):
        try:
            self._history_index = 0
            self._blinkon = True
            start = time.time()
            update = False
            prefix = ""

            while 1:
                if len(self._instance._manager._content) < 60000:
                    threshold = 0.01
                else:
                    threshold = 0.10

                self._buildPrompt()
                self._idle = False

                if lfEval("has('nvim') && exists('g:GuiLoaded')") == '1':
                    time.sleep(0.005) # this is to solve issue 375 leaderF hangs in nvim-qt
                else:
                    time.sleep(0.001)

                if lfEval("get(g:, 'Lf_NoAsync', 0)") == '0':
                    lfCmd("let nr = getchar(1)")
                    if lfEval("!type(nr) && nr == 0") == '1':
                        self._idle = True
                        if lfEval("has('nvim') && exists('g:GuiLoaded')") == '1':
                            time.sleep(0.009) # this is to solve issue 375 leaderF hangs in nvim-qt

                        if update == True:
                            if time.time() - start >= threshold:
                                update = False
                                if ''.join(self._cmdline).startswith(prefix):
                                    yield '<Update>'
                                else:
                                    yield '<Shorten>'
                                start = time.time()
                        else:
                            try:
                                callback()
                            except Exception:
                                lfPrintTraceback()
                                break

                        continue
                    # https://groups.google.com/forum/#!topic/vim_dev/gg-l-kaCz_M
                    # '<80><fc>^B' is <Shift>, '<80><fc>^D' is <Ctrl>,
                    # '<80><fc>^H' is <Alt>, '<80><fc>^L' is <Ctrl + Alt>
                    elif lfEval("type(nr) != 0") == '1':
                        lfCmd("call getchar(0)")
                        lfCmd("call feedkeys('a') | call getchar()")
                        self._idle = True
                        if lfEval("has('nvim') && exists('g:GuiLoaded')") == '1':
                            time.sleep(0.009) # this is to solve issue 375 leaderF hangs in nvim-qt

                        if update == True:
                            if time.time() - start >= threshold:
                                update = False
                                if ''.join(self._cmdline).startswith(prefix):
                                    yield '<Update>'
                                else:
                                    yield '<Shorten>'
                                start = time.time()
                        else:
                            try:
                                callback()
                            except Exception:
                                lfPrintTraceback()
                                break

                        continue
                    else:
                        lfCmd("let nr = getchar()")
                        lfCmd("let ch = !type(nr) ? nr2char(nr) : nr")
                        self._blinkon = True
                else:
                    threshold = 0
                    lfCmd("let nr = getchar()")
                    lfCmd("let ch = !type(nr) ? nr2char(nr) : nr")
                    self._blinkon = True

                if lfEval("!type(nr) && nr >= 0x20") == '1':
                    char = lfEval("ch")
                    if self._quick_select and char in "0123456789":
                        self.last_char = char
                        yield '<QuickSelect>'
                        continue

                    if update == False:
                        update = True
                        prefix = ''.join(self._cmdline)

                    self._insert(char)
                    self._buildPattern()
                    if self._pattern is None or (self._refine and self._pattern[1] == ''): # e.g. abc;
                        continue

                    if time.time() - start < threshold:
                        continue
                    else:
                        update = False
                        yield '<Update>'
                        start = time.time()
                else:
                    cmd = ''
                    for (key, value) in self._key_dict.items():
                        if lfEval(r'ch ==# "\%s"' % key) == '1':
                            cmd = value
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
                        if not self._is_live:
                            self._is_fuzzy = not self._is_fuzzy
                            self._buildPattern()
                            yield '<Mode>'
                    elif equal(cmd, '<BS>') or equal(cmd, '<C-H>'):
                        if not self._pattern and self._refine == False:
                            continue

                        if update == False:
                            update = True
                            prefix = ''.join(self._cmdline)

                        self._backspace()
                        self._buildPattern()

                        if self._pattern and time.time() - start < threshold:
                            continue
                        else:
                            update = False
                            yield '<Shorten>'
                            start = time.time()
                    elif equal(cmd, '<C-U>'):
                        if not self._pattern and self._refine == False:
                            continue
                        self._clearLeft()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<C-W>'):
                        if not self._pattern and self._refine == False:
                            continue
                        self._delLeftWord()
                        self._buildPattern()
                        yield '<Shorten>'
                    elif equal(cmd, '<Del>'):
                        if not self._pattern and self._refine == False:
                            continue
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
                    elif equal(cmd, '<ScrollWheelUp>'):
                        yield '<ScrollWheelUp>'
                    elif equal(cmd, '<ScrollWheelDown>'):
                        yield '<ScrollWheelDown>'
                    elif equal(cmd, '<C-C>'):
                        yield '<Quit>'
                    else:
                        yield cmd
        except KeyboardInterrupt: # <C-C>
            yield '<Quit>'
        except vim.error: # for neovim
            lfCmd("call getchar(0)")
            yield '<Quit>'

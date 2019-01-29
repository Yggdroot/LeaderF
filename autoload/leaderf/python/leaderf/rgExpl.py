#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import tempfile
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *
from .mru import *


#*****************************************************
# RgExplorer
#*****************************************************
class RgExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._pattern_regex = []
        self._context_separator = "..."
        self._display_multi = False

    def getContent(self, *args, **kwargs):
        if "--recall" in kwargs.get("arguments", {}):
            return []

        rg_config = lfEval("get(g:, 'Lf_RgConfig', [])")
        extra_options = ' '.join(rg_config)
        for opt in rg_config:
            opt = opt.strip()
            if opt.startswith("--context-separator"):
                self._context_separator = re.split(r'=|\s+', opt)[1]
                if self._context_separator.startswith('"') and self._context_separator.endswith('"'):
                    self._context_separator = self._context_separator[1:-1]
            if self._display_multi == False and (opt.startswith("-A") or opt.startswith("-B")
                    or opt.startswith("-C") or opt.startswith("--after-context")
                    or opt.startswith("--before-context") or opt.startswith("--context")):
                self._display_multi = True

        arg_line = kwargs.get("arguments", {}).get("arg_line")
        # -S/--smart-case, -s/--case-sensitive, -i/--ignore-case
        index = {}
        index['-S'] = max(arg_line.rfind(' -S '), arg_line.rfind(' --smart-case '))
        index['-s'] = max(arg_line.rfind(' -s '), arg_line.rfind(' --case-sensitive '))
        if index['-S'] > index['-s']:
            case_flag = '-S'
            max_index = index['-S']
        else:
            case_flag = '-s'
            max_index = index['-s']
        index['-i'] = max(arg_line.rfind(' -i '), arg_line.rfind(' --ignore-case '))
        if index['-i'] > max_index:
            case_flag = '-i'
            max_index = index['-i']

        if max_index == -1:
            case_flag = '-S'

        # -x/--line-regex, -w/--word-regexp
        index['-x'] = max(arg_line.rfind(' -x '), arg_line.rfind(' --line-regexp '))
        index['-w'] = max(arg_line.rfind(' -w '), arg_line.rfind(' --word-regexp '))
        if index['-x'] > index['-w']:
            word_or_line = '-x '
        elif index['-x'] < index['-w']:
            word_or_line = '-w '
        else:
            word_or_line = ''

        zero_args_options = ''
        if "-F" in kwargs.get("arguments", {}):
            zero_args_options += "-F "
        if "-L" in kwargs.get("arguments", {}):
            zero_args_options += "-L "
        if "-P" in kwargs.get("arguments", {}):
            zero_args_options += "-P "
            is_perl = True
        else:
            is_perl = False
        if "-v" in kwargs.get("arguments", {}):
            zero_args_options += "-v "
        if "--hidden" in kwargs.get("arguments", {}):
            zero_args_options += "--hidden "
        if "--no-config" in kwargs.get("arguments", {}):
            zero_args_options += "--no-config "
        if "--no-ignore" in kwargs.get("arguments", {}):
            zero_args_options += "--no-ignore "
        if "--no-ignore-global" in kwargs.get("arguments", {}):
            zero_args_options += "--no-ignore-global "
        if "--no-ignore-parent" in kwargs.get("arguments", {}):
            zero_args_options += "--no-ignore-parent "
        if "--no-ignore-vcs" in kwargs.get("arguments", {}):
            zero_args_options += "--no-ignore-vcs "
        if "--no-pcre2-unicode" in kwargs.get("arguments", {}):
            zero_args_options += "--no-pcre2-unicode "

        one_args_options = ''
        if "--context-separator" in kwargs.get("arguments", {}):
            self._context_separator = kwargs.get("arguments", {})["--context-separator"][0]
            if self._context_separator.startswith('"') and self._context_separator.endswith('"'):
                self._context_separator = self._context_separator[1:-1]
            one_args_options += '--context-separator="%s" ' % self._context_separator
        else:
            one_args_options += "--context-separator=%s " % self._context_separator
        if "-A" in kwargs.get("arguments", {}):
            one_args_options += "-A %s " % kwargs.get("arguments", {})["-A"][0]
            self._display_multi = True
        if "-B" in kwargs.get("arguments", {}):
            one_args_options += "-B %s " % kwargs.get("arguments", {})["-B"][0]
            self._display_multi = True
        if "-C" in kwargs.get("arguments", {}):
            one_args_options += "-C %s " % kwargs.get("arguments", {})["-C"][0]
            self._display_multi = True
        if "-E" in kwargs.get("arguments", {}):
            one_args_options += "-E %s " % kwargs.get("arguments", {})["-E"][0]
        if "-M" in kwargs.get("arguments", {}):
            one_args_options += "-M %s " % kwargs.get("arguments", {})["-M"][0]
        if "-m" in kwargs.get("arguments", {}):
            one_args_options += "-m %s " % kwargs.get("arguments", {})["-m"][0]
        if "--max-depth" in kwargs.get("arguments", {}):
            one_args_options += "--max-depth %s " % kwargs.get("arguments", {})["--max-depth"][0]
        if "--max-filesize" in kwargs.get("arguments", {}):
            one_args_options += "--max-filesize %s " % kwargs.get("arguments", {})["--max-filesize"][0]
        if "--path-separator" in kwargs.get("arguments", {}):
            one_args_options += "--path-separator %s " % kwargs.get("arguments", {})["--path-separator"][0]
        if "--sort" in kwargs.get("arguments", {}):
            one_args_options += "--sort %s " % kwargs.get("arguments", {})["--sort"][0]
        if "--sortr" in kwargs.get("arguments", {}):
            one_args_options += "--sortr %s " % kwargs.get("arguments", {})["--sortr"][0]

        repeatable_options = ''
        if "-f" in kwargs.get("arguments", {}):
            repeatable_options += "-f %s " % " -f ".join(kwargs.get("arguments", {})["-f"])
        if "-g" in kwargs.get("arguments", {}):
            repeatable_options += "-g %s " % " -g ".join(kwargs.get("arguments", {})["-g"])
        if "--iglob" in kwargs.get("arguments", {}):
            repeatable_options += "--iglob %s " % " --iglob ".join(kwargs.get("arguments", {})["--iglob"])
        if "--ignore-file" in kwargs.get("arguments", {}):
            repeatable_options += "--ignore-file %s " % " --ignore-file ".join(kwargs.get("arguments", {})["--ignore-file"])
        if "--type-add" in kwargs.get("arguments", {}):
            repeatable_options += "--type-add %s " % " --type-add ".join(kwargs.get("arguments", {})["--type-add"])
        if "-t" in kwargs.get("arguments", {}):
            repeatable_options += "-t %s " % " -t ".join(kwargs.get("arguments", {})["-t"])
        if "-T" in kwargs.get("arguments", {}):
            repeatable_options += "-T %s " % " -T ".join(kwargs.get("arguments", {})["-T"])

        is_literal = "-F" in kwargs.get("arguments", {})
        pattern = ''
        if "--append" not in kwargs.get("arguments", {}):
            self._pattern_regex = []

        for i in kwargs.get("arguments", {}).get("-e", []):
            pattern += r'-e %s ' % i
            if case_flag == '-i':
                case_pattern = r'\c'
            elif case_flag == '-s':
                case_pattern = r'\C'
            else: # smart-case
                if (i + 'a').islower():
                    case_pattern = r'\c'
                else:
                    case_pattern = r'\C'

            if len(i) > 1 and (i[0] == i[-1] == '"' or i[0] == i[-1] == "'"):
                p = i[1:-1]
            else:
                p = i

            # -e ""
            if p == '':
                continue

            if is_literal:
                if len(i) > 1 and i[0] == i[-1] == '"':
                    p = re.sub(r'\\(?!")', r'\\\\', p)
                else:
                    p = p.replace('\\', r'\\')

                if word_or_line == '-w ':
                    p = r'\<' + p + r'\>'

                self._pattern_regex.append(r'\V' + case_pattern + p)
            else:
                if word_or_line == '-w ':
                    p = '<' + p + '>'
                self._pattern_regex.append(self.translateRegex(case_pattern + p, is_perl))

        if pattern == '':
            pattern = '"" '

        path = ' '.join(kwargs.get("arguments", {}).get("PATH", []))
        if path == '' and os.name == 'nt':
            path = '.'

        tmpfilenames = []
        def removeFiles(names):
            for i in names:
                try:
                    os.remove(i)
                except:
                    pass

        if sys.version_info >= (3, 0):
            tmp_file = partial(tempfile.NamedTemporaryFile, encoding=lfEval("&encoding"))
        else:
            tmp_file = tempfile.NamedTemporaryFile

        if "--current-buffer" in kwargs.get("arguments", {}):
            path = ''   # omit the <PATH> option
            if vim.current.buffer.name:
                try:
                    path = '"%s"' % os.path.relpath(lfDecode(vim.current.buffer.name))
                except ValueError:
                    path = '"%s"' % lfDecode(vim.current.buffer.name)
            else:
                file_name = '%d_`No_Name_%d`' % (os.getpid(), vim.current.buffer.number)
                try:
                    with lfOpen(file_name, 'w', errors='ignore') as f:
                        for line in vim.current.buffer[:]:
                            f.write(line + '\n')
                except IOError:
                    with tmp_file(mode='w', suffix='_'+file_name, delete=False) as f:
                        file_name = lfDecode(f.name)
                        for line in vim.current.buffer[:]:
                            f.write(line + '\n')

                path = '"' + file_name + '"'
                tmpfilenames.append(file_name)

        if "--all-buffers" in kwargs.get("arguments", {}):
            path = ''   # omit the <PATH> option
            for b in vim.buffers:
                if lfEval("buflisted(%d)" % b.number) == '1':
                    if b.name:
                        try:
                            path += '"' + os.path.relpath(lfDecode(b.name)) + '" '
                        except ValueError:
                            path += '"' + lfDecode(b.name) + '" '
                    else:
                        file_name = '%d_`No_Name_%d`' % (os.getpid(), b.number)
                        try:
                            with lfOpen(file_name, 'w', errors='ignore') as f:
                                for line in b[:]:
                                    f.write(line + '\n')
                        except IOError:
                            with tmp_file(mode='w', suffix='_'+file_name, delete=False) as f:
                                file_name = lfDecode(f.name)
                                for line in b[:]:
                                    f.write(line + '\n')

                        path += '"' + file_name + '" '
                        tmpfilenames.append(file_name)

        executor = AsyncExecutor()
        self._executor.append(executor)
        cmd = '''rg {} --no-config --no-ignore-messages --no-heading --with-filename --color never --line-number '''\
                '''{} {}{}{}{}{}{}'''.format(extra_options, case_flag, word_or_line, zero_args_options,
                                                  one_args_options, repeatable_options, lfDecode(pattern), path)
        lfCmd("let g:Lf_Debug_RgCmd = '%s'" % escQuote(cmd))
        content = executor.execute(cmd, encoding=lfEval("&encoding"), cleanup=partial(removeFiles, tmpfilenames))
        return content

    def translateRegex(self, regex, is_perl=False):
        vim_regex = regex

        vim_regex = re.sub(r'([%@&])', r'\\\1', vim_regex)

        # non-greedy pattern
        vim_regex = re.sub(r'(?<!\\)\*\?', r'{-}', vim_regex)
        vim_regex = re.sub(r'(?<!\\)\+\?', r'{-1,}', vim_regex)
        vim_regex = re.sub(r'(?<!\\)\?\?', r'{-0,1}', vim_regex)
        vim_regex = re.sub(r'(?<!\\)\{(.*?)\}\?', r'{-\1}', vim_regex)

        if is_perl:
            # *+, ++, ?+, {m,n}+ => *, +, ?, {m,n}
            vim_regex = re.sub(r'(?<!\\)([*+?}])\+', r'\1', vim_regex)
            # remove (?#....)
            vim_regex = re.sub(r'\(\?#.*?\)', r'', vim_regex)
            # (?=atom) => atom\@=
            vim_regex = re.sub(r'\(\?=(.+?)\)', r'(\1)@=', vim_regex)
            # (?!atom) => atom\@!
            vim_regex = re.sub(r'\(\?!(.+?)\)', r'(\1)@!', vim_regex)
            # (?<=atom) => atom\@<=
            vim_regex = re.sub(r'\(\?<=(.+?)\)', r'(\1)@<=', vim_regex)
            # (?<!atom) => atom\@<!
            vim_regex = re.sub(r'\(\?<!(.+?)\)', r'(\1)@<!', vim_regex)
            # (?>atom) => atom\@>
            vim_regex = re.sub(r'\(\?>(.+?)\)', r'(\1)@>', vim_regex)

        # this won't hurt although they are not the same
        vim_regex = vim_regex.replace(r'\A', r'^')
        vim_regex = vim_regex.replace(r'\z', r'$')
        vim_regex = vim_regex.replace(r'\B', r'')

        # word boundary
        vim_regex = re.sub(r'\\b', r'(<|>)', vim_regex)

        # case-insensitive
        vim_regex = vim_regex.replace(r'(?i)', r'\c')
        vim_regex = vim_regex.replace(r'(?-i)', r'\C')

        # (?P<name>exp) => (exp)
        vim_regex = re.sub(r'(?<=\()\?P<\w+>', r'', vim_regex)

        # (?:exp) => %(exp)
        vim_regex =  re.sub(r'\(\?:(.+?)\)', r'%(\1)', vim_regex)

        # \a          bell (\x07)
        # \f          form feed (\x0C)
        # \v          vertical tab (\x0B)
        vim_regex = vim_regex.replace(r'\a', r'%x07')
        vim_regex = vim_regex.replace(r'\f', r'%x0C')
        vim_regex = vim_regex.replace(r'\v', r'%x0B')

        # \123        octal character code (up to three digits) (when enabled)
        # \x7F        hex character code (exactly two digits)
        vim_regex = re.sub(r'\\(x[0-9A-Fa-f][0-9A-Fa-f])', r'%\1', vim_regex)
        # \x{10FFFF}  any hex character code corresponding to a Unicode code point
        # \u007F      hex character code (exactly four digits)
        # \u{7F}      any hex character code corresponding to a Unicode code point
        # \U0000007F  hex character code (exactly eight digits)
        # \U{7F}      any hex character code corresponding to a Unicode code point
        vim_regex = re.sub(r'\\([uU])', r'%\1', vim_regex)

        vim_regex = re.sub(r'\[\[:ascii:\]\]', r'[\\x00-\\x7F]', vim_regex)
        vim_regex = re.sub(r'\[\[:word:\]\]', r'[0-9A-Za-z_]', vim_regex)

        vim_regex = vim_regex.replace(r'[[:^alnum:]]', r'[^0-9A-Za-z]')
        vim_regex = vim_regex.replace(r'[[:^alpha:]]', r'[^A-Za-z]')
        vim_regex = vim_regex.replace(r'[[:^ascii:]]', r'[^\x00-\x7F]')
        vim_regex = vim_regex.replace(r'[[:^blank:]]', r'[^\t ]')
        vim_regex = vim_regex.replace(r'[[:^cntrl:]]', r'[^\x00-\x1F\x7F]')
        vim_regex = vim_regex.replace(r'[[:^digit:]]', r'[^0-9]')
        vim_regex = vim_regex.replace(r'[[:^graph:]]', r'[^!-~]')
        vim_regex = vim_regex.replace(r'[[:^lower:]]', r'[^a-z]')
        vim_regex = vim_regex.replace(r'[[:^print:]]', r'[^ -~]')
        vim_regex = vim_regex.replace(r'[[:^punct:]]', r'[^!-/:-@\[-`{-~]')
        vim_regex = vim_regex.replace(r'[[:^space:]]', r'[^\t\n\r ]')
        vim_regex = vim_regex.replace(r'[[:^upper:]]', r'[^A-Z]')
        vim_regex = vim_regex.replace(r'[[:^word:]]', r'[^0-9A-Za-z_]')
        vim_regex = vim_regex.replace(r'[[:^xdigit:]]', r'[^0-9A-Fa-f]')

        return r'\v' + vim_regex

    def getStlCategory(self):
        return 'Rg'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def supportsNameOnly(self):
        return False

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []

    def getPatternRegex(self):
        return self._pattern_regex

    def getContextSeparator(self):
        return self._context_separator

    def displayMulti(self):
        return self._display_multi


#*****************************************************
# RgExplManager
#*****************************************************
class RgExplManager(Manager):
    def __init__(self):
        super(RgExplManager, self).__init__()
        self._match_ids = []
        self._match_path = False
        self._has_column = False

    def _getExplClass(self):
        return RgExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Rg#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        m = re.match(r'^(.+?)[:-](\d+)[:-]', line)
        file, line_num = m.group(1, 2)
        if file.startswith('+'):
            file = os.path.abspath(file)

        match = re.search(r'\d+_`No_Name_(\d+)`', file)
        if match:
            buf_number = match.group(1)
        else:
            buf_number = -1

        try:
            if buf_number == -1:
                lfCmd("hide edit +%s %s" % (line_num, escSpecial(file)))
            else:
                lfCmd("hide buffer +%s %s" % (line_num, buf_number))
            lfCmd("norm! zz")
            lfCmd("setlocal cursorline! | redraw | sleep 20m | setlocal cursorline!")
        except vim.error as e:
            lfPrintError(e)

    def setArguments(self, arguments):
        self._arguments = arguments
        self._match_path = "--match-path" in arguments
        if "--recall" not in self._arguments:
            self._has_column = "--column" in lfEval("get(g:, 'Lf_RgConfig', [])")

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if self._match_path:
            return line
        else:
            if self._getExplorer().displayMulti():
                if line == self._getExplorer().getContextSeparator():
                    return ""

                if self._has_column:
                    m = re.match(r'^.+?[:-]\d+[:-]', line)
                    file_lineno = m.group(0)
                    if file_lineno.endswith(':'):
                        index = line.find(':', len(file_lineno))
                        return line[index+1:]
                    else:
                        return line[len(file_lineno):]
                else:
                    m = re.match(r'^.+?[:-]\d+[:-]', line)
                    return line[len(m.group(0)):]
            else:
                if self._has_column:
                    return line.split(":", 3)[-1]
                else:
                    return line.split(":", 2)[-1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if self._match_path:
            return 0
        else:
            if self._getExplorer().displayMulti():
                if line == self._getExplorer().getContextSeparator():
                    return len(line)

                if self._has_column:
                    m = re.match(r'^.+?[:-]\d+[:-]', line)
                    file_lineno = m.group(0)
                    if file_lineno.endswith(':'):
                        index = line.find(':', len(file_lineno))
                        return lfBytesLen(line[:index + 1])
                    else:
                        return lfBytesLen(file_lineno)
                else:
                    m = re.match(r'^.+?[:-]\d+[:-]', line)
                    return lfBytesLen(m.group(0))
            else:
                if self._has_column:
                    file_path, line_num, column, content = line.split(":", 3)
                    return lfBytesLen(file_path + line_num + column) + 3
                else:
                    file_path, line_num, content = line.split(":", 2)
                    return lfBytesLen(file_path + line_num) + 2

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" p : preview the result')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q/<Esc> : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(RgExplManager, self)._afterEnter()
        id = int(lfEval("matchadd('Lf_hl_rgFileName', '^.\{-}\ze[:-]\d', 10)"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_rgLineNumber', '^.\{-}\zs:\d\+:', 10)"))
        self._match_ids.append(id)
        id = int(lfEval("matchadd('Lf_hl_rgLineNumber2', '^.\{-}\zs-\d\+-', 10)"))
        self._match_ids.append(id)
        if self._has_column:
            id = int(lfEval("matchadd('Lf_hl_rgColumnNumber', '^.\{-}:\d\+:\zs\d\+:', 10)"))
            self._match_ids.append(id)

        try:
            for i in self._getExplorer().getPatternRegex():
                id = int(lfEval("matchadd('Lf_hl_rgHighlight', '%s', 9)" % escQuote(i)))
                self._match_ids.append(id)
        except vim.error:
            pass

    def _beforeExit(self):
        super(RgExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None

    def _previewResult(self, preview):
        if not self._needPreview(preview):
            return

        line = self._getInstance().currentLine
        orig_pos = self._getInstance().getOriginalPos()
        cur_pos = (vim.current.tabpage, vim.current.window, vim.current.buffer)

        saved_eventignore = vim.options['eventignore']
        vim.options['eventignore'] = 'BufLeave,WinEnter,BufEnter'
        try:
            vim.current.tabpage, vim.current.window = orig_pos[:2]
            self._acceptSelection(line)
        finally:
            vim.current.tabpage, vim.current.window, vim.current.buffer = cur_pos
            vim.options['eventignore'] = saved_eventignore

    def _bangEnter(self):
        super(RgExplManager, self)._bangEnter()
        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return
        if "--recall" not in self._arguments:
            self._workInIdle(bang=True)
            if self._read_finished < 2:
                self._timer_id = lfEval("timer_start(1, 'leaderf#Rg#TimerCallback', {'repeat': -1})")


#*****************************************************
# rgExplManager is a singleton
#*****************************************************
rgExplManager = RgExplManager()

__all__ = ['rgExplManager']

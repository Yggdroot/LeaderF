#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import tempfile
import json
from functools import wraps
from .utils import *
from .explorer import *
from .manager import *
from .mru import *

def workingDirectory(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        if self._getExplorer()._cmd_work_dir == os.getcwd():
            return func(self, *args, **kwargs)

        # https://github.com/neovim/neovim/issues/8336
        if lfEval("has('nvim')") == '1':
            chdir = vim.chdir
        else:
            chdir = os.chdir
        orig_cwd = os.getcwd()
        chdir(self._getExplorer()._cmd_work_dir)
        try:
            return func(self, *args, **kwargs)
        finally:
            chdir(orig_cwd)

    return deco

#*****************************************************
# RgExplorer
#*****************************************************
class RgExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._pattern_regex = []
        self._context_separator = "..."
        self._display_multi = False
        self._cmd_work_dir = ""

    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" in arguments_dict:
            return []

        self._cmd_work_dir = os.getcwd()
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

        arg_line = arguments_dict.get("arg_line")
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
        if "-F" in arguments_dict:
            zero_args_options += "-F "
        if "-L" in arguments_dict:
            zero_args_options += "-L "
        if "-P" in arguments_dict:
            zero_args_options += "-P "
            is_perl = True
        else:
            is_perl = False
        if "-v" in arguments_dict:
            zero_args_options += "-v "
        if "--hidden" in arguments_dict:
            zero_args_options += "--hidden "
        if "--no-config" in arguments_dict:
            zero_args_options += "--no-config "
        if "--no-ignore" in arguments_dict:
            zero_args_options += "--no-ignore "
        if "--no-ignore-global" in arguments_dict:
            zero_args_options += "--no-ignore-global "
        if "--no-ignore-parent" in arguments_dict:
            zero_args_options += "--no-ignore-parent "
        if "--no-ignore-vcs" in arguments_dict:
            zero_args_options += "--no-ignore-vcs "
        if "--no-messages" in arguments_dict:
            zero_args_options += "--no-messages "
        if "--no-pcre2-unicode" in arguments_dict:
            zero_args_options += "--no-pcre2-unicode "

        one_args_options = ''
        if "--context-separator" in arguments_dict:
            self._context_separator = arguments_dict["--context-separator"][0]
            if self._context_separator.startswith('"') and self._context_separator.endswith('"'):
                self._context_separator = self._context_separator[1:-1]
            one_args_options += '--context-separator="%s" ' % self._context_separator
        else:
            one_args_options += "--context-separator=%s " % self._context_separator
        if "-A" in arguments_dict:
            one_args_options += "-A %s " % arguments_dict["-A"][0]
            self._display_multi = True
        if "-B" in arguments_dict:
            one_args_options += "-B %s " % arguments_dict["-B"][0]
            self._display_multi = True
        if "-C" in arguments_dict:
            one_args_options += "-C %s " % arguments_dict["-C"][0]
            self._display_multi = True
        if "-E" in arguments_dict:
            one_args_options += "-E %s " % arguments_dict["-E"][0]
        if "-M" in arguments_dict:
            one_args_options += "-M %s " % arguments_dict["-M"][0]
        if "-m" in arguments_dict:
            one_args_options += "-m %s " % arguments_dict["-m"][0]
        if "--max-depth" in arguments_dict:
            one_args_options += "--max-depth %s " % arguments_dict["--max-depth"][0]
        if "--max-filesize" in arguments_dict:
            one_args_options += "--max-filesize %s " % arguments_dict["--max-filesize"][0]
        if "--path-separator" in arguments_dict:
            one_args_options += "--path-separator %s " % arguments_dict["--path-separator"][0]
        if "--sort" in arguments_dict:
            one_args_options += "--sort %s " % arguments_dict["--sort"][0]
        if "--sortr" in arguments_dict:
            one_args_options += "--sortr %s " % arguments_dict["--sortr"][0]

        repeatable_options = ''
        if "-f" in arguments_dict:
            repeatable_options += "-f %s " % " -f ".join(arguments_dict["-f"])
        if "-g" in arguments_dict:
            repeatable_options += "-g %s " % " -g ".join(arguments_dict["-g"])
        if "--iglob" in arguments_dict:
            repeatable_options += "--iglob %s " % " --iglob ".join(arguments_dict["--iglob"])
        if "--ignore-file" in arguments_dict:
            repeatable_options += "--ignore-file %s " % " --ignore-file ".join(arguments_dict["--ignore-file"])
        if "--type-add" in arguments_dict:
            repeatable_options += "--type-add %s " % " --type-add ".join(arguments_dict["--type-add"])
        if "-t" in arguments_dict:
            repeatable_options += "-t %s " % " -t ".join(arguments_dict["-t"])
        if "-T" in arguments_dict:
            repeatable_options += "-T %s " % " -T ".join(arguments_dict["-T"])

        is_literal = "-F" in arguments_dict
        pattern = ''
        if "--append" not in arguments_dict:
            self._pattern_regex = []

        path_list = arguments_dict.get("PATH", [])
        path = ' '.join(path_list)

        pattern_list = arguments_dict.get("-e", [])
        for i in pattern_list or path_list[:1]:
            if len(pattern_list) == 0:
                # treat the first PATH as pattern
                path = ' '.join(path_list[1:])

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

        if "--current-buffer" in arguments_dict:
            path = ''   # omit the <PATH> option
            if vim.current.buffer.name:
                try:
                    path = '"%s"' % os.path.relpath(lfDecode(vim.current.buffer.name))
                except ValueError:
                    path = '"%s"' % lfDecode(vim.current.buffer.name)
            else:
                file_name = "%d_'No_Name_%d'" % (os.getpid(), vim.current.buffer.number)
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

        if "--all-buffers" in arguments_dict:
            path = ''   # omit the <PATH> option
            for b in vim.buffers:
                if lfEval("buflisted(%d)" % b.number) == '1':
                    if b.name:
                        try:
                            path += '"' + os.path.relpath(lfDecode(b.name)) + '" '
                        except ValueError:
                            path += '"' + lfDecode(b.name) + '" '
                    else:
                        file_name = "%d_'No_Name_%d'" % (os.getpid(), b.number)
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
        if os.name != 'nt':
            pattern = pattern.replace('`', r"\`")

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
        return escQuote(lfEncode(self._cmd_work_dir))

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
        self._match_path = False
        self._has_column = False

    def _getExplClass(self):
        return RgExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Rg#Maps()")

    @workingDirectory
    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        if args[0] == self._getExplorer().getContextSeparator():
            return

        line = args[0]
        if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
            m = re.match(r'^(.+?)([:-])(\d+)\2', line)
            file, sep, line_num = m.group(1, 2, 3)
            if not os.path.exists(lfDecode(file)):
                if sep == ':':
                    sep = '-'
                else:
                    sep = ':'
                m = re.match(r'^(.+?)%s(\d+)%s' % (sep, sep), line)
                if m:
                    file, line_num = m.group(1, 2)
            if not re.search(r"\d+_'No_Name_(\d+)'", file):
                i = 1
                while not os.path.exists(lfDecode(file)):
                    m = re.match(r'^(.+?(?:([:-])\d+.*?){%d})\2(\d+)\2' % i, line)
                    i += 1
                    file, line_num = m.group(1, 3)
        else:
            m = re.match(r'^(.+?):(\d+):', line)
            file, line_num = m.group(1, 2)
            if not re.search(r"\d+_'No_Name_(\d+)'", file):
                i = 1
                while not os.path.exists(lfDecode(file)):
                    m = re.match(r'^(.+?(?::\d+.*?){%d}):(\d+):' % i, line)
                    i += 1
                    file, line_num = m.group(1, 2)

        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        match = re.search(r"\d+_'No_Name_(\d+)'", file)
        if match:
            buf_number = match.group(1)
        else:
            buf_number = -1

        try:
            if buf_number == -1:
                if kwargs.get("mode", '') == 't':
                    lfCmd("tab drop %s | %s" % (escSpecial(file), line_num))
                else:
                    if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufexists('%s')" % escQuote(file)) == '1':
                        lfCmd("keepj hide drop %s | %s" % (escSpecial(file), line_num))
                    else:
                        lfCmd("hide edit +%s %s" % (line_num, escSpecial(file)))
            else:
                lfCmd("hide buffer +%s %s" % (line_num, buf_number))
            lfCmd("norm! ^zv")
            lfCmd("norm! zz")

            if vim.current.window not in self._cursorline_dict:
                self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

            lfCmd("setlocal cursorline")
        except vim.error as e:
            lfPrintError(e)

    def setArguments(self, arguments):
        self._arguments = arguments
        self._match_path = "--match-path" in arguments
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
        help.append('" d : delete the line under the cursor')
        help.append('" Q : output result quickfix list ')
        help.append('" L : output result location list ')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(RgExplManager, self)._afterEnter()
        if self._getInstance().getWinPos() == 'popup':
            if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
                lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgFileName'', ''^.\{-}\ze\(:\d\+:\|-\d\+-\)'', 10)')"""
                        % self._getInstance().getPopupWinId())
            else:
                lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgFileName'', ''^.\{-}\ze\:\d\+:'', 10)')"""
                        % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgLineNumber'', ''^.\{-}\zs:\d\+:'', 10)')"""
                    % self._getInstance().getPopupWinId())
            id = int(lfEval("matchid"))
            self._match_ids.append(id)
            if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
                lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgLineNumber2'', ''^.\{-}\zs-\d\+-'', 10)')"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            if self._has_column:
                lfCmd("""call win_execute(%d, 'let matchid = matchadd(''Lf_hl_rgColumnNumber'', ''^.\{-}:\d\+:\zs\d\+:'', 10)')"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)

            try:
                for i in self._getExplorer().getPatternRegex():
                    lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_rgHighlight', '%s', 9)")"""
                            % (self._getInstance().getPopupWinId(), escQuote(i).replace('\\', '\\\\')))
                    id = int(lfEval("matchid"))
                    self._match_ids.append(id)
            except vim.error:
                pass
        else:
            if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
                id = int(lfEval("matchadd('Lf_hl_rgFileName', '^.\{-}\ze\(:\d\+:\|-\d\+-\)', 10)"))
            else:
                id = int(lfEval("matchadd('Lf_hl_rgFileName', '^.\{-}\ze\:\d\+:', 10)"))
            self._match_ids.append(id)
            id = int(lfEval("matchadd('Lf_hl_rgLineNumber', '^.\{-}\zs:\d\+:', 10)"))
            self._match_ids.append(id)
            if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
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
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

        reg = lfEval("get(g:, 'Lf_RgStorePattern', '')")
        if reg == '':
            return
        patterns = self._getExplorer().getPatternRegex()[:1]
        # \v\cRegex
        # ^^^^---->
        patterns.extend([x[4:] for x in self._getExplorer().getPatternRegex()[1:]])
        regexp = '|'.join(patterns)
        lfCmd("let @%s = '%s'" % (reg, regexp))

    def _bangEnter(self):
        super(RgExplManager, self)._bangEnter()
        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return
        if "--recall" not in self._arguments:
            self._workInIdle(bang=True)
            if self._read_finished < 2:
                self._timer_id = lfEval("timer_start(1, 'leaderf#Rg#TimerCallback', {'repeat': -1})")
        else:
            instance = self._getInstance()
            if instance.isLastReverseOrder():
                instance.window.cursor = (min(instance.cursorRow, len(instance.buffer)), 0)
            else:
                instance.window.cursor = (max(instance.cursorRow - instance.helpLength, 1), 0)
            if instance.getWinPos() == 'popup':
                lfCmd("call win_execute(%d, 'setlocal cursorline')" % instance.getPopupWinId())
            elif instance.getWinPos() == 'floatwin':
                lfCmd("call nvim_win_set_option(%d, 'cursorline', v:true)" % instance.getPopupWinId())
            else:
                instance.window.options["cursorline"] = True

    def _nearestAncestor(self, markers, path):
        """
        return the nearest ancestor path(including itself) of `path` that contains
        one of files or directories in `markers`.
        `markers` is a list of file or directory names.
        """
        if os.name == 'nt':
            # e.g. C:\\
            root = os.path.splitdrive(os.path.abspath(path))[0] + os.sep
        else:
            root = '/'

        path = os.path.abspath(path)
        while path != root:
            for name in markers:
                if os.path.exists(os.path.join(path, name)):
                    return path
            path = os.path.abspath(os.path.join(path, ".."))

        for name in markers:
            if os.path.exists(os.path.join(path, name)):
                return path

        return ""

    def startExplorer(self, win_pos, *args, **kwargs):
        self._orig_cwd = os.getcwd()
        root_markers = lfEval("g:Lf_RootMarkers")
        wd_mode = lfEval("g:Lf_WorkingDirectoryMode")
        mode = kwargs.get("arguments", {}).get("--wd-mode", [wd_mode])[0]
        working_dir = lfEval("g:Lf_WorkingDirectory")

        # https://github.com/neovim/neovim/issues/8336
        if lfEval("has('nvim')") == '1':
            chdir = vim.chdir
        else:
            chdir = os.chdir

        if os.path.exists(working_dir) and os.path.isdir(working_dir):
            chdir(working_dir)
            super(RgExplManager, self).startExplorer(win_pos, *args, **kwargs)
            return

        cur_buf_name = lfDecode(vim.current.buffer.name)
        fall_back = False
        if 'a' in mode:
            working_dir = self._nearestAncestor(root_markers, self._orig_cwd)
            if working_dir: # there exists a root marker in nearest ancestor path
                chdir(working_dir)
            else:
                fall_back = True
        elif 'A' in mode:
            if cur_buf_name:
                working_dir = self._nearestAncestor(root_markers, os.path.dirname(cur_buf_name))
            else:
                working_dir = ""
            if working_dir: # there exists a root marker in nearest ancestor path
                chdir(working_dir)
            else:
                fall_back = True
        else:
            fall_back = True

        if fall_back:
            if 'f' in mode:
                if cur_buf_name:
                    chdir(os.path.dirname(cur_buf_name))
            elif 'F' in mode:
                if cur_buf_name and not os.path.dirname(cur_buf_name).startswith(self._orig_cwd):
                    chdir(os.path.dirname(cur_buf_name))

        super(RgExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def deleteCurrentLine(self):
        instance = self._getInstance()
        if self._inHelpLines():
            return
        if instance.getWinPos() == 'popup':
            lfCmd("call win_execute(%d, 'setlocal modifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal modifiable")
        line = instance._buffer_object[instance.window.cursor[0] - 1]
        if len(self._content) > 0:
            self._content.remove(line)
            self._getInstance().setStlTotal(len(self._content)//self._getUnit())
            self._getInstance().setStlResultsCount(len(self._content)//self._getUnit())
        # `del vim.current.line` does not work in neovim
        # https://github.com/neovim/neovim/issues/9361
        del instance._buffer_object[instance.window.cursor[0] - 1]
        if instance.getWinPos() == 'popup':
            instance.refreshPopupStatusline()
            lfCmd("call win_execute(%d, 'setlocal nomodifiable')" % instance.getPopupWinId())
        else:
            lfCmd("setlocal nomodifiable")

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return

        if args[0] == self._getExplorer().getContextSeparator():
            return

        line = args[0]
        if "-A" in self._arguments or "-B" in self._arguments or "-C" in self._arguments:
            m = re.match(r'^(.+?)([:-])(\d+)\2', line)
            file, sep, line_num = m.group(1, 2, 3)
            if not os.path.exists(lfDecode(file)):
                if sep == ':':
                    sep = '-'
                else:
                    sep = ':'
                m = re.match(r'^(.+?)%s(\d+)%s' % (sep, sep), line)
                if m:
                    file, line_num = m.group(1, 2)
            if not re.search(r"\d+_'No_Name_(\d+)'", file):
                i = 1
                while not os.path.exists(lfDecode(file)):
                    m = re.match(r'^(.+?(?:([:-])\d+.*?){%d})\2(\d+)\2' % i, line)
                    i += 1
                    file, line_num = m.group(1, 3)
        else:
            m = re.match(r'^(.+?):(\d+):', line)
            file, line_num = m.group(1, 2)
            if not re.search(r"\d+_'No_Name_(\d+)'", file):
                i = 1
                while not os.path.exists(lfDecode(file)):
                    m = re.match(r'^(.+?(?::\d+.*?){%d}):(\d+):' % i, line)
                    i += 1
                    file, line_num = m.group(1, 2)

        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        match = re.search(r"\d+_'No_Name_(\d+)'", file)
        if match:
            buf_number = match.group(1)
        else:
            buf_number = lfEval("bufadd('{}')".format(file))

        self._createPopupPreview("", buf_number, line_num)

        if lfEval("get(g:, 'Lf_RgHighlightInPreview', 1)") == '1':
            if lfEval("has('nvim')") != '1':
                for i in self._getExplorer().getPatternRegex():
                    lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_rgHighlight', '%s', 9)")"""
                            % (self._preview_winid, escQuote(i).replace('\\', '\\\\')))
                    id = int(lfEval("matchid"))
                    self._match_ids.append(id)
            else:
                cur_winid = lfEval("win_getid()")
                lfCmd("noautocmd call win_gotoid(%d)" % self._preview_winid)
                try:
                    for i in self._getExplorer().getPatternRegex():
                        id = int(lfEval("matchadd('Lf_hl_rgHighlight', '%s', 9)" % escQuote(i)))
                        self._match_ids.append(id)
                except vim.error:
                    pass
                lfCmd("noautocmd call win_gotoid(%s)" % cur_winid)

    def outputToQflist(self, *args, **kwargs):
        items = self._getFormatedContents()
        lfCmd("call setqflist(%s, 'r')" % json.dumps(items))
        lfCmd("echohl WarningMsg | redraw | echo ' Output result to quickfix list.' | echohl NONE")

    def outputToLoclist(self, *args, **kwargs):
        items = self._getFormatedContents()
        winnr = lfEval('bufwinnr(%s)' % self._cur_buffer.number)
        lfCmd("call setloclist(%d, %s, 'r')" % (int(winnr), json.dumps(items)))
        lfCmd("echohl WarningMsg | redraw | echo ' Output result to location list.' | echohl NONE")

    def _getFormatedContents(self):
        items = []
        for line in self._instance._buffer_object:
            if self._has_column:
                m = re.match(r'^(?:\.[\\/])?([^:]+):(\d+):(\d+):(.*)$', line)
                if m:
                    fpath, lnum, col, text = m.group(1, 2, 3, 4)
                    items.append({
                        "filename": fpath,
                        "lnum": lnum,
                        "col": col,
                        "text": text,
                    })
            else:
                m = re.match(r'^(?:\.[\\/])?([^:]+):(\d+):(.*)$', line)
                if m:
                    fpath, lnum, text = m.group(1, 2, 3)
                    items.append({
                        "filename": fpath,
                        "lnum": lnum,
                        "col": 1,
                        "text": text,
                    })
        return items

#*****************************************************
# rgExplManager is a singleton
#*****************************************************
rgExplManager = RgExplManager()

__all__ = ['rgExplManager']

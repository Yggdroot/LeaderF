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
# GitExplorer
#*****************************************************
class GitExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._pattern_regex = []
        self._context_separator = "..."
        self._display_multi = False
        self._cmd_work_dir = ""
        self._rg = lfEval("get(g:, 'Lf_Rg', 'rg')")

    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        if "--recall" in arguments_dict and "--live" not in arguments_dict:
            return []

        self._cmd_work_dir = lfGetCwd()

        if "--live" in arguments_dict and "pattern" not in kwargs:
            return AsyncExecutor.Result(iter([]))

        git_config = lfEval("get(g:, 'Lf_GitConfig', [])")
        extra_options = ' '.join(git_config)
        for opt in git_config:
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
        if "--no-fixed-strings" in arguments_dict:
            zero_args_options += "--no-fixed-strings "
        if "-L" in arguments_dict:
            zero_args_options += "-L "
        if "-P" in arguments_dict:
            zero_args_options += "-P "
            is_perl = True
        else:
            is_perl = False
        if "-v" in arguments_dict:
            zero_args_options += "-v "
        if "--binary" in arguments_dict:
            zero_args_options += "--binary "
        if "--column" in arguments_dict:
            zero_args_options += "--column "
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
        if "-U" in arguments_dict:
            zero_args_options += "-U "
        if "--multiline-dotall" in arguments_dict:
            zero_args_options += "--multiline-dotall "
        if "--crlf" in arguments_dict:
            zero_args_options += "--crlf "

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
        else:
            for opt in git_config:
                if opt.lstrip().startswith("--max-columns=") or opt.lstrip().startswith("-M "):
                    break
            else:
                one_args_options += "-M 512 "
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

        if "--append" not in arguments_dict:
            self._pattern_regex = []

        path_list = arguments_dict.get("PATH", [])
        path = ' '.join(path_list)

        if "--live" in arguments_dict:
            pattern_list = [kwargs["pattern"]]
            if os.name == 'nt':
                no_error_message = " 2>NUL"
            else:
                no_error_message = " 2>/dev/null"
            # --live implies -F
            if "-F" not in arguments_dict and "--no-fixed-strings" not in arguments_dict:
                zero_args_options += "-F "
                is_literal = True
        else:
            pattern_list = arguments_dict.get("-e", [])
            no_error_message = ""

        pattern = ''
        for i in pattern_list or path_list[:1]:
            if len(pattern_list) == 0:
                # treat the first PATH as pattern
                path = ' '.join(path_list[1:])

            if case_flag == '-i':
                case_pattern = r'\c'
            elif case_flag == '-s':
                case_pattern = r'\C'
            else: # smart-case
                if (i + 'a').islower():
                    case_pattern = r'\c'
                else:
                    case_pattern = r'\C'

            if "--live" in arguments_dict:
                p = i.replace('\\', r'\\').replace('"', r'\"')
                pattern += r'-e "%s" ' % p
            else:
                if len(i) > 1 and (i[0] == i[-1] == '"' or i[0] == i[-1] == "'"):
                    p = i[1:-1]
                else:
                    p = i

                # -e ""
                if p == '':
                    continue

                pattern += r'-e "%s" ' % p

            if is_literal:
                if word_or_line == '-w ':
                    p = r'\<' + p + r'\>'

                self._pattern_regex.append(r'\V' + case_pattern + p)
            else:
                if word_or_line == '-w ':
                    p = '<' + p + '>'
                self._pattern_regex.append(self.translateRegex(case_pattern + p, is_perl))

        if pattern == '':
            pattern = '"" '

        # as per https://github.com/macvim-dev/macvim/issues/1003
        # the following hack code is not needed any more

        # if path == '' and os.name == 'nt':
        #     path = '.'

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

        if "--heading" in arguments_dict:
            heading = "--heading"
        else:
            heading = "--no-heading"

        cmd = '''{} {} --no-config --no-ignore-messages {} --with-filename --color never --line-number '''\
                '''{} {}{}{}{}{}{}{}'''.format(self._rg, extra_options, heading, case_flag, word_or_line, zero_args_options,
                                                  one_args_options, repeatable_options, lfDecode(pattern), path, no_error_message)
        lfCmd("let g:Lf_Debug_GitCmd = '%s'" % escQuote(cmd))
        content = executor.execute(cmd, encoding=lfEval("&encoding"), cleanup=partial(removeFiles, tmpfilenames))
        return content

    def translateRegex(self, regex, is_perl=False):

        def replace(text, pattern, repl):
            """
            only replace pattern with even number of \ preceding it
            """
            result = ''
            for s in re.split(r'((?:\\\\)+)', text):
                result += re.sub(pattern, repl, s)

            return result

        vim_regex = regex

        vim_regex = vim_regex.replace(r"\\", "\\")
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
        vim_regex = replace(vim_regex, r'\\A', r'^')
        vim_regex = replace(vim_regex, r'\\z', r'$')
        vim_regex = replace(vim_regex, r'\\B', r'')

        # word boundary
        vim_regex = replace(vim_regex, r'\\b', r'(<|>)')

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
        vim_regex = replace(vim_regex, r'\\a', r'%x07')
        vim_regex = replace(vim_regex, r'\\f', r'%x0C')
        vim_regex = replace(vim_regex, r'\\v', r'%x0B')

        # \123        octal character code (up to three digits) (when enabled)
        # \x7F        hex character code (exactly two digits)
        vim_regex = replace(vim_regex, r'\\(x[0-9A-Fa-f][0-9A-Fa-f])', r'%\1')
        # \x{10FFFF}  any hex character code corresponding to a Unicode code point
        # \u007F      hex character code (exactly four digits)
        # \u{7F}      any hex character code corresponding to a Unicode code point
        # \U0000007F  hex character code (exactly eight digits)
        # \U{7F}      any hex character code corresponding to a Unicode code point
        vim_regex = replace(vim_regex, r'\\([uU])', r'%\1')

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
        return 'Git'

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
# GitExplManager
#*****************************************************
class GitExplManager(Manager):
    def __init__(self):
        super(GitExplManager, self).__init__()

    def _getExplClass(self):
        return GitExplorer

    def _defineMaps(self):
        pass

    def startGitDiff(self, win_pos, *args, **kwargs):
        pass

    def startGitLog(self, win_pos, *args, **kwargs):
        pass

    def startGitBlame(self, win_pos, *args, **kwargs):
        pass

    def startExplorer(self, win_pos, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        arg_list = arguments_dict.get("arg_line", 'git').split(maxsplit=2)
        if len(arg_list) == 1:
            return

        subcommand = arg_list[1]
        if subcommand == "diff":
            self.startGitDiff(win_pos, *args, **kwargs)
        elif subcommand == "log":
            self.startGitLog(win_pos, *args, **kwargs)
        elif subcommand == "blame":
            self.startGitBlame(win_pos, *args, **kwargs)


#*****************************************************
# gitExplManager is a singleton
#*****************************************************
gitExplManager = GitExplManager()

__all__ = ['gitExplManager']

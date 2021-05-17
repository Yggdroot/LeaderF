#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import shutil
import itertools
import subprocess
from .utils import *
from .explorer import *
from .manager import *

if sys.version_info >= (3, 0):
    import queue as Queue
else:
    import Queue

#*****************************************************
# GtagsExplorer
#*****************************************************
class GtagsExplorer(Explorer):
    def __init__(self):
        self._executor = []
        self._pattern_regex = []
        if os.name == 'nt':
            self._cd_option = '/d '
        else:
            self._cd_option = ''
        self._root_markers = lfEval("g:Lf_RootMarkers")
        self._db_location = os.path.join(lfEval("g:Lf_CacheDirectory"),
                                     '.LfCache',
                                     'gtags')
        self._store_in_project = lfEval("get(g:, 'Lf_GtagsStoreInProject', 0)") == '1'
        self._store_in_rootmarker = lfEval("get(g:, 'Lf_GtagsStoreInRootMarker', 0)") == '1'
        self._project_root = ""
        self._gtagslibpath = []
        self._result_format = None
        self._last_result_format = None
        self._evalVimVar()
        self._has_nvim = lfEval("has('nvim')") == '1'
        self._db_timestamp = 0
        self._last_command = ""
        self._content = []
        self._with_gutentags = lfEval("get(g:, 'Lf_GtagsGutentags', 0)") != '0'
        self._is_debug = False
        self._cmd = ''

        self._task_queue = Queue.Queue()
        self._worker_thread = threading.Thread(target=self._processTask)
        self._worker_thread.daemon = True
        self._worker_thread.start()

    def __del__(self):
        self._task_queue.put(None)
        self._worker_thread.join()

    def _processTask(self):
        while True:
            try:
                task = self._task_queue.get()
                if task is None:
                    break
                task()
            except Exception as e:
                print(e)

    def setContent(self, content):
        if self._last_command == "--all":
            self._content = content

    def getContent(self, *args, **kwargs):
        arguments_dict = kwargs.get("arguments", {})
        self._is_debug = "--debug" in arguments_dict
        if "--recall" in arguments_dict:
            return []

        if vim.current.buffer.name:
            filename = os.path.normpath(lfDecode(vim.current.buffer.name))
        else:
            filename = os.path.join(lfGetCwd(), 'no_name')

        if "--gtagsconf" in arguments_dict:
            self._gtagsconf = arguments_dict["--gtagsconf"][0]
        if "--gtagslabel" in arguments_dict:
            self._gtagslabel = arguments_dict["--gtagslabel"][0]

        if self._gtagsconf == '' and os.name == 'nt':
            self._gtagsconf = os.path.normpath(os.path.join(self._which("gtags.exe"), "..", "share", "gtags", "gtags.conf")).join('""')

        if "--gtagslibpath" in arguments_dict:
            self._gtagslibpath = [os.path.abspath(os.path.expanduser(p)) for p in arguments_dict["--gtagslibpath"]]
            for i in self._gtagslibpath:
                if not os.path.exists(i):
                    print("`%s` does not exist!" % i)
        else:
            self._gtagslibpath = []

        if "--update" in arguments_dict:
            self._evalVimVar()
            if "--accept-dotfiles" in arguments_dict:
                self._accept_dotfiles = "--accept-dotfiles "
            if "--skip-unreadable" in arguments_dict:
                self._skip_unreadable = "--skip-unreadable "
            if "--skip-symlink" in arguments_dict and self._skip_symlink != "":
                skip_symlink = arguments_dict["--skip-symlink"]
                self._skip_symlink = "--skip-symlink%s " % ('=' + skip_symlink[0] if skip_symlink else "")
            self.updateGtags(filename, single_update=False, auto=False)
            return
        elif "--remove" in arguments_dict:
            self._remove(filename)
            return

        if "--path-style" in arguments_dict:
            path_style = "--path-style %s " % arguments_dict["--path-style"][0]
        else:
            path_style = ""

        auto_jump = False
        self._last_result_format = self._result_format
        self._result_format = None
        if "-d" in arguments_dict:
            pattern = arguments_dict["-d"][0]
            pattern_option = "-d -e %s " % pattern
            if "--auto-jump" in arguments_dict:
                auto_jump = True
        elif "-r" in arguments_dict:
            pattern = arguments_dict["-r"][0]
            pattern_option = "-r -e %s " % pattern
            if "--auto-jump" in arguments_dict:
                auto_jump = True
        elif "-s" in arguments_dict:
            pattern = arguments_dict["-s"][0]
            pattern_option = "-s -e %s " % pattern
        elif "-g" in arguments_dict:
            pattern = arguments_dict["-g"][0]
            pattern_option = "-g -e %s " % pattern
        elif "--by-context" in arguments_dict:
            pattern = lfEval('expand("<cword>")')
            pattern_option = '--from-here "%d:%s" %s ' % (vim.current.window.cursor[0], vim.current.buffer.name, pattern)
            if "--auto-jump" in arguments_dict:
                auto_jump = True
        else:
            if "--current-buffer" in arguments_dict:
                pattern_option = '-f "%s" -q' % vim.current.buffer.name
            elif "--all-buffers" in arguments_dict:
                pattern_option = '-f "%s" -q' % '" "'.join(b.name for b in vim.buffers)
            else: # '--all' or empty means the whole project
                pattern_option = None

            root, dbpath, exists = self._root_dbpath(filename)
            if not filename.startswith(root):
                libdb = os.path.join(dbpath, "GTAGSLIBPATH")
                if os.path.exists(libdb):
                    with lfOpen(libdb, 'r', errors='ignore') as f:
                        for line in f:
                            tmp_root, tmp_dbpath = line.rstrip().split('\t', 1)
                            if filename.startswith(tmp_root):
                                root = tmp_root
                                dbpath = tmp_dbpath
                                break

            if "--result" in arguments_dict:
                self._result_format = arguments_dict["--result"][0]
            else:
                self._result_format = "ctags"

            env = os.environ
            env["GTAGSROOT"] = root
            env["GTAGSDBPATH"] = dbpath

            if pattern_option is None:  # '--all' or empty means the whole project
                cmd = 'global -P | global -L- -f {}--gtagslabel={} {}--color=never --result={}'.format(
                            '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                            self._gtagslabel, path_style, self._result_format)
            else:
                cmd = 'global {}--gtagslabel={} {} {}--color=never --result={}'.format(
                            '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                            self._gtagslabel, pattern_option, path_style, self._result_format)

            if not self._isDBModified(os.path.join(dbpath, 'GTAGS')) and self._content \
                    and self._cmd == cmd:
                return self._content

            self._cmd = cmd

            executor = AsyncExecutor()
            self._executor.append(executor)
            lfCmd("let g:Lf_Debug_GtagsCmd = '%s'" % escQuote(cmd))
            self._last_command = "--all"
            content = executor.execute(cmd, env=env, raise_except=False)
            return content

        if "-S" in arguments_dict:
            scope = "--scope %s " % os.path.abspath(arguments_dict["-S"][0])
        else:
            scope = ""

        if "--literal" in arguments_dict:
            literal = "--literal "
        else:
            literal = ""

        if "-i" in arguments_dict:
            ignorecase = "-i "
        else:
            ignorecase = ""

        if "--append" not in arguments_dict or self._last_result_format is not None:
            self._pattern_regex = []

        # build vim regex, which is used for highlighting
        if ignorecase:
            case_pattern = r'\c'
        else:
            case_pattern = r'\C'

        if len(pattern) > 1 and (pattern[0] == pattern[-1] == '"' or pattern[0] == pattern[-1] == "'"):
            p = pattern[1:-1]
        else:
            p = pattern

        if literal:
            if len(pattern) > 1 and pattern[0] == pattern[-1] == '"':
                p = re.sub(r'\\(?!")', r'\\\\', p)
            else:
                p = p.replace('\\', r'\\')

            self._pattern_regex.append(r'\V' + case_pattern + p)
        else:
            if "-g" not in arguments_dict:
                vim_regex = self.translateRegex(case_pattern + p.join([r'\b', r'\b']))
                vim_regex = vim_regex.replace('.', r'\w')
            else:
                vim_regex = self.translateRegex(case_pattern + p)

            self._pattern_regex.append(vim_regex)

        root, dbpath, exists = self._root_dbpath(filename)
        env = os.environ
        env["GTAGSROOT"] = root
        env["GTAGSDBPATH"] = dbpath
        cmd = 'global {}--gtagslabel={} {} {}{}{}{}--color=never --result=ctags-mod'.format(
                    '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                    self._gtagslabel, pattern_option, path_style, scope, literal, ignorecase)

        executor = AsyncExecutor()
        self._executor.append(executor)
        lfCmd("let g:Lf_Debug_GtagsCmd = '%s'" % escQuote(cmd))
        self._last_command = "others"
        content = executor.execute(cmd, env=env)

        libdb = os.path.join(dbpath, "GTAGSLIBPATH")
        if os.path.exists(libdb):
            with lfOpen(libdb, 'r', errors='ignore') as f:
                for line in f:
                    root, dbpath = line.rstrip().split('\t', 1)
                    env = os.environ
                    env["GTAGSROOT"] = root
                    env["GTAGSDBPATH"] = dbpath

                    if path_style == "--path-style abslib ":
                        path_style = "--path-style absolute "

                    cmd = 'global {}--gtagslabel={} {} {}{}{}{}--color=never --result=ctags-mod -q'.format(
                                '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                                self._gtagslabel, pattern_option, path_style, scope, literal, ignorecase)

                    executor = AsyncExecutor()
                    self._executor.append(executor)
                    content += executor.execute(cmd, env=env)

        if auto_jump:
            first_two = list(itertools.islice(content, 2))
            if len(first_two) == 1:
                return first_two
            else:
                return content.join_left(first_two)

        return content

    def translateRegex(self, regex, is_perl=False):
        """
        copied from RgExplorer
        """
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

    def _isVersionControl(self, filename):
        if self._project_root and filename.startswith(self._project_root):
            return True

        ancestor = self._nearestAncestor(self._root_markers, os.path.dirname(filename))
        if ancestor:
            self._project_root = ancestor
            return True
        else:
            return False

    def _generateDbpath(self, path):
        sep_char = '-' if self._with_gutentags else '_'
        if os.name == 'nt':
            if self._with_gutentags:
                db_folder = re.sub(r'[:\\/]', sep_char, path)
            else:
                db_folder = re.sub(r'[\\/]', sep_char, path.replace(':\\', sep_char, 1))
        else:
            if self._with_gutentags:
                db_folder = path[1:].replace('/', sep_char)
            else:
                db_folder = path.replace('/', sep_char)

        if self._store_in_project:
            return path
        elif self._store_in_rootmarker:
            for name in self._root_markers:
                if os.path.exists(os.path.join(path, name)):
                    return os.path.join(path, name, '.LfGtags')
            # if not exist root marker, store in project
            return os.path.join(path, '.LfGtags')
        else:
            return os.path.join(self._db_location, db_folder)

    def _root_dbpath(self, filename):
        """
        return the (root, dbpath, whether gtags exists)
        """
        if self._project_root and filename.startswith(self._project_root):
            root = self._project_root
        else:
            ancestor = self._nearestAncestor(self._root_markers, os.path.dirname(filename))
            if ancestor:
                self._project_root = ancestor
                root = self._project_root
            else:
                ancestor = self._nearestAncestor(self._root_markers, lfGetCwd())
                if ancestor:
                    self._project_root = ancestor
                    root = self._project_root
                else:
                    root = lfGetCwd()

        dbpath = self._generateDbpath(root)
        return (root, dbpath, os.path.exists(os.path.join(dbpath, "GTAGS")))

    def updateGtags(self, filename, single_update, auto):
        self._task_queue.put(partial(self._update, filename, single_update, auto))

    def _isDBModified(self, dbpath):
        try:
            if self._db_timestamp == os.path.getmtime(dbpath):
                return False
            else:
                self._db_timestamp = os.path.getmtime(dbpath)
                return True
        except:
            return True

    def _remove(self, filename):
        if filename == "":
            return

        root, dbpath, exists = self._root_dbpath(filename)
        try:
            lfCmd("echohl Question")
            if self._store_in_project:
                if lfEval('input("Are you sure you want to remove GTAGS files?[Ny] ")') in ["Y","y"]:
                    os.remove(os.path.join(dbpath, "GTAGS"))
                    os.remove(os.path.join(dbpath, "GPATH"))
                    os.remove(os.path.join(dbpath, "GRTAGS"))
                    if os.path.exists(os.path.join(dbpath, "GTAGSLIBPATH")):
                        os.remove(os.path.join(dbpath, "GTAGSLIBPATH"))
            elif lfEval('input("Are you sure you want to remove directory `{}`?[Ny] ")'.format(lfEncode(dbpath.replace('\\', r'\\')))) in ["Y","y"]:
                shutil.rmtree(dbpath)

            lfCmd("redraw | echo 'Done!'")
        except Exception:
            lfPrintTraceback()
        finally:
            lfCmd("echohl NONE")

    def _update(self, filename, single_update, auto):
        if filename == "":
            return

        if self._gtagsconf == '' and os.name == 'nt':
            self._gtagsconf = os.path.normpath(os.path.join(self._which("gtags.exe"), "..", "share", "gtags", "gtags.conf")).join('""')

        root, dbpath, exists = self._root_dbpath(filename)
        if not filename.startswith(root):
            # if self._has_nvim:
            #     vim.async_call(lfCmd, "let g:Lf_Debug_Gtags = '%s'" % escQuote(str((filename, root))))
            # else:
            #     lfCmd("let g:Lf_Debug_Gtags = '%s'" % escQuote(str((filename, root))))

            return

        self._updateLibGtags(root, dbpath)
        if single_update:
            if exists:
                cmd = 'cd {}"{}" && gtags {}{}{}{}--gtagslabel {} --single-update "{}" "{}"'.format(self._cd_option, root,
                            self._accept_dotfiles, self._skip_unreadable, self._skip_symlink,
                            '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                            self._gtagslabel, filename, dbpath)
                env = os.environ
                # env["GTAGSFORCECPP"] = "" # lead to issue #489
                proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stderr=subprocess.PIPE, env=env)
                _, error = proc.communicate()
        elif not auto:
            self._executeCmd(root, dbpath)
        elif self._isVersionControl(filename):
            if not exists:
                self._executeCmd(root, dbpath)

    def _updateLibGtags(self, root, dbpath):
        if not self._gtagslibpath:
            return

        if not os.path.exists(dbpath):
            os.makedirs(dbpath)

        libpaths = ["%s\t%s\n" % (p, self._generateDbpath(p)) for p in self._gtagslibpath if os.path.exists(p) and p != root]
        if libpaths:
            libdb = os.path.join(dbpath, "GTAGSLIBPATH")
            with lfOpen(libdb, 'w', errors='ignore') as f:
                f.writelines(libpaths)

        if self._gtagsconf == '' and os.name == 'nt':
            self._gtagsconf = os.path.normpath(os.path.join(self._which("gtags.exe"), "..", "share", "gtags", "gtags.conf")).join('""')

        env = os.environ
        # env["GTAGSFORCECPP"] = "" # lead to issue #489
        for path in self._gtagslibpath:
            if not os.path.exists(path):
                continue
            libdbpath = self._generateDbpath(path)
            if not os.path.exists(libdbpath):
                os.makedirs(libdbpath)
            cmd = 'cd {}"{}" && gtags -i {}{}{}{}--gtagslabel {} "{}"'.format(self._cd_option, path,
                        self._accept_dotfiles, self._skip_unreadable, self._skip_symlink,
                        '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                        self._gtagslabel, libdbpath)

            proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stderr=subprocess.PIPE, env=env)
            _, error = proc.communicate()

    def _which(self, executable):
        for p in os.environ["PATH"].split(";"):
            if os.path.exists(os.path.join(p, executable)):
                return p

        return ""

    def _evalVimVar(self):
        """
        vim variables can not be accessed from a python thread,
        so we should evaluate the value in advance.
        """
        self._accept_dotfiles = "--accept-dotfiles " if lfEval("get(g:, 'Lf_GtagsAcceptDotfiles', '0')") == '1' else ""
        self._skip_unreadable = "--skip-unreadable " if lfEval("get(g:, 'Lf_GtagsSkipUnreadable', '0')") == '1' else ""
        self._skip_symlink = "--skip-symlink%s " % ('=' + lfEval("get(g:, 'Lf_GtagsSkipSymlink', '')")
                                if lfEval("get(g:, 'Lf_GtagsSkipSymlink', '')") != '' else "")
        if lfEval("get(g:, 'Lf_GtagsHigherThan6_6_2', '1')") == '0':
            self._skip_symlink = ""
        self._gtagsconf = lfEval("get(g:, 'Lf_Gtagsconf', '')")
        if self._gtagsconf:
            self._gtagsconf = self._gtagsconf.join('""')
        self._gtagslabel = lfEval("get(g:, 'Lf_Gtagslabel', 'default')")

        self._Lf_GtagsSource = int(lfEval("get(g:, 'Lf_GtagsSource', 0)"))
        if self._Lf_GtagsSource not in [0, 1, 2]:
            self._Lf_GtagsSource = 0
        if self._Lf_GtagsSource != 1: # only using FileExplorer needs to evaluate the following variables
            if self._Lf_GtagsSource == 2:
                self._Lf_GtagsfilesCmd = lfEval("g:Lf_GtagsfilesCmd")
            return

        if lfEval("exists('g:Lf_ExternalCommand')") == '1':
            self._Lf_ExternalCommand = lfEval("g:Lf_ExternalCommand")
            return
        else:
            self._Lf_ExternalCommand = None

        self._Lf_UseVersionControlTool = lfEval("g:Lf_UseVersionControlTool") == '1'
        self._Lf_WildIgnore = lfEval("g:Lf_WildIgnore")
        self._Lf_RecurseSubmodules = lfEval("get(g:, 'Lf_RecurseSubmodules', 0)") == '1'
        if lfEval("exists('g:Lf_DefaultExternalTool')") == '1':
            self._default_tool = {"rg": 0, "pt": 0, "ag": 0, "find": 0}
            tool = lfEval("g:Lf_DefaultExternalTool")
            if tool and lfEval("executable('%s')" % tool) == '0':
                raise Exception("executable '%s' can not be found!" % tool)
            self._default_tool[tool] = 1
        else:
            self._default_tool = {"rg": 1, "pt": 1, "ag": 1, "find": 1}
        self._is_rg_executable = lfEval("executable('rg')") == '1'
        self._Lf_ShowHidden = lfEval("g:Lf_ShowHidden") != '0'
        self._Lf_FollowLinks = lfEval("g:Lf_FollowLinks") == '1'
        self._is_pt_executable = lfEval("executable('pt')") == '1'
        self._is_ag_executable = lfEval("executable('ag')") == '1'
        self._is_find_executable = lfEval("executable('find')") == '1'

    def _exists(self, path, dir):
        """
        return True if `dir` exists in `path` or its ancestor path,
        otherwise return False
        """
        if os.name == 'nt':
            # e.g. C:\\
            root = os.path.splitdrive(os.path.abspath(path))[0] + os.sep
        else:
            root = '/'

        while os.path.abspath(path) != root:
            cur_dir = os.path.join(path, dir)
            if os.path.exists(cur_dir) and os.path.isdir(cur_dir):
                return True
            path = os.path.join(path, "..")

        cur_dir = os.path.join(path, dir)
        if os.path.exists(cur_dir) and os.path.isdir(cur_dir):
            return True

        return False

    def _buildCmd(self, dir, **kwargs):
        """
        this function comes from FileExplorer
        """
        # do not use external command if the encoding of `dir` is not ascii
        if not isAscii(dir):
            return None

        if self._Lf_ExternalCommand:
            return self._Lf_ExternalCommand.replace('"%s"', '%s') % dir.join('""')

        arguments_dict = kwargs.get("arguments", {})
        if self._Lf_UseVersionControlTool:
            if self._exists(dir, ".git"):
                wildignore = self._Lf_WildIgnore
                if ".git" in wildignore.get("dir", []):
                    wildignore.get("dir", []).remove(".git")
                if ".git" in wildignore.get("file", []):
                    wildignore.get("file", []).remove(".git")
                ignore = ""
                for i in wildignore.get("dir", []):
                    ignore += ' -x "%s"' % i
                for i in wildignore.get("file", []):
                    ignore += ' -x "%s"' % i

                if "--no-ignore" in arguments_dict:
                    no_ignore = ""
                else:
                    no_ignore = "--exclude-standard"

                if self._Lf_RecurseSubmodules:
                    recurse_submodules = "--recurse-submodules"
                else:
                    recurse_submodules = ""

                cmd = 'git ls-files %s "%s" && git ls-files --others %s %s "%s"' % (recurse_submodules, dir, no_ignore, ignore, dir)
                return cmd
            elif self._exists(dir, ".hg"):
                wildignore = self._Lf_WildIgnore
                if ".hg" in wildignore.get("dir", []):
                    wildignore.get("dir", []).remove(".hg")
                if ".hg" in wildignore.get("file", []):
                    wildignore.get("file", []).remove(".hg")
                ignore = ""
                for i in wildignore.get("dir", []):
                    ignore += ' -X "%s"' % self._expandGlob("dir", i)
                for i in wildignore.get("file", []):
                    ignore += ' -X "%s"' % self._expandGlob("file", i)

                cmd = 'hg files %s "%s"' % (ignore, dir)
                return cmd

        default_tool = self._default_tool

        if default_tool["rg"] and self._is_rg_executable:
            wildignore = self._Lf_WildIgnore
            if os.name == 'nt': # https://github.com/BurntSushi/ripgrep/issues/500
                color = ""
                ignore = ""
                for i in wildignore.get("dir", []):
                    if self._Lf_ShowHidden or not i.startswith('.'): # rg does not show hidden files by default
                        ignore += ' -g "!%s"' % i
                for i in wildignore.get("file", []):
                    if self._Lf_ShowHidden or not i.startswith('.'):
                        ignore += ' -g "!%s"' % i
            else:
                color = "--color never"
                ignore = ""
                for i in wildignore.get("dir", []):
                    if self._Lf_ShowHidden or not i.startswith('.'):
                        ignore += " -g '!%s'" % i
                for i in wildignore.get("file", []):
                    if self._Lf_ShowHidden or not i.startswith('.'):
                        ignore += " -g '!%s'" % i

            if self._Lf_FollowLinks:
                followlinks = "-L"
            else:
                followlinks = ""

            if self._Lf_ShowHidden:
                show_hidden = "--hidden"
            else:
                show_hidden = ""

            if "--no-ignore" in arguments_dict:
                no_ignore = "--no-ignore"
            else:
                no_ignore = ""

            if dir == '.':
                cur_dir = ''
            else:
                cur_dir = '"%s"' % dir

            cmd = 'rg --no-messages --files %s %s %s %s %s %s' % (color, ignore, followlinks, show_hidden, no_ignore, cur_dir)
        elif default_tool["pt"] and self._is_pt_executable and os.name != 'nt': # there is bug on Windows
            wildignore = self._Lf_WildIgnore
            ignore = ""
            for i in wildignore.get("dir", []):
                if self._Lf_ShowHidden or not i.startswith('.'): # pt does not show hidden files by default
                    ignore += " --ignore=%s" % i
            for i in wildignore.get("file", []):
                if self._Lf_ShowHidden or not i.startswith('.'):
                    ignore += " --ignore=%s" % i

            if self._Lf_FollowLinks:
                followlinks = "-f"
            else:
                followlinks = ""

            if self._Lf_ShowHidden:
                show_hidden = "--hidden"
            else:
                show_hidden = ""

            if "--no-ignore" in arguments_dict:
                no_ignore = "-U"
            else:
                no_ignore = ""

            cmd = 'pt --nocolor %s %s %s %s -g="" "%s"' % (ignore, followlinks, show_hidden, no_ignore, dir)
        elif default_tool["ag"] and self._is_ag_executable and os.name != 'nt': # https://github.com/vim/vim/issues/3236
            wildignore = self._Lf_WildIgnore
            ignore = ""
            for i in wildignore.get("dir", []):
                if self._Lf_ShowHidden or not i.startswith('.'): # ag does not show hidden files by default
                    ignore += ' --ignore "%s"' % i
            for i in wildignore.get("file", []):
                if self._Lf_ShowHidden or not i.startswith('.'):
                    ignore += ' --ignore "%s"' % i

            if self._Lf_FollowLinks:
                followlinks = "-f"
            else:
                followlinks = ""

            if self._Lf_ShowHidden:
                show_hidden = "--hidden"
            else:
                show_hidden = ""

            if "--no-ignore" in arguments_dict:
                no_ignore = "-U"
            else:
                no_ignore = ""

            cmd = 'ag --nocolor --silent %s %s %s %s -g "" "%s"' % (ignore, followlinks, show_hidden, no_ignore, dir)
        elif default_tool["find"] and self._is_find_executable and os.name != 'nt':
            wildignore = self._Lf_WildIgnore
            ignore_dir = ""
            for d in wildignore.get("dir", []):
                ignore_dir += '-type d -name "%s" -prune -o ' % d

            ignore_file = ""
            for f in wildignore.get("file", []):
                    ignore_file += '-type f -name "%s" -o ' % f

            if self._Lf_FollowLinks:
                followlinks = "-L"
            else:
                followlinks = ""

            if os.name == 'nt':
                redir_err = ""
            else:
                redir_err = " 2>/dev/null"

            if self._Lf_ShowHidden:
                show_hidden = ""
            else:
                show_hidden = '-name ".*" -prune -o'

            cmd = 'find %s "%s" -name "." -o %s %s %s -type f -print %s %s' % (followlinks,
                                                                               dir,
                                                                               ignore_dir,
                                                                               ignore_file,
                                                                               show_hidden,
                                                                               redir_err)
        else:
            cmd = None

        return cmd

    def _file_list_cmd(self, root):
        if self._Lf_GtagsSource == 1:
            cmd = self._buildCmd(root)
        elif self._Lf_GtagsSource == 2:
            if os.path.exists(os.path.join(root, ".git")) and os.path.isdir(os.path.join(root, ".git")):
                cmd = self._Lf_GtagsfilesCmd[".git"]
            elif os.path.exists(os.path.join(root, ".hg")) and os.path.isdir(os.path.join(root, ".hg")):
                cmd = self._Lf_GtagsfilesCmd[".hg"]
            else:
                cmd = self._Lf_GtagsfilesCmd["default"]
        else:
            cmd = None

        return cmd

    def _executeCmd(self, root, dbpath):
        if not os.path.exists(dbpath):
            os.makedirs(dbpath)
        cmd = self._file_list_cmd(root)
        if cmd:
            if os.name == 'nt':
                cmd = 'cd {}"{}" && ( {} ) | gtags -i {}{}{}{}--gtagslabel {} -f- "{}"'.format(self._cd_option, root, cmd,
                            self._accept_dotfiles, self._skip_unreadable, self._skip_symlink,
                            '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                            self._gtagslabel, dbpath)
            else:
                cmd = 'cd {}"{}" && {{ {}; }} | gtags -i {}{}{}{}--gtagslabel {} -f- "{}"'.format(self._cd_option, root, cmd,
                            self._accept_dotfiles, self._skip_unreadable, self._skip_symlink,
                            '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                            self._gtagslabel, dbpath)
        else:
            cmd = 'cd {}"{}" && gtags -i {}{}{}{}--gtagslabel {} "{}"'.format(self._cd_option, root,
                        self._accept_dotfiles, self._skip_unreadable, self._skip_symlink,
                        '--gtagsconf %s ' % self._gtagsconf if self._gtagsconf else "",
                        self._gtagslabel, dbpath)

        env = os.environ
        # env["GTAGSFORCECPP"] = "" # lead to issue #489
        proc = subprocess.Popen(cmd, shell=True, universal_newlines=True, stderr=subprocess.PIPE, env=env)
        _, error = proc.communicate()

        def print_log(args):
            print(args)

        if error:
            if self._has_nvim:
                vim.async_call(print_log, cmd)
                vim.async_call(print_log, error)
                vim.async_call(print_log, "gtags error!")
            else:
                print(cmd)
                print(error)
                print("gtags error!")
        else:
            if self._has_nvim:
                vim.async_call(print_log, "gtags generated successfully!")
            else:
                print("gtags generated successfully!")

        if self._is_debug:
            if self._has_nvim:
                vim.async_call(print_log, cmd)
            else:
                print(cmd)

    def getStlCategory(self):
        return 'Gtags'

    def getStlCurDir(self):
        return escQuote(lfEncode(lfGetCwd()))

    def cleanup(self):
        for exe in self._executor:
            exe.killProcess()
        self._executor = []

    def getPatternRegex(self):
        return self._pattern_regex

    def getResultFormat(self):
        return self._result_format

    def getLastResultFormat(self):
        return self._last_result_format


#*****************************************************
# GtagsExplManager
#*****************************************************
class GtagsExplManager(Manager):
    def __init__(self):
        super(GtagsExplManager, self).__init__()
        self._match_path = False

    def _getExplClass(self):
        return GtagsExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Gtags#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        if self._getExplorer().getResultFormat() is None:
            file, line_num = line.split('\t', 2)[:2]
        elif self._getExplorer().getResultFormat() == "ctags":
            file, line_num = line.split('\t', 2)[1:]
        elif self._getExplorer().getResultFormat() == "ctags-x":
            line_num, file = line.split(None, 3)[1:3]
        else: # ctags-mod
            file, line_num = line.split('\t', 2)[:2]

        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        try:
            if kwargs.get("mode", '') == 't':
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('tab', file, line_num)
                else:
                    lfCmd("tabe %s | %s" % (escSpecial(file), line_num))
            else:
                if lfEval("get(g:, 'Lf_JumpToExistingWindow', 1)") == '1' and lfEval("bufloaded('%s')" % escQuote(file)) == '1':
                    lfDrop('', file, line_num)
                else:
                    lfCmd("hide edit +%s %s" % (line_num, escSpecial(file)))
            lfCmd("norm! ^zv")
            lfCmd("norm! zz")

            if "preview" not in kwargs:
                lfCmd("setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!")

            if vim.current.window not in self._cursorline_dict:
                self._cursorline_dict[vim.current.window] = vim.current.window.options["cursorline"]

            lfCmd("setlocal cursorline")
        except vim.error:
            lfPrintTraceback()

    def updateGtags(self, filename, single_update, auto=True):
        self._getExplorer().updateGtags(filename, single_update, auto)

    def setArguments(self, arguments):
        self._arguments = arguments
        self._match_path = "--match-path" in arguments

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if self._match_path or mode == 0:
            return line

        if self._getExplorer().getResultFormat() in [None, "ctags-mod"]:
            if mode == 2:
                return line[:line.find('\t')]
            else:
                return line[line.find('\t', line.find('\t')) + 1:]
        elif self._getExplorer().getResultFormat() == "ctags":
            if mode == 2:
                return line[line.find('\t')+1:]
            else:
                return line[:line.find('\t')]
        elif self._getExplorer().getResultFormat() == "ctags-x":
            if mode == 2:
                return line[line.find(' ') + 1:]
            else:
                return line[:line.find(' ')]
        else:
            return line

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start postion of full path
                  1, return the start postion of name only
                  2, return the start postion of directory name
        """
        if self._match_path or mode == 0:
            return 0

        if self._getExplorer().getResultFormat() in [None, "ctags-mod"]:
            if mode == 2:
                return 0

            return lfBytesLen(line[:line.find('\t', line.find('\t'))]) + 1
        elif self._getExplorer().getResultFormat() == "ctags":
            if mode == 2:
                return lfBytesLen(line[:line.find('\t')]) + 1
            else:
                return 0
        elif self._getExplorer().getResultFormat() == "ctags-x":
            if mode == 2:
                return lfBytesLen(line[:line.find(' ')]) + 1
            else:
                return 0
        else:
            return 0

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" p : preview the result')
        help.append('" d : delete the line under the cursor')
        help.append('" i/<Tab> : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(GtagsExplManager, self)._afterEnter()

        lfCmd("augroup Lf_Gtags")
        lfCmd("autocmd!")
        lfCmd("autocmd VimLeavePre * call leaderf#Gtags#cleanup()")
        lfCmd("augroup END")

        if self._getInstance().getWinPos() == 'popup':
            if self._getExplorer().getResultFormat() is None:
                # \ should be escaped as \\\\
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsFileName', '^.\\\\{-}\\\\ze\\\\t')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsLineNumber', '\\\\t\\\\zs\\\\d\\\\+\\\\ze\\\\t')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            elif self._getExplorer().getResultFormat() == "ctags":
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsFileName', '\\\\t\\\\zs.\\\\{-}\\\\ze\\\\t')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsLineNumber', '\\\\t\\\\zs\\\\d\\\\+$')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            elif self._getExplorer().getResultFormat() == "ctags-x":
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsFileName', '^\\\\S\\\\+\\\\s\\\\+\\\\d\\\\+\\\\s\\\\+\\\\zs\\\\S\\\\+')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsLineNumber', '^\\\\S\\\\+\\\\s\\\\+\\\\zs\\\\d\\\\+')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            else: # ctags-mod
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsFileName', '^.\\\\{-}\\\\ze\\\\t')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
                lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsLineNumber', '\\\\t\\\\zs\\\\d\\\\+\\\\ze\\\\t')")"""
                        % self._getInstance().getPopupWinId())
                id = int(lfEval("matchid"))
                self._match_ids.append(id)
            try:
                for i in self._getExplorer().getPatternRegex():
                    lfCmd("""call win_execute(%d, "let matchid = matchadd('Lf_hl_gtagsHighlight', '%s', 9)")"""
                            % (self._getInstance().getPopupWinId(), re.sub(r'\\(?!")', r'\\\\', escQuote(i))))
                    id = int(lfEval("matchid"))
                    self._match_ids.append(id)
            except vim.error:
                pass
        else:
            if self._getExplorer().getResultFormat() is None:
                id = int(lfEval("""matchadd('Lf_hl_gtagsFileName', '^.\{-}\ze\t')"""))
                self._match_ids.append(id)
                id = int(lfEval("""matchadd('Lf_hl_gtagsLineNumber', '\t\zs\d\+\ze\t')"""))
                self._match_ids.append(id)
            elif self._getExplorer().getResultFormat() == "ctags":
                id = int(lfEval("""matchadd('Lf_hl_gtagsFileName', '\t\zs.\{-}\ze\t')"""))
                self._match_ids.append(id)
                id = int(lfEval("""matchadd('Lf_hl_gtagsLineNumber', '\t\zs\d\+$')"""))
                self._match_ids.append(id)
            elif self._getExplorer().getResultFormat() == "ctags-x":
                id = int(lfEval("""matchadd('Lf_hl_gtagsFileName', '^\S\+\s\+\d\+\s\+\zs\S\+')"""))
                self._match_ids.append(id)
                id = int(lfEval("""matchadd('Lf_hl_gtagsLineNumber', '^\S\+\s\+\zs\d\+')"""))
                self._match_ids.append(id)
            else: # ctags-mod
                id = int(lfEval("""matchadd('Lf_hl_gtagsFileName', '^.\{-}\ze\t')"""))
                self._match_ids.append(id)
                id = int(lfEval("""matchadd('Lf_hl_gtagsLineNumber', '\t\zs\d\+\ze\t')"""))
                self._match_ids.append(id)
            try:
                for i in self._getExplorer().getPatternRegex():
                    id = int(lfEval("matchadd('Lf_hl_gtagsHighlight', '%s', 9)" % escQuote(i)))
                    self._match_ids.append(id)
            except vim.error:
                pass

    def _beforeExit(self):
        super(GtagsExplManager, self)._beforeExit()
        if self._timer_id is not None:
            lfCmd("call timer_stop(%s)" % self._timer_id)
            self._timer_id = None
        for k, v in self._cursorline_dict.items():
            if k.valid:
                k.options["cursorline"] = v
        self._cursorline_dict.clear()

    def _bangEnter(self):
        super(GtagsExplManager, self)._bangEnter()
        if lfEval("exists('*timer_start')") == '0':
            lfCmd("echohl Error | redraw | echo ' E117: Unknown function: timer_start' | echohl NONE")
            return
        if "--recall" not in self._arguments:
            self._workInIdle(bang=True)
            if self._read_finished < 2:
                self._timer_id = lfEval("timer_start(1, 'leaderf#Gtags#TimerCallback', {'repeat': -1})")
        else:
            instance = self._getInstance()
            if instance.isLastReverseOrder():
                instance.window.cursor = (min(instance.cursorRow, len(instance.buffer)), 0)
            else:
                instance.window.cursor = (instance.cursorRow, 0)

            if instance.getWinPos() == 'popup':
                lfCmd("call win_execute(%d, 'setlocal cursorline')" % instance.getPopupWinId())
            elif instance.getWinPos() == 'floatwin':
                lfCmd("call nvim_win_set_option(%d, 'cursorline', v:true)" % instance.getPopupWinId())
            else:
                instance.window.options["cursorline"] = True

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

    def getArguments(self):
        if self._getExplorer().getLastResultFormat() is not None and \
                "--append" in self._arguments:
            del self._arguments["--append"]
        return self._arguments

    def _supportsRefine(self):
        return True

    def startExplorer(self, win_pos, *args, **kwargs):
        if  "through" in kwargs.get("arguments", {}).get("--path-style", []):
            self._orig_cwd = lfGetCwd()

            # https://github.com/neovim/neovim/issues/8336
            if lfEval("has('nvim')") == '1':
                chdir = vim.chdir
            else:
                chdir = os.chdir

            if vim.current.buffer.name:
                path = os.path.dirname(lfDecode(vim.current.buffer.name))
            else:
                path = lfGetCwd()
            root_markers = lfEval("g:Lf_RootMarkers")
            project_root = self._getExplorer()._nearestAncestor(root_markers, path)
            if project_root == "" and path != lfGetCwd():
                project_root = self._getExplorer()._nearestAncestor(root_markers, lfGetCwd())
            if project_root:
                chdir(project_root)

        super(GtagsExplManager, self).startExplorer(win_pos, *args, **kwargs)

    def _previewInPopup(self, *args, **kwargs):
        if len(args) == 0:
            return

        line = args[0]
        if self._getExplorer().getResultFormat() is None:
            file, line_num = line.split('\t', 2)[:2]
        elif self._getExplorer().getResultFormat() == "ctags":
            file, line_num = line.split('\t', 2)[1:]
        elif self._getExplorer().getResultFormat() == "ctags-x":
            line_num, file = line.split(None, 3)[1:3]
        else: # ctags-mod
            file, line_num = line.split('\t', 2)[:2]

        if not os.path.isabs(file):
            file = os.path.join(self._getInstance().getCwd(), lfDecode(file))
            file = os.path.normpath(lfEncode(file))

        if lfEval("bufloaded('%s')" % escQuote(file)) == '1':
            source = int(lfEval("bufadd('%s')" % escQuote(file)))
        else:
            source = file
        self._createPopupPreview("", source, line_num)


#*****************************************************
# gtagsExplManager is a singleton
#*****************************************************
gtagsExplManager = GtagsExplManager()

__all__ = ['gtagsExplManager']

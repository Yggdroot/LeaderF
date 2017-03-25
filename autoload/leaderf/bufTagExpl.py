#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import os
import os.path
import subprocess
import tempfile
from leaderf.utils import *
from leaderf.explorer import *
from leaderf.manager import *


#*****************************************************
# BufTagExplorer
#*****************************************************
class BufTagExplorer(Explorer):
    def __init__(self):
        self._ctags = lfEval("g:Lf_Ctags")
        self._supports_preview = int(lfEval("g:Lf_PreviewCode"))
        self._tag_list = {}        # a dict with (key, value) = (buffer number, taglist)
        self._buf_changedtick = {} # a dict with (key, value) = (buffer number, changedtick)
        for buf in vim.buffers:
            changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buf.number))
            self._buf_changedtick[buf.number] = changedtick

    def getContent(self, *args, **kwargs):
        tag_list = []
        if len(args) > 0: # all buffers
            for b in vim.buffers:
                if b.options["buflisted"]:
                    tag_list.extend(self._getTaglist(b))
        else:
            tag_list = self._getTaglist(vim.current.buffer)
        return tag_list

    def _getTaglist(self, buffer):
        changedtick = int(lfEval("getbufvar(%d, 'changedtick')" % buffer.number))
        # there is no change since last call
        if changedtick == self._buf_changedtick.get(buffer.number, -1):
            if buffer.number in self._tag_list:
                return self._tag_list[buffer.number]
        else:
            self._buf_changedtick[buffer.number] = changedtick

        if buffer.options["filetype"] == b"cpp":
            extra_options = "--c++-kinds=+p"
        elif buffer.options["filetype"] == b"c":
            extra_options = "--c-kinds=+p"
        else:
            extra_options = ""

        # {tagname}<Tab>{tagfile}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
        # {tagname}<Tab>{tagfile}<Tab>{tagaddress};"<Tab>{kind}<Tab>{scope}
        process = subprocess.Popen("{} -n -u --fields=-ft+Ks {} -f- -L- ".format(self._ctags,
                                                                                 extra_options),
                                   shell=True,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
        if buffer.options["modified"] == True:
            with tempfile.NamedTemporaryFile(mode='w+',
                                             suffix='_'+os.path.basename(buffer.name),
                                             delete=False) as f:
                for line in buffer[:]:
                    f.write(line + '\n')
                file_name = f.name
            out = process.communicate(lfDecode(file_name))
            os.remove(file_name)
        else:
            out = process.communicate(lfDecode(buffer.name))

        if out[1]:
            lfCmd("echoerr '%s'" % escQuote(out[1].rstrip()))

        if not out[0]:
            return []

        # a list of [tag, file, line, kind, scope]
        output = [line.split('\t') for line in out[0].splitlines()]
        if len(output[0]) < 4:
            lfCmd("echoerr '%s'" % escQuote(out[0].rstrip()))
            return []

        tag_total_len = 0
        max_kind_len = 0
        for _, item  in enumerate(output):
            tag_total_len += len(item[0])
            kind_len = len(item[3])
            if kind_len > max_kind_len:
                max_kind_len = kind_len
        ave_taglen = tag_total_len // len(output)
        tag_len = ave_taglen * 3 // 2

        tab_len = buffer.options["shiftwidth"]
        std_tag_kind_len = tag_len // tab_len * tab_len + tab_len + max_kind_len

        tag_list = []
        for _, item  in enumerate(output):
            scope = item[4] if len(item) > 4 else "Global"
            tag_kind = "{:{taglen}s}\t{}".format(item[0],   # tag
                                                 item[3],   # kind
                                                 taglen=tag_len
                                                 )
            tag_kind_len = int(lfEval("strdisplaywidth('%s')" % escQuote(tag_kind)))
            num = std_tag_kind_len - tag_kind_len
            space_num = num if num > 0 else 0
            bufname = buffer.name if vim.options["autochdir"] else lfRelpath(buffer.name)
            line = "{}{}\t{}\t{:2s}{}\t{}".format(tag_kind,
                                                  ' ' * space_num,
                                                  scope,          # scope
                                                  ' ',
                                                  bufname,        # file
                                                  item[2][:-2]    # line
                                                  )
            tag_list.append(line)
            if self._supports_preview:
                # code = "{:{taglen}s}\t{}".format(' ' * len(item[0]),
                #                                  buffer[int(item[2][:-2]) - 1].lstrip(),
                #                                  taglen=tag_len
                #                                  )
                code = "\t\t{}".format(buffer[int(item[2][:-2]) - 1].lstrip())
                tag_list.append(code)

        self._tag_list[buffer.number] = tag_list

        return tag_list

    def getStlCategory(self):
        return 'BufTag'

    def getStlCurDir(self):
        return escQuote(lfEncode(os.getcwd()))

    def isFilePath(self):
        return False


#*****************************************************
# BufTagExplManager
#*****************************************************
class BufTagExplManager(Manager):
    def __init__(self):
        super(BufTagExplManager, self).__init__()
        self._match_ids = []
        self._supports_preview = int(lfEval("g:Lf_PreviewCode"))

    def _getExplClass(self):
        return BufTagExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#bufTagExplMaps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        if line[0].isspace():
            buffer = args[1]
            line_nr = args[2]
            line = buffer[line_nr - 2]
        # {tag} {kind} {scope} {file} {line}
        items = re.split(" *\t *", line)
        tagname = items[0]
        tagfile, line_nr = items[3:]
        lfCmd("hide buffer +%s %s" % (line_nr, escSpecial(tagfile)))
        lfCmd("norm! ^")
        lfCmd("call search('\V%s', 'Wc', line('.'))" % escQuote(tagname))
        lfCmd("norm! zz")

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the whole line
                  1, return the tagname
                  2, return the remaining part
        """
        if mode == 0:
            return line
        elif mode == 1:
            return re.split(" *\t *", line, 1)[0]
        else:
            return re.split(" *\t *", line, 1)[1]

    def _getDigestStartPos(self, line, mode):
        """
        return the start position of the digest returned by _getDigest()
        Args:
            mode: 0, return the start position of the whole line
                  1, return the start position of tagname
                  2, return the start position remaining part
        """
        if mode == 0:
            return 0
        elif mode == 1:
            return 0
        else:
            return len(line) - len(re.split(" *\t *", line, 1)[1])

    def _createHelp(self):
        help = []
        help.append('" <CR>/<double-click>/o : open file under cursor')
        help.append('" x : open file under cursor in a horizontally split window')
        help.append('" v : open file under cursor in a vertically split window')
        help.append('" t : open file under cursor in a new tabpage')
        help.append('" i : switch to input mode')
        help.append('" q : quit')
        help.append('" <F1> : toggle this help')
        help.append('" ---------------------------------------------------------')
        return help

    def _afterEnter(self):
        super(BufTagExplManager, self)._afterEnter()
        id = int(lfEval('''matchadd('Lf_hl_buftagKind', '^[^\t]*\t\zs\S\+')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_buftagScopeType', '[^\t]*\t\S\+\s*\zs\w\+:')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_buftagScope', '^[^\t]*\t\S\+\s*\(\w\+:\)\=\zs\S\+')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_buftagDirname', '[^\t]*\t\S\+\s*\S\+\s*\zs[^\t]\+')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_buftagLineNum', '\d\+$')'''))
        self._match_ids.append(id)
        id = int(lfEval('''matchadd('Lf_hl_buftagCode', '^\s\+.*')'''))
        self._match_ids.append(id)

    def _beforeExit(self):
        super(BufTagExplManager, self)._beforeExit()
        for i in self._match_ids:
            lfCmd("silent! call matchdelete(%d)" % i)
        self._match_ids = []

    def _getUnit(self):
        """
        indicates how many lines are considered as a unit
        """
        if self._supports_preview:
            return 2
        else:
            return 1

    def _supportsRefine(self):
        return True

    def _fuzzyFilter(self, is_full_path, get_weight, iterable):
        """
        return a list, each item is a triple (weight, line1, line2)
        """
        if self._supports_preview:
            if len(iterable) < 2:
                return []
            getDigest = partial(self._getDigest, mode=0 if is_full_path else 1)
            triples = ((get_weight(getDigest(line)), line, iterable[2*i+1])
                       for i, line in enumerate(iterable[::2]))
            return (t for t in triples if t[0])
        else:
            return super(BufTagExplManager, self)._fuzzyFilter(is_full_path,
                                                               get_weight,
                                                               iterable)

    def _refineFilter(self, first_get_weight, get_weight, iterable):
        if self._supports_preview:
            if len(iterable) < 2:
                return []
            getDigest = self._getDigest
            tuples = ((first_get_weight(getDigest(line, 1)), get_weight(getDigest(line, 2)),
                       line, iterable[2*i+1]) for i, line in enumerate(iterable[::2]))
            return ((i[0] + i[1], i[2], i[3]) for i in tuples if i[0] and i[1])
        else:
            return super(BufTagExplManager, self)._refineFilter(first_get_weight,
                                                                get_weight,
                                                                iterable)

    def _regexFilter(self, iterable):
        try:
            if ('-2' == lfEval("g:LfNoErrMsgMatch('', '%s')" % escQuote(self._cli.pattern))):
                return iter([])
            else:
                result = []
                for i, line in enumerate(iterable[::2]):
                    if ('-1' != lfEval("g:LfNoErrMsgMatch('%s', '%s')" %
                        (escQuote(self._getDigest(line, 1).strip()),
                            escQuote(self._cli.pattern)))):
                        result.append(line)
                        result.append(iterable[2*i+1])
                return result
        except vim.error:
            return iter([])

    def _getList(self, pairs):
        """
        return a list constructed from pairs
        Args:
            pairs: a list of tuple(weight, line, ...)
        """
        if self._supports_preview:
            result = []
            for _, p in enumerate(pairs):
                result.append(p[1])
                result.append(p[2])
            return result
        else:
            return super(BufTagExplManager, self)._getList(pairs)

    def _toUp(self):
        if self._supports_preview:
            lfCmd("norm! 2k")
        else:
            super(BufTagExplManager, self)._toUp()

    def _toDown(self):
        if self._supports_preview:
            if lfEval("line('$') - line('.') > 2") == '1':
                lfCmd("norm! 2j")
        else:
            super(BufTagExplManager, self)._toDown()

#*****************************************************
# bufTagExplManager is a singleton
#*****************************************************
bufTagExplManager = BufTagExplManager()

__all__ = ['bufTagExplManager']

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import sys
import re
import os
import os.path
import locale
import traceback

lfCmd = vim.command
lfEval = vim.eval

lf_encoding = lfEval("&encoding")

if sys.version_info >= (3, 0):

    def lfEncode(str):
        return str

    def lfDecode(str):
        return str

    def lfOpen(file, mode='r', buffering=-1, encoding=None, errors=None,
               newline=None, closefd=True):
        return open(file, mode, buffering, encoding, errors, newline, closefd)

    def lfBytesLen(str):
        """ string length in bytes """
        return len(str.encode(lf_encoding, errors="ignore"))

    def lfBytes2Str(bytes, encoding=None):
        try:
            if encoding:
                return bytes.decode(encoding)
            else:
                if locale.getdefaultlocale()[1] is None:
                    return bytes.decode()
                else:
                    return bytes.decode(locale.getdefaultlocale()[1])
        except ValueError:
            return bytes.decode(errors="ignore")
        except UnicodeDecodeError:
            return bytes.decode(errors="ignore")

    def lfGetCwd():
        return os.getcwd()

else: # python 2.x

    range = xrange

    def lfEncode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(locale.getdefaultlocale()[1]).encode(lf_encoding)
        except ValueError:
            return str
        except UnicodeDecodeError:
            return str

    def lfDecode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(lf_encoding).encode(
                        locale.getdefaultlocale()[1])
        except UnicodeDecodeError:
            return str
        except:
            return str

    def lfOpen(file, mode='r', buffering=-1, encoding=None, errors=None,
               newline=None, closefd=True):
        return open(file, mode, buffering)

    def lfBytesLen(str):
        """ string length in bytes """
        return len(str)

    def lfBytes2Str(bytes, encoding=None):
        return bytes

    def lfGetCwd():
        return os.getcwdu().encode(lf_encoding)

#-----------------------------------------------------------------------------

if os.name == 'nt':

    # os.path.basename is too slow!
    def getBasename(path):
        for i, c in enumerate(reversed(path)):
            if c in '/\\':
                backslash_pos = len(path) - i
                break
        else:
            return path

        return path[backslash_pos:]

    # os.path.dirname is too slow!
    def getDirname(path):
        for i, c in enumerate(reversed(path)):
            if c in '/\\':
                backslash_pos = len(path) - i
                break
        else:
            return ''

        return path[:backslash_pos]

else:

    # os.path.basename is too slow!
    def getBasename(path):
        slash_pos = path.rfind(os.sep)
        return path if slash_pos == -1 else path[slash_pos + 1:]

    # os.path.dirname is too slow!
    def getDirname(path):
        slash_pos = path.rfind(os.sep)
        return '' if slash_pos == -1 else path[:slash_pos+1]

def escQuote(str):
    return "" if str is None else str.replace("'","''")

def escSpecial(str):
    return re.sub('([%#$" ])', r"\\\1", str)

def equal(str1, str2, ignorecase=True):
    if ignorecase:
        return str1.upper() == str2.upper()
    else:
        return str1 == str2

def lfRelpath(path, start=os.curdir):
    try:
        return lfEncode(os.path.relpath(lfDecode(path), start))
    except ValueError:
        return path

def lfWinId(winnr, tab=None):
    if lfEval("exists('*win_getid')") == '1':
        if tab:
            return int(lfEval("win_getid(%d, %d)" % (winnr, tab)))
        else:
            return int(lfEval("win_getid(%d)" % winnr))
    else:
        return None

def lfPrintError(error):
    if lfEval("get(g:, 'Lf_Exception', 0)") == '1':
        raise error
    else:
        error = lfEncode(str(repr(error)))
        lfCmd("echohl Error | redraw | echo '%s' | echohl None" % escQuote(error))

def lfPrintTraceback(msg=''):
    error = traceback.format_exc()
    error = error[error.find("\n") + 1:].strip()
    if msg:
        error = msg + "\n" + error
    lfCmd("echohl WarningMsg | redraw")
    lfCmd("echom '%s' | echohl None" % escQuote(error))

def lfActualLineCount(buffer, start, end, col_width):
    num = 0
    for i in buffer[start:end]:
        try:
            num += (int(lfEval("strdisplaywidth('%s')" % escQuote(i))) + col_width - 1) // col_width
        except:
            num += (int(lfEval("strdisplaywidth('%s')" % escQuote(i).replace('\x00', '\x01'))) + col_width - 1) // col_width
    return num

def lfDrop(type, file_name, line_num=None):
    if line_num:
        line_num = int(line_num)

    if 0 and lfEval("has('patch-8.0.1508')") == '1':
        if type == "tab":
            if line_num:
                lfCmd("keepj tab drop %s | %d" % (escSpecial(file_name), line_num))
            else:
                lfCmd("keepj tab drop %s" % escSpecial(file_name))
        else:
            if line_num:
                lfCmd("keepj hide drop %s | %d" % (escSpecial(file_name), line_num))
            else:
                lfCmd("keepj hide drop %s" % escSpecial(file_name))
    else:
        if type == "tab":
            for tp, w in ((tp, window) for tp in vim.tabpages for window in tp.windows):
                if w.buffer.name == file_name:
                    vim.current.tabpage = tp
                    vim.current.window = w
                    if line_num:
                        vim.current.window.cursor = (line_num, 0)
                    break
            else:
                if line_num:
                    lfCmd("tabe %s | %d" % (escSpecial(file_name), line_num))
                else:
                    lfCmd("tabe %s" % escSpecial(file_name))
        else:
            for w in vim.windows:
                if w.buffer.name == file_name:
                    vim.current.window = w
                    if line_num:
                        vim.current.window.cursor = (line_num, 0)
                    break
            else:
                if line_num:
                    lfCmd("hide edit +%d %s" % (line_num, escSpecial(file_name)))
                else:
                    lfCmd("hide edit %s" % escSpecial(file_name))

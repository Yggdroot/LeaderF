#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import sys
import re
import os
import locale
from functools import wraps

if sys.version_info >= (3, 0):

    def lfEncode(str):
        return str

    def lfDecode(str):
        return str

    def lfOpen(file, mode='r', buffering=-1, encoding=None, errors=None,
               newline=None, closefd=True):
        return open(file, mode, buffering, encoding, errors, newline, closefd)

else: # python 2.x

    range = xrange

    def lfEncode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(locale.getdefaultlocale()[1]).encode(
                        vim.eval("&encoding"))
        except ValueError:
            return str
        except UnicodeDecodeError:
            return str

    def lfDecode(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(vim.eval("&encoding")).encode(
                        locale.getdefaultlocale()[1])
        except UnicodeDecodeError:
            return str

    def lfOpen(file, mode='r', buffering=-1, encoding=None, errors=None,
               newline=None, closefd=True):
        return open(file, mode, buffering)


#-----------------------------------------------------------------------------

def showRelativePath(func):
    @wraps(func)
    def deco(*args, **kwargs):
        if vim.eval("g:Lf_ShowRelativePath") == '1':
            try:
                return [os.path.relpath(line) for line in func(*args, **kwargs)]
            except ValueError:
                return func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    return deco

# os.path.basename is too slow!
def getBasename(path):
    slash_pos = path.rfind(os.sep)
    return path if slash_pos == -1 else path[slash_pos + 1:]

# os.path.dirname is too slow!
def getDirname(path):
    slash_pos = path.rfind(os.sep)
    return ('' if slash_pos == -1
            else '/' if slash_pos == 0
            else path[:slash_pos+1] if os.name == 'nt' and path[slash_pos-1] == ':'
            else path[:slash_pos])

def escQuote(str):
    return "" if str is None else str.replace("'","''")

def escSpecial(str):
    return re.sub('([%#" ])', r"\\\1", str)

def hasBug():
    return int(vim.eval("v:version")) < 704 and sys.version_info >= (3,0)

# In vim7.3, `buffer[nr:] = content` will raise
# "TypeError: sequence index must be integer, not 'slice'"
def appendBuffer(buffer, content, nr):
    """
    this function operations on the vim.current.buffer, the `buffer` argument
    is vim.current.buffer; replace the lines of current buffer below line
    `nr`(start from 1) with new list of lines,
    """
    if hasBug():
        for i, line in enumerate(content):
            vim.command("call setline(%d, '%s')" % (nr+i+1, escQuote(line).rstrip()))
    else:
        buffer[nr:] = content

# vim.current.buffer.append() has bug about multibyte characters in vim7.3
def insertBuffer(buffer, content, nr):
    """
    this function operations on the vim.current.buffer like appendBuffer();
    insert a list of lines to the current buffer below line `nr`(start from 1)
    """
    if int(vim.eval("v:version")) < 704:
        for i, line in enumerate(content):
            vim.command("call append(%d, '%s')" % (nr+i, escQuote(line).rstrip()))
    else:
        buffer.append(content, nr)

def setBuffer(buffer, content):
    if hasBug():
        for i in range(len(buffer)):
            del buffer[0]
        appendBuffer(buffer, content, 0)
    else:
        buffer[:] = content

def swapLine(m, n):
    if m == n:
        return
    cb = vim.current.buffer
    if hasBug():
        linem = cb[m]
        linen = cb[n]
        linem, linen = linen, linem
        vim.command("call setline(%d, '%s')" % (m+1, escQuote(linem)))
        vim.command("call setline(%d, '%s')" % (n+1, escQuote(linen)))
    else:
        cb[m], cb[n] = cb[n], cb[m]

def equal(str1, str2, ignorecase=True):
    if ignorecase:
        return str1.upper() == str2.upper()
    else:
        return str1 == str2

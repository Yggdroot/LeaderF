#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import sys
import re
import os
import locale

if sys.version_info >= (3,0):

    def uniCoding(str):
        return str

    def lfOpen(file, mode = 'r', buffering = -1, encoding = None, errors = None, newline = None, closefd = True):
        return open(file, mode, buffering, encoding, errors, newline, closefd)

else: # python 2.x

    range = xrange

    def uniCoding(str):
        try:
            if locale.getdefaultlocale()[1] is None:
                return str
            else:
                return str.decode(locale.getdefaultlocale()[1]).encode(vim.eval("&encoding"))
        except UnicodeDecodeError:
            return str

    def lfOpen(file, mode = 'r', buffering = -1, encoding = None, errors = None, newline = None, closefd = True):
        return open(file, mode, buffering)


#-----------------------------------------------------------------------------

def escQuote(str):
    return "" if str is None else str.replace("'","''")

def escSpecial(str):
    return re.sub('([%#" ])', r"\\\1", str)

def hasBug():
    return int(vim.eval("v:version")) < 704 and sys.version_info >= (3,0)

#append() has bug in vim7.3
def appendBuffer(buffer, content, nr):
    if hasBug():
        for i, line in enumerate(content):
            vim.command("call setline(%d, '%s')" % (nr+i+1, escQuote(line).rstrip()))
    else:
        buffer[nr:] = content

def append(buffer, content, nr):
    if int(vim.eval("v:version")) < 704:
        for i, line in enumerate(content):
            vim.command("call append(%d, '%s')" % (nr+i, escQuote(line).rstrip()))
    else:
        buffer.append(content, nr)

def setBuffer(buffer, content):
    if hasBug():
        num = len(buffer)
        for i in range(num):
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

def equal(str1, str2, ignorecase = True):
    if ignorecase:
        return str1.upper() == str2.upper()
    else:
        return str1 == str2

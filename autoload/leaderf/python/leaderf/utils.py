#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import sys
import re
import os
import os.path
import time
import locale
import traceback
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from functools import wraps


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

def nearestAncestor(markers, path):
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

extension_ft = {
    ".8th"         : "8th",
    ".aap"         : "aap",
    ".abap"        : "abap",
    ".abc"         : "abc",
    ".abl"         : "abel",
    ".wrm"         : "acedb",
    ".adb"         : "ada",
    ".ads"         : "ada",
    ".ada"         : "ada",
    ".gpr"         : "ada",
    ".tdf"         : "ahdl",
    ".aidl"        : "aidl",
    ".run"         : "ampl",
    ".ino"         : "arduino",
    ".pde"         : "arduino",
    ".a65"         : "a65",
    ".scpt"        : "applescript",
    ".am"          : "elf",
    ".aml"         : "aml",
    ".art"         : "art",
    ".asciidoc"    : "asciidoc",
    ".adoc"        : "asciidoc",
    ".asn"         : "asn",
    ".asn1"        : "asn",
    ".demo"        : "maxima",
    ".wxm"         : "maxima",
    ".mar"         : "vmasm",
    ".astro"       : "astro",
    ".atl"         : "atlas",
    ".as"          : "atlas",
    ".atom"        : "xml",
    ".au3"         : "autoit",
    ".ahk"         : "autohotkey",
    ".at"          : "m4",
    ".ave"         : "ave",
    ".awk"         : "awk",
    ".gawk"        : "awk",
    ".mch"         : "b",
    ".ref"         : "b",
    ".imp"         : "b",
    ".bass"        : "bass",
    ".vb"          : "vb",
    ".vbs"         : "vb",
    ".dsm"         : "vb",
    ".ctl"         : "vb",
    ".iba"         : "ibasic",
    ".ibi"         : "ibasic",
    ".fb"          : "freebasic",
    ".bat"         : "dosbatch",
    ".bc"          : "bc",
    ".bdf"         : "bdf",
    ".beancount"   : "beancount",
    ".bib"         : "bib",
    ".bst"         : "bst",
    ".bicep"       : "bicep",
    ".bl"          : "blank",
    ".bb"          : "bitbake",
    ".bbappend"    : "bitbake",
    ".bbclass"     : "bitbake",
    ".bsd"         : "bsdl",
    ".bsdl"        : "bsdl",
    ".bzl"         : "bzl",
    ".bazel"       : "bzl",
    ".BUILD"       : "bzl",
    ".lpc"         : "lpc",
    ".ulpc"        : "lpc",
    ".cairo"       : "cairo",
    ".capnp"       : "capnp",
    ".cs"          : "cs",
    ".csx"         : "cs",
    ".csdl"        : "csdl",
    ".cabal"       : "cabal",
    ".toc"         : "cdrtoc",
    ".chai"        : "chaiscript",
    ".chatito"     : "chatito",
    ".cdl"         : "cdl",
    ".recipe"      : "conaryrecipe",
    ".cpon"        : "cpon",
    ".crm"         : "crm",
    ".cyn"         : "cynpp",
    ".c"           : "c",
    ".cc"          : "cpp",
    ".cpp"         : "cpp",
    ".cxx"         : "cpp",
    ".c++"         : "cpp",
    ".c++m"        : "cpp",
    ".h"           : "cpp",
    ".hh"          : "cpp",
    ".hxx"         : "cpp",
    ".hpp"         : "cpp",
    ".ipp"         : "cpp",
    ".moc"         : "cpp",
    ".tcc"         : "cpp",
    ".inl"         : "cpp",
    ".C"           : "cpp",
    ".H"           : "cpp",
    ".cppm"        : "cpp",
    ".ccm"         : "cpp",
    ".cxxm"        : "cpp",
    ".chf"         : "ch",
    ".tlh"         : "cpp",
    ".css"         : "css",
    ".con"         : "cterm",
    ".chopro"      : "chordpro",
    ".crd"         : "chordpro",
    ".cho"         : "chordpro",
    ".crdpro"      : "chordpro",
    ".chordpro"    : "chordpro",
    ".dcl"         : "clean",
    ".icl"         : "clean",
    ".eni"         : "cl",
    ".clj"         : "clojure",
    ".cljs"        : "clojure",
    ".cljx"        : "clojure",
    ".cljc"        : "clojure",
    ".cmake"       : "cmake",
    ".cbl"         : "cobol",
    ".cob"         : "cobol",
    ".lib"         : "cobol",
    ".atg"         : "coco",
    ".cfm"         : "cf",
    ".cfi"         : "cf",
    ".cfc"         : "cf",
    ".cook"        : "cook",
    ".cql"         : "cqlang",
    ".cr"          : "crystal",
    ".csv"         : "csv",
    ".cu"          : "cuda",
    ".cuh"         : "cuda",
    ".cue"         : "cue",
    ".dcd"         : "dcd",
    ".exs"         : "elixir",
    ".eex"         : "eelixir",
    ".leex"        : "eelixir",
    ".elv"         : "elvish",
    ".lrc"         : "lyrics",
    ".quake"       : "m3quake",
    ".qc"          : "c",
    ".feature"     : "cucumber",
    ".csp"         : "csp",
    ".fdr"         : "csp",
    ".pld"         : "cupl",
    ".si"          : "cuplsim",
    ".dart"        : "dart",
    ".drt"         : "dart",
    ".dhall"       : "dhall",
    ".desc"        : "desc",
    ".desktop"     : "desktop",
    ".directory"   : "desktop",
    ".diff"        : "diff",
    ".rej"         : "diff",
    ".dot"         : "dot",
    ".gv"          : "dot",
    ".lid"         : "dylanlid",
    ".intr"        : "dylanintr",
    ".dylan"       : "dylan",
    ".def"         : "def",
    ".drac"        : "dracula",
    ".drc"         : "dracula",
    ".ds"          : "datascript",
    ".dtd"         : "dtd",
    ".dts"         : "dts",
    ".dtsi"        : "dts",
    ".ecd"         : "ecd",
    ".erl"         : "erlang",
    ".hrl"         : "erlang",
    ".yaws"        : "erlang",
    ".elm"         : "elm",
    ".lc"          : "elsa",
    ".esdl"        : "esdl",
    ".ec"          : "esqlc",
    ".EC"          : "esqlc",
    ".strl"        : "esterel",
    ".csc"         : "csc",
    ".exp"         : "expect",
    ".fal"         : "falcon",
    ".fan"         : "fan",
    ".fwt"         : "fan",
    ".factor"      : "factor",
    ".fnl"         : "fennel",
    ".fir"         : "firrtl",
    ".fish"        : "fish",
    ".fex"         : "focexec",
    ".focexec"     : "focexec",
    ".mas"         : "master",
    ".master"      : "master",
    ".ft"          : "forth",
    ".fth"         : "forth",
    ".frt"         : "reva",
    ".F"           : "fortran",
    ".FOR"         : "fortran",
    ".FPP"         : "fortran",
    ".FTN"         : "fortran",
    ".F77"         : "fortran",
    ".F90"         : "fortran",
    ".F95"         : "fortran",
    ".F03"         : "fortran",
    ".F08"         : "fortran",
    ".f"           : "fortran",
    ".for"         : "fortran",
    ".fortran"     : "fortran",
    ".fpp"         : "fortran",
    ".ftn"         : "fortran",
    ".f77"         : "fortran",
    ".f90"         : "fortran",
    ".f95"         : "fortran",
    ".f03"         : "fortran",
    ".f08"         : "fortran",
    ".fsl"         : "framescript",
    ".fc"          : "func",
    ".fusion"      : "fusion",
    ".fsh"         : "fsh",
    ".fsi"         : "fsharp",
    ".fsx"         : "fsharp",
    ".gdb"         : "gdb",
    ".mo"          : "gdmo",
    ".gdmo"        : "gdmo",
    ".gd"          : "gdscript",
    ".tscn"        : "gdresource",
    ".tres"        : "gdresource",
    ".gdshader"    : "gdshader",
    ".shader"      : "gdshader",
    ".ged"         : "gedcom",
    ".gmi"         : "gemtext",
    ".gemini"      : "gemtext",
    ".gift"        : "gift",
    ".gleam"       : "gleam",
    ".glsl"        : "glsl",
    ".gp"          : "gp",
    ".gts"         : "typescript.glimmer",
    ".gjs"         : "javascript.glimmer",
    ".gpi"         : "gnuplot",
    ".go"          : "go",
    ".gs"          : "grads",
    ".graphql"     : "graphql",
    ".graphqls"    : "graphql",
    ".gql"         : "graphql",
    ".gretl"       : "gretl",
    ".gradle"      : "groovy",
    ".groovy"      : "groovy",
    ".gsp"         : "gsp",
    ".gyp"         : "gyp",
    ".gypi"        : "gyp",
    ".hack"        : "hack",
    ".hackpartial" : "hack",
    ".haml"        : "haml",
    ".hsm"         : "hamster",
    ".hbs"         : "handlebars",
    ".ha"          : "hare",
    ".hs"          : "haskell",
    ".hsc"         : "haskell",
    ".hsig"        : "haskell",
    ".lhs"         : "lhaskell",
    ".chs"         : "chaskell",
    ".ht"          : "haste",
    ".htpp"        : "hastepreproc",
    ".hcl"         : "hcl",
    ".vc"          : "hercules",
    ".ev"          : "hercules",
    ".sum"         : "hercules",
    ".errsum"      : "hercules",
    ".heex"        : "heex",
    ".hex"         : "hex",
    ".h32"         : "hex",
    ".hjson"       : "hjson",
    ".m3u"         : "hlsplaylist",
    ".m3u8"        : "hlsplaylist",
    ".hws"         : "hollywood",
    ".hoon"        : "hoon",
    ".htm"         : "html",
    ".html"        : "html",
    ".shtml"       : "html",
    ".stm"         : "html",
    ".cshtml"      : "html",
    ".cshtml"      : "html",
    ".erb"         : "eruby",
    ".rhtml"       : "eruby",
    ".tmpl"        : "template",
    ".hb"          : "hb",
    ".htt"         : "httest",
    ".htb"         : "httest",
    ".icn"         : "icon",
    ".odl"         : "msidl",
    ".mof"         : "msidl",
    ".inf"         : "inform",
    ".INF"         : "inform",
    ".ii"          : "initng",
    ".4gl"         : "fgl",
    ".4gh"         : "fgl",
    ".m4gl"        : "fgl",
    ".ini"         : "dosini",
    ".iss"         : "iss",
    ".ijs"         : "j",
    ".jal"         : "jal",
    ".JAL"         : "jal",
    ".jpl"         : "jam",
    ".jpr"         : "jam",
    ".java"        : "java",
    ".jav"         : "java",
    ".jj"          : "javacc",
    ".jjt"         : "javacc",
    ".js"          : "javascript",
    ".jsm"         : "javascript",
    ".javascript"  : "javascript",
    ".es"          : "javascript",
    ".mjs"         : "javascript",
    ".cjs"         : "javascript",
    ".jsx"         : "javascriptreact",
    ".jsp"         : "jsp",
    ".properties"  : "jproperties",
    ".clp"         : "jess",
    ".jgr"         : "jgraph",
    ".jov"         : "jovial",
    ".j73"         : "jovial",
    ".jovial"      : "jovial",
    ".jq"          : "jq",
    ".json5"       : "json5",
    ".ipynb"       : "json",
    ".jsonc"       : "jsonc",
    ".json"        : "json",
    ".jsonp"       : "json",
    ".webmanifest" : "json",
    ".jsonnet"     : "jsonnet",
    ".libsonnet"   : "jsonnet",
    ".jl"          : "julia",
    ".kdl"         : "kdl",
    ".kix"         : "kix",
    ".k"           : "kwt",
    ".kv"          : "kivy",
    ".kt"          : "kotlin",
    ".ktm"         : "kotlin",
    ".kts"         : "kotlin",
    ".ks"          : "kscript",
    ".ace"         : "lace",
    ".ACE"         : "lace",
    ".latte"       : "latte",
    ".lte"         : "latte",
    ".ldif"        : "ldif",
    ".ld"          : "ld",
    ".lean"        : "lean",
    ".ldg"         : "ledger",
    ".ledger"      : "ledger",
    ".journal"     : "ledger",
    ".less"        : "less",
    ".lex"         : "lex",
    ".l"           : "lex",
    ".lxx"         : "lex",
    ".ll"          : "lifelines",
    ".ly"          : "lilypond",
    ".ily"         : "lilypond",
    ".lsp"         : "lisp",
    ".lisp"        : "lisp",
    ".asd"         : "lisp",
    ".el"          : "lisp",
    ".cl"          : "lisp",
    ".L"           : "lisp",
    ".liquid"      : "liquid",
    ".lite"        : "lite",
    ".lt"          : "lite",
    ".livemd"      : "livebook",
    ".lgt"         : "logtalk",
    ".lot"         : "lotos",
    ".lotos"       : "lotos",
    ".lou"         : "lout",
    ".lout"        : "lout",
    ".lua"         : "lua",
    ".luau"        : "luau",
    ".rockspec"    : "lua",
    ".lss"         : "lss",
    ".mgp"         : "mgp",
    ".eml"         : "mail",
    ".mk"          : "make",
    ".mak"         : "make",
    ".dsp"         : "make",
    ".ist"         : "ist",
    ".mst"         : "ist",
    ".page"        : "mallard",
    ".man"         : "man",
    ".mv"          : "maple",
    ".mpl"         : "maple",
    ".mws"         : "maple",
    ".map"         : "map",
    ".markdown"    : "markdown",
    ".mdown"       : "markdown",
    ".mkd"         : "markdown",
    ".mkdn"        : "markdown",
    ".mdwn"        : "markdown",
    ".md"          : "markdown",
    ".mason"       : "mason",
    ".mhtml"       : "mason",
    ".comp"        : "mason",
    ".nb"          : "mma",
    ".mel"         : "mel",
    ".hgrc"        : "cfg",
    ".mmd"         : "mermaid",
    ".mmdc"        : "mermaid",
    ".mermaid"     : "mermaid",
    ".wrap"        : "dosini",
    ".mf"          : "mf",
    ".mp"          : "mp",
    ".mgl"         : "mgl",
    ".mix"         : "mix",
    ".mixal"       : "mix",
    ".mmp"         : "mmp",
    ".m2"          : "modula2",
    ".DEF"         : "modula2",
    ".mi"          : "modula2",
    ".lm3"         : "modula3",
    ".isc"         : "monk",
    ".monk"        : "monk",
    ".ssc"         : "monk",
    ".tsc"         : "monk",
    ".moo"         : "moo",
    ".moon"        : "moonscript",
    ".move"        : "move",
    ".mpd"         : "xml",
    ".s19"         : "srec",
    ".s28"         : "srec",
    ".s37"         : "srec",
    ".mot"         : "srec",
    ".srec"        : "srec",
    ".msql"        : "msql",
    ".mysql"       : "mysql",
    ".mu"          : "mupad",
    ".mush"        : "mush",
    ".n1ql"        : "n1ql",
    ".nql"         : "n1ql",
    ".nanorc"      : "nanorc",
    ".nginx"       : "nginx",
    ".nim"         : "nim",
    ".nims"        : "nim",
    ".nimble"      : "nim",
    ".ninja"       : "ninja",
    ".nix"         : "nix",
    ".ncf"         : "ncf",
    ".tr"          : "nroff",
    ".nr"          : "nroff",
    ".roff"        : "nroff",
    ".tmac"        : "nroff",
    ".mom"         : "nroff",
    ".nqc"         : "nqc",
    ".nse"         : "lua",
    ".nsi"         : "nsis",
    ".nsh"         : "nsis",
    ".obl"         : "obse",
    ".obse"        : "obse",
    ".oblivion"    : "obse",
    ".obscript"    : "obse",
    ".ml"          : "ocaml",
    ".mli"         : "ocaml",
    ".mll"         : "ocaml",
    ".mly"         : "ocaml",
    ".mlt"         : "ocaml",
    ".mlp"         : "ocaml",
    ".mlip"        : "ocaml",
    ".occ"         : "occam",
    ".odin"        : "odin",
    ".xom"         : "omnimark",
    ".xin"         : "omnimark",
    ".opam"        : "opam",
    ".or"          : "openroad",
    ".scad"        : "openscad",
    ".ora"         : "ora",
    ".org"         : "org",
    ".org_archive" : "org",
    ".nmconnection": "confini",
    ".papp"        : "papp",
    ".pxml"        : "papp",
    ".pxsl"        : "papp",
    ".pas"         : "pascal",
    ".dpr"         : "pascal",
    ".lpr"         : "pascal",
    ".fpc"         : "fpcmake",
    ".filter"      : "poefilter",
    ".pdf"         : "pdf",
    ".pcmk"        : "pcmk",
    ".plx"         : "perl",
    ".al"          : "perl",
    ".psgi"        : "perl",
    ".pod"         : "pod",
    ".php"         : "php",
    ".phtml"       : "php",
    ".ctp"         : "php",
    ".phpt"        : "php",
    ".theme"       : "php",
    ".pike"        : "pike",
    ".pmod"        : "pike",
    ".cmod"        : "cmod",
    ".rcp"         : "pilrc",
    ".pli"         : "pli",
    ".pl1"         : "pli",
    ".plm"         : "plm",
    ".p36"         : "plm",
    ".pac"         : "plm",
    ".pls"         : "plsql",
    ".plsql"       : "plsql",
    ".plp"         : "plp",
    ".po"          : "po",
    ".pot"         : "po",
    ".pony"        : "pony",
    ".ps"          : "postscr",
    ".pfa"         : "postscr",
    ".afm"         : "postscr",
    ".eps"         : "postscr",
    ".epsf"        : "postscr",
    ".epsi"        : "postscr",
    ".ai"          : "postscr",
    ".ppd"         : "ppd",
    ".pov"         : "pov",
    ".ps1"         : "ps1",
    ".psd1"        : "ps1",
    ".psm1"        : "ps1",
    ".pssc"        : "ps1",
    ".ps1xml"      : "ps1xml",
    ".cdxml"       : "xml",
    ".psc1"        : "xml",
    ".prisma"      : "prisma",
    ".g"           : "pccts",
    ".it"          : "ppwiz",
    ".ih"          : "ppwiz",
    ".pug"         : "pug",
    ".epp"         : "epuppet",
    ".obj"         : "obj",
    ".pc"          : "proc",
    ".action"      : "privoxy",
    ".psf"         : "psf",
    ".pdb"         : "prolog",
    ".pml"         : "promela",
    ".psl"         : "psl",
    ".proto"       : "proto",
    ".pbtxt"       : "pbtxt",
    ".pk"          : "poke",
    ".arr"         : "pyret",
    ".pyx"         : "pyrex",
    ".pxd"         : "pyrex",
    ".py"          : "python",
    ".pyw"         : "python",
    ".ptl"         : "python",
    ".pyi"         : "python",
    ".ql"          : "ql",
    ".qll"         : "ql",
    ".qmd"         : "quarto",
    ".rkt"         : "racket",
    ".rktd"        : "racket",
    ".rktl"        : "racket",
    ".rad"         : "radiance",
    ".mat"         : "radiance",
    ".pm6"         : "raku",
    ".p6"          : "raku",
    ".t6"          : "raku",
    ".pod6"        : "raku",
    ".raku"        : "raku",
    ".rakumod"     : "raku",
    ".rakudoc"     : "raku",
    ".rakutest"    : "raku",
    ".rib"         : "rib",
    ".rego"        : "rego",
    ".rex"         : "rexx",
    ".orx"         : "rexx",
    ".rxo"         : "rexx",
    ".rxj"         : "rexx",
    ".jrexx"       : "rexx",
    ".rexxj"       : "rexx",
    ".rexx"        : "rexx",
    ".testGroup"   : "rexx",
    ".testUnit"    : "rexx",
    ".rd"          : "rhelp",
    ".Rd"          : "rhelp",
    ".Rnw"         : "rnoweb",
    ".rnw"         : "rnoweb",
    ".Snw"         : "rnoweb",
    ".snw"         : "rnoweb",
    ".Rmd"         : "rmd",
    ".rmd"         : "rmd",
    ".Smd"         : "rmd",
    ".smd"         : "rmd",
    ".rss"         : "xml",
    ".Rrst"        : "rrst",
    ".rrst"        : "rrst",
    ".Srst"        : "rrst",
    ".srst"        : "rrst",
    ".remind"      : "remind",
    ".rem"         : "remind",
    ".res"         : "rescript",
    ".resi"        : "rescript",
    ".rnc"         : "rnc",
    ".rng"         : "rng",
    ".rpgle"       : "rpgle",
    ".rpgleinc"    : "rpgle",
    ".rpl"         : "rpl",
    ".robot"       : "robot",
    ".resource"    : "robot",
    ".ron"         : "ron",
    ".rsc"         : "routeros",
    ".x"           : "rpcgen",
    ".rst"         : "rst",
    ".rtf"         : "rtf",
    ".rb"          : "ruby",
    ".rbw"         : "ruby",
    ".gemspec"     : "ruby",
    ".rbs"         : "rbs",
    ".ru"          : "ruby",
    ".builder"     : "ruby",
    ".rxml"        : "ruby",
    ".rjs"         : "ruby",
    ".rant"        : "ruby",
    ".rake"        : "ruby",
    ".rs"          : "rust",
    ".sl"          : "slang",
    ".sage"        : "sage",
    ".sas"         : "sas",
    ".sass"        : "sass",
    ".sa"          : "sather",
    ".scala"       : "scala",
    ".sbt"         : "sbt",
    ".quark"       : "supercollider",
    ".sci"         : "scilab",
    ".sce"         : "scilab",
    ".scss"        : "scss",
    ".sd"          : "sd",
    ".sdl"         : "sdl",
    ".pr"          : "sdl",
    ".sed"         : "sed",
    ".srt"         : "srt",
    ".ass"         : "ssa",
    ".ssa"         : "ssa",
    ".svelte"      : "svelte",
    ".siv"         : "sieve",
    ".sieve"       : "sieve",
    ".zig"         : "zig",
    ".zir"         : "zir",
    ".zsh"         : "zsh",
    ".scm"         : "scheme",
    ".ss"          : "scheme",
    ".sld"         : "scheme",
    ".sexp"        : "sexplib",
    ".sim"         : "simula",
    ".sin"         : "sinda",
    ".s85"         : "sinda",
    ".sst"         : "sisu",
    ".ssm"         : "sisu",
    ".ssi"         : "sisu",
    "._sst"        : "sisu",
    ".il"          : "skill",
    ".ils"         : "skill",
    ".cdf"         : "skill",
    ".cdc"         : "cdc",
    ".score"       : "slrnsc",
    ".smali"       : "smali",
    ".st"          : "st",
    ".tpl"         : "smarty",
    ".smt"         : "smith",
    ".smith"       : "smith",
    ".smithy"      : "smithy",
    ".sno"         : "snobol4",
    ".spt"         : "snobol4",
    ".mib"         : "mib",
    ".my"          : "mib",
    ".hog"         : "hog",
    ".sol"         : "solidity",
    ".rq"          : "sparql",
    ".sparql"      : "sparql",
    ".spec"        : "spec",
    ".speedup"     : "spup",
    ".spdata"      : "spup",
    ".spd"         : "spup",
    ".ice"         : "slice",
    ".sln"         : "solution",
    ".slnf"        : "json",
    ".sp"          : "spice",
    ".spice"       : "spice",
    ".spy"         : "spyce",
    ".spi"         : "spyce",
    ".tyb"         : "sql",
    ".tyc"         : "sql",
    ".pkb"         : "sql",
    ".pks"         : "sql",
    ".sqlj"        : "sqlj",
    ".prql"        : "prql",
    ".sqr"         : "sqr",
    ".sqi"         : "sqr",
    ".nut"         : "squirrel",
    ".ipd"         : "starlark",
    ".star"        : "starlark",
    ".starlark"    : "starlark",
    ".ovpn"        : "openvpn",
    ".ado"         : "stata",
    ".do"          : "stata",
    ".imata"       : "stata",
    ".mata"        : "stata",
    ".hlp"         : "smcl",
    ".ihlp"        : "smcl",
    ".smcl"        : "smcl",
    ".stp"         : "stp",
    ".sml"         : "sml",
    ".cm"          : "voscm",
    ".swift"       : "swift",
    ".sdc"         : "sdc",
    ".svg"         : "svg",
    ".sface"       : "surface",
    ".td"          : "tablegen",
    ".tak"         : "tak",
    ".tal"         : "tal",
    ".task"        : "taskedit",
    ".tcl"         : "tcl",
    ".tm"          : "tcl",
    ".tk"          : "tcl",
    ".itcl"        : "tcl",
    ".itk"         : "tcl",
    ".jacl"        : "tcl",
    ".tl"          : "teal",
    ".tli"         : "tli",
    ".slt"         : "tsalt",
    ".ti"          : "terminfo",
    ".tfvars"      : "terraform-vars",
    ".latex"       : "tex",
    ".sty"         : "tex",
    ".dtx"         : "tex",
    ".ltx"         : "tex",
    ".bbl"         : "tex",
    ".mkii"        : "context",
    ".mkiv"        : "context",
    ".mkvi"        : "context",
    ".mkxl"        : "context",
    ".mklx"        : "context",
    ".texinfo"     : "texinfo",
    ".texi"        : "texinfo",
    ".txi"         : "texinfo",
    ".thrift"      : "thrift",
    ".tla"         : "tla",
    ".toml"        : "toml",
    ".tpp"         : "tpp",
    ".treetop"     : "treetop",
    ".tssgm"       : "tssgm",
    ".tssop"       : "tssop",
    ".tsscl"       : "tsscl",
    ".tsv"         : "tsv",
    ".twig"        : "twig",
    ".mts"         : "typescript",
    ".cts"         : "typescript",
    ".tsx"         : "typescriptreact",
    ".uit"         : "uil",
    ".uil"         : "uil",
    ".ungram"      : "ungrammar",
    ".uc"          : "uc",
    ".vala"        : "vala",
    ".vdf"         : "vdf",
    ".vdmpp"       : "vdmpp",
    ".vpp"         : "vdmpp",
    ".vdmrt"       : "vdmrt",
    ".vdmsl"       : "vdmsl",
    ".vdm"         : "vdmsl",
    ".vr"          : "vera",
    ".vri"         : "vera",
    ".vrh"         : "vera",
    ".va"          : "verilogams",
    ".vams"        : "verilogams",
    ".sv"          : "systemverilog",
    ".svh"         : "systemverilog",
    ".tape"        : "vhs",
    ".hdl"         : "vhdl",
    ".vhd"         : "vhdl",
    ".vhdl"        : "vhdl",
    ".vbe"         : "vhdl",
    ".vst"         : "vhdl",
    ".vho"         : "vhdl",
    ".vim"         : "vim",
    ".vba"         : "vim",
    ".sba"         : "vb",
    ".wrl"         : "vrml",
    ".vroom"       : "vroom",
    ".vue"         : "vue",
    ".wat"         : "wat",
    ".wast"        : "wast",
    ".wit"         : "wit",
    ".wm"          : "webmacro",
    ".wml"         : "wml",
    ".wbt"         : "winbatch",
    ".wsml"        : "wsml",
    ".wpl"         : "xml",
    ".xhtml"       : "xhtml",
    ".xht"         : "xhtml",
    ".xpm2"        : "xpm2",
    ".xs"          : "xs",
    ".ad"          : "xdefaults",
    ".msc"         : "xmath",
    ".msf"         : "xmath",
    ".xmi"         : "xml",
    ".csproj"      : "xml",
    ".fsproj"      : "xml",
    ".vbproj"      : "xml",
    ".ui"          : "xml",
    ".tpm"         : "xml",
    ".wsdl"        : "xml",
    ".wdl"         : "wdl",
    ".xlf"         : "xml",
    ".xliff"       : "xml",
    ".xul"         : "xml",
    ".xq"          : "xquery",
    ".xql"         : "xquery",
    ".xqm"         : "xquery",
    ".xquery"      : "xquery",
    ".xqy"         : "xquery",
    ".xsd"         : "xsd",
    ".xsl"         : "xslt",
    ".xslt"        : "xslt",
    ".yy"          : "yacc",
    ".yxx"         : "yacc",
    ".yaml"        : "yaml",
    ".yml"         : "yaml",
    ".raml"        : "raml",
    ".yang"        : "yang",
    ".yuck"        : "yuck",
    ".zu"          : "zimbu",
    ".zut"         : "zimbutempl",
    ".z8a"         : "z8a",
    ".text"        : "text",
    ".usda"        : "usd",
    ".usd"         : "usd",
    ".blp"         : "blueprint",
    ".dm1"         : "maxima",
    ".dm2"         : "maxima",
    ".dm3"         : "maxima",
    ".dmt"         : "maxima",
    ".dockerfile"  : "dockerfile",
    ".Dockerfile"  : "dockerfile",
    ".edf"         : "edif",
    ".edif"        : "edif",
    ".edo"         : "edif",
    ".hs-boot"     : "haskell",
    ".json-patch"  : "json",
    ".sub"         : "krl",
    ".l++"         : "lex",
    ".opl"         : "opl",
    ".-sst"        : "sisu",
    ".-sst.meta"   : "sisu",
    ".wsf"         : "wsh",
    ".wsc"         : "wsh",
    ".y++"         : "yacc",
    ".ebuild"      : "sh",
    ".sh"          : "sh",
    ".bash"        : "sh",
    ".env"         : "sh",
    ".eclass"      : "sh",
    ".ksh"         : "ksh",
    ".csh"         : "csh",
    ".tcsh"        : "tcsh",
    ".xml"         : "xml",
    ".csproj.user"        : "xml",
    ".fsproj.user"        : "xml",
    ".vbproj.user"        : "xml",
    ".cmake.in"           : "cmake",
    ".t.html"             : "tilde",
    ".html.m4"            : "htmlm4",
    ".upstream.dat"       : "upstreamdat",
    ".upstream.log"       : "upstreamlog",
    ".upstreaminstall.log": "upstreaminstalllog",
    ".usserver.log"       : "usserverlog",
    ".usw2kagt.log"       : "usw2kagtlog",
    ".mli.cppo"           : "ocaml",
    ".ml.cppo"            : "ocaml",
    ".opam.template"      : "opam",
    ".sst.meta"           : "sisu",
    "._sst.meta"          : "sisu",
    ".swift.gyb"          : "swiftgyb",
}

name_ft = {
    "a2psrc"             : "a2ps",
    ".a2psrc"            : "a2ps",
    "build.xml"          : "ant",
    ".htaccess"          : "apache",
    "makefile"           : "make",
    "Makefile"           : "make",
    "GNUmakefile"        : "make",
    "makefile.am"        : "automake",
    "Makefile.am"        : "automake",
    "GNUmakefile.am"     : "automake",
    ".asoundrc"          : "alsaconf",
    "apt.conf"           : "aptconf",
    ".arch-inventory"    : "arch",
    "=tagging-method"    : "arch",
    "maxima-init.mac"    : "maxima",
    "named.root"         : "bindzone",
    "WORKSPACE"          : "bzl",
    "WORKSPACE.bzlmod"   : "bzl",
    "BUILD"              : "bzl",
    ".busted"            : "lua",
    "calendar"           : "calendar",
    ".cdrdao"            : "cdrdaoconf",
    "cfengine.conf"      : "cfengine",
    "changelog.Debian"   : "debchangelog",
    "changelog.dch"      : "debchangelog",
    "NEWS.Debian"        : "debchangelog",
    "NEWS.dch"           : "debchangelog",
    ".clangd"            : "yaml",
    ".clang-format"      : "yaml",
    ".clang-tidy"        : "yaml",
    "CMakeLists.txt"     : "cmake",
    "configure.in"       : "config",
    "configure.ac"       : "config",
    "Containerfile"      : "dockerfile",
    "Dockerfile"         : "dockerfile",
    "dockerfile"         : "dockerfile",
    "mix.lock"           : "elixir",
    "lynx.cfg"           : "lynx",
    "cm3.cfg"            : "m3quake",
    "m3makefile"         : "m3build",
    "m3overrides"        : "m3build",
    "denyhosts.conf"     : "denyhosts",
    "dict.conf"          : "dictconf",
    ".dictrc"            : "dictconf",
    ".dir_colors"        : "dircolors",
    ".dircolors"         : "dircolors",
    "jbuild"             : "dune",
    "dune"               : "dune",
    "dune-project"       : "dune",
    "dune-workspace"     : "dune",
    ".editorconfig"      : "editorconfig",
    "elinks.conf"        : "elinks",
    "filter-rules"       : "elmfilt",
    "exim.conf"          : "exim",
    "exports"            : "exports",
    ".fetchmailrc"       : "fetchmail",
    "auto.master"        : "conf",
    "fstab"              : "fstab",
    "mtab"               : "fstab",
    ".gdbinit"           : "gdb",
    "gdbinit"            : "gdb",
    ".gdbearlyinit"      : "gdb",
    "gdbearlyinit"       : "gdb",
    "lltxxxxx.txt"       : "gedcom",
    "COMMIT_EDITMSG"     : "gitcommit",
    "MERGE_MSG"          : "gitcommit",
    "TAG_EDITMSG"        : "gitcommit",
    "NOTES_EDITMSG"      : "gitcommit",
    "EDIT_DESCRIPTION"   : "gitcommit",
    ".gitconfig"         : "gitconfig",
    ".gitmodules"        : "gitconfig",
    ".gitattributes"     : "gitattributes",
    ".gitignore"         : "gitignore",
    "git-rebase-todo"    : "gitrebase",
    "gkrellmrc"          : "gkrellmrc",
    ".gprc"              : "gp",
    "gnashrc"            : "gnash",
    ".gnashrc"           : "gnash",
    "gnashpluginrc"      : "gnash",
    ".gnashpluginrc"     : "gnash",
    "gitolite.conf"      : "gitolite",
    ".gitolite.rc"       : "perl",
    "example.gitolite.rc": "perl",
    ".gnuplot"           : "gnuplot",
    "Gopkg.lock"         : "toml",
    "go.work"            : "gowork",
    "Jenkinsfile"        : "groovy",
    ".gtkrc"             : "gtkrc",
    "gtkrc"              : "gtkrc",
    "cabal.project"      : "cabalproject",
    "cabal.config"       : "cabalconfig",
    "go.sum"             : "gosum",
    "go.work.sum"        : "gosum",
    ".indent.pro"        : "indent",
    "indentrc"           : "indent",
    "upstream.dat"       : "upstreamdat",
    "fdrupstream.log"    : "upstreamlog",
    "upstream.log"       : "upstreamlog",
    "upstreaminstall.log": "upstreaminstalllog",
    "usserver.log"       : "usserverlog",
    "usw2kagt.log"       : "usw2kagtlog",
    "ipf.conf"           : "ipfilter",
    "ipf6.conf"          : "ipfilter",
    "ipf.rules"          : "ipfilter",
    "inittab"            : "inittab",
    ".prettierrc"        : "json",
    ".firebaserc"        : "json",
    ".stylelintrc"       : "json",
    ".babelrc"           : "jsonc",
    ".eslintrc"          : "jsonc",
    ".jsfmtrc"           : "jsonc",
    ".jshintrc"          : "jsonc",
    ".hintrc"            : "jsonc",
    ".swrc"              : "jsonc",
    "Kconfig"            : "kconfig",
    "Kconfig.debug"      : "kconfig",
    ".latexmkrc"         : "perl",
    "latexmkrc"          : "perl",
    "lftp.conf"          : "lftp",
    ".lftprc"            : "lftp",
    "lilo.conf"          : "lilo",
    ".emacs"             : "lisp",
    ".sawfishrc"         : "lisp",
    "sbclrc"             : "lisp",
    ".sbclrc"            : "lisp",
    ".luacheckrc"        : "lua",
    ".letter"            : "mail",
    ".followup"          : "mail",
    ".article"           : "mail",
    ".mailcap"           : "mailcap",
    "mailcap"            : "mailcap",
    "man.config"         : "manconf",
    "meson.build"        : "meson",
    "meson_options.txt"  : "meson",
    "mplayer.conf"       : "mplayerconf",
    "mrxvtrc"            : "mrxvtrc",
    ".mrxvtrc"           : "mrxvtrc",
    "tclsh.rc"           : "tcl",
    "Neomuttrc"          : "neomuttrc",
    ".netrc"             : "netrc",
    "npmrc"              : "dosini",
    ".npmrc"             : "dosini",
    "env.nu"             : "nu",
    "config.nu"          : "nu",
    ".ocamlinit"         : "ocaml",
    "octave.conf"        : "octave",
    ".octaverc"          : "octave",
    "octaverc"           : "octave",
    "opam"               : "opam",
    "pf.conf"            : "pf",
    "mpv.conf"           : "confini",
    "pam_env.conf"       : "pamenv",
    ".pam_environment"   : "pamenv",
    ".pinerc"            : "pine",
    "pinerc"             : "pine",
    ".pinercex"          : "pine",
    "pinercex"           : "pine",
    "Pipfile"            : "toml",
    "Pipfile.lock"       : "json",
    "main.cf"            : "pfmain",
    "main.cf.proto"      : "pfmain",
    ".povrayrc"          : "povini",
    "Puppetfile"         : "ruby",
    ".procmail"          : "procmail",
    ".procmailrc"        : "procmail",
    ".pythonstartup"     : "python",
    ".pythonrc"          : "python",
    "SConstruct"         : "python",
    "qmldir"             : "qmldir",
    ".ratpoisonrc"       : "ratpoison",
    "ratpoisonrc"        : "ratpoison",
    ".inputrc"           : "readline",
    "inputrc"            : "readline",
    ".Rprofile"          : "r",
    "Rprofile"           : "r",
    "Rprofile.site"      : "r",
    ".reminders"         : "remind",
    "resolv.conf"        : "resolv",
    "robots.txt"         : "robots",
    ".irbrc"             : "ruby",
    "irbrc"              : "ruby",
    "Gemfile"            : "ruby",
    "rantfile"           : "ruby",
    "Rantfile"           : "ruby",
    "rakefile"           : "ruby",
    "Rakefile"           : "ruby",
    "Cargo.lock"         : "toml",
    "smb.conf"           : "samba",
    "sendmail.cf"        : "sm",
    "catalog"            : "catalog",
    ".zprofile"          : "zsh",
    ".zfbfmarks"         : "zsh",
    ".zshrc"             : "zsh",
    ".zshenv"            : "zsh",
    ".zlogin"            : "zsh",
    ".zlogout"           : "zsh",
    ".zcompdump"         : "zsh",
    ".screenrc"          : "screen",
    "screenrc"           : "screen",
    ".slrnrc"            : "slrnrc",
    "snort.conf"         : "hog",
    "vision.conf"        : "hog",
    "squid.conf"         : "squid",
    "ssh_config"         : "sshconfig",
    "sshd_config"        : "sshdconfig",
    "sudoers.tmp"        : "sudoers",
    "tags"               : "tags",
    "pending.data"       : "taskdata",
    "completed.data"     : "taskdata",
    "undo.data"          : "taskdata",
    ".tclshrc"           : "tcl",
    ".wishrc"            : "tcl",
    "texmf.cnf"          : "texmf",
    ".tidyrc"            : "tidy",
    "tidyrc"             : "tidy",
    "tidy.conf"          : "tidy",
    ".tfrc"              : "tf",
    "tfrc"               : "tf",
    "trustees.conf"      : "trustees",
    "Vagrantfile"        : "ruby",
    ".vimrc"             : "vim",
    "_vimrc"             : "vim",
    ".exrc"              : "vim",
    "_exrc"              : "vim",
    ".viminfo"           : "viminfo",
    "_viminfo"           : "viminfo",
    "vgrindefs"          : "vgrindefs",
    ".wgetrc"            : "wget",
    "wgetrc"             : "wget",
    ".wget2rc"           : "wget2",
    "wget2rc"            : "wget2",
    "wvdial.conf"        : "wvdial",
    ".wvdialrc"          : "wvdial",
    ".cvsrc"             : "cvsrc",
    ".Xdefaults"         : "xdefaults",
    ".Xpdefaults"        : "xdefaults",
    ".Xresources"        : "xdefaults",
    "xdm-config"         : "xdefaults",
    "fglrxrc"            : "xml",
    "README"             : "text",
    "LICENSE"            : "text",
    "COPYING"            : "text",
    "AUTHORS"            : "text",
    ".bashrc"            : "sh",
    "bashrc"             : "sh",
    "bash.bashrc"        : "sh",
    ".bash_profile"      : "sh",
    ".bash-profile"      : "sh",
    ".bash_logout"       : "sh",
    ".bash-logout"       : "sh",
    ".bash_aliases"      : "sh",
    ".bash-aliases"      : "sh",
    ".profile"           : "sh",
    "bash-fc-"           : "sh",
    "bash-fc."           : "sh",
    ".kshrc"             : "ksh",
    ".tcshrc"            : "tcsh",
    "tcsh.tcshrc"        : "tcsh",
    "tcsh.login"         : "tcsh",
    ".login"             : "csh",
    ".cshrc"             : "csh",
    "csh.cshrc"          : "csh",
    "csh.login"          : "csh",
    "csh.logout"         : "csh",
    ".alias"             : "csh",
    ".kshrc"             : "ksh",
    ".zshrc"             : "zsh",
}

def getExtension(path):
    basename = os.path.basename(path)
    if basename in name_ft:
        return name_ft[basename]
    else:
        root, ext = os.path.splitext(basename)
        if ext == '':
            return None

        _, ext2 = os.path.splitext(root)
        if ext2 != '':
            extension = ext2 + ext
            if extension in extension_ft:
                return extension_ft[extension]

        if ext == '.txt' and os.path.dirname(path) == lfEval("expand('$VIMRUNTIME/doc')"):
            return "help"

        return extension_ft.get(ext, None)

def ignoreEvent(events):
    def wrapper(func):
        @wraps(func)
        def deco(self, *args, **kwargs):
            try:
                saved_eventignore = vim.options['eventignore']
                vim.options['eventignore'] = events

                return func(self, *args, **kwargs)
            finally:
                vim.options['eventignore'] = saved_eventignore
        return deco
    return wrapper

def printTime(func):
    @wraps(func)
    def deco(self, *args, **kwargs):
        try:
            start = time.time()
            return func(self, *args, **kwargs)
        finally:
            print(func.__name__, time.time() - start)

    return deco

def tabmove():
    tab_pos = int(lfEval("g:Lf_TabpagePosition"))
    if tab_pos == 0:
        lfCmd("tabm 0")
    elif tab_pos == 1:
        lfCmd("tabm -1")
    elif tab_pos == 3:
        lfCmd("tabm")

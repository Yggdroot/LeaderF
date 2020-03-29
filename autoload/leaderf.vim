" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if !exists("g:Lf_PythonVersion")
    if has("python3")
        let g:Lf_PythonVersion = 3
        let g:Lf_py = "py3 "
    elseif has("python")
        let g:Lf_PythonVersion = 2
        let g:Lf_py = "py "
    else
        echoe "Error: LeaderF requires vim compiled with +python or +python3"
        finish
    endif
else
    if g:Lf_PythonVersion == 2
        if has("python")
            let g:Lf_py = "py "
        else
            echoe 'LeaderF Error: has("python") == 0'
            finish
        endif
    else
        if has("python3")
            let g:Lf_py = "py3 "
        else
            echoe 'LeaderF Error: has("python3") == 0'
            finish
        endif
    endif
endif

if exists('g:leaderf#loaded')
    finish
else
    let g:leaderf#loaded = 1
endif

silent! exec g:Lf_py "pass"
exec g:Lf_py "import vim, sys, os, re, os.path"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "cwd = re.sub(r'(?<=^.)', ':', os.sep.join(cwd.split('/')[1:])) if os.name == 'nt' and cwd.startswith('/') else cwd"
exec g:Lf_py "sys.path.insert(0, os.path.join(cwd, 'leaderf', 'python'))"

function! s:InitVar(var, value)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:value)
    endif
endfunction

function! s:InitDict(var, dict)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:dict)
    else
        let tmp = a:dict
        for [key, value] in items(eval(a:var))
            let tmp[key] = value
        endfor
        exec 'let '.a:var.'='.string(tmp)
    endif
endfunction

call s:InitVar('g:Lf_WindowHeight', '0.5')
call s:InitVar('g:Lf_TabpagePosition', 2)
call s:InitVar('g:Lf_ShowRelativePath', 1)
call s:InitVar('g:Lf_DefaultMode', 'FullPath')
call s:InitVar('g:Lf_CursorBlink', 1)
call s:InitVar('g:Lf_NeedCacheTime', '1.5')
call s:InitVar('g:Lf_NumberOfCache', 5)
call s:InitVar('g:Lf_UseMemoryCache', 1)
call s:InitVar('g:Lf_IndexTimeLimit', 120)
call s:InitVar('g:Lf_FollowLinks', 0)
call s:InitVar('g:Lf_DelimiterChar', ';')
call s:InitVar('g:Lf_MruFileExclude', [])
call s:InitVar('g:Lf_MruMaxFiles', 100)
call s:InitVar('g:Lf_HighlightIndividual', 1)
call s:InitVar('g:Lf_NumberOfHighlight', 100)
call s:InitVar('g:Lf_WildIgnore', {
            \ 'dir': [],
            \ 'file': []
            \})
call s:InitVar('g:Lf_MruWildIgnore', {
            \ 'dir': [],
            \ 'file': []
            \})
call s:InitVar('g:Lf_HistoryExclude', {
            \ 'cmd': [],
            \ 'search': []
            \})
if &encoding ==? "utf-8"
    call s:InitVar('g:Lf_StlSeparator', {
                \ 'left': '►',
                \ 'right': '◄',
                \ 'font': ''
                \})
else
    call s:InitVar('g:Lf_StlSeparator', {
                \ 'left': '',
                \ 'right': '',
                \ 'font': ''
                \})
endif
call s:InitVar('g:Lf_StlPalette', {})
call s:InitVar('g:Lf_Ctags', 'ctags')
call s:InitVar('g:Lf_PreviewCode', 0)
call s:InitVar('g:Lf_UseVersionControlTool', 1)
call s:InitVar('g:Lf_RememberLastSearch', 0)
call s:InitVar('g:Lf_UseCache', 1)
call s:InitVar('g:Lf_RootMarkers', ['.git', '.hg', '.svn'])
call s:InitVar('g:Lf_WorkingDirectoryMode', 'c')
call s:InitVar('g:Lf_WorkingDirectory', '')
call s:InitVar('g:Lf_ShowHidden', 0)
call s:InitDict('g:Lf_PreviewResult', {
            \ 'File': 0,
            \ 'Buffer': 0,
            \ 'Mru': 0,
            \ 'Tag': 0,
            \ 'BufTag': 1,
            \ 'Function': 1,
            \ 'Line': 0,
            \ 'Colorscheme': 0
            \})
call s:InitDict('g:Lf_NormalMap', {})
call s:InitVar('g:Lf_Extensions', {})
call s:InitDict('g:Lf_CtagsFuncOpts', {})
call s:InitVar('g:Lf_MaxCount', 2000000)
call s:InitDict('g:Lf_GtagsfilesCmd', {
            \ '.git': 'git ls-files --recurse-submodules',
            \ '.hg': 'hg files',
            \ 'default': 'rg --no-messages --files'
            \})
call s:InitVar('g:Lf_HistoryEditPromptIfEmpty', 1)

let s:Lf_CommandMap = {
            \ '<C-A>':         ['<C-A>'],
            \ '<C-B>':         ['<C-B>'],
            \ '<C-C>':         ['<C-C>'],
            \ '<C-D>':         ['<C-D>'],
            \ '<C-E>':         ['<C-E>'],
            \ '<C-F>':         ['<C-F>'],
            \ '<C-G>':         ['<C-G>'],
            \ '<C-H>':         ['<C-H>'],
            \ '<C-J>':         ['<C-J>'],
            \ '<C-K>':         ['<C-K>'],
            \ '<C-L>':         ['<C-L>'],
            \ '<C-N>':         ['<C-N>'],
            \ '<C-O>':         ['<C-O>'],
            \ '<C-P>':         ['<C-P>'],
            \ '<C-Q>':         ['<C-Q>'],
            \ '<C-R>':         ['<C-R>'],
            \ '<C-S>':         ['<C-S>'],
            \ '<C-T>':         ['<C-T>'],
            \ '<C-U>':         ['<C-U>'],
            \ '<C-V>':         ['<C-V>'],
            \ '<C-W>':         ['<C-W>'],
            \ '<C-X>':         ['<C-X>'],
            \ '<C-Y>':         ['<C-Y>'],
            \ '<C-Z>':         ['<C-Z>'],
            \ '<C-]>':         ['<C-]>'],
            \ '<F1>':          ['<F1>'],
            \ '<F2>':          ['<F2>'],
            \ '<F3>':          ['<F3>'],
            \ '<F4>':          ['<F4>'],
            \ '<F5>':          ['<F5>'],
            \ '<F6>':          ['<F6>'],
            \ '<F7>':          ['<F7>'],
            \ '<F8>':          ['<F8>'],
            \ '<F9>':          ['<F9>'],
            \ '<F10>':         ['<F10>'],
            \ '<F11>':         ['<F11>'],
            \ '<F12>':         ['<F12>'],
            \ '<CR>':          ['<CR>', '<C-M>'],
            \ '<BS>':          ['<BS>'],
            \ '<Tab>':         ['<Tab>', '<C-I>'],
            \ '<Del>':         ['<Del>'],
            \ '<Esc>':         ['<Esc>'],
            \ '<Up>':          ['<Up>'],
            \ '<Down>':        ['<Down>'],
            \ '<Left>':        ['<Left>'],
            \ '<Right>':       ['<Right>'],
            \ '<Home>':        ['<Home>'],
            \ '<End>':         ['<End>'],
            \ '<PageUp>':      ['<PageUp>'],
            \ '<PageDown>':    ['<PageDown>'],
            \ '<C-Up>':        ['<C-Up>'],
            \ '<C-Down>':      ['<C-Down>'],
            \ '<C-Left>':      ['<C-Left>'],
            \ '<C-Right>':     ['<C-Right>'],
            \ '<C-Home>':      ['<C-Home>'],
            \ '<C-End>':       ['<C-End>'],
            \ '<C-PageUp>':    ['<C-PageUp>'],
            \ '<C-PageDown>':  ['<C-PageDown>'],
            \ '<S-Up>':        ['<S-Up>'],
            \ '<S-Down>':      ['<S-Down>'],
            \ '<S-Left>':      ['<S-Left>'],
            \ '<S-Right>':     ['<S-Right>'],
            \ '<S-Home>':      ['<S-Home>'],
            \ '<S-End>':       ['<S-End>'],
            \ '<S-PageUp>':    ['<S-PageUp>'],
            \ '<S-PageDown>':  ['<S-PageDown>'],
            \ '<S-Insert>':    ['<S-Insert>'],
            \ '<LeftMouse>':   ['<LeftMouse>'],
            \ '<RightMouse>':  ['<RightMouse>'],
            \ '<MiddleMouse>': ['<MiddleMouse>'],
            \ '<2-LeftMouse>': ['<2-LeftMouse>'],
            \ '<C-LeftMouse>': ['<C-LeftMouse>'],
            \ '<S-LeftMouse>': ['<S-LeftMouse>'],
            \ '<ScrollWheelUp>': ['<ScrollWheelUp>'],
            \ '<ScrollWheelDown>': ['<ScrollWheelDown>'],
            \}

let g:Lf_KeyMap = {
            \ "\<C-A>":         '<C-A>',
            \ "\<C-B>":         '<C-B>',
            \ "\<C-C>":         '<C-C>',
            \ "\<C-D>":         '<C-D>',
            \ "\<C-E>":         '<C-E>',
            \ "\<C-F>":         '<C-F>',
            \ "\<C-G>":         '<C-G>',
            \ "\<C-H>":         '<C-H>',
            \ "\<C-J>":         '<C-J>',
            \ "\<C-K>":         '<C-K>',
            \ "\<C-L>":         '<C-L>',
            \ "\<C-N>":         '<C-N>',
            \ "\<C-O>":         '<C-O>',
            \ "\<C-P>":         '<C-P>',
            \ "\<C-Q>":         '<C-Q>',
            \ "\<C-R>":         '<C-R>',
            \ "\<C-S>":         '<C-S>',
            \ "\<C-T>":         '<C-T>',
            \ "\<C-U>":         '<C-U>',
            \ "\<C-V>":         '<C-V>',
            \ "\<C-W>":         '<C-W>',
            \ "\<C-X>":         '<C-X>',
            \ "\<C-Y>":         '<C-Y>',
            \ "\<C-Z>":         '<C-Z>',
            \ "\<C-]>":         '<C-]>',
            \ "\<F1>":          '<F1>',
            \ "\<F2>":          '<F2>',
            \ "\<F3>":          '<F3>',
            \ "\<F4>":          '<F4>',
            \ "\<F5>":          '<F5>',
            \ "\<F6>":          '<F6>',
            \ "\<F7>":          '<F7>',
            \ "\<F8>":          '<F8>',
            \ "\<F9>":          '<F9>',
            \ "\<F10>":         '<F10>',
            \ "\<F11>":         '<F11>',
            \ "\<F12>":         '<F12>',
            \ "\<CR>":          '<CR>',
            \ "\<BS>":          '<BS>',
            \ "\<TAB>":         '<TAB>',
            \ "\<DEL>":         '<DEL>',
            \ "\<ESC>":         '<ESC>',
            \ "\<UP>":          '<UP>',
            \ "\<DOWN>":        '<DOWN>',
            \ "\<LEFT>":        '<LEFT>',
            \ "\<RIGHT>":       '<RIGHT>',
            \ "\<HOME>":        '<HOME>',
            \ "\<END>":         '<END>',
            \ "\<PAGEUP>":      '<PAGEUP>',
            \ "\<PAGEDOWN>":    '<PAGEDOWN>',
            \ "\<C-UP>":        '<C-UP>',
            \ "\<C-DOWN>":      '<C-DOWN>',
            \ "\<C-LEFT>":      '<C-LEFT>',
            \ "\<C-RIGHT>":     '<C-RIGHT>',
            \ "\<C-HOME>":      '<C-HOME>',
            \ "\<C-END>":       '<C-END>',
            \ "\<C-PAGEUP>":    '<C-PAGEUP>',
            \ "\<C-PAGEDOWN>":  '<C-PAGEDOWN>',
            \ "\<S-UP>":        '<S-UP>',
            \ "\<S-DOWN>":      '<S-DOWN>',
            \ "\<S-LEFT>":      '<S-LEFT>',
            \ "\<S-RIGHT>":     '<S-RIGHT>',
            \ "\<S-HOME>":      '<S-HOME>',
            \ "\<S-END>":       '<S-END>',
            \ "\<S-PAGEUP>":    '<S-PAGEUP>',
            \ "\<S-PAGEDOWN>":  '<S-PAGEDOWN>',
            \ "\<S-INSERT>":    '<S-INSERT>',
            \ "\<LEFTMOUSE>":   '<LEFTMOUSE>',
            \ "\<RIGHTMOUSE>":  '<RIGHTMOUSE>',
            \ "\<MIDDLEMOUSE>": '<MIDDLEMOUSE>',
            \ "\<2-LEFTMOUSE>": '<2-LEFTMOUSE>',
            \ "\<C-LEFTMOUSE>": '<C-LEFTMOUSE>',
            \ "\<S-LEFTMOUSE>": '<S-LEFTMOUSE>',
            \ "\<SCROLLWHEELUP>": '<SCROLLWHEELUP>',
            \ "\<SCROLLWHEELDOWN>": '<SCROLLWHEELDOWN>'
            \}

let g:Lf_DevIconsPallete = {
            \ '_':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'default':      { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'erl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            \ 'styl':         { 'guifg': '#1572b6', 'ctermfg': '25'   },
            \ 'rmd':          { 'guifg': '#755838', 'ctermfg': '94'   },
            \ 'c++':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'pyc':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \ 'pyd':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \ 'go':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \ 'suo':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            \ 'lua':          { 'guifg': '#3e6dbf', 'ctermfg': '25'   },
            \ 'bash':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'pyo':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \ 'mustache':     { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'gif':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'fs':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            \ 'leex':         { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \ 'lhs':          { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \ 'csh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'scala':        { 'guifg': '#7ce1ff', 'ctermfg': '117'  },
            \ 'zsh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'jpeg':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'ts':           { 'guifg': '#007acc', 'ctermfg': '32'   },
            \ 'xcplayground': { 'guifg': '#f88535', 'ctermfg': '208'  },
            \ 'fsi':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            \ 'vim':          { 'guifg': '#007F00', 'ctermfg': '28'   },
            \ 'scss':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            \ 'js':           { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \ 'hbs':          { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'xul':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \ 'mdx':          { 'guifg': '#755838', 'ctermfg': '94'   },
            \ 'fish':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'java':         { 'guifg': '#5382a1', 'ctermfg': '67'   },
            \ 'htm':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \ 'rb':           { 'guifg': '#871101', 'ctermfg': '88'   },
            \ 'f#':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            \ 'c':            { 'guifg': '#005f91', 'ctermfg': '24'   },
            \ 'd':            { 'guifg': '#b03931', 'ctermfg': '124'  },
            \ 'md':           { 'guifg': '#755838', 'ctermfg': '94'   },
            \ 'h':            { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'mli':          { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            \ 'ml':           { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            \ 'css':          { 'guifg': '#1572b6', 'ctermfg': '25'   },
            \ 'hh':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'php':          { 'guifg': '#6280b6', 'ctermfg': '67'   },
            \ 'cc':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'swift':        { 'guifg': '#f88535', 'ctermfg': '208'  },
            \ 't':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'jl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \ 'cljc':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            \ 'exs':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \ 'ksh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'hs':           { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \ 'sql':          { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \ 'cp':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'ps1':          { 'guifg': '#af4343', 'ctermfg': '124'  },
            \ 'cs':           { 'guifg': '#368832', 'ctermfg': '28'   },
            \ 'bmp':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'sln':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            \ 'cljs':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            \ 'html':         { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \ 'cpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'hrl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            \ 'rs':           { 'guifg': '#817871', 'ctermfg': '101'  },
            \ 'sass':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            \ 'vue':          { 'guifg': '#41b883', 'ctermfg': '36'   },
            \ 'awk':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'conf':         { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \ 'pl':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \ 'pm':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \ 'rlib':         { 'guifg': '#817871', 'ctermfg': '101'  },
            \ 'pp':           { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \ 'dart':         { 'guifg': '#66c3fa', 'ctermfg': '81'   },
            \ 'elm':          { 'guifg': '#5fb4cb', 'ctermfg': '74'   },
            \ 'jpg':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'toml':         { 'guifg': '#7e7f7f', 'ctermfg': '243'  },
            \ 'py':           { 'guifg': '#366994', 'ctermfg': '24'   },
            \ 'mjs':          { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \ 'less':         { 'guifg': '#2a4f84', 'ctermfg': '24'   },
            \ 'ai':           { 'guifg': '#F37021', 'ctermfg': '202'  },
            \ 'jsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            \ 'webp':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'psd':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            \ 'psb':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            \ 'json':         { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \ 'rss':          { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \ 'cxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'png':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'sh':           { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \ 'hpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'bat':          { 'guifg': '#bedcdc', 'ctermfg': '152'  },
            \ 'fsx':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            \ 'ini':          { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \ 'markdown':     { 'guifg': '#755838', 'ctermfg': '94'   },
            \ 'db':           { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \ 'twig':         { 'guifg': '#63bf6a', 'ctermfg': '71'   },
            \ 'yaml':         { 'guifg': '#ffe885', 'ctermfg': '222'  },
            \ 'coffee':       { 'guifg': '#6f4e37', 'ctermfg': '58'   },
            \ 'ejs':          { 'guifg': '#90a93a', 'ctermfg': '106'  },
            \ 'clj':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \ 'ex':           { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \ 'edn':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \ 'slim':         { 'guifg': '#719E40', 'ctermfg': '70'   },
            \ 'eex':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \ 'tsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            \ 'dump':         { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \ 'hxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \ 'diff':         { 'guifg': '#dd4c35', 'ctermfg': '166'  },
            \ 'ico':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \ 'fsscript':     { 'guifg': '#378bba', 'ctermfg': '31'   },
            \ 'yml':          { 'guifg': '#ffe885', 'ctermfg': '222'  },
            \}

function! s:InitCommandMap(var, dict)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:dict)
    else
        let tmp = a:dict
        for [key, value] in items(eval(a:var))
            call filter(tmp, 'v:key !=? key')
            for i in value
                if index(['<TAB>', '<C-I>'], toupper(i)) >= 0
                    call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? ''<TAB>'' && v:val !=? ''<C-I>''"))')
                elseif index(['<CR>', '<C-M>'], toupper(i)) >= 0
                    call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? ''<CR>'' && v:val !=? ''<C-M>''"))')
                else
                    call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? i"))')
                endif
            endfor
            let tmp[toupper(key)] = map(value, 'toupper(v:val)')
        endfor
        exec 'let '.a:var.'='.string(tmp)
    endif
    let g:Lf_KeyDict = {}
    for [key, val] in items(eval(a:var))
        for i in val
            let g:Lf_KeyDict[toupper(i)] = toupper(key)
        endfor
    endfor
endfunction

call s:InitCommandMap('g:Lf_CommandMap', s:Lf_CommandMap)

function! leaderf#versionCheck()
    if g:Lf_PythonVersion == 2 && pyeval("sys.version_info < (2, 7)")
        echohl Error
        echo "Error: LeaderF requires python2.7+, your current version is " . pyeval("sys.version")
        echohl None
        return 0
    elseif g:Lf_PythonVersion == 3 && py3eval("sys.version_info < (3, 1)")
        echohl Error
        echo "Error: LeaderF requires python3.1+, your current version is " . py3eval("sys.version")
        echohl None
        return 0
    elseif g:Lf_PythonVersion != 2 && g:Lf_PythonVersion != 3
        echohl Error
        echo "Error: Invalid value of `g:Lf_PythonVersion`, value must be 2 or 3."
        echohl None
        return 0
    endif
    return 1
endfunction

function! leaderf#LfPy(cmd) abort
    exec g:Lf_py . a:cmd
endfunction

" return the visually selected text and quote it with double quote
function! leaderf#visual() abort
    try
        let x_save = @x
        norm! gv"xy
        return '"' . escape(@x, '"') . '"'
    finally
        let @x = x_save
    endtry
endfunction

function! leaderf#popupModePreviewFilter(winid, key) abort
    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)
    if key ==? "<ESC>"
        call popup_close(a:winid)
        redraw
        return 1
    elseif key ==? "<CR>"
        call popup_close(a:winid)
        " https://github.com/vim/vim/issues/5216
        "redraw
        return 0
    elseif key ==? "<LeftMouse>" && has('patch-8.1.2266')
        " v:mouse_winid is always 0 in popup window(fixed in vim 8.1.2292)
        " the below workaround can make v:mouse_winid have the value
        if v:mouse_winid == 0
            silent! call feedkeys("\<LeftMouse>", "n")
            silent! call getchar()
        endif

        "echom v:mouse_winid v:mouse_lnum v:mouse_col v:mouse_win
        " in normal window, v:mouse_lnum and v:mouse_col are always 0 after getchar()
        if v:mouse_winid == a:winid
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            redraw
            return 1
        else
            call popup_close(a:winid)
            call win_execute(v:mouse_winid, "exec v:mouse_lnum")
            call win_execute(v:mouse_winid, "exec 'norm!'.v:mouse_col.'|'")
            redraw
            return 1
        endif
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        redraw
        return 1
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        redraw
        return 1
    endif
    return 0
endfunction

function! leaderf#normalModePreviewFilter(winid, key) abort
    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)
    if key ==? "<ESC>"
        call popup_close(a:winid)
        redraw
        return 1
    elseif key ==? "<CR>"
        call popup_close(a:winid)
        " https://github.com/vim/vim/issues/5216
        "redraw
        return 0
    elseif key ==? "<LeftMouse>" && has('patch-8.1.2266')
        return 0
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        redraw
        return 1
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        redraw
        return 1
    elseif key ==? "<C-Up>"
        call win_execute(a:winid, "norm! k")
        redraw
        return 1
    elseif key ==? "<C-Down>"
        call win_execute(a:winid, "norm! j")
        redraw
        return 1
    endif
    return 0
endfunction

function! leaderf#PopupFilter(winid, key) abort
    return 0
endfunction

function! leaderf#NormalModeFilter(id, winid, key) abort
    exec g:Lf_py "import ctypes"

    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)

    if key !=# "g"
        call win_execute(a:winid, printf("let g:Lf_%d_is_g_pressed = 0", a:id))
    endif

    if key ==# "j" || key ==? "<Down>"
        call win_execute(a:winid, "norm! j")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        "redraw
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
    elseif key ==# "k" || key ==? "<Up>"
        call win_execute(a:winid, "norm! k")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        "redraw
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
    elseif key ==? "<PageUp>" || key ==? "<C-B>"
        call win_execute(a:winid, "norm! \<PageUp>")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
    elseif key ==? "<PageDown>" || key ==? "<C-F>"
        call win_execute(a:winid, "norm! \<PageDown>")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
    elseif key ==# "g"
        if get(g:, printf("Lf_%d_is_g_pressed", a:id), 0) == 0
            let g:Lf_{a:id}_is_g_pressed = 1
        else
            let g:Lf_{a:id}_is_g_pressed = 0
            call win_execute(a:winid, "norm! gg")
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
            redraw
        endif
    elseif key ==# "G"
        call win_execute(a:winid, "norm! G")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        redraw
    elseif key ==? "<C-U>"
        call win_execute(a:winid, "norm! \<C-U>")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        redraw
    elseif key ==? "<C-D>"
        call win_execute(a:winid, "norm! \<C-D>")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        redraw
    elseif key ==? "<LeftMouse>"
        if has('patch-8.1.2266')
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
            redraw
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
        endif
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        redraw
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        redraw
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
    elseif key ==# "q" || key ==? "<ESC>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.quit()", a:id)
    elseif key ==# "i" || key ==? "<Tab>"
        call leaderf#ResetPopupOptions(a:winid, 'filter', 'leaderf#PopupFilter')
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.input()", a:id)
    elseif key ==# "o" || key ==? "<CR>" || key ==? "<2-LeftMouse>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.accept()", a:id)
    elseif key ==# "x"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.accept('h')", a:id)
    elseif key ==# "v"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.accept('v')", a:id)
    elseif key ==# "t"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.accept('t')", a:id)
    elseif key ==# "s"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.addSelections()", a:id)
    elseif key ==# "a"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.selectAll()", a:id)
    elseif key ==# "c"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.clearSelections()", a:id)
    elseif key ==# "p"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(True)", a:id)
    elseif key ==? "<F1>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.toggleHelp()", a:id)
    elseif key ==? "<C-Up>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._toUpInPopup()", a:id)
    elseif key ==? "<C-Down>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._toDownInPopup()", a:id)
    endif

    return 1
endfunction

function! leaderf#PopupClosed(id_list, manager_id, winid, result) abort
    " result is -1 if CTRL-C was pressed,
    if a:result == -1
        exec g:Lf_py "import ctypes"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.quit()", a:manager_id)
        for id in a:id_list
            if id != a:winid
                call popup_close(id)
            endif
        endfor
    endif
endfunction

function! leaderf#ResetPopupOptions(winid, option, value) abort
    let opts = popup_getoptions(a:winid)
    " https://github.com/vim/vim/issues/5081
    silent! unlet opts.mousemoved
    silent! unlet opts.moved
    let opts[a:option] = a:value
    call popup_setoptions(a:winid, opts)
endfunction

function! leaderf#ResetFloatwinOptions(winid, option, value) abort
    let opts = nvim_win_get_config(a:winid)
    let opts[a:option] = a:value
    call nvim_win_set_config(a:winid, opts)
endfunction

" `pos` - A list with three numbers, e.g., [23, 11, 3]. As above, but
" the third number gives the length of the highlight in bytes.
function! leaderf#matchaddpos(group, pos) abort
    for pos in a:pos
        call prop_add(pos[0], pos[1], {'length': pos[2], 'type': a:group})
    endfor
endfunction

function! leaderf#closeAllFloatwin(input_win_id, content_win_id, statusline_win_id, show_statusline) abort
    if winbufnr(a:input_win_id) == -1
        silent! call nvim_win_close(a:content_win_id, 0)
        if a:show_statusline
            silent! call nvim_win_close(a:statusline_win_id, 0)
        endif
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    elseif winbufnr(a:content_win_id) == -1
        silent! call nvim_win_close(a:input_win_id, 0)
        if a:show_statusline
            silent! call nvim_win_close(a:statusline_win_id, 0)
        endif
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    elseif a:show_statusline && winbufnr(a:statusline_win_id) == -1
        silent! call nvim_win_close(a:input_win_id, 0)
        silent! call nvim_win_close(a:content_win_id, 0)
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    endif
endfunction

autocmd FileType leaderf let b:coc_enabled = 0 | let b:coc_suggest_disable = 1


" for devicons
autocmd OptionSet ambiwidth call leaderf#setAmbiwidth(v:option_new)

function! leaderf#setAmbiwidth(val) abort
    exec g:Lf_py "from leaderf.devicons import setAmbiwidth"
    exec g:Lf_py printf("setAmbiwidth('%s')", a:val)
endfunction

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

let g:Lf_DevIconsPalette = {
            \   'light': {
            \       '_':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'default':      { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       '.gvimrc':      { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       '.vimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       '_gvimrc':      { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       '_vimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       'ai':           { 'guifg': '#F37021', 'ctermfg': '202'  },
            \       'awk':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'bash':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'bat':          { 'guifg': '#7ab8b8', 'ctermfg': '109'  },
            \       'bmp':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'c':            { 'guifg': '#005f91', 'ctermfg': '24'   },
            \       'c++':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'cc':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'chs':          { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \       'cl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'clj':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'cljc':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'cljs':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'cljx':         { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'coffee':       { 'guifg': '#6f4e37', 'ctermfg': '58'   },
            \       'conf':         { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \       'cp':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'cpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'cs':           { 'guifg': '#368832', 'ctermfg': '28'   },
            \       'csh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'css':          { 'guifg': '#1572b6', 'ctermfg': '25'   },
            \       'cxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'd':            { 'guifg': '#b03931', 'ctermfg': '124'  },
            \       'dart':         { 'guifg': '#66c3fa', 'ctermfg': '81'   },
            \       'db':           { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            \       'diff':         { 'guifg': '#dd4c35', 'ctermfg': '166'  },
            \       'dump':         { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            \       'edn':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'eex':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \       'ejs':          { 'guifg': '#90a93a', 'ctermfg': '106'  },
            \       'el':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'elm':          { 'guifg': '#5fb4cb', 'ctermfg': '74'   },
            \       'erl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            \       'es':           { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'ex':           { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \       'exs':          { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \       'f#':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            \       'fish':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'fs':           { 'guifg': '#378bba', 'ctermfg': '31'   },
            \       'fsi':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            \       'fsscript':     { 'guifg': '#378bba', 'ctermfg': '31'   },
            \       'fsx':          { 'guifg': '#378bba', 'ctermfg': '31'   },
            \       'gif':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'go':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'gvimrc':       { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       'h':            { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'hbs':          { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'hh':           { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'hpp':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'hrl':          { 'guifg': '#a2003e', 'ctermfg': '124'  },
            \       'hs':           { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \       'hs-boot':      { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \       'htm':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'html':         { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'hxx':          { 'guifg': '#984c93', 'ctermfg': '96'   },
            \       'ico':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'ini':          { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \       'java':         { 'guifg': '#5382a1', 'ctermfg': '67'   },
            \       'javascript':   { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'jl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'jpeg':         { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'jpg':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'js':           { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'json':         { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'jsx':          { 'guifg': '#00a6ff', 'ctermfg': '39'   },
            \       'ksh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'leex':         { 'guifg': '#6f567e', 'ctermfg': '60'   },
            \       'less':         { 'guifg': '#2a4f84', 'ctermfg': '24'   },
            \       'lhs':          { 'guifg': '#8f4e8b', 'ctermfg': '96'   },
            \       'lua':          { 'guifg': '#3e6dbf', 'ctermfg': '25'   },
            \       'markdown':     { 'guifg': '#755838', 'ctermfg': '94'   },
            \       'md':           { 'guifg': '#755838', 'ctermfg': '94'   },
            \       'mdx':          { 'guifg': '#755838', 'ctermfg': '94'   },
            \       'mjs':          { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'ml':           { 'guifg': '#a1a1a1', 'ctermfg': '246'  },
            \       'mli':          { 'guifg': '#a1a1a1', 'ctermfg': '246'  },
            \       'mustache':     { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'php':          { 'guifg': '#6280b6', 'ctermfg': '67'   },
            \       'pl':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'pm':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'png':          { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'pp':           { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'ps1':          { 'guifg': '#af4343', 'ctermfg': '124'  },
            \       'psb':          { 'guifg': '#00ade6', 'ctermfg': '38'   },
            \       'psd':          { 'guifg': '#00ade6', 'ctermfg': '38'   },
            \       'py':           { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'pyc':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'pyd':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'pyi':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'pyo':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'pyw':          { 'guifg': '#366994', 'ctermfg': '24'   },
            \       'rb':           { 'guifg': '#871101', 'ctermfg': '88'   },
            \       'rbw':          { 'guifg': '#871101', 'ctermfg': '88'   },
            \       'rlib':         { 'guifg': '#817871', 'ctermfg': '101'  },
            \       'rmd':          { 'guifg': '#755838', 'ctermfg': '94'   },
            \       'rs':           { 'guifg': '#817871', 'ctermfg': '101'  },
            \       'rss':          { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'sass':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            \       'scala':        { 'guifg': '#33bbff', 'ctermfg': '39'   },
            \       'scss':         { 'guifg': '#cd6799', 'ctermfg': '168'  },
            \       'sh':           { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'slim':         { 'guifg': '#719E40', 'ctermfg': '70'   },
            \       'sln':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            \       'sql':          { 'guifg': '#8b93a2', 'ctermfg': '103'  },
            \       'styl':         { 'guifg': '#1572b6', 'ctermfg': '25'   },
            \       'suo':          { 'guifg': '#00519a', 'ctermfg': '24'   },
            \       'swift':        { 'guifg': '#f88535', 'ctermfg': '208'  },
            \       't':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'toml':         { 'guifg': '#7e7f7f', 'ctermfg': '243'  },
            \       'ts':           { 'guifg': '#007acc', 'ctermfg': '32'   },
            \       'tsx':          { 'guifg': '#00a6ff', 'ctermfg': '39'   },
            \       'twig':         { 'guifg': '#63bf6a', 'ctermfg': '71'   },
            \       'vim':          { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       'vimrc':        { 'guifg': '#007F00', 'ctermfg': '28'   },
            \       'vue':          { 'guifg': '#41b883', 'ctermfg': '36'   },
            \       'webp':         { 'guifg': '#28b48f', 'ctermfg': '36'   },
            \       'xcplayground': { 'guifg': '#f88535', 'ctermfg': '208'  },
            \       'xul':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'yaml':         { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'yml':          { 'guifg': '#d7a723', 'ctermfg': '178'  },
            \       'zsh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \   },
            \   'dark': {
            \       '_':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'default':      { 'guifg': '#d8e698', 'ctermfg': '186' },
            \       '.gvimrc':      { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       '.vimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       '_gvimrc':      { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       '_vimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       'ai':           { 'guifg': '#F37021', 'ctermfg': '202'  },
            \       'awk':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'bash':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'bat':          { 'guifg': '#bedcdc', 'ctermfg': '152'  },
            \       'bmp':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'c':            { 'guifg': '#44cef6', 'ctermfg': '81'   },
            \       'c++':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'cc':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'chs':          { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            \       'cl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'clj':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'cljc':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            \       'cljs':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            \       'cljx':         { 'guifg': '#9cd775', 'ctermfg': '150'  },
            \       'coffee':       { 'guifg': '#bc9372', 'ctermfg': '137'  },
            \       'conf':         { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \       'cp':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'cpp':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'cs':           { 'guifg': '#57c153', 'ctermfg': '71'   },
            \       'csh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'css':          { 'guifg': '#3199e9', 'ctermfg': '32'   },
            \       'cxx':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'd':            { 'guifg': '#b03931', 'ctermfg': '124'  },
            \       'dart':         { 'guifg': '#66c3fa', 'ctermfg': '81'   },
            \       'db':           { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \       'diff':         { 'guifg': '#dd4c35', 'ctermfg': '166'  },
            \       'dump':         { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \       'edn':          { 'guifg': '#63b132', 'ctermfg': '70'   },
            \       'eex':          { 'guifg': '#957aa5', 'ctermfg': '103'  },
            \       'ejs':          { 'guifg': '#bed27b', 'ctermfg': '150'  },
            \       'el':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'elm':          { 'guifg': '#5fb4cb', 'ctermfg': '74'   },
            \       'erl':          { 'guifg': '#eb0057', 'ctermfg': '197'  },
            \       'es':           { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \       'ex':           { 'guifg': '#957aa5', 'ctermfg': '103'  },
            \       'exs':          { 'guifg': '#957aa5', 'ctermfg': '103'  },
            \       'f#':           { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            \       'fish':         { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'fs':           { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            \       'fsi':          { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            \       'fsscript':     { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            \       'fsx':          { 'guifg': '#71b1d6', 'ctermfg': '74'   },
            \       'gif':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'go':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'gvimrc':       { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       'h':            { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'hbs':          { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'hh':           { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'hpp':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'hrl':          { 'guifg': '#eb0057', 'ctermfg': '197'  },
            \       'hs':           { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            \       'hs-boot':      { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            \       'htm':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'html':         { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'hxx':          { 'guifg': '#87d37c', 'ctermfg': '114'  },
            \       'ico':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'ini':          { 'guifg': '#99b8c4', 'ctermfg': '110'  },
            \       'java':         { 'guifg': '#abc3ee', 'ctermfg': '153'  },
            \       'javascript':   { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \       'jl':           { 'guifg': '#aa79c1', 'ctermfg': '139'  },
            \       'jpeg':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'jpg':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'js':           { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \       'json':         { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \       'jsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            \       'ksh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'leex':         { 'guifg': '#957aa5', 'ctermfg': '103'  },
            \       'less':         { 'guifg': '#779dd6', 'ctermfg': '110'  },
            \       'lhs':          { 'guifg': '#b87bb4', 'ctermfg': '139'  },
            \       'lua':          { 'guifg': '#658ace', 'ctermfg': '68'   },
            \       'markdown':     { 'guifg': '#b48d60', 'ctermfg': '137'  },
            \       'md':           { 'guifg': '#b48d60', 'ctermfg': '137'  },
            \       'mdx':          { 'guifg': '#b48d60', 'ctermfg': '137'  },
            \       'mjs':          { 'guifg': '#f5de19', 'ctermfg': '220'  },
            \       'ml':           { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            \       'mli':          { 'guifg': '#cfcfcf', 'ctermfg': '251'  },
            \       'mustache':     { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'php':          { 'guifg': '#859cc7', 'ctermfg': '110'  },
            \       'pl':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'pm':           { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'png':          { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'pp':           { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'ps1':          { 'guifg': '#af4343', 'ctermfg': '124'  },
            \       'psb':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            \       'psd':          { 'guifg': '#26C9FF', 'ctermfg': '45'   },
            \       'py':           { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'pyc':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'pyd':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'pyi':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'pyo':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'pyw':          { 'guifg': '#5790c3', 'ctermfg': '68'   },
            \       'rb':           { 'guifg': '#e52002', 'ctermfg': '160'  },
            \       'rbw':          { 'guifg': '#e52002', 'ctermfg': '160'  },
            \       'rlib':         { 'guifg': '#bbb5b0', 'ctermfg': '145'  },
            \       'rmd':          { 'guifg': '#b48d60', 'ctermfg': '137'  },
            \       'rs':           { 'guifg': '#bbb5b0', 'ctermfg': '145'  },
            \       'rss':          { 'guifg': '#00acd7', 'ctermfg': '38'   },
            \       'sass':         { 'guifg': '#d287da', 'ctermfg': '176'  },
            \       'scala':        { 'guifg': '#7ce1ff', 'ctermfg': '117'  },
            \       'scss':         { 'guifg': '#d287da', 'ctermfg': '176'  },
            \       'sh':           { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \       'slim':         { 'guifg': '#a0c875', 'ctermfg': '150'  },
            \       'sln':          { 'guifg': '#0078cc', 'ctermfg': '32'   },
            \       'sql':          { 'guifg': '#c4c7ce', 'ctermfg': '188'  },
            \       'styl':         { 'guifg': '#3199e9', 'ctermfg': '32'   },
            \       'suo':          { 'guifg': '#0078cc', 'ctermfg': '32'   },
            \       'swift':        { 'guifg': '#f88535', 'ctermfg': '208'  },
            \       't':            { 'guifg': 'NONE',    'ctermfg': 'NONE' },
            \       'toml':         { 'guifg': '#9b9898', 'ctermfg': '138'  },
            \       'ts':           { 'guifg': '#33aaff', 'ctermfg': '39'   },
            \       'tsx':          { 'guifg': '#00d8ff', 'ctermfg': '45'   },
            \       'twig':         { 'guifg': '#63bf6a', 'ctermfg': '71'   },
            \       'vim':          { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       'vimrc':        { 'guifg': '#00cc00', 'ctermfg': '40'   },
            \       'vue':          { 'guifg': '#41b883', 'ctermfg': '36'   },
            \       'webp':         { 'guifg': '#2dcc9f', 'ctermfg': '43'   },
            \       'xcplayground': { 'guifg': '#f88535', 'ctermfg': '208'  },
            \       'xul':          { 'guifg': '#f1662a', 'ctermfg': '202'  },
            \       'yaml':         { 'guifg': '#ffe885', 'ctermfg': '222'  },
            \       'yml':          { 'guifg': '#ffe885', 'ctermfg': '222'  },
            \       'zsh':          { 'guifg': '#d9b400', 'ctermfg': '178'  },
            \   }
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

function! leaderf#highlightDevIcons() abort
    exec g:Lf_py 'from leaderf.devicons import highlightDevIcons'
    exec g:Lf_py 'highlightDevIcons()'
endfunction

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
call s:InitDict('g:Lf_MaxCount', 2000000)

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
            \ '<S-Left>':      ['<S-Left>'],
            \ '<S-Right>':     ['<S-Right>'],
            \ '<S-Insert>':    ['<S-Insert>'],
            \ '<LeftMouse>':   ['<LeftMouse>'],
            \ '<RightMouse>':  ['<RightMouse>'],
            \ '<MiddleMouse>': ['<MiddleMouse>'],
            \ '<2-LeftMouse>': ['<2-LeftMouse>'],
            \ '<C-LeftMouse>': ['<C-LeftMouse>'],
            \ '<S-LeftMouse>': ['<S-LeftMouse>'],
            \ '<ScrollWheelUp>': ['<ScrollWheelUp>'],
            \ '<ScrollWheelDown>': ['<ScrollWheelDown>']
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
        echo "Error: LeaderF requires python3.1+, your current version is " . pyeval("sys.version")
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

function! leaderf#LfPy(cmd)
    exec g:Lf_py . a:cmd
endfunction


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
        let g:Lf_PyEval = function("py3eval")
    elseif has("python")
        let g:Lf_PythonVersion = 2
        let g:Lf_py = "py "
        let g:Lf_PyEval = function("pyeval")
    else
        echoe "Error: LeaderF requires vim compiled with +python or +python3"
        finish
    endif
else
    if g:Lf_PythonVersion == 2
        if has("python")
            let g:Lf_py = "py "
            let g:Lf_PyEval = function("pyeval")
        else
            echoe 'LeaderF Error: has("python") == 0'
            finish
        endif
    else
        if has("python3")
            let g:Lf_py = "py3 "
            let g:Lf_PyEval = function("py3eval")
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
call s:InitVar('g:Lf_TabpagePosition', 3)
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
            \ 'File': 1,
            \ 'Buffer': 1,
            \ 'Mru': 1,
            \ 'Tag': 1,
            \ 'BufTag': 1,
            \ 'Function': 1,
            \ 'Line': 1,
            \ 'Colorscheme': 0,
            \ 'Rg': 1,
            \ 'Jumps': 1
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
call s:InitVar('g:Lf_PopupBorders', ["─","│","─","│","╭","╮","╯","╰"])
call s:InitVar('g:Lf_GitFolderIcons', {
            \ 'open': '',
            \ 'closed': '',
            \})

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
            \ '<C-\>':         ['<C-\>'],
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
            \ "\<C-\>":         '<C-\>',
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

function! leaderf#execute(cmd)
    if exists('*execute')
        return execute(a:cmd)
    else
        redir => l:output
        silent! execute a:cmd
        redir END
        return l:output
    endif
endfunction

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
        let x_save = getreg("x", 1)
        let type = getregtype("x")
        norm! gv"xy
        return '"' . escape(@x, '"') . '"'
    finally
        call setreg("x", x_save, type)
    endtry
endfunction

function! leaderf#popupModePreviewFilter(winid, key) abort
    let key = get(g:Lf_KeyMap, a:key, a:key)
    if key ==? "<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            if pos.winid == a:winid
                call win_execute(pos.winid, "call cursor([pos.line, pos.column])")
                redraw
                return 1
            endif
        elseif has('patch-8.1.2266')
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
                noautocmd call popup_close(a:winid)
                call win_execute(v:mouse_winid, "exec v:mouse_lnum")
                call win_execute(v:mouse_winid, "exec 'norm!'.v:mouse_col.'|'")
                redraw
                return 1
            endif
        endif
    elseif key ==? "<ScrollWheelUp>" && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == a:winid
            call win_execute(a:winid, "norm! 3\<C-Y>")
            redraw
            return 1
        endif
    elseif key ==? "<ScrollWheelDown>" && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == a:winid
            call win_execute(a:winid, "norm! 3\<C-E>")
            redraw
            return 1
        endif
    endif
    return 0
endfunction

function! leaderf#PopupFilter(winid, key) abort
    return 0
endfunction

function! leaderf#RemapKey(id, key) abort
    exec g:Lf_py "import ctypes"

    let normal_map = get(g:, 'Lf_NormalCommandMap', {})
    let key_map = get(normal_map, '*', {})
    let category = g:Lf_PyEval(printf("ctypes.cast(%d, ctypes.py_object).value._getExplorer().getStlCategory()", a:id))
    for [old, new] in items(get(normal_map, category, {}))
        let has_key = 0
        for [k, v] in items(key_map)
            if old =~ '\m<.\{-}>' && old ==? k
                let key_map[k] = new
                let has_key = 1
                break
            endif
        endfor
        if has_key == 0
            let key_map[old] = new
        endif
    endfor

    let key = a:key
    let is_old = 0
    let is_new = 0
    for [old, new] in items(key_map)
        if key =~ '\m<.\{-}>' && key ==? new || key ==# new
            let key = old
            let is_new = 1
        endif
        if key =~ '\m<.\{-}>' && key ==? old || key ==# old
            let is_old = 1
        endif
    endfor

    if is_old && is_new == 0
        let key = ''
    endif

    return key
endfunction

function! leaderf#NormalModeFilter(id, winid, key) abort
    exec g:Lf_py "import ctypes"

    let key = leaderf#RemapKey(a:id, get(g:Lf_KeyMap, a:key, a:key))

    if key !=# "g"
        call win_execute(a:winid, printf("let g:Lf_%d_is_g_pressed = 0", a:id))
    endif

    if key ==# "j" || key ==? "<Down>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.move('j')", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
        "redraw
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
    elseif key ==# "k" || key ==? "<Up>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.move('k')", a:id)
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
        if exists("*getmousepos")
            let pos = getmousepos()
            if pos.winid == a:winid
                call win_execute(pos.winid, "call cursor([pos.line, pos.column])")
                exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
                exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
                redraw
                return 1
            else
                return 0
            endif
        elseif has('patch-8.1.2266')
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
            redraw
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
        endif
    elseif key ==? "<ScrollWheelUp>" && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == a:winid
            call win_execute(a:winid, "norm! 3\<C-Y>")
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
            redraw
            return 1
        else
            return 0
        endif
    elseif key ==? "<ScrollWheelDown>" && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == a:winid
            call win_execute(a:winid, "norm! 3\<C-E>")
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._cli._buildPopupPrompt()", a:id)
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._getInstance().refreshPopupStatusline()", a:id)
            exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(False)", a:id)
            redraw
            return 1
        else
            return 0
        endif
    elseif key ==# "q"
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
    elseif key ==# "p"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._previewResult(True)", a:id)
    elseif key ==? "<F1>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.toggleHelp()", a:id)
    elseif key ==? "<C-Up>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._toUpInPopup()", a:id)
    elseif key ==? "<C-Down>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._toDownInPopup()", a:id)
    elseif key ==? "<ESC>"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.closePreviewPopupOrQuit()", a:id)
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
                noautocmd call popup_close(id)
            endif
        endfor
    endif
endfunction

function! leaderf#Quit(manager_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.quit()", a:manager_id)
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

function! leaderf#closeAllFloatwin(input_win_id, content_win_id, statusline_win_id, show_statusline, id) abort
    if winbufnr(a:input_win_id) == -1
        silent! call nvim_win_close(g:Lf_PreviewWindowID[a:id], 0)
        silent! call nvim_win_close(a:content_win_id, 0)
        if a:show_statusline
            silent! call nvim_win_close(a:statusline_win_id, 0)
        endif
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    elseif winbufnr(a:content_win_id) == -1
        silent! call nvim_win_close(g:Lf_PreviewWindowID[a:id], 0)
        silent! call nvim_win_close(a:input_win_id, 0)
        if a:show_statusline
            silent! call nvim_win_close(a:statusline_win_id, 0)
        endif
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    elseif a:show_statusline && winbufnr(a:statusline_win_id) == -1
        silent! call nvim_win_close(g:Lf_PreviewWindowID[a:id], 0)
        silent! call nvim_win_close(a:input_win_id, 0)
        silent! call nvim_win_close(a:content_win_id, 0)
        augroup Lf_Floatwin_Close
            autocmd!
        augroup end
    endif
endfunction

autocmd FileType leaderf let b:coc_enabled = 0 | let b:coc_suggest_disable = 1


if exists("##OptionSet")
    " for devicons
    autocmd OptionSet ambiwidth call leaderf#setAmbiwidth(v:option_new)
endif

function! leaderf#setAmbiwidth(val) abort
    exec g:Lf_py "from leaderf.devicons import setAmbiwidth"
    exec g:Lf_py printf("setAmbiwidth('%s')", a:val)
endfunction

function! leaderf#highlightDevIcons() abort
    exec g:Lf_py 'from leaderf.devicons import highlightDevIcons'
    exec g:Lf_py 'highlightDevIcons()'
endfunction

" ============================================================================
" File:        Rg.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.rgExpl import *"

function! leaderf#Rg#Maps(heading)
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "rgExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "rgExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "rgExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "rgExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "rgExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "rgExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "rgExplManager.quit()"<CR>
    if a:heading == 0
        nnoremap <buffer> <silent> i             :exec g:Lf_py "rgExplManager.input()"<CR>
        nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "rgExplManager.input()"<CR>
    endif
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "rgExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "rgExplManager.deleteCurrentLine()"<CR>
    nnoremap <buffer> <silent> Q             :exec g:Lf_py "rgExplManager.outputToQflist()"<CR>
    nnoremap <buffer> <silent> L             :exec g:Lf_py "rgExplManager.outputToLoclist()"<CR>
    nnoremap <buffer> <silent> r             :exec g:Lf_py "rgExplManager.replace()"<CR>
    nnoremap <buffer> <silent> w             :call leaderf#Rg#ApplyChangesAndSave(0)<CR>
    nnoremap <buffer> <silent> W             :call leaderf#Rg#ApplyChangesAndSave(1)<CR>
    nnoremap <buffer> <silent> U             :call leaderf#Rg#UndoLastChange()<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py "rgExplManager._toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py "rgExplManager._toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py "rgExplManager._closePreviewPopup()"<CR>
    endif
    if has_key(g:Lf_NormalMap, "Rg")
        for i in g:Lf_NormalMap["Rg"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

" return the visually selected text and quote it with double quote
function! leaderf#Rg#visual()
    try
        let x_save = getreg("x", 1)
        let type = getregtype("x")
        norm! gv"xy
        return '"' . escape(@x, '"') . '"'
    finally
        call setreg("x", x_save, type)
    endtry
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Rg#getPattern(type)
    if a:type == 0
        return expand('<cword>')
    elseif a:type == 1
        return escape(expand('<cWORD>'))
    elseif a:type == 2
        return leaderf#Rg#visual()
    else
        return ''
    endif
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Rg#startCmdline(type, is_bang, is_regex, is_whole_word)
    return printf("Leaderf%s rg %s%s-e %s ", a:is_bang ? '!' : '', a:is_regex ? '' : '-F ',
                \ a:is_whole_word ? '-w ' : '', leaderf#Rg#getPattern(a:type))
endfunction

function! leaderf#Rg#Interactive()
    try
        echohl Question
        let pattern = input("Search pattern: ")
        let pattern = escape(pattern,'"')
        let glob = input("Search in files(e.g., *.c, *.cpp): ", "*")
        if glob =~ '^\s*$'
            return
        endif
        let globList = map(split(glob, '[ ,]\+'), 'v:val =~ ''^".*"$'' ? v:val : ''"''.v:val.''"''')
        exec printf("Leaderf rg %s\"%s\" -g %s", pattern =~ '^\s*$' ? '' : '-e ', pattern, join(globList, ' -g '))
    finally
        echohl None
    endtry
endfunction

function! leaderf#Rg#TimerCallback(id)
    call leaderf#LfPy("rgExplManager._workInIdle(bang=True)")
endfunction

function! leaderf#Rg#ApplyChanges()
    call leaderf#LfPy("rgExplManager.applyChanges()")
endfunction

function! leaderf#Rg#UndoLastChange()
    call leaderf#LfPy("rgExplManager.undo()")
endfunction

function! leaderf#Rg#Quit()
    call leaderf#LfPy("rgExplManager.quit()")
endfunction

function! leaderf#Rg#ApplyChangesAndSave(save)
    if ! &modified
        return
    endif
    try
        if a:save
            let g:Lf_rg_apply_changes_and_save = 1
        endif
        write
    finally
        silent! unlet g:Lf_rg_apply_changes_and_save
    endtry
endfunction

function! leaderf#Rg#Undo(buf_number_dict)
    if has_key(a:buf_number_dict, bufnr('%'))
        undo
    endif
endfunction

let s:type_list = []
function! s:rg_type_list() abort
    if len(s:type_list) > 0
        return s:type_list
    endif

    let l:ret = {}
    let l:output = systemlist('rg --type-list')

    for l:line in l:output
        " e,g,. 'c: *.[chH], *.[chH].in, *.cats'
        let [l:type, l:pattern_str] = split(l:line, ': ')
        let l:pattern_list = split(l:pattern_str, ', ')

        let l:ret[l:type] = map(l:pattern_list, 'glob2regpat(v:val)')
    endfor

    let s:type_list = l:ret
    return s:type_list
endfunction

function! s:getType(fname) abort
    for [l:type, l:pattern_list] in items(s:rg_type_list())
        for l:pattern in l:pattern_list
            if a:fname =~# l:pattern
                return l:type
            endif
        endfor
    endfor
    return ''
endfunction

" Returns the type of rg matching the filename.
" e,g,: nnoremap <Leader>fg :<C-u><C-r>=printf('Leaderf rg %s ', leaderf#Rg#getTypeByFileName(expand('%')))<CR>
function! leaderf#Rg#getTypeByFileName(fname) abort
    let l:type = s:getType(a:fname)
    return empty(l:type) ? '' : printf('-t "%s"', l:type)
endfunction


function! leaderf#Rg#NormalModeFilter(winid, key) abort
    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)

    if key !=# "g"
        call win_execute(a:winid, "let g:Lf_Rg_is_g_pressed = 0")
    endif

    if key ==# "j" || key ==? "<Down>"
        call win_execute(a:winid, "norm! j")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "rgExplManager._previewResult(False)"
    elseif key ==# "k" || key ==? "<Up>"
        call win_execute(a:winid, "norm! k")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "rgExplManager._previewResult(False)"
    elseif key ==? "<PageUp>" || key ==? "<C-B>"
        call win_execute(a:winid, "norm! \<PageUp>")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "rgExplManager._previewResult(False)"
    elseif key ==? "<PageDown>" || key ==? "<C-F>"
        call win_execute(a:winid, "norm! \<PageDown>")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "rgExplManager._previewResult(False)"
    elseif key ==# "g"
        if get(g:, "Lf_Rg_is_g_pressed", 0) == 0
            let g:Lf_Rg_is_g_pressed = 1
        else
            let g:Lf_Rg_is_g_pressed = 0
            call win_execute(a:winid, "norm! gg")
            exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
            redraw
        endif
    elseif key ==# "G"
        call win_execute(a:winid, "norm! G")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-U>"
        call win_execute(a:winid, "norm! \<C-U>")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-D>"
        call win_execute(a:winid, "norm! \<C-D>")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            call win_execute(pos.winid, "call cursor([pos.line, pos.column])")
            exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "rgExplManager._previewResult(False)"
        elseif has('patch-8.1.2266')
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "rgExplManager._previewResult(False)"
        endif
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        exec g:Lf_py "rgExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "rgExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==# "q" || key ==? "<ESC>"
        exec g:Lf_py "rgExplManager.quit()"
    elseif key ==# "i" || key ==? "<Tab>"
        if g:Lf_py == "py "
            let has_heading = pyeval("'--heading' in rgExplManager._arguments")
        else
            let has_heading = py3eval("'--heading' in rgExplManager._arguments")
        endif
        if !has_heading
            call leaderf#ResetPopupOptions(a:winid, 'filter', 'leaderf#PopupFilter')
            exec g:Lf_py "rgExplManager.input()"
        endif
    elseif key ==# "o" || key ==? "<CR>" || key ==? "<2-LeftMouse>"
        exec g:Lf_py "rgExplManager.accept()"
    elseif key ==# "x"
        exec g:Lf_py "rgExplManager.accept('h')"
    elseif key ==# "v"
        exec g:Lf_py "rgExplManager.accept('v')"
    elseif key ==# "t"
        exec g:Lf_py "rgExplManager.accept('t')"
    elseif key ==# "p"
        exec g:Lf_py "rgExplManager._previewResult(True)"
    elseif key ==? "<F1>"
        exec g:Lf_py "rgExplManager.toggleHelp()"
    elseif key ==# "d"
        exec g:Lf_py "rgExplManager.deleteCurrentLine()"
    elseif key ==# "Q"
        exec g:Lf_py "rgExplManager.outputToQflist()"
    elseif key ==# "L"
        exec g:Lf_py "rgExplManager.outputToLoclist()"
    elseif key ==? "<C-Up>"
        exec g:Lf_py "rgExplManager._toUpInPopup()"
    elseif key ==? "<C-Down>"
        exec g:Lf_py "rgExplManager._toDownInPopup()"
    endif

    return 1
endfunction

" ============================================================================
" File:        Git.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.gitExpl import *"

function! leaderf#Git#Maps(heading)
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "gitExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "gitExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "gitExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "gitExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "gitExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "gitExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "gitExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :exec g:Lf_py "gitExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :exec g:Lf_py "gitExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :exec g:Lf_py "gitExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :exec g:Lf_py "gitExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :exec g:Lf_py "gitExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :exec g:Lf_py "gitExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "gitExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gitExplManager.quit()"<CR>
    if a:heading == 0
        nnoremap <buffer> <silent> i             :exec g:Lf_py "gitExplManager.input()"<CR>
        nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "gitExplManager.input()"<CR>
    endif
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "gitExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "gitExplManager.deleteCurrentLine()"<CR>
    nnoremap <buffer> <silent> Q             :exec g:Lf_py "gitExplManager.outputToQflist()"<CR>
    nnoremap <buffer> <silent> L             :exec g:Lf_py "gitExplManager.outputToLoclist()"<CR>
    nnoremap <buffer> <silent> r             :exec g:Lf_py "gitExplManager.replace()"<CR>
    nnoremap <buffer> <silent> w             :call leaderf#Git#ApplyChangesAndSave(0)<CR>
    nnoremap <buffer> <silent> W             :call leaderf#Git#ApplyChangesAndSave(1)<CR>
    nnoremap <buffer> <silent> U             :call leaderf#Git#UndoLastChange()<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "gitExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "gitExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gitExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "Git")
        for i in g:Lf_NormalMap["Git"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

" return the visually selected text and quote it with double quote
function! leaderf#Git#visual()
    try
        let x_save = getreg("x", 1)
        let type = getregtype("x")
        norm! gv"xy
        return '"' . escape(@x, '\"') . '"'
    finally
        call setreg("x", x_save, type)
    endtry
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Git#getPattern(type)
    if a:type == 0
        return expand('<cword>')
    elseif a:type == 1
        return '"' . escape(expand('<cWORD>'), '"') . '"'
    elseif a:type == 2
        return leaderf#Git#visual()
    else
        return ''
    endif
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Git#startCmdline(type, is_bang, is_regex, is_whole_word)
    return printf("Leaderf%s git %s%s-e %s ", a:is_bang ? '!' : '', a:is_regex ? '' : '-F ',
                \ a:is_whole_word ? '-w ' : '', leaderf#Git#getPattern(a:type))
endfunction

function! leaderf#Git#TimerCallback(view_id, id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.writeBuffer()", a:view_id)
endfunction

function! leaderf#Git#Cleanup(view_id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.cleanup()", a:view_id)
endfunction

function! leaderf#Git#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(gitExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "i" || key ==? "<Tab>"
        if g:Lf_py == "py "
            let has_heading = pyeval("'--heading' in gitExplManager._agituments")
        else
            let has_heading = py3eval("'--heading' in gitExplManager._agituments")
        endif
        if !has_heading
            call leaderf#ResetPopupOptions(a:winid, 'filter', 'leaderf#PopupFilter')
            exec g:Lf_py "gitExplManager.input()"
        endif
    elseif key ==# "d"
        exec g:Lf_py "gitExplManager.deleteCurrentLine()"
    elseif key ==# "Q"
        exec g:Lf_py "gitExplManager.outputToQflist()"
    elseif key ==# "L"
        exec g:Lf_py "gitExplManager.outputToLoclist()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(gitExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

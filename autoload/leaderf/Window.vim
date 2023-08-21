" ============================================================================
" File:        Window.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.windowExpl import *"

function! leaderf#Window#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "windowExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "windowExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "windowExplManager.accept()"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "windowExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "windowExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "windowExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "windowExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "windowExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "windowExplManager.deleteWindow()"<CR>
    if has_key(g:Lf_NormalMap, "Window")
        for i in g:Lf_NormalMap["Window"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Window#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(windowExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "x"
    elseif key ==# "v"
    elseif key ==# "t"
    elseif key ==# "p"
    elseif key ==? "<C-Up>"
    elseif key ==? "<C-Down>"
    elseif key ==# "d"
        exec g:Lf_py "windowExplManager.deleteWindow()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(windowExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction


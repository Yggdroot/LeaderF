" ============================================================================
" File:        History.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.historyExpl import *"

function! leaderf#History#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "historyExplManager.accept()"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "historyExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "historyExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <C-I>         :exec g:Lf_py "historyExplManager.input()"<CR>
    nnoremap <buffer> <silent> e             :exec g:Lf_py "historyExplManager.editHistory()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "historyExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "History")
        for i in g:Lf_NormalMap["History"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#History#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(historyExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "x"
    elseif key ==# "v"
    elseif key ==# "t"
    elseif key ==# "p"
    elseif key ==? "<C-Up>"
    elseif key ==? "<C-Down>"
    elseif key ==# "e"
        exec g:Lf_py "historyExplManager.editHistory()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(historyExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

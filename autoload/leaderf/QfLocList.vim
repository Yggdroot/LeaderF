" ============================================================================
" File:        QfLocList.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.qfloclistExpl import *"

function! leaderf#QfLocList#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "qfloclistExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "qfloclistExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "qfloclistExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "qfloclistExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "qfloclistExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "qfloclistExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "qfloclistExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "qfloclistExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "qfloclistExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "qfloclistExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "qfloclistExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "qfloclistExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "qfloclistExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "qfloclistExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "QfLocList")
        for i in g:Lf_NormalMap["QfLocList"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction


function! leaderf#QfLocList#NormalModeFilter(winid, key) abort
    return leaderf#NormalModeFilter(g:Lf_PyEval("id(qfloclistExplManager)"), a:winid, a:key)
endfunction

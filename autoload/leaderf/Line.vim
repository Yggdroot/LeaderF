" ============================================================================
" File:        Line.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.lineExpl import *"

function! leaderf#Line#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "lineExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "lineExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "lineExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "lineExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "lineExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "lineExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "lineExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "lineExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "lineExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "lineExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> Q             :exec g:Lf_py "lineExplManager.outputToQflist()"<CR>
    nnoremap <buffer> <silent> L             :exec g:Lf_py "lineExplManager.outputToLoclist()"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "lineExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "lineExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "lineExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "Line")
        for i in g:Lf_NormalMap["Line"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Line#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(lineExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==? "<F5>"
        exec g:Lf_py "lineExplManager.refresh()"
    elseif key ==# "Q"
        exec g:Lf_py "lineExplManager.outputToQflist()"
    elseif key ==# "L"
        exec g:Lf_py "lineExplManager.outputToLoclist()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(lineExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

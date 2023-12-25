" ============================================================================
" File:        Buffer.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.bufExpl import *"

function! leaderf#Buffer#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "bufExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "bufExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "bufExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "bufExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "bufExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "bufExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "bufExplManager.deleteBuffer(1)"<CR>
    nnoremap <buffer> <silent> D             :exec g:Lf_py "bufExplManager.deleteBuffer()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "bufExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "bufExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "bufExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "bufExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "bufExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "Buffer")
        for i in g:Lf_NormalMap["Buffer"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Buffer#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(bufExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "d"
        exec g:Lf_py "bufExplManager.deleteBuffer(1)"
    elseif key ==# "D"
        exec g:Lf_py "bufExplManager.deleteBuffer()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(bufExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

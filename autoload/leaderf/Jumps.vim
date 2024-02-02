" ============================================================================
" File:        Jumps.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.jumpsExpl import *"

function! leaderf#Jumps#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "jumpsExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "jumpsExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "jumpsExplManager.accept()"<CR>
    "nnoremap <buffer> <silent> x             :exec g:Lf_py "jumpsExplManager.accept('h')"<CR>
    "nnoremap <buffer> <silent> v             :exec g:Lf_py "jumpsExplManager.accept('v')"<CR>
    "nnoremap <buffer> <silent> t             :exec g:Lf_py "jumpsExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "jumpsExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "jumpsExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "jumpsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "jumpsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "jumpsExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "jumpsExplManager.refresh()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "jumpsExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "jumpsExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "jumpsExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "jumpsExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "jumpsExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "Jumps")
        for i in g:Lf_NormalMap["Jumps"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

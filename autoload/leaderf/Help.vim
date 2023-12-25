" ============================================================================
" File:        Help.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0
    finish
endif

exec g:Lf_py "from leaderf.helpExpl import *"

function! leaderf#Help#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "helpExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "helpExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "helpExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "helpExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "helpExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "helpExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "helpExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "helpExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "helpExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "helpExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "helpExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "helpExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "helpExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "Help")
        for i in g:Lf_NormalMap["Help"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

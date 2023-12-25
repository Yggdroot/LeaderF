" ============================================================================
" File:        Colors.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0
    finish
endif

exec g:Lf_py "from leaderf.colorschemeExpl import *"

function! leaderf#Colors#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "colorschemeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "colorschemeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "colorschemeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "colorschemeExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "colorschemeExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "colorschemeExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "colorschemeExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "colorschemeExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "colorschemeExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "colorschemeExplManager.moveAndPreview('PageDown')"<CR>
    if has_key(g:Lf_NormalMap, "Colorscheme")
        for i in g:Lf_NormalMap["Colorscheme"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

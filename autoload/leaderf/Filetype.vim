" ============================================================================
" File:        Filetype.vim
" Description:
" Author:      tamago324 <tamago_pad@yahoo.co.jp>
" Website:     https://github.com/tamago324
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0
    finish
endif

exec g:Lf_py "from leaderf.filetypeExpl import *"

function! leaderf#Filetype#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "filetypeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "filetypeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "filetypeExplManager.accept()"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "filetypeExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "filetypeExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "filetypeExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "Filetype")
        for i in g:Lf_NormalMap["Filetype"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

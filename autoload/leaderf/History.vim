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
    nnoremap <buffer> <silent> <ESC>         :exec g:Lf_py "historyExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <C-I>         :exec g:Lf_py "historyExplManager.input()"<CR>
endfunction

function! leaderf#History#startExpl(win_pos, type)
    call leaderf#LfPy("historyExplManager.startExplorer('".a:win_pos."', '".a:type."')")
endfunction

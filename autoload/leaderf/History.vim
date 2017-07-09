" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.historyExpl import *"

function! leaderf#History#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "historyExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "historyExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "historyExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "historyExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "historyExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "historyExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "historyExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "historyExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "historyExplManager.toggleHelp()"<CR>
endfunction

function! leaderf#History#startExpl(win_pos, type)
    call leaderf#LfPy("historyExplManager.startExplorer('".a:win_pos."', '".a:type."')")
endfunction

" ============================================================================
" File:        Line.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
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
    nnoremap <buffer> <silent> i             :exec g:Lf_py "lineExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "lineExplManager.toggleHelp()"<CR>
endfunction

function! leaderf#Line#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("lineExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("lineExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

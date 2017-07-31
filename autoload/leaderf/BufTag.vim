" ============================================================================
" File:        BufTag.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

let g:Lf_bufTagExpl_loaded = 1

exec g:Lf_py "from leaderf.bufTagExpl import *"

function! leaderf#BufTag#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "bufTagExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "bufTagExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "bufTagExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "bufTagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <ESC>         :exec g:Lf_py "bufTagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufTagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufTagExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <LeftMouse>   <LeftMouse>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
endfunction

function! leaderf#BufTag#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("bufTagExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("bufTagExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

function! leaderf#BufTag#removeCache(bufNum)
    call leaderf#LfPy("bufTagExplManager.removeCache(".a:bufNum.")")
endfunction

function! leaderf#BufTag#cleanup()
    call leaderf#LfPy("bufTagExplManager._beforeExit()")
endfunction

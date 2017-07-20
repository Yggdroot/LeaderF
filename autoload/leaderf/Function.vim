" ============================================================================
" File:        Function.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

let g:Lf_functionExpl_loaded = 1

exec g:Lf_py "from leaderf.functionExpl import *"

function! leaderf#Function#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "functionExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "functionExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "functionExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "functionExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "functionExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "functionExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <LeftMouse>   <LeftMouse>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
endfunction

function! leaderf#Function#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("functionExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("functionExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

function! leaderf#Function#removeCache(bufNum)
    call leaderf#LfPy("functionExplManager.removeCache(".a:bufNum.")")
endfunction

function! leaderf#Function#cleanup()
    call leaderf#LfPy("functionExplManager._beforeExit()")
endfunction

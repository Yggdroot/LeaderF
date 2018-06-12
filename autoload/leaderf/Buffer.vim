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
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "bufExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "bufExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "bufExplManager.deleteBuffer(1)"<CR>
    nnoremap <buffer> <silent> D             :exec g:Lf_py "bufExplManager.deleteBuffer()"<CR>
    if has_key(g:Lf_NormalMap, "Buffer")
        for i in g:Lf_NormalMap["Buffer"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Buffer#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."')")
    elseif a:1 == 1
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."', arguments={'--all': []})")
    elseif a:1 == 2
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."', arguments={'--tabpage': []})")
    else
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."', arguments={'--tabpage': [], '--all': []})")
    endif
endfunction

function! leaderf#Buffer#startExplPattern(win_pos, pattern)
    call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."', pattern='".a:pattern."')")
endfunction

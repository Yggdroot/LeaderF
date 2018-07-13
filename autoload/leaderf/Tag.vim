" ============================================================================
" File:        Tag.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.tagExpl import *"

function! leaderf#Tag#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "tagExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "tagExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "tagExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "tagExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "tagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "tagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "tagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "tagExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "tagExplManager.refresh()"<CR>
    if has_key(g:Lf_NormalMap, "Tag")
        for i in g:Lf_NormalMap["Tag"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Tag#startExpl(win_pos, ...)
    call leaderf#LfPy("tagExplManager.startExplorer('".a:win_pos."')")
endfunction

function! leaderf#Tag#startExplPattern(win_pos, pattern)
    call leaderf#LfPy("tagExplManager.startExplorer('".a:win_pos."', pattern='".a:pattern."')")
endfunction

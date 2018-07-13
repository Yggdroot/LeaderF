" ============================================================================
" File:        File.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.fileExpl import *"

function! leaderf#File#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "fileExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "fileExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "fileExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "fileExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "fileExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "fileExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "fileExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "fileExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "fileExplManager.refresh()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "fileExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "fileExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "fileExplManager.clearSelections()"<CR>
    if has_key(g:Lf_NormalMap, "File")
        for i in g:Lf_NormalMap["File"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#File#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("fileExplManager.startExplorer('".a:win_pos."')")
    else
        let dir = fnamemodify(a:1.'/',":h:gs?\\?/?")
        call leaderf#LfPy("fileExplManager.startExplorer('".a:win_pos."', arguments={'directory': ['".dir."']})")
    endif
endfunction

function! leaderf#File#startExplPattern(win_pos, pattern)
    call leaderf#LfPy("fileExplManager.startExplorer('".a:win_pos."', pattern='".a:pattern."')")
endfunction

function! leaderf#File#cleanup()
    call leaderf#LfPy("fileExplManager._beforeExit()")
endfunction

" ============================================================================
" File:        Mru.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.mruExpl import *"

function! leaderf#Mru#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "mruExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "mruExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "mruExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "mruExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "mruExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "mruExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "mruExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "mruExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "mruExplManager.deleteMru()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "mruExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "mruExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "mruExplManager.clearSelections()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "mruExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <LeftMouse>   <LeftMouse>:exec g:Lf_py "mruExplManager._previewResult(False)"<CR>
    if has_key(g:Lf_NormalMap, "Mru")
        for i in g:Lf_NormalMap["Mru"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Mru#startExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."cb_name=vim.current.buffer.name)")
    else
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."cb_name=vim.current.buffer.name, arguments={'--cwd': []})")
    endif
endfunction

function! leaderf#Mru#startExplPattern(win_pos, cwd, pattern)
    if a:cwd == 0
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."cb_name=vim.current.buffer.name, pattern='".a:pattern."')")
    else
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."cb_name=vim.current.buffer.name, arguments={'--cwd': []}, pattern='".a:pattern."')")
    endif
endfunction

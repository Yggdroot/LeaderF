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
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "bufTagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufTagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "bufTagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufTagExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "bufTagExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "bufTagExplManager._previewResult(False)"<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py "bufTagExplManager._toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py "bufTagExplManager._toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py "bufTagExplManager._closePreviewPopup()"<CR>
    endif
    if has_key(g:Lf_NormalMap, "BufTag")
        for i in g:Lf_NormalMap["BufTag"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#BufTag#removeCache(bufNum)
    call leaderf#LfPy("bufTagExplManager.removeCache(".a:bufNum.")")
endfunction

function! leaderf#BufTag#cleanup()
    call leaderf#LfPy("bufTagExplManager._beforeExit()")
endfunction

function! leaderf#BufTag#TimerCallback(id)
    call leaderf#LfPy("bufTagExplManager._callback(bang=True)")
endfunction

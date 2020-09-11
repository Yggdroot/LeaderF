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
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "functionExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "functionExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "functionExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "functionExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "functionExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "functionExplManager._previewResult(False)"<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py "functionExplManager._toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py "functionExplManager._toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py "functionExplManager._closePreviewPopup()"<CR>
    endif
    if has_key(g:Lf_NormalMap, "Function")
        for i in g:Lf_NormalMap["Function"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Function#removeCache(bufNum)
    call leaderf#LfPy("functionExplManager.removeCache(".a:bufNum.")")
endfunction

function! leaderf#Function#cleanup()
    call leaderf#LfPy("functionExplManager._beforeExit()")
endfunction

function! leaderf#Function#TimerCallback(id)
    call leaderf#LfPy("functionExplManager._callback(bang=True)")
endfunction

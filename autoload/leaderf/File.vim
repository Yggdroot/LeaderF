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
    nnoremap <buffer> <silent> p             :exec g:Lf_py "fileExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "fileExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "fileExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "fileExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "fileExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "File")
        for i in g:Lf_NormalMap["File"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#File#cleanup()
    call leaderf#LfPy("fileExplManager._beforeExit()")
endfunction

function! leaderf#File#TimerCallback(id)
    call leaderf#LfPy("fileExplManager._workInIdle(bang=True)")
endfunction

function! leaderf#File#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(fileExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==? "<F5>"
        exec g:Lf_py "fileExplManager.refresh()"
    elseif key ==# "s"
        exec g:Lf_py "fileExplManager.addSelections()"
    elseif key ==# "a"
        exec g:Lf_py "fileExplManager.selectAll()"
    elseif key ==# "c"
        exec g:Lf_py "fileExplManager.clearSelections()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(fileExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

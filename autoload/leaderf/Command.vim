" ============================================================================
" File:        Command.vim
" Description:
" Author:      tamago324 <tamago_pad@yahoo.co.jp>
" Website:     https://github.com/tamago324
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0
    finish
endif

exec g:Lf_py "from leaderf.commandExpl import *"

function! leaderf#Command#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "commandExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "commandExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "commandExplManager.accept()"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "commandExplManager.quit()"<CR>
    nnoremap <buffer> <silent> <C-I>         :exec g:Lf_pI "commandExplManager.input()"<CR>
    nnoremap <buffer> <silent> e             :exec g:Lf_py "commandExplManager.editCommand()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "commandExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "Command")
        for i in g:Lf_NormalMap["Command"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Command#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(commandExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "x"
    elseif key ==# "v"
    elseif key ==# "t"
    elseif key ==# "p"
    elseif key ==? "<C-Up>"
    elseif key ==? "<C-Down>"
    elseif key ==# "e"
        exec g:Lf_py "commandExplManager.editCommand()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(commandExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

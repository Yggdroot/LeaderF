" ============================================================================
" File:        Cmd_History.vim
" Description:
" Author:      tamago324 <tamago_pad@yahoo.co.jp>
" Website:     https://github.com/tamago324
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

function! leaderf#Cmd_History#NormalModeFilter(winid, key) abort
    return leaderf#History#NormalModeFilter(a:winid, a:key)
endfunction

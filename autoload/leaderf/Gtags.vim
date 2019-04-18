" ============================================================================
" File:        Gtags.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.gtagsExpl import *"
exec g:Lf_py "from leaderf.utils import *"

function! leaderf#Gtags#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "gtagsExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "gtagsExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "gtagsExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "gtagsExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "gtagsExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "gtagsExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> p             :exec g:Lf_py "gtagsExplManager._previewResult(True)"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "gtagsExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "gtagsExplManager.deleteCurrentLine()"<CR>
    if has_key(g:Lf_NormalMap, "Gtags")
        for i in g:Lf_NormalMap["Gtags"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

function! leaderf#Gtags#startExpl(win_pos, ...)
exec g:Lf_py "<< EOF"
gtagsExplManager.startExplorer(vim.eval("a:win_pos"))
EOF
endfunction

function! leaderf#Gtags#updateGtags(filename, single_update)
exec g:Lf_py "<< EOF"
gtagsExplManager.updateGtags(lfDecode(vim.eval("a:filename")), True if int(vim.eval("a:single_update")) else False)
EOF
endfunction

function! leaderf#Gtags#TimerCallback(id)
exec g:Lf_py "<< EOF"
gtagsExplManager._workInIdle(bang=True)
EOF
endfunction

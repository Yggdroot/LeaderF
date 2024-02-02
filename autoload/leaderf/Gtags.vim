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
    nnoremap <buffer> <silent> j             :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('j')"<CR>
    nnoremap <buffer> <silent> k             :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('k')"<CR>
    nnoremap <buffer> <silent> <Up>          :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('Up')"<CR>
    nnoremap <buffer> <silent> <Down>        :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('Down')"<CR>
    nnoremap <buffer> <silent> <PageUp>      :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('PageUp')"<CR>
    nnoremap <buffer> <silent> <PageDown>    :<C-U>exec g:Lf_py "gtagsExplManager.moveAndPreview('PageDown')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "gtagsExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "gtagsExplManager.deleteCurrentLine()"<CR>
    nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "gtagsExplManager._toUpInPopup()"<CR>
    nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "gtagsExplManager._toDownInPopup()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gtagsExplManager.closePreviewPopupOrQuit()"<CR>
    if has_key(g:Lf_NormalMap, "Gtags")
        for i in g:Lf_NormalMap["Gtags"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

" return the visually selected text and quote it with double quote
function! leaderf#Gtags#visual()
    try
        let x_save = getreg("x", 1)
        let type = getregtype("x")
        norm! gv"xy
        return '"' . escape(@x, '"') . '"'
    finally
        call setreg("x", x_save, type)
    endtry
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Gtags#getPattern(type)
    if a:type == 0
        return expand('<cword>')
    elseif a:type == 1
        return '"' . escape(expand('<cWORD>'), '"') . '"'
    elseif a:type == 2
        return leaderf#Gtags#visual()
    else
        return ''
    endif
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, text visually selected
function! leaderf#Gtags#startCmdline(type, is_bang, param)
    return printf("Leaderf%s gtags -%s %s --literal --auto-jump", a:is_bang ? '!' : '',
                \ a:param, leaderf#Gtags#getPattern(a:type))
endfunction

function! leaderf#Gtags#cleanup()
exec g:Lf_py "<< EOF"
gtagsExplManager._beforeExit()
EOF
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

function! leaderf#Gtags#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(gtagsExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "d"
        exec g:Lf_py "gtagsExplManager.deleteCurrentLine()"
    elseif key ==# "s"
        exec g:Lf_py "gtagsExplManager.addSelections()"
    elseif key ==# "a"
        exec g:Lf_py "gtagsExplManager.selectAll()"
    elseif key ==# "c"
        exec g:Lf_py "gtagsExplManager.clearSelections()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(gtagsExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

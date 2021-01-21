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
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "gtagsExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "gtagsExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "gtagsExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "gtagsExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "gtagsExplManager.deleteCurrentLine()"<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py "gtagsExplManager._toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py "gtagsExplManager._toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py "gtagsExplManager._closePreviewPopup()"<CR>
    endif
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
        return escape(expand('<cWORD>'))
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
    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)

    if key !=# "g"
        call win_execute(a:winid, "let g:Lf_Gtags_is_g_pressed = 0")
    endif

    if key ==# "j" || key ==? "<Down>"
        call win_execute(a:winid, "norm! j")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "gtagsExplManager._previewResult(False)"
    elseif key ==# "k" || key ==? "<Up>"
        call win_execute(a:winid, "norm! k")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "gtagsExplManager._previewResult(False)"
    elseif key ==? "<PageUp>" || key ==? "<C-B>"
        call win_execute(a:winid, "norm! \<PageUp>")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "gtagsExplManager._previewResult(False)"
    elseif key ==? "<PageDown>" || key ==? "<C-F>"
        call win_execute(a:winid, "norm! \<PageDown>")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "gtagsExplManager._previewResult(False)"
    elseif key ==# "g"
        if get(g:, "Lf_Gtags_is_g_pressed", 0) == 0
            let g:Lf_Gtags_is_g_pressed = 1
        else
            let g:Lf_Gtags_is_g_pressed = 0
            call win_execute(a:winid, "norm! gg")
            exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
            redraw
        endif
    elseif key ==# "G"
        call win_execute(a:winid, "norm! G")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-U>"
        call win_execute(a:winid, "norm! \<C-U>")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-D>"
        call win_execute(a:winid, "norm! \<C-D>")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            call win_execute(pos.winid, "call cursor([pos.line, pos.column])")
            exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "gtagsExplManager._previewResult(False)"
        elseif has('patch-8.1.2266')
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "gtagsExplManager._previewResult(False)"
        endif
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        exec g:Lf_py "gtagsExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "gtagsExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==# "q" || key ==? "<ESC>"
        exec g:Lf_py "gtagsExplManager.quit()"
    elseif key ==# "i" || key ==? "<Tab>"
        call leaderf#ResetPopupOptions(a:winid, 'filter', 'leaderf#PopupFilter')
        exec g:Lf_py "gtagsExplManager.input()"
    elseif key ==# "o" || key ==? "<CR>" || key ==? "<2-LeftMouse>"
        exec g:Lf_py "gtagsExplManager.accept()"
    elseif key ==# "x"
        exec g:Lf_py "gtagsExplManager.accept('h')"
    elseif key ==# "v"
        exec g:Lf_py "gtagsExplManager.accept('v')"
    elseif key ==# "t"
        exec g:Lf_py "gtagsExplManager.accept('t')"
    elseif key ==# "p"
        exec g:Lf_py "gtagsExplManager._previewResult(True)"
    elseif key ==? "<F1>"
        exec g:Lf_py "gtagsExplManager.toggleHelp()"
    elseif key ==# "d"
        exec g:Lf_py "gtagsExplManager.deleteCurrentLine()"
    elseif key ==? "<C-Up>"
        exec g:Lf_py "gtagsExplManager._toUpInPopup()"
    elseif key ==? "<C-Down>"
        exec g:Lf_py "gtagsExplManager._toDownInPopup()"
    endif

    return 1
endfunction

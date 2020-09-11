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
    nnoremap <buffer> <silent> j             j:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py "fileExplManager._previewResult(False)"<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py "fileExplManager._toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py "fileExplManager._toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py "fileExplManager._closePreviewPopup()"<CR>
    endif
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
    let key = get(g:Lf_KeyDict, get(g:Lf_KeyMap, a:key, a:key), a:key)

    if key !=# "g"
        call win_execute(a:winid, "let g:Lf_File_is_g_pressed = 0")
    endif

    if key ==# "j" || key ==? "<Down>"
        call win_execute(a:winid, "norm! j")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "fileExplManager._previewResult(False)"
    elseif key ==# "k" || key ==? "<Up>"
        call win_execute(a:winid, "norm! k")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        "redraw
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "fileExplManager._previewResult(False)"
    elseif key ==? "<PageUp>" || key ==? "<C-B>"
        call win_execute(a:winid, "norm! \<PageUp>")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "fileExplManager._previewResult(False)"
    elseif key ==? "<PageDown>" || key ==? "<C-F>"
        call win_execute(a:winid, "norm! \<PageDown>")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
        exec g:Lf_py "fileExplManager._previewResult(False)"
    elseif key ==# "g"
        if get(g:, "Lf_File_is_g_pressed", 0) == 0
            let g:Lf_File_is_g_pressed = 1
        else
            let g:Lf_File_is_g_pressed = 0
            call win_execute(a:winid, "norm! gg")
            exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
            redraw
        endif
    elseif key ==# "G"
        call win_execute(a:winid, "norm! G")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-U>"
        call win_execute(a:winid, "norm! \<C-U>")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<C-D>"
        call win_execute(a:winid, "norm! \<C-D>")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        redraw
    elseif key ==? "<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            call win_execute(pos.winid, "call cursor([pos.line, pos.column])")
            exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "fileExplManager._previewResult(False)"
        elseif has('patch-8.1.2266')
            call win_execute(a:winid, "exec v:mouse_lnum")
            call win_execute(a:winid, "exec 'norm!'.v:mouse_col.'|'")
            exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
            redraw
            exec g:Lf_py "fileExplManager._previewResult(False)"
        endif
    elseif key ==? "<ScrollWheelUp>"
        call win_execute(a:winid, "norm! 3k")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==? "<ScrollWheelDown>"
        call win_execute(a:winid, "norm! 3j")
        exec g:Lf_py "fileExplManager._cli._buildPopupPrompt()"
        redraw
        exec g:Lf_py "fileExplManager._getInstance().refreshPopupStatusline()"
    elseif key ==# "q" || key ==? "<ESC>"
        exec g:Lf_py "fileExplManager.quit()"
    elseif key ==# "i" || key ==? "<Tab>"
        call leaderf#ResetPopupOptions(a:winid, 'filter', 'leaderf#PopupFilter')
        exec g:Lf_py "fileExplManager.input()"
    elseif key ==# "o" || key ==? "<CR>" || key ==? "<2-LeftMouse>"
        exec g:Lf_py "fileExplManager.accept()"
    elseif key ==# "x"
        exec g:Lf_py "fileExplManager.accept('h')"
    elseif key ==# "v"
        exec g:Lf_py "fileExplManager.accept('v')"
    elseif key ==# "t"
        exec g:Lf_py "fileExplManager.accept('t')"
    elseif key ==# "s"
        exec g:Lf_py "fileExplManager.addSelections()"
    elseif key ==# "a"
        exec g:Lf_py "fileExplManager.selectAll()"
    elseif key ==# "c"
        exec g:Lf_py "fileExplManager.clearSelections()"
    elseif key ==# "p"
        exec g:Lf_py "fileExplManager._previewResult(True)"
    elseif key ==? "<F1>"
        exec g:Lf_py "fileExplManager.toggleHelp()"
    elseif key ==? "<F5>"
        exec g:Lf_py "fileExplManager.refresh()"
    elseif key ==? "<C-Up>"
        exec g:Lf_py "fileExplManager._toUpInPopup()"
    elseif key ==? "<C-Down>"
        exec g:Lf_py "fileExplManager._toDownInPopup()"
    endif

    return 1
endfunction

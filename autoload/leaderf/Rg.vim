" ============================================================================
" File:        Rg.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.rgExpl import *"

function! leaderf#Rg#Maps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "rgExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "rgExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "rgExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "rgExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "rgExplManager.quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "rgExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "rgExplManager.input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "rgExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "rgExplManager.toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, "Rg")
        for i in g:Lf_NormalMap["Rg"]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, word visually selected
function! leaderf#Rg#getPattern(type)
    if a:type == 0
        return expand('<cword>')
    elseif a:type == 1
        return escape(expand('<cWORD>'))
    elseif a:type == 2
        try
            let x_save = @x
            norm! gv"xy
            return '"' . escape(@x, '"') . '"'
        finally
            let @x = x_save
        endtry
    else
        return ''
    endif
endfunction

" type: 0, word under cursor
"       1, WORD under cursor
"       2, word visually selected
function! leaderf#Rg#startCmdline(type, is_bang, is_regex, is_whole_word)
    return printf("Leaderf%s rg %s%s-e %s ", a:is_bang ? '!' : '', a:is_regex ? '' : '-F ',
                \ a:is_whole_word ? '-w ' : '', leaderf#Rg#getPattern(a:type))
endfunction

function! leaderf#Rg#Interactive()
    try
        echohl Question
        let pattern = input("Search pattern: ")
        let glob = input("Search in files(e.g., *.c, *.cpp): ", "*")
        exec printf("Leaderf rg %s%s -g %s", pattern == '' ? '' : '-e ', pattern, join(split(glob), ' -g '))
    finally
        echohl None
    endtry
endfunction

function! leaderf#Rg#TimerCallback(id)
    call leaderf#LfPy("rgExplManager._workInIdle(bang=True)")
endfunction

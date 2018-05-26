" ============================================================================
" File:        Any.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.anyExpl import *"

function! leaderf#Any#Maps(category)
    let b:Lf_AnyExplManager = "anyHub._managers['".a:category."']."
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py b:Lf_AnyExplManager."accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py b:Lf_AnyExplManager."accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py b:Lf_AnyExplManager."accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py b:Lf_AnyExplManager."quit()"<CR>
    nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py b:Lf_AnyExplManager."quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py b:Lf_AnyExplManager."input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py b:Lf_AnyExplManager."input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py b:Lf_AnyExplManager."toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, a:category)
        for i in g:Lf_NormalMap[a:category]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

let s:Lf_Categorys = {
            \ "file":[],
            \ "buffer":["--all", "--tabpage"],
            \ "mru":["--cwd"],
            \ "tag":[],
            \ "bufTag":["--all"],
            \ "function":["--all"],
            \ "line":["--all"],
            \ "cmdHistory":[],
            \ "searchHistory":[],
            \ "help":[],
            \ "colorscheme":[]
            \}

let s:Lf_CommonOptions = [
            \ ["--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"],
            \ "--cword"
            \ ]

function! leaderf#Any#parseArguments(argLead, cmdline, cursorPos)
    let argList = split(a:cmdline, '[ \t!]\+')
    let argNum = len(argList)
    if argNum == 1  " Leaderf
        return keys(s:Lf_Categorys) + keys(g:Lf_Extensions)
    elseif argNum == 2 && a:cmdline[a:cursorPos-1] !~ '\s'  " 'Leaderf b'
        return filter(keys(s:Lf_Categorys) + keys(g:Lf_Extensions), "v:val =~? '^".a:argLead."'")
    else
        let existingOptions = a:cmdline[a:cursorPos-1] !~ '\s' ? argList[2:-2] : argList[2:]
        let options = []
        if has_key(g:Lf_Extensions, argList[1])
            let options = filter(copy(get(g:Lf_Extensions[argList[1]], "options", [])), "index(".string(existingOptions).", v:val) == -1")
        elseif has_key(s:Lf_Categorys, argList[1])
            let options = filter(copy(s:Lf_Categorys[argList[1]]), "index(".string(existingOptions).", v:val) == -1")
        endif
        for opt in s:Lf_CommonOptions
            if type(opt) == type([])
                if len(filter(copy(opt), "index(".string(existingOptions).", v:val) >= 0")) == 0
                    let options += opt
                endif
            elseif index(existingOptions, opt) == -1
                call add(options, opt)
            endif
        endfor
        return filter(sort(copy(options)), "v:val =~? '^".a:argLead."'")
    endif
endfunction

function! leaderf#Any#start(bang, ...)
    if a:0 == 0

    else
        if !has_key(g:Lf_Extensions, a:1) && index(keys(s:Lf_Categorys), a:1) == -1
            echohl Error
            echo "Unknown argument '" . a:1 . "'!"
            echohl NONE
            return
        else
            call leaderf#LfPy("anyHub.start('".a:1."', bang=".a:bang.", options=".string(a:000[1:]).")")
        endif
    endif
endfunction


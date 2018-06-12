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

let g:Lf_Arguments = {
            \ "file":[
            \           {"name": ["directory"], "nargs": "?", "help": "serarch files under <directory>"},
            \   ],
            \ "buffer":[
            \           {"name": ["--all"], "nargs": 0, "help": "search all buffers in addition to the listed buffers"},
            \           {"name": ["--tabpage"], "nargs": 0, "help": "search buffers in current tabpage."},
            \   ],
            \ "mru":[
            \           {"name": ["--cwd"], "nargs": 0, "help": "search MRU in current working directory."},
            \   ],
            \ "tag":[],
            \ "bufTag":[
            \           {"name": ["--all"], "nargs": 0, "help": "search bufTag in all opening buffers."},
            \   ],
            \ "function":[
            \           {"name": ["--all"], "nargs": 0, "help": "search functions in all opening buffers."},
            \   ],
            \ "line":[
            \           {"name": ["--all"], "nargs": 0, "help": "search lines in all opening buffers."},
            \   ],
            \ "cmdHistory":[],
            \ "searchHistory":[],
            \ "help":[],
            \ "colorscheme":[]
            \}

let g:Lf_CommonArguments = [
            \ [
            \   {"name": ["--input"], "nargs": 1, "help": "specifies INPUT as the pattern inputted in advance."},
            \   {"name": ["--cword"], "nargs": 0, "help": "current word under cursor is inputted in advance."},
            \ ],
            \ [
            \   {"name": ["--top"],        "nargs": 0, "help": "the LeaderF window is at the top of the screen."},
            \   {"name": ["--bottom"],     "nargs": 0, "help": "the LeaderF window is at the bottom of the screen."},
            \   {"name": ["--left"],       "nargs": 0, "help": "the LeaderF window is at the left of the screen."},
            \   {"name": ["--right"],      "nargs": 0, "help": "the LeaderF window is at the right of the screen."},
            \   {"name": ["--belowright"], "nargs": 0, "help": "the LeaderF window is at the belowright of the screen."},
            \   {"name": ["--aboveleft"],  "nargs": 0, "help": "the LeaderF window is at the aboveleft of the screen."},
            \   {"name": ["--fullScreen"], "nargs": 0, "help": "the LeaderF window takes up the full screen."},
            \ ],
            \ [
            \   {"name": ["--nameOnly"], "nargs": 0, "help": "LeaderF is in NameOnly mode by default."},
            \   {"name": ["--fullPath"], "nargs": 0, "help": "LeaderF is in FullPath mode by default."},
            \   {"name": ["--fuzzy"],    "nargs": 0, "help": "LeaderF is in Fuzzy mode by default."},
            \   {"name": ["--regex"],    "nargs": 0, "help": "LeaderF is in Regex mode by default."},
            \ ],
            \]

" arguments is something like g:Lf_CommonArguments
" return something like
" [
"   ["--input", "--cword"],
"   ["--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"],
"   ["--nameOnly", "--fullPath", "--fuzzy", "--regex"],
" ]
function! s:Lf_Refine(arguments)
    let result = []
    for arg in a:arguments
        if type(arg) == type([])
            let sublist = []
            for i in arg
                let sublist += i["name"]
            endfor
            call add(result, sublist)
        else
            call extend(result, arg["name"])
        endif
    endfor
    return result
endfunction

function! leaderf#Any#parseArguments(argLead, cmdline, cursorPos)
    let argList = split(a:cmdline, '[ \t!]\+')
    let argNum = len(argList)
    if argNum == 1  " Leaderf
        return keys(g:Lf_Arguments) + keys(g:Lf_Extensions)
    elseif argNum == 2 && a:cmdline[a:cursorPos-1] !~ '\s'  " 'Leaderf b'
        return filter(keys(g:Lf_Arguments) + keys(g:Lf_Extensions), "v:val =~? '^".a:argLead."'")
    else
        let existingOptions = a:cmdline[a:cursorPos-1] !~ '\s' ? argList[2:-2] : argList[2:]
        let options = []
        if has_key(g:Lf_Extensions, argList[1])
            let arguments = get(g:Lf_Extensions[argList[1]], "arguments", [])
        elseif has_key(g:Lf_Arguments, argList[1])
            let arguments = g:Lf_Arguments[argList[1]]
        endif
        for opt in s:Lf_Refine(arguments + g:Lf_CommonArguments)
            if type(opt) == type([])
                if len(filter(copy(opt), "index(".string(existingOptions).", v:val) >= 0")) == 0
                    let options += opt
                endif
            elseif index(existingOptions, opt) == -1
                call add(options, opt)
            endif
        endfor
        return filter(filter(copy(options), "v:val =~? '^".a:argLead."'"), "v:val =~ '^-'")
    endif
endfunction

function! leaderf#Any#start(bang, args)
    if a:args == ""

    else
        let category = split(a:args)[0]
        if !has_key(g:Lf_Extensions, category) && index(keys(g:Lf_Arguments), category) == -1
            echohl Error
            echo "Unrecognized argument '" . category . "'!"
            echohl NONE
            return
        else
            call leaderf#LfPy("anyHub.start('".category."', '".a:args."', bang=".a:bang.")")
        endif
    endif
endfunction


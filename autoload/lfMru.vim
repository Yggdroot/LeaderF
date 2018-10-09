" ============================================================================
" File:        lfMru.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

let g:Lf_CacheDirectory = substitute(g:Lf_CacheDirectory, '[\/]$', '', '')

if !isdirectory(g:Lf_CacheDirectory)
    call mkdir(g:Lf_CacheDirectory, "p")
endif

if !isdirectory(g:Lf_CacheDirectory . '/.LfCache')
    call mkdir(g:Lf_CacheDirectory . '/.LfCache', "p")
endif

let g:Lf_MruCacheFileName = g:Lf_CacheDirectory . '/.LfCache/tempMru'

if !filereadable(g:Lf_MruCacheFileName)
    call writefile([], g:Lf_MruCacheFileName)
endif

function! lfMru#CacheFileName()
    return g:Lf_MruCacheFileName
endfunction

function! lfMru#record(name)
    if a:name == '' || !filereadable(a:name) || strpart(a:name, 0, 2) == '\\'
        return
    endif
    let file_list = readfile(g:Lf_MruCacheFileName)
    if empty(file_list)
        call writefile([a:name], g:Lf_MruCacheFileName)
    elseif a:name != file_list[0]
        call filter(file_list, 'v:val != a:name')
        call writefile([a:name] + file_list, g:Lf_MruCacheFileName)
    endif
endfunction

function! lfMru#recordBuffer(bufNum)
    call add(g:Lf_MruBufnrs, a:bufNum)
endfunction

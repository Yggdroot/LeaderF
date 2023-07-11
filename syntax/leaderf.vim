" ============================================================================
" File:        leaderf.vim
" Description: LeaderF syntax settings
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

scriptencoding utf-8

if exists("b:current_syntax")
    finish
endif

if has("syntax")
    syn clear
    syn match Lf_hl_help     display '^".*'
    syn match Lf_hl_helpCmd  display '^"\s*\zs.\{-}\ze\s*:' containedin=Lf_hl_help contained
    syn match Lf_hl_nonHelp  display '^[^"].*$'
    if has("win32") || has("win64")
        syn match Lf_hl_filename display '[^\/]*$' containedin=Lf_hl_nonHelp contained
        syn match Lf_hl_dirname  display '^.*[\/]' containedin=Lf_hl_nonHelp contained
    else
        syn match Lf_hl_filename display '[^/]*$' containedin=Lf_hl_nonHelp contained
        syn match Lf_hl_dirname  display '^.*/'   containedin=Lf_hl_nonHelp contained
    endif
endif

let b:current_syntax = "leaderf"

" define the highlight groups
" new highlight groups will be defined in autoload/leaderf/colorscheme/popup/default.vim

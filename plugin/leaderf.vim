" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if exists('g:leaderf_loaded') || &compatible
    finish
elseif v:version < 704 || v:version == 704 && has("patch330") == 0
    echohl Error
    echomsg "LeaderF requires Vim 7.4.330+."
    echohl None
    finish
elseif !has('pythonx') && !has('python3') && !has('python')
    echohl Error
    echomsg "LeaderF requires Vim compiled with python and/or a compatible python version."
    echohl None
    finish
else
    let g:leaderf_loaded = 1
endif

function! s:InitVar(var, value)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:value)
    endif
endfunction

call s:InitVar('g:Lf_ShortcutF', '<Leader>f')
call s:InitVar('g:Lf_ShortcutB', '<Leader>b')
call s:InitVar('g:Lf_WindowPosition', 'bottom')
call s:InitVar('g:Lf_MruBufnrs', [])
call s:InitVar('g:Lf_PythonExtensions', {})
call s:InitVar('g:Lf_PreviewWindowID', {})

if has('win32') || has('win64')
    let s:cache_dir = $APPDATA
    if s:cache_dir == ''
        let s:cache_dir = $HOME
    endif
else
    let s:cache_dir = $XDG_CACHE_HOME
    if s:cache_dir == ''
        let s:cache_dir = $HOME . '/.cache'
    endif
endif
call s:InitVar('g:Lf_CacheDirectory', s:cache_dir)

function! g:LfNoErrMsgMatch(expr, pat)
    try
        return match(a:expr, a:pat)
    catch /^Vim\%((\a\+)\)\=:E/
    endtry
    return -2
endfunction

function! g:LfNoErrMsgCmd(cmd)
    try
        exec a:cmd
        return 1
    catch /^Vim\%((\a\+)\)\=:/
        return 0
    endtry
endfunction

call s:InitVar('g:Lf_SelfContent', {})

function! g:LfRegisterSelf(cmd, description)
    let g:Lf_SelfContent[a:cmd] = a:description
endfunction

function! g:LfRegisterPythonExtension(name, dict)
    let g:Lf_PythonExtensions[a:name] = a:dict
endfunction

let s:leaderf_path = expand("<sfile>:p:h:h")
function! s:InstallCExtension(install) abort
    let win_exists = 0
    let bot_split = "botright new | let w:leaderf_installC = 1 |"
    let use_cur_win = has("nvim") ? "" : " ++curwin"
    for n in range(winnr('$'))
        if getwinvar(n+1, 'leaderf_installC', 0) == 1
            let win_exists = 1
            let bot_split = ""
            exec string(n+1) . "wincmd w"
            break
        endif
    endfor
    let terminal = exists(':terminal') == 2 ? bot_split ." terminal". use_cur_win : "!"
    if has('win32') || has('win64')
        let shell =  "cmd /c"
        let cd_cmd = "cd /d"
        let script = "install.bat"
    else
        let shell =  "sh -c"
        let cd_cmd = "cd"
        let script = "./install.sh"
    endif
    let reverse = a:install ? "" : " --reverse"
    let cmd = printf('%s %s "%s %s && %s%s"', terminal, shell, cd_cmd, s:leaderf_path, script, reverse)
    exec cmd
    if has("nvim")
        norm! G
    endif
endfunction

function! s:Normalize(filename)
    if has("nvim") && (has('win32') || has('win64'))
        if &shellslash
            return tr(a:filename, '\', '/')
        else
            return tr(a:filename, '/', '\')
        endif
    else
        return a:filename
    endif
endfunction

if get(g:, 'Lf_MruEnable', 1) == 1
    augroup LeaderF_Mru
        autocmd BufEnter,BufWritePost * call lfMru#record(s:Normalize(expand('<afile>:p'))) |
                    \ call lfMru#recordBuffer(expand('<abuf>'))
    augroup END
endif

augroup LeaderF_Gtags
    autocmd!
    if get(g:, 'Lf_GtagsAutoGenerate', 0) == 1
        autocmd BufRead * call leaderf#Gtags#updateGtags(expand('<afile>:p'), 0)
    endif
    if get(g:, 'Lf_GtagsAutoUpdate', 1) == 1
        autocmd BufWritePost * call leaderf#Gtags#updateGtags(expand('<afile>:p'), 1)
    endif
augroup END

noremap <silent> <Plug>LeaderfFileTop        :<C-U>Leaderf file --top<CR>
noremap <silent> <Plug>LeaderfFileBottom     :<C-U>Leaderf file --bottom<CR>
noremap <silent> <Plug>LeaderfFileLeft       :<C-U>Leaderf file --left<CR>
noremap <silent> <Plug>LeaderfFileRight      :<C-U>Leaderf file --right<CR>
noremap <silent> <Plug>LeaderfFileFullScreen :<C-U>Leaderf file --fullScreen<CR>

noremap <silent> <Plug>LeaderfBufferTop        :<C-U>Leaderf buffer --top<CR>
noremap <silent> <Plug>LeaderfBufferBottom     :<C-U>Leaderf buffer --bottom<CR>
noremap <silent> <Plug>LeaderfBufferLeft       :<C-U>Leaderf buffer --left<CR>
noremap <silent> <Plug>LeaderfBufferRight      :<C-U>Leaderf buffer --right<CR>
noremap <silent> <Plug>LeaderfBufferFullScreen :<C-U>Leaderf buffer --fullScreen<CR>

noremap <silent> <Plug>LeaderfMruCwdTop        :<C-U>Leaderf mru --top<CR>
noremap <silent> <Plug>LeaderfMruCwdBottom     :<C-U>Leaderf mru --bottom<CR>
noremap <silent> <Plug>LeaderfMruCwdLeft       :<C-U>Leaderf mru --left<CR>
noremap <silent> <Plug>LeaderfMruCwdRight      :<C-U>Leaderf mru --right<CR>
noremap <silent> <Plug>LeaderfMruCwdFullScreen :<C-U>Leaderf mru --fullScreen<CR>

noremap <Plug>LeaderfRgPrompt :<C-U>Leaderf rg -e<Space>
noremap <Plug>LeaderfRgCwordLiteralNoBoundary :<C-U><C-R>=leaderf#Rg#startCmdline(0, 0, 0, 0)<CR>
noremap <Plug>LeaderfRgCwordLiteralBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(0, 0, 0, 1)<CR>
noremap <Plug>LeaderfRgCwordRegexNoBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(0, 0, 1, 0)<CR>
noremap <Plug>LeaderfRgCwordRegexBoundary     :<C-U><C-R>=leaderf#Rg#startCmdline(0, 0, 1, 1)<CR>

noremap <Plug>LeaderfRgBangCwordLiteralNoBoundary :<C-U><C-R>=leaderf#Rg#startCmdline(0, 1, 0, 0)<CR>
noremap <Plug>LeaderfRgBangCwordLiteralBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(0, 1, 0, 1)<CR>
noremap <Plug>LeaderfRgBangCwordRegexNoBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(0, 1, 1, 0)<CR>
noremap <Plug>LeaderfRgBangCwordRegexBoundary     :<C-U><C-R>=leaderf#Rg#startCmdline(0, 1, 1, 1)<CR>

noremap <Plug>LeaderfRgWORDLiteralNoBoundary :<C-U><C-R>=leaderf#Rg#startCmdline(1, 0, 0, 0)<CR>
noremap <Plug>LeaderfRgWORDLiteralBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(1, 0, 0, 0)<CR>
noremap <Plug>LeaderfRgWORDRegexNoBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(1, 0, 1, 0)<CR>
noremap <Plug>LeaderfRgWORDRegexBoundary     :<C-U><C-R>=leaderf#Rg#startCmdline(1, 0, 1, 1)<CR>

vnoremap <silent> <Plug>LeaderfRgVisualLiteralNoBoundary :<C-U><C-R>=leaderf#Rg#startCmdline(2, 0, 0, 0)<CR>
vnoremap <silent> <Plug>LeaderfRgVisualLiteralBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(2, 0, 0, 1)<CR>
vnoremap <silent> <Plug>LeaderfRgVisualRegexNoBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(2, 0, 1, 0)<CR>
vnoremap <silent> <Plug>LeaderfRgVisualRegexBoundary     :<C-U><C-R>=leaderf#Rg#startCmdline(2, 0, 1, 1)<CR>

vnoremap <silent> <Plug>LeaderfRgBangVisualLiteralNoBoundary :<C-U><C-R>=leaderf#Rg#startCmdline(2, 1, 0, 0)<CR>
vnoremap <silent> <Plug>LeaderfRgBangVisualLiteralBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(2, 1, 0, 1)<CR>
vnoremap <silent> <Plug>LeaderfRgBangVisualRegexNoBoundary   :<C-U><C-R>=leaderf#Rg#startCmdline(2, 1, 1, 0)<CR>
vnoremap <silent> <Plug>LeaderfRgBangVisualRegexBoundary     :<C-U><C-R>=leaderf#Rg#startCmdline(2, 1, 1, 1)<CR>

noremap <Plug>LeaderfGtagsDefinition :<C-U><C-R>=leaderf#Gtags#startCmdline(0, 1, 'd')<CR><CR>
noremap <Plug>LeaderfGtagsReference :<C-U><C-R>=leaderf#Gtags#startCmdline(0, 1, 'r')<CR><CR>
noremap <Plug>LeaderfGtagsSymbol :<C-U><C-R>=leaderf#Gtags#startCmdline(0, 1, 's')<CR><CR>
noremap <Plug>LeaderfGtagsGrep :<C-U><C-R>=leaderf#Gtags#startCmdline(0, 1, 'g')<CR><CR>

vnoremap <silent> <Plug>LeaderfGtagsDefinition :<C-U><C-R>=leaderf#Gtags#startCmdline(2, 1, 'd')<CR><CR>
vnoremap <silent> <Plug>LeaderfGtagsReference :<C-U><C-R>=leaderf#Gtags#startCmdline(2, 1, 'r')<CR><CR>
vnoremap <silent> <Plug>LeaderfGtagsSymbol :<C-U><C-R>=leaderf#Gtags#startCmdline(2, 1, 's')<CR><CR>
vnoremap <silent> <Plug>LeaderfGtagsGrep :<C-U><C-R>=leaderf#Gtags#startCmdline(2, 1, 'g')<CR><CR>

command! -bar -nargs=* -complete=dir LeaderfFile Leaderf file <args>
command! -bar -nargs=* -complete=dir LeaderfFileFullScreen Leaderf file --fullScreen <args>
command! -bar -nargs=1 LeaderfFilePattern Leaderf file --input <args>
command! -bar -nargs=0 LeaderfFileCword Leaderf file --cword

command! -bar -nargs=0 LeaderfBuffer Leaderf buffer
command! -bar -nargs=0 LeaderfBufferAll Leaderf buffer --all
command! -bar -nargs=0 LeaderfTabBuffer Leaderf buffer --tabpage
command! -bar -nargs=0 LeaderfTabBufferAll Leaderf buffer --tabpage --all
command! -bar -nargs=1 LeaderfBufferPattern Leaderf buffer --input <args>
command! -bar -nargs=0 LeaderfBufferCword Leaderf buffer --cword

command! -bar -nargs=0 LeaderfMru Leaderf mru
command! -bar -nargs=0 LeaderfMruCwd Leaderf mru --cwd
command! -bar -nargs=1 LeaderfMruPattern Leaderf mru --input <args>
command! -bar -nargs=0 LeaderfMruCword Leaderf mru --cword
command! -bar -nargs=1 LeaderfMruCwdPattern Leaderf mru --cwd --input <args>
command! -bar -nargs=0 LeaderfMruCwdCword Leaderf mru --cwd --cword

command! -bar -nargs=0 LeaderfTag Leaderf tag
command! -bar -nargs=1 LeaderfTagPattern Leaderf tag --input <args>
command! -bar -nargs=0 LeaderfTagCword Leaderf tag --cword

command! -bar -nargs=0 -bang LeaderfBufTag Leaderf<bang> bufTag
command! -bar -nargs=0 -bang LeaderfBufTagAll Leaderf<bang> bufTag --all
command! -bar -nargs=1 -bang LeaderfBufTagPattern Leaderf<bang> bufTag --input <args>
command! -bar -nargs=0 -bang LeaderfBufTagCword Leaderf<bang> bufTag --cword
command! -bar -nargs=1 -bang LeaderfBufTagAllPattern Leaderf<bang> bufTag --all --input <args>
command! -bar -nargs=0 -bang LeaderfBufTagAllCword Leaderf<bang> bufTag --all --cword

command! -bar -nargs=0 -bang LeaderfFunction Leaderf<bang> function
command! -bar -nargs=0 -bang LeaderfFunctionAll Leaderf<bang> function --all
command! -bar -nargs=1 -bang LeaderfFunctionPattern Leaderf<bang> function --input <args>
command! -bar -nargs=0 -bang LeaderfFunctionCword Leaderf<bang> function --cword
command! -bar -nargs=1 -bang LeaderfFunctionAllPattern Leaderf<bang> function --all --input <args>
command! -bar -nargs=0 -bang LeaderfFunctionAllCword Leaderf<bang> function --all --cword

command! -bar -nargs=0 LeaderfLine Leaderf line
command! -bar -nargs=0 LeaderfLineAll Leaderf line --all
command! -bar -nargs=1 LeaderfLinePattern Leaderf line --input <args>
command! -bar -nargs=0 LeaderfLineCword Leaderf line --cword
command! -bar -nargs=1 LeaderfLineAllPattern Leaderf line --all --input <args>
command! -bar -nargs=0 LeaderfLineAllCword Leaderf line --all --cword

command! -bar -nargs=0 LeaderfHistoryCmd Leaderf cmdHistory
command! -bar -nargs=0 LeaderfHistorySearch exec "Leaderf searchHistory" | silent! norm! n

command! -bar -nargs=0 LeaderfSelf Leaderf self

command! -bar -nargs=0 LeaderfHelp Leaderf help
command! -bar -nargs=1 LeaderfHelpPattern Leaderf help --input <args>
command! -bar -nargs=0 LeaderfHelpCword Leaderf help --cword

command! -bar -nargs=0 LeaderfColorscheme Leaderf colorscheme

command! -bar -nargs=0 LeaderfRgInteractive call leaderf#Rg#Interactive()
command! -bar -nargs=0 LeaderfRgRecall exec "Leaderf! rg --recall"

command! -bar -nargs=0 LeaderfFiletype Leaderf filetype

command! -bar -nargs=0 LeaderfCommand Leaderf command

command! -bar -nargs=0 LeaderfWindow Leaderf window

command! -bar -nargs=0 LeaderfQuickFix Leaderf quickfix
command! -bar -nargs=0 LeaderfLocList  Leaderf loclist

command! -bar -nargs=0 LeaderfGit           Leaderf git
command! -bar -nargs=0 LeaderfGitSplitDiff  Leaderf git diff --current-file --side-by-side

try
    if g:Lf_ShortcutF != ""
        exec 'nnoremap <silent><unique> ' g:Lf_ShortcutF ':<C-U>LeaderfFile<CR>'
    endif
catch /^Vim\%((\a\+)\)\=:E227/
endtry

try
    if g:Lf_ShortcutB != ""
        exec 'nnoremap <silent><unique> ' g:Lf_ShortcutB ':<C-U>LeaderfBuffer<CR>'
    endif
catch /^Vim\%((\a\+)\)\=:E227/
endtry

command! -nargs=* -bang -complete=customlist,leaderf#Any#parseArguments Leaderf call leaderf#Any#start(<bang>0, <q-args>)
command! -nargs=0 LeaderfInstallCExtension call s:InstallCExtension(1)
command! -nargs=0 LeaderfUninstallCExtension call s:InstallCExtension(0)

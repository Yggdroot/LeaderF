" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

" temporary fix
" https://github.com/vim/vim/issues/3117
if has('python3')
  silent! python3 1
endif

if exists('g:leaderf_loaded') || &compatible
    finish
elseif v:version < 704 || v:version == 704 && has("patch330") == 0
    echohl Error
    echo "LeaderF requires Vim 7.4.330+."
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
call s:InitVar('g:Lf_CacheDirectory', $HOME)
call s:InitVar('g:Lf_MruBufnrs', [])

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

augroup LeaderF_Mru
    autocmd BufAdd,BufEnter,BufWritePost * call lfMru#record(expand('<afile>:p')) |
                \ call lfMru#recordBuffer(expand('<abuf>'))
augroup END

nnoremap <silent> <Plug>LeaderfFileTop :<C-U>call leaderf#File#startExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfFileBottom :<C-U>call leaderf#File#startExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfFileLeft :<C-U>call leaderf#File#startExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfFileRight :<C-U>call leaderf#File#startExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfFileFullScreen :<C-U>call leaderf#File#startExpl('fullScreen')<CR>

nnoremap <silent> <Plug>LeaderfBufferTop :<C-U>call leaderf#Buffer#startExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfBufferBottom :<C-U>call leaderf#Buffer#startExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfBufferLeft :<C-U>call leaderf#Buffer#startExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfBufferRight :<C-U>call leaderf#Buffer#startExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfBufferFullScreen :<C-U>call leaderf#Buffer#startExpl('fullScreen')<CR>

nnoremap <silent> <Plug>LeaderfMruCwdTop :<C-U>call leaderf#Mru#startExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdBottom :<C-U>call leaderf#Mru#startExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdLeft :<C-U>call leaderf#Mru#startExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdRight :<C-U>call leaderf#Mru#startExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdFullScreen :<C-U>call leaderf#Mru#startExpl('fullScreen')<CR>

command! -bar -nargs=? -complete=dir LeaderfFile call leaderf#File#startExpl(g:Lf_WindowPosition, <f-args>)
command! -bar -nargs=? -complete=dir LeaderfFileFullScreen call leaderf#File#startExpl('fullScreen', <f-args>)
command! -bar -nargs=1 LeaderfFilePattern call leaderf#File#startExplPattern(g:Lf_WindowPosition, <q-args>)
command! -bar -nargs=0 LeaderfFileCword call leaderf#File#startExplPattern(g:Lf_WindowPosition, expand('<cword>'))

command! -bar -nargs=0 LeaderfBuffer call leaderf#Buffer#startExpl(g:Lf_WindowPosition)
command! -bar -nargs=0 LeaderfBufferAll call leaderf#Buffer#startExpl(g:Lf_WindowPosition, 1)
command! -bar -nargs=0 LeaderfTabBuffer call leaderf#Buffer#startExpl(g:Lf_WindowPosition, 2)
command! -bar -nargs=0 LeaderfTabBufferAll call leaderf#Buffer#startExpl(g:Lf_WindowPosition, 3)
command! -bar -nargs=1 LeaderfBufferPattern call leaderf#Buffer#startExplPattern(g:Lf_WindowPosition, <q-args>)
command! -bar -nargs=0 LeaderfBufferCword call leaderf#Buffer#startExplPattern(g:Lf_WindowPosition, expand('<cword>'))

command! -bar -nargs=0 LeaderfMru call leaderf#Mru#startExpl(g:Lf_WindowPosition)
command! -bar -nargs=0 LeaderfMruCwd call leaderf#Mru#startExpl(g:Lf_WindowPosition, 1)
command! -bar -nargs=1 LeaderfMruPattern call leaderf#Mru#startExplPattern(g:Lf_WindowPosition, 0, <q-args>)
command! -bar -nargs=0 LeaderfMruCword call leaderf#Mru#startExplPattern(g:Lf_WindowPosition, 0, expand('<cword>'))
command! -bar -nargs=1 LeaderfMruCwdPattern call leaderf#Mru#startExplPattern(g:Lf_WindowPosition, 1, <q-args>)
command! -bar -nargs=0 LeaderfMruCwdCword call leaderf#Mru#startExplPattern(g:Lf_WindowPosition, 1, expand('<cword>'))

command! -bar -nargs=0 LeaderfTag call leaderf#Tag#startExpl(g:Lf_WindowPosition)
command! -bar -nargs=1 LeaderfTagPattern call leaderf#Tag#startExplPattern(g:Lf_WindowPosition, <q-args>)
command! -bar -nargs=0 LeaderfTagCword call leaderf#Tag#startExplPattern(g:Lf_WindowPosition, expand('<cword>'))

command! -bar -nargs=0 -bang LeaderfBufTag call leaderf#BufTag#startExpl(g:Lf_WindowPosition, <bang>0)
command! -bar -nargs=0 -bang LeaderfBufTagAll call leaderf#BufTag#startExpl(g:Lf_WindowPosition, <bang>0, 1)
command! -bar -nargs=1 -bang LeaderfBufTagPattern call leaderf#BufTag#startExplPattern(g:Lf_WindowPosition, <bang>0, 0, <q-args>)
command! -bar -nargs=0 -bang LeaderfBufTagCword call leaderf#BufTag#startExplPattern(g:Lf_WindowPosition, <bang>0, 0, expand('<cword>'))
command! -bar -nargs=1 -bang LeaderfBufTagAllPattern call leaderf#BufTag#startExplPattern(g:Lf_WindowPosition, <bang>0, 1, <q-args>)
command! -bar -nargs=0 -bang LeaderfBufTagAllCword call leaderf#BufTag#startExplPattern(g:Lf_WindowPosition, <bang>0, 1, expand('<cword>'))

command! -bar -nargs=0 -bang LeaderfFunction call leaderf#Function#startExpl(g:Lf_WindowPosition, <bang>0)
command! -bar -nargs=0 -bang LeaderfFunctionAll call leaderf#Function#startExpl(g:Lf_WindowPosition, <bang>0, 1)
command! -bar -nargs=1 -bang LeaderfFunctionPattern call leaderf#Function#startExplPattern(g:Lf_WindowPosition, <bang>0, 0, <q-args>)
command! -bar -nargs=0 -bang LeaderfFunctionCword call leaderf#Function#startExplPattern(g:Lf_WindowPosition, <bang>0, 0, expand('<cword>'))
command! -bar -nargs=1 -bang LeaderfFunctionAllPattern call leaderf#Function#startExplPattern(g:Lf_WindowPosition, <bang>0, 1, <q-args>)
command! -bar -nargs=0 -bang LeaderfFunctionAllCword call leaderf#Function#startExplPattern(g:Lf_WindowPosition, <bang>0, 1, expand('<cword>'))

command! -bar -nargs=0 LeaderfLine call leaderf#Line#startExpl(g:Lf_WindowPosition)
command! -bar -nargs=0 LeaderfLineAll call leaderf#Line#startExpl(g:Lf_WindowPosition, 1)
command! -bar -nargs=1 LeaderfLinePattern call leaderf#Line#startExplPattern(g:Lf_WindowPosition, 0, <q-args>)
command! -bar -nargs=0 LeaderfLineCword call leaderf#Line#startExplPattern(g:Lf_WindowPosition, 0, expand('<cword>'))
command! -bar -nargs=1 LeaderfLineAllPattern call leaderf#Line#startExplPattern(g:Lf_WindowPosition, 1, <q-args>)
command! -bar -nargs=0 LeaderfLineAllCword call leaderf#Line#startExplPattern(g:Lf_WindowPosition, 1, expand('<cword>'))

command! -bar -nargs=0 LeaderfHistoryCmd call leaderf#History#startExpl(g:Lf_WindowPosition, "cmd")
command! -bar -nargs=0 LeaderfHistorySearch call leaderf#History#startExpl(g:Lf_WindowPosition, "search") | silent! norm! n

command! -bar -nargs=0 LeaderfSelf call leaderf#Self#startExpl(g:Lf_WindowPosition)

command! -bar -nargs=0 LeaderfHelp call leaderf#Help#startExpl(g:Lf_WindowPosition)
command! -bar -nargs=1 LeaderfHelpPattern call leaderf#Help#startExplPattern(g:Lf_WindowPosition, <q-args>)
command! -bar -nargs=0 LeaderfHelpCword call leaderf#Help#startExplPattern(g:Lf_WindowPosition, expand('<cword>'))

command! -bar -nargs=0 LeaderfColorscheme call leaderf#Colors#startExpl(g:Lf_WindowPosition)

try
    exec 'nnoremap <silent><unique> ' g:Lf_ShortcutF ':<C-U>LeaderfFile<CR>'
catch /^Vim\%((\a\+)\)\=:E227/
endtry

try
    exec 'nnoremap <silent><unique> ' g:Lf_ShortcutB ':<C-U>LeaderfBuffer<CR>'
catch /^Vim\%((\a\+)\)\=:E227/
endtry

command! -nargs=* -bang -complete=customlist,leaderf#Any#parseArguments Leaderf call leaderf#Any#start(<bang>0, <q-args>)

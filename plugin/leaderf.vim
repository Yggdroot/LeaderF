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
    echo "LeaderF requires Vim 7.4.330+."
    echohl None
    finish
else
    let g:leaderf_loaded = 1
endif

if !exists("g:Lf_PythonVersion")
    if has("python3")
        let g:Lf_PythonVersion = 3
        let g:Lf_py = "py3 "
    elseif has("python")
        let g:Lf_PythonVersion = 2
        let g:Lf_py = "py "
    else
        echohl Error
        echo "Error: LeaderF requires vim compiled with +python or +python3"
        echohl None
        finish
    endif
else
    if g:Lf_PythonVersion == 2
        if has("python")
            let g:Lf_py = "py "
        else
            echohl Error
            echo 'LeaderF Error: has("python") == 0'
            echohl None
            finish
        endif
    else
        if has("python3")
            let g:Lf_py = "py3 "
        else
            echohl Error
            echo 'LeaderF Error: has("python3") == 0'
            echohl None
            finish
        endif
    endif
endif

function! s:InitVar(var, value)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:value)
    endif
endfunction

function! s:InitDict(var, dict)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:dict)
    else
        let tmp = a:dict
        for [key, value] in items(eval(a:var))
            let tmp[key] = value
        endfor
        exec 'let '.a:var.'='.string(tmp)
    endif
endfunction

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

call s:InitVar('g:Lf_ShortcutF', '<Leader>f')
call s:InitVar('g:Lf_ShortcutB', '<Leader>b')
call s:InitVar('g:Lf_WindowPosition', 'bottom')
call s:InitVar('g:Lf_WindowHeight', '0.5')
call s:InitVar('g:Lf_TabpagePosition', 2)
call s:InitVar('g:Lf_ShowRelativePath', 1)
call s:InitVar('g:Lf_DefaultMode', 'NameOnly')
call s:InitVar('g:Lf_CursorBlink', 1)
call s:InitVar('g:Lf_CacheDirectory', $HOME)
call s:InitVar('g:Lf_NeedCacheTime', '1.5')
call s:InitVar('g:Lf_NumberOfCache', 5)
call s:InitVar('g:Lf_UseMemoryCache', 1)
call s:InitVar('g:Lf_IndexTimeLimit', 120)
call s:InitVar('g:Lf_FollowLinks', 0)
call s:InitVar('g:Lf_DelimiterChar', ';')
call s:InitVar('g:Lf_MruFileExclude', [])
call s:InitVar('g:Lf_MruMaxFiles', 100)
call s:InitVar('g:Lf_HighlightIndividual', 1)
call s:InitVar('g:Lf_NumberOfHighlight', 100)
call s:InitVar('g:Lf_WildIgnore', {
            \ 'dir': [],
            \ 'file': []
            \})
call s:InitVar('g:Lf_MruWildIgnore', {
            \ 'dir': [],
            \ 'file': []
            \})
if &encoding ==? "utf-8"
    call s:InitVar('g:Lf_StlSeparator', {
                \ 'left': '►',
                \ 'right': '◄',
                \ 'font': ''
                \})
else
    call s:InitVar('g:Lf_StlSeparator', {
                \ 'left': '',
                \ 'right': '',
                \ 'font': ''
                \})
endif
call s:InitVar('g:Lf_StlPalette', {})
call s:InitVar('g:Lf_Ctags', 'ctags')
call s:InitVar('g:Lf_PreviewCode', 0)
call s:InitVar('g:Lf_UseVersionControlTool', 1)
call s:InitVar('g:Lf_RememberLastSearch', 0)
call s:InitVar('g:Lf_UseCache', 1)
call s:InitVar('g:Lf_RootMarkers', ['.git', '.hg', '.svn'])
call s:InitVar('g:Lf_WorkingDirectoryMode', 'c')
call s:InitVar('g:Lf_ShowHidden', 0)
call s:InitDict('g:Lf_PreviewResult', {
            \ 'File': 0,
            \ 'Buffer': 0,
            \ 'Mru': 0,
            \ 'Tag': 0,
            \ 'BufTag': 1,
            \ 'Function': 1,
            \ 'Line': 0,
            \ 'Colorscheme': 0
            \})
call s:InitDict('g:Lf_NormalMap', {})
call s:InitVar('g:Lf_Extensions', {})

let s:Lf_CommandMap = {
            \ '<C-A>':         ['<C-A>'],
            \ '<C-B>':         ['<C-B>'],
            \ '<C-C>':         ['<C-C>'],
            \ '<C-D>':         ['<C-D>'],
            \ '<C-E>':         ['<C-E>'],
            \ '<C-F>':         ['<C-F>'],
            \ '<C-G>':         ['<C-G>'],
            \ '<C-H>':         ['<C-H>'],
            \ '<C-J>':         ['<C-J>'],
            \ '<C-K>':         ['<C-K>'],
            \ '<C-L>':         ['<C-L>'],
            \ '<C-N>':         ['<C-N>'],
            \ '<C-O>':         ['<C-O>'],
            \ '<C-P>':         ['<C-P>'],
            \ '<C-Q>':         ['<C-Q>'],
            \ '<C-R>':         ['<C-R>'],
            \ '<C-S>':         ['<C-S>'],
            \ '<C-T>':         ['<C-T>'],
            \ '<C-U>':         ['<C-U>'],
            \ '<C-V>':         ['<C-V>', '<S-Insert>'],
            \ '<C-W>':         ['<C-W>'],
            \ '<C-X>':         ['<C-X>'],
            \ '<C-Y>':         ['<C-Y>'],
            \ '<C-Z>':         ['<C-Z>'],
            \ '<C-]>':         ['<C-]>'],
            \ '<F1>':          ['<F1>'],
            \ '<F2>':          ['<F2>'],
            \ '<F3>':          ['<F3>'],
            \ '<F4>':          ['<F4>'],
            \ '<F5>':          ['<F5>'],
            \ '<F6>':          ['<F6>'],
            \ '<F7>':          ['<F7>'],
            \ '<F8>':          ['<F8>'],
            \ '<F9>':          ['<F9>'],
            \ '<F10>':         ['<F10>'],
            \ '<F11>':         ['<F11>'],
            \ '<F12>':         ['<F12>'],
            \ '<CR>':          ['<CR>'],
            \ '<BS>':          ['<BS>'],
            \ '<Tab>':         ['<Tab>', '<C-I>'],
            \ '<Del>':         ['<Del>'],
            \ '<Esc>':         ['<Esc>'],
            \ '<Up>':          ['<Up>'],
            \ '<Down>':        ['<Down>'],
            \ '<Left>':        ['<Left>'],
            \ '<Right>':       ['<Right>'],
            \ '<Home>':        ['<Home>', '<C-B>'],
            \ '<End>':         ['<End>'],
            \ '<PageUp>':      ['<PageUp>'],
            \ '<PageDown>':    ['<PageDown>'],
            \ '<S-Left>':      ['<S-Left>'],
            \ '<S-Right>':     ['<S-Right>'],
            \ '<LeftMouse>':   ['<LeftMouse>'],
            \ '<RightMouse>':  ['<RightMouse>'],
            \ '<MiddleMouse>': ['<MiddleMouse>'],
            \ '<2-LeftMouse>': ['<2-LeftMouse>'],
            \ '<C-LeftMouse>': ['<C-LeftMouse>'],
            \ '<S-LeftMouse>': ['<S-LeftMouse>']
            \}

function! s:InitCommandMap(var, dict)
    if !exists(a:var)
        exec 'let '.a:var.'='.string(a:dict)
    else
        let tmp = a:dict
        for [key, value] in items(eval(a:var))
            call filter(tmp, 'v:key !=? key')
            for i in value
                if index(['<TAB>', '<C-I>'], toupper(i)) >= 0
                    call filter(tmp, "v:key != '<Tab>'")
                endif
                call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? i"))')
            endfor
            let tmp[toupper(key)] = map(value, 'toupper(v:val)')
        endfor
        exec 'let '.a:var.'='.string(tmp)
    endif
endfunction

call s:InitCommandMap('g:Lf_CommandMap', s:Lf_CommandMap)


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

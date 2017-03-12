" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
" ============================================================================

if exists('g:leaderf_loaded') || &compatible
    finish
elseif v:version < 704 || v:version == 704 && has("patch330") == 0
    echohl WarningMsg
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
        echohl WarningMsg
        echo "Error: LeaderF requires vim compiled with +python or +python3"
        echohl None
        finish
    endif
else
    if g:Lf_PythonVersion == 2
        if has("python")
            let g:Lf_py = "py "
        else
            echohl WarningMsg
            echo 'LeaderF Error: has("python") == 0'
            echohl None
            finish
        endif
    else
        if has("python3")
            let g:Lf_py = "py3 "
        else
            echohl WarningMsg
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

call s:InitVar('g:Lf_ShortcutF', '<Leader>f')
call s:InitVar('g:Lf_ShortcutB', '<Leader>b')
call s:InitVar('g:Lf_WindowPosition', 'bottom')
call s:InitVar('g:Lf_WindowHeight', 0.5)
call s:InitVar('g:Lf_TabpagePosition', 2)
call s:InitVar('g:Lf_ShowRelativePath', 1)
call s:InitVar('g:Lf_DefaultMode', 'NameOnly')
call s:InitVar('g:Lf_CursorBlink', 1)
call s:InitVar('g:Lf_CacheDiretory', $HOME)
call s:InitVar('g:Lf_NeedCacheTime', 1.5)
call s:InitVar('g:Lf_NumberOfCache', 5)
call s:InitVar('g:Lf_UseMemoryCache', 1)
call s:InitVar('g:Lf_IndexTimeLimit', 120)
call s:InitVar('g:Lf_FollowLinks', 0)
call s:InitVar('g:Lf_DelimiterChar', ';')
call s:InitVar('g:Lf_MruFileExclude', [])
call s:InitVar('g:Lf_MruMaxFiles', 100)
call s:InitVar('g:Lf_HighlightIndividual', 1)
call s:InitVar('g:Lf_NumberOfHighlight', 100)
call s:InitVar('g:Lf_WildIgnore',{
            \ 'dir': ['.svn','.git'],
            \ 'file': ['*.sw?','~$*','*.bak','*.exe','*.o','*.so','*.py[co]']
            \})
call s:InitVar('g:Lf_StlSeparator',{
            \ 'left': '►',
            \ 'right': '◄'
            \})
call s:InitVar('g:Lf_StlPalette',{})

let s:Lf_CommandMap = {
            \ '<C-A>':         ['<C-A>'],
            \ '<C-C>':         ['<C-C>'],
            \ '<C-D>':         ['<C-D>'],
            \ '<C-F>':         ['<C-F>'],
            \ '<C-G>':         ['<C-G>'],
            \ '<C-L>':         ['<C-L>'],
            \ '<C-N>':         ['<C-N>'],
            \ '<C-O>':         ['<C-O>'],
            \ '<C-P>':         ['<C-P>'],
            \ '<C-Q>':         ['<C-Q>'],
            \ '<C-R>':         ['<C-R>'],
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
            \ '<BS>':          ['<BS>', '<C-H>'],
            \ '<Tab>':         ['<Tab>'],
            \ '<Del>':         ['<Del>'],
            \ '<Esc>':         ['<Esc>'],
            \ '<Up>':          ['<Up>', '<C-K>'],
            \ '<Down>':        ['<Down>', '<C-J>'],
            \ '<Left>':        ['<Left>'],
            \ '<Right>':       ['<Right>'],
            \ '<Home>':        ['<Home>', '<C-B>'],
            \ '<End>':         ['<End>', '<C-E>'],
            \ '<S-Left>':      ['<S-Left>'],
            \ '<S-Right>':     ['<S-Right>'],
            \ '<LeftMouse>':   ['<LeftMouse>'],
            \ '<RightMouse>':  ['<RightMouse>'],
            \ '<MiddleMouse>': ['<MiddleMouse>'],
            \ '<2-LeftMouse>': ['<2-LeftMouse>'],
            \ '<C-LeftMouse>': ['<C-LeftMouse>', '<C-S>'],
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
                call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? i"))')
            endfor
            let tmp[toupper(key)] = map(value, 'toupper(v:val)')
        endfor
        exec 'let '.a:var.'='.string(tmp)
    endif
endfunction

call s:InitCommandMap('g:Lf_CommandMap', s:Lf_CommandMap)


autocmd BufAdd,BufEnter,BufWritePost * call lfMru#record(expand('<afile>:p')) |
            \ call lfMru#recordBuffer(expand('<abuf>'))

nnoremap <silent> <Plug>LeaderfFileTop :<C-U>call leaderf#startFileExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfFileBottom :<C-U>call leaderf#startFileExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfFileLeft :<C-U>call leaderf#startFileExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfFileRight :<C-U>call leaderf#startFileExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfFileFullScreen :<C-U>call leaderf#startFileExpl('fullScreen')<CR>

nnoremap <silent> <Plug>LeaderfBufferTop :<C-U>call leaderf#startBufExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfBufferBottom :<C-U>call leaderf#startBufExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfBufferLeft :<C-U>call leaderf#startBufExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfBufferRight :<C-U>call leaderf#startBufExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfBufferFullScreen :<C-U>call leaderf#startBufExpl('fullScreen')<CR>

nnoremap <silent> <Plug>LeaderfMruCwdTop :<C-U>call leaderf#startMruExpl('top')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdBottom :<C-U>call leaderf#startMruExpl('bottom')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdLeft :<C-U>call leaderf#startMruExpl('left')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdRight :<C-U>call leaderf#startMruExpl('right')<CR>
nnoremap <silent> <Plug>LeaderfMruCwdFullScreen :<C-U>call leaderf#startMruExpl('fullScreen')<CR>

command! -bar -nargs=? -complete=dir LeaderfFile call leaderf#startFileExpl(g:Lf_WindowPosition, <f-args>)
command! -bar -nargs=? -complete=dir LeaderfFileFullScreen call leaderf#startFileExpl('fullScreen', <f-args>)

command! -bar -nargs=0 LeaderfBuffer call leaderf#startBufExpl(g:Lf_WindowPosition)
command! -bar -nargs=0 LeaderfBufferAll call leaderf#startBufExpl(g:Lf_WindowPosition, 1)
command! -bar -nargs=0 LeaderfMru call leaderf#startMruExpl(g:Lf_WindowPosition)
command! -bar -nargs=0 LeaderfMruCwd call leaderf#startMruExpl(g:Lf_WindowPosition, 1)
command! -bar -nargs=0 LeaderfTag call leaderf#startTagExpl(g:Lf_WindowPosition)


exec 'nnoremap <silent> ' g:Lf_ShortcutF ':<C-U>LeaderfFile<CR>'
exec 'nnoremap <silent> ' g:Lf_ShortcutB ':<C-U>LeaderfBuffer<CR>'


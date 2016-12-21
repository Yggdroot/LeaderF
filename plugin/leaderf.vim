" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
" ============================================================================

if exists('g:leaderf_loaded') || v:version < 700 || &compatible
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
        echoe "Error: LeaderF requires vim compiled with +python or +python3"
        finish
    endif
else
    if g:Lf_PythonVersion == 2
        if has("python")
            let g:Lf_py = "py "
        else
            echoe 'LeaderF Error: has("python") == 0'
            finish
        endif
    else
        if has("python3")
            let g:Lf_py = "py3 "
        else
            echoe 'LeaderF Error: has("python3") == 0'
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
            call filter(tmp, 'v:key !=? key')
            for i in value
                call filter(tmp, '!empty(filter(tmp[v:key], "v:val !=? i"))')
            endfor
            let tmp[toupper(key)] = map(value, 'toupper(v:val)')
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

call s:InitVar('g:Lf_ShortcutF', '<Leader>f')
call s:InitVar('g:Lf_ShortcutB', '<Leader>b')
call s:InitVar('g:Lf_WindowPosition', 1)
call s:InitVar('g:Lf_WindowHeight', 0.5)
call s:InitVar('g:Lf_TabpagePosition', 2)
call s:InitVar('g:Lf_SplitPath', 0)
call s:InitVar('g:Lf_ShowRelativePath', 1)
call s:InitVar('g:Lf_DefaultMode', 0)
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
call s:InitDict('g:Lf_CommandMap', s:Lf_CommandMap)


autocmd BufAdd,BufEnter,BufWritePost * call lfMru#record(expand('<afile>:p')) |
            \ call lfMru#recordBuffer(expand('<abuf>'))


command! -bar -nargs=? -complete=dir Leaderf call leaderf#startFileExpl(<f-args>)
command! -bar -nargs=0 LeaderfBuffer call leaderf#startBufExpl()
command! -bar -nargs=0 LeaderfBufferAll call leaderf#startBufExpl(1)
command! -bar -nargs=0 LeaderfMru call leaderf#startMruExpl()
command! -bar -nargs=0 LeaderfMruCwd call leaderf#startMruExpl(1)
command! -bar -nargs=0 LeaderfTag call leaderf#startTagExpl()

exec 'nnoremap <silent>' g:Lf_ShortcutF ':<C-U>Leaderf<CR>'
exec 'nnoremap <silent>' g:Lf_ShortcutB ':<C-U>LeaderfBuffer<CR>'


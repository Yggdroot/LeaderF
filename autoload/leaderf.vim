" ============================================================================
" File:        leaderf.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
" ============================================================================

exec g:Lf_py "import vim, sys"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "sys.path.insert(0, cwd)"
exec g:Lf_py "from leaderf.bufExpl import *"
exec g:Lf_py "from leaderf.fileExpl import *"
exec g:Lf_py "from leaderf.mruExpl import *"
exec g:Lf_py "from leaderf.tagExpl import *"


function! g:LfFileExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "fileExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "fileExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "fileExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "fileExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "fileExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "fileExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "fileExplManager.refresh()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "fileExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "fileExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "fileExplManager.clearSelections()"<CR>
endfunction

function! g:LfBufExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "bufExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "bufExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "bufExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "bufExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "bufExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "bufExplManager.deleteBuffer(1)"<CR>
    nnoremap <buffer> <silent> D             :exec g:Lf_py "bufExplManager.deleteBuffer()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "bufExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "bufExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "bufExplManager.clearSelections()"<CR>
endfunction

function! g:LfMruExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "mruExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "mruExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "mruExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "mruExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "mruExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "mruExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "mruExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "mruExplManager.deleteMru()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "mruExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "mruExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "mruExplManager.clearSelections()"<CR>
endfunction

function! g:LfTagExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "tagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "tagExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "tagExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "tagExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "tagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "tagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "tagExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "tagExplManager.deleteMru()"<CR>
    nnoremap <buffer> <silent> s             :exec g:Lf_py "tagExplManager.addSelections()"<CR>
    nnoremap <buffer> <silent> a             :exec g:Lf_py "tagExplManager.selectAll()"<CR>
    nnoremap <buffer> <silent> c             :exec g:Lf_py "tagExplManager.clearSelections()"<CR>
endfunction

function! leaderf#LfPy(cmd)
    if v:version > 703
        exec g:Lf_py . a:cmd
    else
        let old_gcr = &gcr
        let old_t_ve = &t_ve
        try
            exec g:Lf_py . a:cmd
        catch /^Vim:Interrupt$/	" catch interrupts (CTRL-C)
            let &gcr = old_gcr
            let &t_ve = old_t_ve
            let obj = substitute(a:cmd,'\..*', '', '')
            exec g:Lf_py . obj .".quit()"
            call getchar(0)
            redraw
            echo
        catch /^Vim\%((\a\+)\)\=:E/
        endtry
    endif
endfunction

function! leaderf#startFileExpl(...)
    if a:0 == 0
        call leaderf#LfPy("fileExplManager.startExplorer()")
    else
        let dir = fnamemodify(a:1.'/',":h:gs?\\?/?")
        call leaderf#LfPy("fileExplManager.startExplorer('".dir."')")
    endif
endfunction

function! leaderf#startBufExpl(...)
    if a:0 == 0
        call leaderf#LfPy("bufExplManager.startExplorer()")
    else
        let arg = a:1 == 0 ? 'False' : 'True'
        call leaderf#LfPy("bufExplManager.startExplorer(".arg.")")
    endif
endfunction

function! leaderf#startMruExpl(...)
    if a:0 == 0
        call leaderf#LfPy("mruExplManager.startExplorer(vim.current.buffer.name)")
    else
        call leaderf#LfPy("mruExplManager.startExplorer(vim.current.buffer.name, f='cwd')")
    endif
endfunction

function! leaderf#startTagExpl(...)
    let a:cmd = "tagExplManager.startExplorer()"
    call leaderf#LfPy(a:cmd)
endfunction

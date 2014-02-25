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


function! g:LfFileExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "fileExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "fileExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "fileExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "fileExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "fileExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "fileExplManager.startExplAction()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "fileExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "fileExplManager.refresh()"<CR>
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
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufExplManager.startExplAction()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "bufExplManager.deleteBuffer(1)"<CR>
    nnoremap <buffer> <silent> D             :exec g:Lf_py "bufExplManager.deleteBuffer()"<CR>
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
    nnoremap <buffer> <silent> i             :exec g:Lf_py "mruExplManager.startExplAction()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "mruExplManager.toggleHelp()"<CR>
    nnoremap <buffer> <silent> d             :exec g:Lf_py "mruExplManager.deleteMru()"<CR>
endfunction

function! leaderf#LfPy(cmd) 
    if v:version > 703
        exec g:Lf_py . a:cmd
    else
        try
            exec g:Lf_py . a:cmd
        catch /^Vim:Interrupt$/	" catch interrupts (CTRL-C)
            set gcr&
            set t_ve&
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
    call leaderf#LfPy("mruExplManager.startExplorer()")
endfunction


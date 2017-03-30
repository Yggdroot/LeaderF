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
exec g:Lf_py "from leaderf.bufTagExpl import *"
exec g:Lf_py "from leaderf.functionExpl import *"
exec g:Lf_py "from leaderf.lineExpl import *"


function! leaderf#fileExplMaps()
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

function! leaderf#bufExplMaps()
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
endfunction

function! leaderf#mruExplMaps()
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

function! leaderf#tagExplMaps()
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
    nnoremap <buffer> <silent> <F5>          :exec g:Lf_py "tagExplManager.refresh()"<CR>
endfunction

function! leaderf#bufTagExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "bufTagExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "bufTagExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "bufTagExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "bufTagExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "bufTagExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "bufTagExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "bufTagExplManager.toggleHelp()"<CR>
endfunction

function! leaderf#functionExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "functionExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "functionExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "functionExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "functionExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "functionExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "functionExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "functionExplManager.toggleHelp()"<CR>
endfunction

function! leaderf#lineExplMaps()
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "lineExplManager.accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py "lineExplManager.accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py "lineExplManager.accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py "lineExplManager.accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py "lineExplManager.quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py "lineExplManager.input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "lineExplManager.toggleHelp()"<CR>
endfunction

function! leaderf#LfPy(cmd)
    exec g:Lf_py . a:cmd
endfunction

function! leaderf#startFileExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("fileExplManager.startExplorer('".a:win_pos."')")
    else
        let dir = fnamemodify(a:1.'/',":h:gs?\\?/?")
        call leaderf#LfPy("fileExplManager.startExplorer('".a:win_pos."','".dir."')")
    endif
endfunction

function! leaderf#startBufExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."')")
    else
        let arg = a:1 == 0 ? 'False' : 'True'
        call leaderf#LfPy("bufExplManager.startExplorer('".a:win_pos."',".arg.")")
    endif
endfunction

function! leaderf#startMruExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."vim.current.buffer.name)")
    else
        call leaderf#LfPy("mruExplManager.startExplorer('".a:win_pos."',"."vim.current.buffer.name, f='cwd')")
    endif
endfunction

function! leaderf#startTagExpl(win_pos, ...)
    call leaderf#LfPy("tagExplManager.startExplorer('".a:win_pos."')")
endfunction

function! leaderf#removeCache(bufNum)
    call leaderf#LfPy("bufTagExplManager.removeCache(".a:bufNum.")")
    call leaderf#LfPy("functionExplManager.removeCache(".a:bufNum.")")
endfunction

function! leaderf#startBufTagExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("bufTagExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("bufTagExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

function! leaderf#startFunctionExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("functionExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("functionExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

function! leaderf#startLineExpl(win_pos, ...)
    if a:0 == 0
        call leaderf#LfPy("lineExplManager.startExplorer('".a:win_pos."')")
    else
        call leaderf#LfPy("lineExplManager.startExplorer('".a:win_pos."',"."1)")
    endif
endfunction

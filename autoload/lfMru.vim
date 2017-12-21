" ============================================================================
" File:        lfMru.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

exec g:Lf_py "import vim, sys, os.path"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "sys.path.insert(0, os.path.join(cwd, 'leaderf', 'python'))"
exec g:Lf_py "from leaderf.mru import *"

function! lfMru#record(name)
    if a:name == '' || !filereadable(a:name)
        return
    endif

    exec g:Lf_py 'mru.saveToCache(r"""'.a:name.'""")'
endfunction

function! lfMru#recordBuffer(bufNum)
    exec g:Lf_py 'mru.setBufferTimestamp('.a:bufNum.')'
endfunction

" ============================================================================
" File:        mru.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     This script is released under the Vim License.
" ============================================================================

exec g:Lf_py "import vim, sys"
exec g:Lf_py "cwd = vim.eval('expand(\"<sfile>:p:h\")')"
exec g:Lf_py "sys.path.insert(0, cwd)"
exec g:Lf_py "from leaderf.mru import *"

function! lfMru#record(name)
    if a:name == '' || &buftype != '' || !filereadable(a:name)
        return
    endif

    exec g:Lf_py 'mru.saveToCache(r"""'.a:name.'""")'
endfunction


" ============================================================================
" File:        Git.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.gitExpl import *"

function! leaderf#Git#Maps(id) abort
    nmapclear <buffer>
    exec g:Lf_py "import ctypes"
    let manager = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "%s.accept()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> o             :exec g:Lf_py "%s.accept()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "%s.accept()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> x             :exec g:Lf_py "%s.accept(''h'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> v             :exec g:Lf_py "%s.accept(''v'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> t             :exec g:Lf_py "%s.accept(''t'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> p             :exec g:Lf_py "%s._previewResult(True)"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> j             :exec g:Lf_py "%s.moveAndPreview(''j'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> k             :exec g:Lf_py "%s.moveAndPreview(''k'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <Up>          :exec g:Lf_py "%s.moveAndPreview(''Up'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <Down>        :exec g:Lf_py "%s.moveAndPreview(''Down'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <PageUp>      :exec g:Lf_py "%s.moveAndPreview(''PageUp'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <PageDown>    :exec g:Lf_py "%s.moveAndPreview(''PageDown'')"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> q             :exec g:Lf_py "%s.quit()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> i             :exec g:Lf_py "%s.input()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py "%s.input()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <F1>          :exec g:Lf_py "%s.toggleHelp()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <C-Up>        :exec g:Lf_py "%s._toUpInPopup()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <C-Down>      :exec g:Lf_py "%s._toDownInPopup()"<CR>', manager)
    exec printf('nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py "%s.closePreviewPopupOrQuit()"<CR>', manager)
endfunction

" direction:
"   0, backward
"   1, forward
function! leaderf#Git#OuterIndent(direction) abort
    let spaces = substitute(getline('.'), '^\(\s*\).*', '\1', '')
    let width = strdisplaywidth(spaces)
    if width == 0
        return 0
    endif
    if a:direction == 0
        let flags = 'sbW'
    else
        let flags = 'sW'
    endif
    return search(printf('^\s\{,%d}\zs\S', width-1), flags)
endfunction

" direction:
"   0, backward
"   1, forward
function! leaderf#Git#SameIndent(direction) abort
    let spaces = substitute(getline('.'), '^\(\s*\).*', '\1', '')
    let width = strdisplaywidth(spaces)
    if a:direction == 0
        let flags = 'sbW'
    else
        let flags = 'sW'
    endif
    if width == 0
        let stopline = 0
    else
        let stopline = search(printf('^\s\{,%d}\zs\S', width-1), flags[1:].'n')
    endif

    noautocmd norm! ^
    call search(printf('^\s\{%d}\zs\S', width), flags, stopline)
endfunction

function! leaderf#Git#SpecificMaps(id) abort
    exec g:Lf_py "import ctypes"
    let manager = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> e :exec g:Lf_py "%s.editCommand()"<CR>', manager)
endfunction

" direction:
"   0, backward
"   1, forward
function! leaderf#Git#OuterBlock(direction) abort
    let column = col('.')
    if column >= match(getline('.'), '\S') + 1
        noautocmd norm! ^
        let column = col('.') - 1
    endif
    let width = (column - 1) / 2 * 2
    if a:direction == 0
        let flags = 'sbW'
    else
        let flags = 'sW'
    endif
    call search(printf('^\s\{%d}\zs\S', width), flags)
endfunction

let s:help = {
            \ "tree": [
            \   "o:             open the folder or open the diffs of current file",
            \   "<CR>:          open the folder or open the diffs of current file",
            \   "<2-LeftMouse>: open the folder or open the diffs of current file",
            \   "O:             open the folder recursively",
            \   "t:             open the diffs in a new tabpage",
            \   "s:             toggle between side by side diff view and unified diff view",
            \   "i:             toggle between ignoring whitespace and not ignoring whitespace",
            \   "p:             preview the diffs, i.e., like 'o', but leave the cursor in the current panel",
            \   "x:             collapse the parent folder",
            \   "X:             collapse all the children of the current folder",
            \   "f:             fuzzy search files",
            \   "F:             resume the previous fuzzy searching",
            \   "m:             show the commit message",
            \   "-:             go to the parent folder",
            \   "+:             go to the next sibling of the parent folder",
            \   "<C-J>:         go to the next sibling of the current folder",
            \   "<C-K>:         go to the previous sibling of the current folder",
            \   "(:             go to the start of the current indent level",
            \   "):             go to the end of the current indent level",
            \   "q:             quit the navigation window",
            \   ":LeaderfGitNavigationOpen",
            \   "               open the navigation window",
            \ ],
            \ "blame": [
            \   "<F1>:          toggle the help",
            \   "o:             show the details of current commit in an explorer page",
            \   "<CR>:          show the details of current commit in an explorer page",
            \   "<2-LeftMouse>: show the details of current commit in an explorer page",
            \   "h:             blame the parent commit of this line",
            \   "l:             go to the previous blame status",
            \   "m:             show the commit message",
            \   "p:             preview the diffs around the current line",
            \   "q:             quit the blame window",
            \ ],
            \}

function s:HelpFilter(winid, key) abort
    if a:key == "\<ESC>" || a:key == "\<F1>"
        call popup_close(a:winid)
        return 1
    elseif a:key == "\<ScrollWheelDown>" || a:key == "\<ScrollWheelUp>"
        return 0
    endif

    return 1
endfunction

function! s:GetRowCol(width, height) abort
    let win_width = &columns
    let win_height = &lines

    let row = (win_height - a:height) / 2 - 1
    let col = (win_width - a:width) / 2

    return {'row': row, 'col': col}
endfunction

function! leaderf#Git#ShowHelp(type) abort
    if has("nvim")
        let borderchars = [
                    \ [g:Lf_PopupBorders[4],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[0],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[5],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[1],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[6],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[2],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[7],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[3],  "Lf_hl_popupBorder"]
                    \]
        let width = 100
        let height = len(s:help[a:type])
        let row_col = s:GetRowCol(width, height)
        let options = {
                    \ "title":           " Help ",
                    \ "title_pos":       "center",
                    \ "relative":        "editor",
                    \ "row":             row_col["row"],
                    \ "col":             row_col["col"],
                    \ "width":           width,
                    \ "height":          height,
                    \ "zindex":          20482,
                    \ "noautocmd":       1,
                    \ "border":          borderchars,
                    \ "style":           "minimal",
                    \}
        let scratch_buffer = nvim_create_buf(v:false, v:true)
        call nvim_buf_set_option(scratch_buffer, 'bufhidden', 'wipe')
        call nvim_buf_set_lines(scratch_buffer, 0, -1, v:false, s:help[a:type])
        call nvim_buf_set_option(scratch_buffer, 'modifiable', v:false)
        let id = nvim_open_win(scratch_buffer, 1, options)
        call nvim_win_set_option(id, 'winhighlight', 'Normal:Lf_hl_popup_window')
        call win_execute(id, 'call matchadd("Special", ''^.\{-}\(:\)\@='')')
        call win_execute(id, 'call matchadd("Special", ''^:\w\+'')')
        call win_execute(id, 'call matchadd("Comment", ''\(^.\{-1,}:\s*\)\@<=.*'')')
        call win_execute(id, 'call matchadd("Comment", ''\(^\s\+\)\@<=.*'')')
        call win_execute(id, 'nnoremap <buffer> <silent> <ESC> <C-W>c')
        call win_execute(id, 'nnoremap <buffer> <silent> <F1> <C-W>c')
    else
        let options = {
                    \ "title":           " Help ",
                    \ "zindex":          20482,
                    \ "scrollbar":       1,
                    \ "padding":         [0, 0, 0, 0],
                    \ "border":          [1, 1, 1, 1],
                    \ "borderchars":     g:Lf_PopupBorders,
                    \ "borderhighlight": ["Lf_hl_popupBorder"],
                    \ "filter":          "s:HelpFilter",
                    \ "mapping":         0,
                    \}

        let id = popup_create(s:help[a:type], options)
        call win_execute(id, 'setlocal wincolor=Lf_hl_popup_window')
        call win_execute(id, 'call matchadd("Special", ''^.\{-}\(:\)\@='')')
        call win_execute(id, 'call matchadd("Special", ''^:\w\+'')')
        call win_execute(id, 'call matchadd("Comment", ''\(^.\{-1,}:\s*\)\@<=.*'')')
        call win_execute(id, 'call matchadd("Comment", ''\(^\s\+\)\@<=.*'')')
    endif
endfunction


function! leaderf#Git#CloseFloatWinMouse() abort
    if exists("b:blame_cursorline") && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == b:lf_blame_winid && b:blame_cursorline != pos["line"]
            if exists("b:commit_msg_winid") && winbufnr(b:commit_msg_winid) != -1
                call nvim_win_close(b:commit_msg_winid, 1)
            endif
        endif
    endif
    if exists("b:lf_blame_preview_cursorline") && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == b:lf_blame_winid && b:lf_blame_preview_cursorline != pos["line"]
            if exists("b:lf_preview_winid") && winbufnr(b:lf_preview_winid) != -1
                call nvim_win_close(b:lf_preview_winid, 1)
            endif
        endif
    endif
endfunction

function! leaderf#Git#ShowCommitMessage(message) abort
    let b:blame_cursorline = line('.')
    let b:lf_blame_winid = win_getid()
    if has("nvim")
        let borderchars = [
                    \ [g:Lf_PopupBorders[4],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[0],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[5],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[1],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[6],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[2],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[7],  "Lf_hl_popupBorder"],
                    \ [g:Lf_PopupBorders[3],  "Lf_hl_popupBorder"]
                    \]
        let width = 80
        let height = len(a:message)
        let row_col = s:GetRowCol(width, height)
        let options = {
                    \ "title":           " Commit Message ",
                    \ "title_pos":       "center",
                    \ "relative":        "editor",
                    \ "row":             row_col["row"],
                    \ "col":             row_col["col"],
                    \ "width":           width,
                    \ "height":          height,
                    \ "zindex":          20482,
                    \ "noautocmd":       1,
                    \ "border":          borderchars,
                    \ "style":           "minimal",
                    \}
        let scratch_buffer = nvim_create_buf(v:false, v:true)
        call nvim_buf_set_option(scratch_buffer, 'bufhidden', 'wipe')
        call nvim_buf_set_lines(scratch_buffer, 0, -1, v:false, a:message)
        call nvim_buf_set_option(scratch_buffer, 'modifiable', v:false)
        if exists("b:commit_msg_winid") && winbufnr(b:commit_msg_winid) != -1
            call nvim_win_close(b:commit_msg_winid, 1)
        endif
        let b:commit_msg_winid = nvim_open_win(scratch_buffer, 0, options)
        call nvim_win_set_option(b:commit_msg_winid, 'winhighlight', 'Normal:Lf_hl_popup_window')
        call win_execute(b:commit_msg_winid, 'nnoremap <buffer> <silent> <ESC> <C-W>c')
        call win_execute(b:commit_msg_winid, 'setlocal filetype=git')
    else
        let maxheight = &lines / 3
        let options = {
                    \ "title":           " Commit Message ",
                    \ "maxwidth":        80,
                    \ "minwidth":        80,
                    \ "maxheight":       maxheight,
                    \ "minheight":       maxheight,
                    \ "zindex":          20482,
                    \ "scrollbar":       1,
                    \ "padding":         [0, 0, 0, 0],
                    \ "border":          [1, 1, 1, 1],
                    \ "borderchars":     g:Lf_PopupBorders,
                    \ "borderhighlight": ["Lf_hl_popupBorder"],
                    \ "filter":          "leaderf#Git#ShowMsgFilter",
                    \ "mapping":         0,
                    \}

        let id = popup_create(a:message, options)
        call win_execute(id, 'setlocal wincolor=Lf_hl_popup_window')
        call win_execute(id, 'setlocal filetype=git')
    endif
endfunction

function leaderf#Git#PreviewFilter(winid, key) abort
    if a:key == "\<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            if pos.winid != a:winid
                call popup_close(a:winid)
            endif
        endif
    endif

    if a:key == "\<ESC>"
        call popup_close(a:winid)
        return 1
    elseif a:key == "j" || a:key == "k"
        call popup_close(a:winid)
        return 0
    elseif a:key == "\<CR>"
        call popup_close(a:winid)
        call feedkeys("\<CR>", 't')
        return 1
    elseif a:key == "q"
        call popup_close(a:winid)
        call feedkeys("q", 't')
        return 1
    elseif a:key == "h"
        let manager_id = getbufvar(winbufnr(a:winid), 'lf_blame_manager_id')
        exec g:Lf_py "import ctypes"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.blamePrevious()", manager_id)
        return 1
    elseif a:key == "l"
        let manager_id = getbufvar(winbufnr(a:winid), 'lf_blame_manager_id')
        exec g:Lf_py "import ctypes"
        exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.blameNext()", manager_id)
        return 1
    elseif a:key == "\<C-J>"
        call win_execute(a:winid, "norm! j")
        return 1
    elseif a:key == "\<C-K>"
        call win_execute(a:winid, "norm! k")
        return 1
    else
        return leaderf#popupModePreviewFilter(a:winid, a:key)
    endif

    return 1
endfunction

function leaderf#Git#ShowMsgFilter(winid, key) abort
    if a:key == "\<LeftMouse>"
        if exists("*getmousepos")
            let pos = getmousepos()
            if pos.winid != a:winid
                call popup_close(a:winid)
            endif
        endif
    endif

    if a:key == "\<ESC>"
        call popup_close(a:winid)
        return 1
    elseif a:key == "j" || a:key == "k"
        call popup_close(a:winid)
        return 0
    elseif a:key == "\<CR>"
        call popup_close(a:winid)
        call feedkeys("\<CR>", 't')
        return 1
    elseif a:key == "\<C-J>"
        call win_execute(a:winid, "norm! j")
        return 1
    elseif a:key == "\<C-K>"
        call win_execute(a:winid, "norm! k")
        return 1
    else
        return leaderf#popupModePreviewFilter(a:winid, a:key)
    endif

    return 1
endfunction

function! leaderf#Git#TreeViewMaps(id) abort
    exec g:Lf_py "import ctypes"
    let tree_view = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <silent> X         :exec g:Lf_py "%s.collapseChildren()"<CR>', tree_view)
    nnoremap <buffer> <silent> <F1>          :call leaderf#Git#ShowHelp("tree")<CR>
    nnoremap <buffer> <silent> -             :call leaderf#Git#OuterIndent(0)<CR>
    nnoremap <buffer> <silent> +             :call leaderf#Git#OuterIndent(1)<CR>
    nnoremap <buffer> <silent> <C-K>         :call leaderf#Git#SameIndent(0)<CR>
    nnoremap <buffer> <silent> <C-J>         :call leaderf#Git#SameIndent(1)<CR>
    nnoremap <buffer> <silent> (             :call leaderf#Git#OuterBlock(0)<CR>
    nnoremap <buffer> <silent> )             :call leaderf#Git#OuterBlock(1)<CR>
endfunction

function! leaderf#Git#CollapseParent(navigation_panel) abort
    if leaderf#Git#OuterIndent(0) != 0
        exec g:Lf_py printf("%s.openDiffView(False)", a:navigation_panel)
    endif
endfunction

function! leaderf#Git#NavigationPanelMaps(id) abort
    exec g:Lf_py "import ctypes"
    let navigation_panel = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> o             :exec g:Lf_py "%s.openDiffView(False)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "%s.openDiffView(False)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "%s.openDiffView(False)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> O             :exec g:Lf_py "%s.openDiffView(True)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> t             :exec g:Lf_py "%s.openDiffView(False, mode=''t'')"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> s             :exec g:Lf_py "%s.toggleDiffViewMode()"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> i             :exec g:Lf_py "%s.toggleIgnoreWhitespace()"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> p             :exec g:Lf_py "%s.openDiffView(False, preview=True)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> x             :call leaderf#Git#CollapseParent("%s")<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> f             :exec g:Lf_py "%s.fuzzySearch()"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> F             :exec g:Lf_py "%s.fuzzySearch(True)"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> m             :exec g:Lf_py "%s.showCommitMessage()"<CR>', navigation_panel)
    exec printf('nnoremap <buffer> <silent> <LeftRelease> <LeftRelease>:exec g:Lf_py "%s.selectOption()"<CR>', navigation_panel)
    nnoremap <buffer> <silent> q             :q<CR>
endfunction

function! leaderf#Git#CloseFloatWin() abort
    if exists("b:commit_msg_winid") && winbufnr(b:commit_msg_winid) != -1
        call nvim_win_close(b:commit_msg_winid, 1)
    endif
    if exists("b:lf_preview_winid") && winbufnr(b:lf_preview_winid) != -1
        call nvim_win_close(b:lf_preview_winid, 1)
    endif
endfunction

function! leaderf#Git#BlameMaps(id) abort
    exec g:Lf_py "import ctypes"
    let blame_manager = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> o             :exec g:Lf_py "%s.open()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "%s.open()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "%s.open()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> h             :exec g:Lf_py "%s.blamePrevious()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> l             :exec g:Lf_py "%s.blameNext()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> m             :exec g:Lf_py "%s.showCommitMessage()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> p             :exec g:Lf_py "%s.preview()"<CR>', blame_manager)
    exec printf('nnoremap <buffer> <silent> q             :exec g:Lf_py "%s.quit()"<CR>', blame_manager)
    if has("nvim")
        nnoremap <buffer> <silent> j         :call leaderf#Git#CloseFloatWin()<CR>j
        nnoremap <buffer> <silent> k         :call leaderf#Git#CloseFloatWin()<CR>k
        nnoremap <buffer> <silent> <ESC>     :call leaderf#Git#CloseFloatWin()<CR>
        nnoremap <buffer> <silent> <LeftMouse>     :call leaderf#Git#CloseFloatWinMouse()<CR><LeftMouse>
    endif
    nnoremap <buffer> <silent> <F1>          :call leaderf#Git#ShowHelp("blame")<CR>
endfunction

function! leaderf#Git#TimerCallback(manager_id, id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._callback(bang=True)", a:manager_id)
endfunction

function! leaderf#Git#WriteBuffer(view_id, id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.writeBuffer()", a:view_id)
endfunction

function! leaderf#Git#Cleanup(owner_id, id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.cleanup()", a:owner_id)
endfunction

function! leaderf#Git#Suicide(view_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.suicide()", a:view_id)
endfunction

function! leaderf#Git#Bufhidden(view_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.bufHidden()", a:view_id)
endfunction

function! leaderf#Git#UpdateInlineBlame(manager_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.updateInlineBlame()", a:manager_id)
endfunction

function! leaderf#Git#StartInlineBlame() abort
    Leaderf git blame --inline
endfunction

function! leaderf#Git#DisableInlineBlame() abort
    if !exists("g:lf_blame_manager_id") || g:lf_blame_manager_id == 0
        return
    endif

    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.disableInlineBlame()", g:lf_blame_manager_id)
endfunction

function! leaderf#Git#RestartInlineBlame() abort
    call leaderf#Git#DisableInlineBlame()
    call leaderf#Git#StartInlineBlame()
endfunction

function! leaderf#Git#HideInlineBlame(manager_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.hideInlineBlame()", a:manager_id)
endfunction

function! leaderf#Git#ShowInlineBlame(manager_id) abort
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.showInlineBlame()", a:manager_id)
endfunction

function! leaderf#Git#ToggleInlineBlame() abort
    if !exists("g:Lf_git_inline_blame_enabled") || g:Lf_git_inline_blame_enabled == 0
        call leaderf#Git#StartInlineBlame()
    else
        call leaderf#Git#DisableInlineBlame()
    endif
endfunction

function! leaderf#Git#ClearMatches() abort
    for m in b:Leaderf_matches
        call matchdelete(m.id)
    endfor
endfunction

function! leaderf#Git#SetMatches() abort
    call setmatches(b:Leaderf_matches)
endfunction

function! leaderf#Git#Commands() abort
    if !exists("g:Lf_GitCommands")
        let g:Lf_GitCommands = [
                    \ {"Leaderf git diff":                         "fuzzy search and view the diffs"},
                    \ {"Leaderf git diff --side-by-side":          "fuzzy search and view the side-by-side diffs"},
                    \ {"Leaderf git diff --side-by-side --current-file":"view the side-by-side diffs of the current file"},
                    \ {"Leaderf git diff --explorer":              "view the diffs in an explorer tabpage"},
                    \ {"Leaderf git diff --explorer --unified":    "view the diffs in an explorer tabpage, the diffs is shown in unified view"},
                    \ {"Leaderf git diff --directly":              "view the diffs directly"},
                    \ {"Leaderf git diff --directly --position right":"view the diffs in the right split window"},
                    \ {"Leaderf git diff --cached":                "fuzzy search and view `git diff --cached`"},
                    \ {"Leaderf git diff --cached --side-by-side": "fuzzy search and view the side-by-side diffs of `git diff --cached`"},
                    \ {"Leaderf git diff --cached --explorer":     "view `git diff --cached` in an explorer tabpage"},
                    \ {"Leaderf git diff --cached --directly":     "view `git diff --cached` directly"},
                    \ {"Leaderf git diff --cached --directly --position right": "view `git diff --cached` directly in the right split window"},
                    \ {"Leaderf git diff HEAD":                    "fuzzy search and view `git diff HEAD`"},
                    \ {"Leaderf git diff HEAD --side-by-side":     "fuzzy search and view the side-by-side diffs of `git diff HEAD`"},
                    \ {"Leaderf git diff HEAD --explorer":         "view `git diff HEAD` in an explorer tabpage"},
                    \ {"Leaderf git diff HEAD --directly":         "view `git diff HEAD` directly"},
                    \ {"Leaderf git diff HEAD --directly --position right":     "view `git diff HEAD` directly in the right split window"},
                    \ {"Leaderf git log":                          "fuzzy search and view the log"},
                    \ {"Leaderf git log --directly":               "view the logs directly"},
                    \ {"Leaderf git log --explorer":               "fuzzy search and view the log in an explorer tabpage"},
                    \ {"Leaderf git log --explorer --unified":     "fuzzy search and view the log in an explorer tabpage, the diffs is shown in unified view"},
                    \ {"Leaderf git log --explorer --navigation-position bottom": "specify the position of navigation panel in explorer tabpage"},
                    \ {"Leaderf git log --current-file":           "fuzzy search and view the log of current file"},
                    \ {"Leaderf git log --current-file --explorer":"fuzzy search and view the log of current file in explorer tabpage"},
                    \ {"Leaderf git log --current-line":           "fuzzy search and view the log of current line"},
                    \ {"Leaderf git log --current-line --explorer":"fuzzy search and view the log of current line in explorer tabpage"},
                    \ {"Leaderf git blame":                        "git blame current file"},
                    \ {"Leaderf git blame -w":                     "ignore whitespace when git blame current file"},
                    \ {"Leaderf git blame --date relative":        "show relative date when git blame current file"},
                    \ {"LeaderfGitInlineBlameEnable":              "Enable inline blame. This command is a shortcut of `:Leaderf git blame --inline`."},
                    \ {"LeaderfGitInlineBlameDisable":             "Disable inline blame."},
                    \ {"LeaderfGitInlineBlameToggle":              "Toggle inline blame."},
                    \ {"LeaderfGitInlineBlameUpdate":              "If the file is updated in the git repository, we need to use this command to update the inline blame."},
                    \ ]
    endif

    return g:Lf_GitCommands
endfunction

function! leaderf#Git#NormalModeFilter(winid, key) abort
    let key = leaderf#RemapKey(g:Lf_PyEval("id(gitExplManager)"), get(g:Lf_KeyMap, a:key, a:key))

    if key ==# "e"
        exec g:Lf_py "gitExplManager.editCommand()"
    else
        return leaderf#NormalModeFilter(g:Lf_PyEval("id(gitExplManager)"), a:winid, a:key)
    endif

    return 1
endfunction

function! leaderf#Git#DefineSyntax() abort
    syntax region Lf_hl_gitStat start=/^---$/ end=/^ \d\+ files\? changed,/
    syn match Lf_hl_gitStatPath /^ \S*\%(\s*|\s*\d\+\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /^ \S*\%(\s*|\s*Bin\%( \d\+ -> \d\+ bytes\?\)\?$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /^ \S*\%( => \S*\s*|\s*\d\+\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /^ \S*\%( => \S*\s*|\s*Bin\%( \d\+ -> \d\+ bytes\?\)\?$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /\%(^ \S* => \)\@<=\S*\%(\s*|\s*\d\+\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /\%(^ \S* => \)\@<=\S*\%(\s*|\s*Bin\%( \d\+ -> \d\+ bytes\?\)\?$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatNumber /\%(^ \S*\%( => \S*\)\?\s*|\s*\)\@<=\d\+\%(\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatNumber /\%(^ \S*\%( => \S*\)\?\s*|\s*Bin \)\@<=\d\+ -> \d\+\%( bytes\?$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPlus /\%(^ \S*\%( => \S*\)\?\s*|\s*\d\+\s*\)\@<=+*\%(-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatMinus /\%(^ \S*\%( => \S*\)\?\s*|\s*\d\+\s*+*\)\@<=-*$/ display containedin=Lf_hl_gitStat contained
    syn match gitIdentityHeader /^Committer:/ contained containedin=gitHead nextgroup=gitIdentity skipwhite contains=@NoSpell
endfunction

function! leaderf#Git#DiffOff(win_ids) abort
    for id in a:win_ids
        call win_execute(id, "diffoff")
    endfor
endfunction

function! leaderf#Git#FoldExpr() abort
    return has_key(b:Leaderf_fold_ranges_dict, v:lnum)
endfunction

function! leaderf#Git#SetLineNumberWin(line_num_content, buffer_num) abort
    if len(a:line_num_content) == 0
        return
    endif

    let line = a:line_num_content[0]
    let line_len = strlen(line)

    let hi_line_num = get(g:, 'Lf_GitHightlightLineNumber', 1)
    let delimiter = get(g:, 'Lf_GitDelimiter', '│')
    let delimiter_len = len(delimiter)
    let ns_id = nvim_create_namespace('LeaderF')

    for i in range(len(a:line_num_content))
        let line = a:line_num_content[i]
        let last_part = strcharpart(line, line_len - (delimiter_len + 1), 2)

        if last_part[0] == '-'
            if hi_line_num == 1
                let hl_group1 = "Lf_hl_gitDiffDelete"
            else
                let hl_group1 = "Lf_hl_LineNr"
            endif
            let hl_group2 = "Lf_hl_gitDiffDelete"
            let first_part = strcharpart(line, 0, line_len - (delimiter_len + 1))
            call nvim_buf_set_extmark(a:buffer_num, ns_id, i, 0, {'virt_text': [[first_part, hl_group1], [last_part, hl_group2]], 'virt_text_pos': 'inline'})
        elseif last_part[0] == '+'
            if hi_line_num == 1
                let hl_group1 = "Lf_hl_gitDiffAdd"
            else
                let hl_group1 = "Lf_hl_LineNr"
            endif
            let hl_group2 = "Lf_hl_gitDiffAdd"
            let first_part = strcharpart(line, 0, line_len - (delimiter_len + 1))
            call nvim_buf_set_extmark(a:buffer_num, ns_id, i, 0, {'virt_text': [[first_part, hl_group1], [last_part, hl_group2]], 'virt_text_pos': 'inline'})
        else
            let hl_group = "Lf_hl_LineNr"
            call nvim_buf_set_extmark(a:buffer_num, ns_id, i, 0, {'virt_text': [[line, hl_group]], 'virt_text_pos': 'inline'})
        endif
    endfor
endfunction

function! leaderf#Git#SignPlace(added_line_nums, deleted_line_nums, buf_number) abort
    for i in a:added_line_nums
        call sign_place(0, "LeaderF", "Leaderf_diff_add", a:buf_number, {'lnum': i})
    endfor

    for i in a:deleted_line_nums
        call sign_place(0, "LeaderF", "Leaderf_diff_delete", a:buf_number, {'lnum': i})
    endfor
endfunction

function! leaderf#Git#PreviousChange(tag) abort
    if a:tag == 0
        let n = line('.')
        let low = 0
        let high = len(b:lf_change_start_lines)
        while low < high
            let mid = (low + high)/2
            if b:lf_change_start_lines[mid] < n
                let low = mid + 1
            else
                let high = mid
            endif
        endwhile

        if low - 1 >= 0
            exec printf("norm! %dG0", b:lf_change_start_lines[low - 1])
        endif
    else
        call s:PreviousChange()
    endif
endfunction

function! s:PreviousChange() abort
exec g:Lf_py "<< EOF"
cur_line = vim.current.window.cursor[0]
flag = False
for i, line in enumerate(reversed(vim.current.buffer[:cur_line])):
    if len(line) > 0 and line[0] in '-+':
        if flag == True:
            vim.current.window.cursor = [cur_line - i, 0]
            break
    else:
        flag = True

EOF
endfunction

function! leaderf#Git#NextChange(tag) abort
    if a:tag == 0
        let n = line('.')
        let low = 0
        let size = len(b:lf_change_start_lines)
        let high = size
        while low < high
            let mid = (low + high)/2
            if b:lf_change_start_lines[mid] <= n
                let low = mid + 1
            else
                let high = mid
            endif
        endwhile

        if high < size
            exec printf("norm! %dG0", b:lf_change_start_lines[high])
        endif
    else
        call s:NextChange()
    endif
endfunction

function! s:NextChange() abort
exec g:Lf_py "<< EOF"
cur_line = vim.current.window.cursor[0] - 1
flag = False
for i, line in enumerate(vim.current.buffer[cur_line:], cur_line):
    if len(line) > 0 and line[0] in '-+':
        if flag == True:
            vim.current.window.cursor = [i+1, 0]
            break
    else:
        flag = True

EOF
endfunction

function! s:GoToFile(file_name) abort
    if !filereadable(a:file_name)
        echohl WarningMsg
        echo a:file_name .. " does not exist."
        echohl None
        return
    endif

    let buffer_num = bufnr(fnamemodify(a:file_name, ':p'))
    if buffer_num == -1
        exec "tabedit " . a:file_name
    else
        let buf_ids = win_findbuf(buffer_num)
        if len(buf_ids) == 0
            exec "tabedit " . a:file_name
        else
            call win_gotoid(buf_ids[0])
        endif
    endif
endfunction

function! leaderf#Git#EditFile(tag) abort
    if a:tag == 0
        if !filereadable(b:lf_git_buffer_name)
            echohl WarningMsg
            echo b:lf_git_buffer_name .. " does not exist."
            echohl None
            return
        endif

        let start_line_num = line('.')
        let line_num_content = b:lf_git_line_num_content
        if len(line_num_content) == 0
            return
        endif

        let line = line_num_content[0]
        let line_len = strlen(line)

        let delimiter = get(g:, 'Lf_GitDelimiter', '│')
        let delimiter_len = len(delimiter)

        let buffer_num = bufnr(b:lf_git_buffer_name)
        if buffer_num == -1
            exec "tabedit " . b:lf_git_buffer_name
        else
            let buf_ids = win_findbuf(buffer_num)
            if len(buf_ids) == 0
                exec "tabedit " . b:lf_git_buffer_name
            else
                call win_gotoid(buf_ids[0])
            endif
        endif

        let i = start_line_num - 1
        while i < len(line_num_content)
            let line = line_num_content[i]
            let last_part = strcharpart(line, line_len - (delimiter_len + 1), 2)
            if last_part[0] != '-'
                let numbers = split(line, ' ')
                if len(numbers) == 2
                    let line_num = numbers[0]
                else
                    let line_num = numbers[1]
                endif
                exec "norm! " . line_num . "G"
                return
            endif
            let i += 1
        endwhile
        norm! G
    elseif a:tag == 1
        let cur_line = getline('.')
        if cur_line =~ '^diff --git a/\S* b/\S*'
            let file_name = split(getline('.'))[3][2:]
            call s:GoToFile(file_name)
            return
        endif

        let diff_line_num = search('^diff --git a/\S* b/\S*', 'bnW')
        if diff_line_num == 0
            return
        endif
        let diff_line = getline(diff_line_num)
        let file_name = split(diff_line)[3][2:]
        let at_line_num = search('^@@', 'bnW')
        if at_line_num < diff_line_num || cur_line =~ '^@@'
            call s:GoToFile(file_name)
            return
        endif

        let start_line_num = matchstr(getline(at_line_num), '+\zs\(\d\+\)')
        let i = at_line_num + 1
        let cur_line_num = line('.')
        let delta = 0
        while i <= cur_line_num
            if getline(i) !~ '^-'
                let delta += 1
            endif
            let i += 1
        endwhile

        if cur_line !~ '^-'
            let line_num = start_line_num + delta - 1
        else
            let line_num = start_line_num + delta
        endif
        call s:GoToFile(file_name)
        exec "norm! " . line_num . "G"
        setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!
    else
        let file_name = b:lf_git_buffer_name
        if b:lf_git_diff_win_pos == 1
            let line_num = line('.')
        else
            let line_num = getcurpos(b:lf_git_diff_win_id)[1]
        endif
        call s:GoToFile(file_name)
        exec "norm! " . line_num . "G"
        setlocal cursorline! | redraw | sleep 150m | setlocal cursorline!
    endif
endfunction

function! leaderf#Git#OpenNavigationPanel() abort
    if !exists("b:lf_explorer_page_id") || b:lf_explorer_page_id == 0
        return
    endif

    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.openNavigationPanel()", b:lf_explorer_page_id)
endfunction

function! leaderf#Git#RemoveExtmarks(buffer_num) abort
    let ns_id_0 = nvim_create_namespace('LeaderF_Git_Blame_0')
    for [mark_id, row, col] in nvim_buf_get_extmarks(a:buffer_num, ns_id_0, 0, -1, {})
        call nvim_buf_del_extmark(a:buffer_num, ns_id_0, mark_id)
    endfor

    let ns_id_1 = nvim_create_namespace('LeaderF_Git_Blame_1')
    for [mark_id, row, col] in nvim_buf_get_extmarks(a:buffer_num, ns_id_1, 0, -1, {})
        call nvim_buf_del_extmark(a:buffer_num, ns_id_1, mark_id)
    endfor
endfunction

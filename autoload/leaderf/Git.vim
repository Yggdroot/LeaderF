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

function! leaderf#Git#Maps(id)
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
function! leaderf#Git#OuterIndent(direction)
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
function! leaderf#Git#SameIndent(direction)
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

function! leaderf#Git#SpecificMaps(id)
    exec g:Lf_py "import ctypes"
    let manager = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> e :exec g:Lf_py "%s.editCommand()"<CR>', manager)
endfunction

" direction:
"   0, backward
"   1, forward
function! leaderf#Git#OuterBlock(direction)
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
            \ ],
            \ "blame": [
            \   "o:             show the details of current commit in an explorer page",
            \   "<CR>:          show the details of current commit in an explorer page",
            \   "<2-LeftMouse>: show the details of current commit in an explorer page",
            \   "h:             blame the parent commit",
            \   "l:             go to the previous blame status",
            \   "m:             show the commit message",
            \ ],
            \}

function s:HelpFilter(winid, key)
    if a:key == "\<ESC>" || a:key == "\<F1>"
        call popup_close(a:winid)
        return 1
    elseif a:key == "\<ScrollWheelDown>" || a:key == "\<ScrollWheelUp>"
        return 0
    endif

    return 1
endfunction

function! s:GetRowCol(width, height)
    let win_width = &columns
    let win_height = &lines

    let row = (win_height - a:height) / 2 - 1
    let col = (win_width - a:width) / 2

    return {'row': row, 'col': col}
endfunction

function! leaderf#Git#ShowHelp(type)
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
        call win_execute(id, 'call matchadd("Comment", ''\(^.\{-}:\s*\)\@<=.*'')')
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
        call win_execute(id, 'call matchadd("Comment", ''\(^.\{-}:\s*\)\@<=.*'')')
    endif
endfunction


function! leaderf#Git#CloseCommitMessageWin()
    if exists("b:blame_cursorline") && exists("*getmousepos")
        let pos = getmousepos()
        if pos.winid == b:blame_winid && b:blame_cursorline != pos["line"]
            if exists("b:commit_msg_winid") && winbufnr(b:commit_msg_winid) != -1
                call nvim_win_close(b:commit_msg_winid, 1)
            endif
        endif
    endif
endfunction

function s:CommitMessageFilter(winid, key)
    if a:key == "\<ESC>"
        call popup_close(a:winid)
        return 1
    elseif a:key == "j" || a:key == "k"
        call popup_close(a:winid)
        return 0
    elseif a:key == "\<LeftMouse>"
        if exists("b:blame_cursorline") && exists("*getmousepos")
            let pos = getmousepos()
            if pos.winid == b:blame_winid && b:blame_cursorline != pos["line"]
                call popup_close(a:winid)
            endif
        endif
        return 0
    elseif a:key == "\<ScrollWheelDown>" || a:key == "\<ScrollWheelUp>"
        return 0
    endif

    return 1
endfunction

function! leaderf#Git#ShowCommitMessage(message)
    let b:blame_cursorline = line('.')
    let b:blame_winid = win_getid()
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
        let options = {
                    \ "title":           " Commit Message ",
                    \ "zindex":          20482,
                    \ "scrollbar":       1,
                    \ "padding":         [0, 0, 0, 0],
                    \ "border":          [1, 1, 1, 1],
                    \ "borderchars":     g:Lf_PopupBorders,
                    \ "borderhighlight": ["Lf_hl_popupBorder"],
                    \ "filter":          "s:CommitMessageFilter",
                    \ "mapping":         0,
                    \}

        let id = popup_create(a:message, options)
        call win_execute(id, 'setlocal wincolor=Lf_hl_popup_window')
        call win_execute(id, 'setlocal filetype=git')
    endif
endfunction

function! leaderf#Git#TreeViewMaps(id)
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

function! leaderf#Git#CollapseParent(explorer_page)
    if leaderf#Git#OuterIndent(0) != 0
        exec g:Lf_py printf("%s.open(False)", a:explorer_page)
    endif
endfunction

function! leaderf#Git#ExplorerMaps(id)
    exec g:Lf_py "import ctypes"
    let explorer_page = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> o             :exec g:Lf_py "%s.open(False)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "%s.open(False)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "%s.open(False)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> O             :exec g:Lf_py "%s.open(True)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> t             :exec g:Lf_py "%s.open(False, mode=''t'')"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> p             :exec g:Lf_py "%s.open(False, preview=True)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> x             :call leaderf#Git#CollapseParent("%s")<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> f             :exec g:Lf_py "%s.fuzzySearch()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> F             :exec g:Lf_py "%s.fuzzySearch(True)"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> m             :exec g:Lf_py "%s.showCommitMessage()"<CR>', explorer_page)
    nnoremap <buffer> <silent> q             :q<CR>
endfunction

function! leaderf#Git#BlameMaps(id)
    exec g:Lf_py "import ctypes"
    let explorer_page = printf("ctypes.cast(%d, ctypes.py_object).value", a:id)
    exec printf('nnoremap <buffer> <silent> o             :exec g:Lf_py "%s.open()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py "%s.open()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> <CR>          :exec g:Lf_py "%s.open()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> h             :exec g:Lf_py "%s.blamePrevious()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> l             :exec g:Lf_py "%s.blameNext()"<CR>', explorer_page)
    exec printf('nnoremap <buffer> <silent> m             :exec g:Lf_py "%s.showCommitMessage()"<CR>', explorer_page)
    if has("nvim")
        nnoremap <buffer> <silent> j         :silent! call nvim_win_close(b:commit_msg_winid, 1)<CR>j
        nnoremap <buffer> <silent> k         :silent! call nvim_win_close(b:commit_msg_winid, 1)<CR>k
        nnoremap <buffer> <silent> <ESC>     :silent! call nvim_win_close(b:commit_msg_winid, 1)<CR>
        nnoremap <buffer> <silent> <LeftMouse>     :call leaderf#Git#CloseCommitMessageWin()<CR><LeftMouse>
    endif
    nnoremap <buffer> <silent> <F1>          :call leaderf#Git#ShowHelp("blame")<CR>
    nnoremap <buffer> <silent> q             :bwipe<CR>
endfunction

function! leaderf#Git#TimerCallback(manager_id, id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value._callback(bang=True)", a:manager_id)
endfunction

function! leaderf#Git#WriteBuffer(view_id, id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.writeBuffer()", a:view_id)
endfunction

function! leaderf#Git#Cleanup(owner_id, id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.cleanup()", a:owner_id)
endfunction

function! leaderf#Git#Suicide(view_id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.suicide()", a:view_id)
endfunction

function! leaderf#Git#Bufhidden(view_id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.bufHidden()", a:view_id)
endfunction

function! leaderf#Git#CleanupExplorerPage(view_id)
    exec g:Lf_py "import ctypes"
    exec g:Lf_py printf("ctypes.cast(%d, ctypes.py_object).value.cleanupExplorerPage()", a:view_id)
endfunction

function! leaderf#Git#Commands()
    if !exists("g:Lf_GitCommands")
        let g:Lf_GitCommands = [
                    \ {"Leaderf git diff":                         "fuzzy search and view the diffs"},
                    \ {"Leaderf git diff --side-by-side":          "fuzzy search and view the side-by-side diffs"},
                    \ {"Leaderf git diff --side-by-side --current-file":"view the side-by-side diffs of the current file"},
                    \ {"Leaderf git diff --explorer":              "view the diffs in an explorer tabpage"},
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
                    \ {"Leaderf git log --explorer --navigation-position bottom": "specify the position of navigation panel in explorer tabpage"},
                    \ {"Leaderf git log --current-file":           "fuzzy search and view the log of current file"},
                    \ {"Leaderf git log --current-file --explorer":"fuzzy search and view the log of current file in explorer tabpage"},
                    \ {"Leaderf git blame":                        "git blame current file"},
                    \ {"Leaderf git blame -w":                     "ignore whitespace when git blame current file"},
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
    syn match Lf_hl_gitStatPath /^ \S*\%(\s*|\s*Bin \d\+ -> \d\+ bytes\?$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /^ \S*\%( => \S*\s*|\s*\d\+\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
    syn match Lf_hl_gitStatPath /\%(^ \S* => \)\@<=\S*\%(\s*|\s*\d\+\s*+*-*$\)\@=/ display containedin=Lf_hl_gitStat contained
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

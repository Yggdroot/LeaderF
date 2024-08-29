" ============================================================================
" File:        colorscheme.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

let s:matchModeMap = {
            \   'NameOnly': 'Lf_hl_popup_nameOnlyMode',
            \   'FullPath': 'Lf_hl_popup_fullPathMode',
            \   'Contents': 'Lf_hl_popup_nameOnlyMode',
            \   'WholeLine': 'Lf_hl_popup_fullPathMode',
            \   'Fuzzy': 'Lf_hl_popup_fuzzyMode',
            \   'Regex': 'Lf_hl_popup_regexMode',
            \   'Live': 'Lf_hl_popup_fuzzyMode'
            \ }

let s:leftSep = {
            \   'sep0': {
            \       'left': 'mode',
            \       'right': 'category'
            \   },
            \   'sep1': {
            \       'left': 'category',
            \       'right': 'matchMode'
            \   },
            \   'sep2': {
            \       'left': 'matchMode',
            \       'right': 'cwd'
            \   },
            \   'sep3': {
            \       'left': 'cwd',
            \       'right': 'blank'
            \   }
            \ }

let s:rightSep = {
            \   'sep4': {
            \       'left': 'inputText',
            \       'right': 'lineInfo'
            \   },
            \   'sep5': {
            \       'left': 'lineInfo',
            \       'right': 'total'
            \   }
            \ }

function! s:HighlightGroup(category, name) abort
    if a:name == 'mode' || a:name == 'matchMode'
        return printf("Lf_hl_popup_%s_%s", a:category, a:name)
    else
        return printf("Lf_hl_popup_%s", a:name)
    endif
endfunction

function! s:SynIDattr(synID, what, ...) abort
    if a:0 == 0
        let result = synIDattr(a:synID, a:what)
    else
        let result = synIDattr(a:synID, a:what, a:1)
    endif

    if result == -1
        return ''
    else
        return result
    endif
endfunction

function! s:HighlightSeperator(category) abort
    exec printf("highlight link Lf_hl_popup_%s_mode Lf_hl_popup_inputMode", a:category)
    exec printf("highlight link Lf_hl_popup_%s_matchMode %s", a:category, s:matchModeMap[g:Lf_DefaultMode])
    let hi_group = printf("Lf_hl_popup_%s_mode", a:category)
    silent! call prop_type_add(hi_group, {'highlight': hi_group, 'priority': 20})
    let hi_group = printf("Lf_hl_popup_%s_matchMode", a:category)
    silent! call prop_type_add(hi_group, {'highlight': hi_group, 'priority': 20})
    for [sep, dict] in items(s:leftSep)
        let sid_left = synIDtrans(hlID(s:HighlightGroup(a:category, dict.left)))
        let sid_right = synIDtrans(hlID(s:HighlightGroup(a:category, dict.right)))
        let left_guibg = s:SynIDattr(sid_left, "bg", "gui")
        let left_ctermbg = s:SynIDattr(sid_left, "bg", "cterm")
        let right_guibg = s:SynIDattr(sid_right, "bg", "gui")
        let right_ctermbg = s:SynIDattr(sid_right, "bg", "cterm")
        let hiCmd = printf("hi Lf_hl_popup_%s_%s", a:category, sep)
        let hiCmd .= printf(" guifg=%s guibg=%s", left_guibg == '' ? 'NONE': left_guibg, right_guibg == '' ? 'NONE': right_guibg)
        let hiCmd .= printf(" ctermfg=%s ctermbg=%s", left_ctermbg == '' ? 'NONE': left_ctermbg, right_ctermbg == '' ? 'NONE': right_ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let hiCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec hiCmd
        let hi_group = printf("Lf_hl_popup_%s_%s", a:category, sep)
        silent! call prop_type_add(hi_group, {'highlight': hi_group, 'priority': 20})
    endfor

    for [sep, dict] in items(s:rightSep)
        let sid_left = synIDtrans(hlID(s:HighlightGroup(a:category, dict.left)))
        let sid_right = synIDtrans(hlID(s:HighlightGroup(a:category, dict.right)))
        let left_guibg = s:SynIDattr(sid_left, "bg", "gui")
        let left_ctermbg = s:SynIDattr(sid_left, "bg", "cterm")
        let right_guibg = s:SynIDattr(sid_right, "bg", "gui")
        let right_ctermbg = s:SynIDattr(sid_right, "bg", "cterm")
        let hiCmd = printf("hi Lf_hl_popup_%s_%s", a:category, sep)
        let hiCmd .= printf(" guifg=%s guibg=%s", right_guibg == '' ? 'NONE': right_guibg, left_guibg == '' ? 'NONE': left_guibg)
        let hiCmd .= printf(" ctermfg=%s ctermbg=%s", right_ctermbg == '' ? 'NONE': right_ctermbg, left_ctermbg == '' ? 'NONE': left_ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let hiCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec hiCmd
        let hi_group = printf("Lf_hl_popup_%s_%s", a:category, sep)
        silent! call prop_type_add(hi_group, {'highlight': hi_group, 'priority': 20})
    endfor
endfunction

function! s:getSynAttr(sid) abort
    let attr = ""
    if s:SynIDattr(a:sid, "bold")
        let attr = "bold"
    endif
    if s:SynIDattr(a:sid, "italic")
        if attr == ""
            let attr = "italic"
        else
            let attr = attr . ",italic"
        endif
    endif
    if s:SynIDattr(a:sid, "standout")
        if attr == ""
            let attr = "standout"
        else
            let attr = attr . ",standout"
        endif
    endif
    if s:SynIDattr(a:sid, "underline")
        if attr == ""
            let attr = "underline"
        else
            let attr = attr . ",underline"
        endif
    endif
    if s:SynIDattr(a:sid, "undercurl")
        if attr == ""
            let attr = "undercurl"
        else
            let attr = attr . ",undercurl"
        endif
    endif
    if s:SynIDattr(a:sid, "strike")
        if attr == ""
            let attr = "strike"
        else
            let attr = attr . ",strike"
        endif
    endif
    if s:SynIDattr(a:sid, "nocombine")
        if attr == ""
            let attr = "nocombine"
        else
            let attr = attr . ",nocombine"
        endif
    endif
    return attr
endfunction

" https://github.com/vim/vim/issues/5227
" same as `hi link` but filter out the `reverse` attribute
function! leaderf#colorscheme#popup#link_no_reverse(from, to) abort
    let sid = synIDtrans(hlID(a:to))
    if s:SynIDattr(sid, "reverse") || s:SynIDattr(sid, "inverse")
        let guibg = s:SynIDattr(sid, "fg", "gui")
        let guifg = s:SynIDattr(sid, "bg", "gui")
        let ctermbg = s:SynIDattr(sid, "fg", "cterm")
        let ctermfg = s:SynIDattr(sid, "bg", "cterm")
    else
        let guibg = s:SynIDattr(sid, "bg", "gui")
        let guifg = s:SynIDattr(sid, "fg", "gui")
        let ctermbg = s:SynIDattr(sid, "bg", "cterm")
        let ctermfg = s:SynIDattr(sid, "fg", "cterm")
    endif

    let attr = s:getSynAttr(sid)
    if attr == ""
        let attr = "gui=NONE cterm=NONE"
    else
        let attr = "gui=" . attr . " cterm=" . attr
    endif
    let hiCmd = printf("hi def %s %s", a:from, attr)
    let hiCmd .= printf(" guifg=%s guibg=%s", guifg == '' ? 'NONE': guifg, guibg == '' ? 'NONE': guibg)
    let hiCmd .= printf(" ctermfg=%s ctermbg=%s", ctermfg == '' ? 'NONE': ctermfg, ctermbg == '' ? 'NONE': ctermbg)
    exec hiCmd
endfunction

" link to bg's background color and fg's foreground color
function! leaderf#colorscheme#popup#link_two(from, bg, fg, no_attr) abort
    let bg_sid = synIDtrans(hlID(a:bg))
    if s:SynIDattr(bg_sid, "reverse") || s:SynIDattr(bg_sid, "inverse")
        let guibg = s:SynIDattr(bg_sid, "fg", "gui")
        let ctermbg = s:SynIDattr(bg_sid, "fg", "cterm")
    else
        let guibg = s:SynIDattr(bg_sid, "bg", "gui")
        let ctermbg = s:SynIDattr(bg_sid, "bg", "cterm")
    endif

    let fg_sid = synIDtrans(hlID(a:fg))
    if s:SynIDattr(fg_sid, "reverse") || s:SynIDattr(fg_sid, "inverse")
        let guifg = s:SynIDattr(fg_sid, "bg", "gui")
        if guifg == guibg
            let guifg = s:SynIDattr(fg_sid, "fg", "gui")
        endif
        let ctermfg = s:SynIDattr(fg_sid, "bg", "cterm")
        if ctermfg == ctermbg
            let ctermfg = s:SynIDattr(fg_sid, "fg", "cterm")
        endif
    else
        let guifg = s:SynIDattr(fg_sid, "fg", "gui")
        if guifg == guibg
            let guifg = s:SynIDattr(fg_sid, "bg", "gui")
        endif
        let ctermfg = s:SynIDattr(fg_sid, "fg", "cterm")
        if ctermfg == ctermbg
            let ctermfg = s:SynIDattr(fg_sid, "bg", "cterm")
        endif
    endif

    if a:no_attr
        let attr = "gui=NONE cterm=NONE"
    else
        let attr = s:getSynAttr(sid)
        if attr == ""
            let attr = "gui=NONE cterm=NONE"
        else
            let attr = "gui=" . attr . "cterm=" . attr
        endif
    endif
    let hiCmd = printf("hi def %s %s", a:from, attr)
    let hiCmd .= printf(" guifg=%s guibg=%s", guifg == '' ? 'NONE': guifg, guibg == '' ? 'NONE': guibg)
    let hiCmd .= printf(" ctermfg=%s ctermbg=%s", ctermfg == '' ? 'NONE': ctermfg, ctermbg == '' ? 'NONE': ctermbg)
    exec hiCmd
endfunction

" nvim has a weird bug, if `hi Cursor cterm=reverse gui=reverse`
" and `hi def link Lf_hl_popup_cursor Cursor`, the bug occurs.
function! leaderf#colorscheme#popup#link_cursor(from) abort
    let sid = synIDtrans(hlID("Cursor"))
    if s:SynIDattr(sid, "bg") == '' || s:SynIDattr(sid, "fg") == ''
        exec printf("hi def %s gui=reverse guifg=NONE guibg=NONE cterm=reverse ctermfg=NONE ctermbg=NONE", a:from)
    else
        exec printf("hi def link %s Cursor", a:from)
    endif
endfunction

" mode can be:
" 1. INPUT mode
" 2. NORMAL mode
function! leaderf#colorscheme#popup#hiMode(category, mode) abort
    if a:mode == 'NORMAL'
        exec printf("hi link Lf_hl_popup_%s_mode Lf_hl_popup_normalMode", a:category)
    else
        exec printf("hi link Lf_hl_popup_%s_mode Lf_hl_popup_inputMode", a:category)
    endif
    let sid = synIDtrans(hlID(printf("Lf_hl_popup_%s_mode", a:category)))
    let guibg = s:SynIDattr(sid, "bg", "gui")
    let ctermbg = s:SynIDattr(sid, "bg", "cterm")
    exec printf("hi Lf_hl_popup_%s_sep0 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep0 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
endfunction

" mode can be:
" 1. NameOnly mode
" 2. FullPath mode
" 3. Fuzzy mode
" 4. Regex mode
function! leaderf#colorscheme#popup#hiMatchMode(category, mode) abort
    let sid = synIDtrans(hlID(s:matchModeMap[a:mode]))
    let guibg = s:SynIDattr(sid, "bg", "gui")
    let ctermbg = s:SynIDattr(sid, "bg", "cterm")
    exec printf("hi link Lf_hl_popup_%s_matchMode %s", a:category, s:matchModeMap[a:mode])
    exec printf("hi Lf_hl_popup_%s_sep1 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep1 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_popup_%s_sep2 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep2 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
endfunction

" define Lf_hl_LineNr
function! s:hiDefineLineNr() abort
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_LineNr", "LineNr")
    let sid = synIDtrans(hlID("Lf_hl_LineNr"))
    if s:SynIDattr(sid, "nocombine") == ""
        let attr = s:getSynAttr(sid)
        if attr == ""
            let attr = "nocombine"
        else
            let attr = attr . ",nocombine"
        endif

        let guibg = s:SynIDattr(sid, "bg", "gui")
        let ctermbg = s:SynIDattr(sid, "bg", "cterm")
        if guibg == ""
            let guibg = s:SynIDattr(synIDtrans(hlID("Normal")), "bg", "gui")
            if guibg == ""
                let guibg = "NONE"
            endif
        endif
        if ctermbg == ""
            let ctermbg = s:SynIDattr(synIDtrans(hlID("Normal")), "bg", "cterm")
            if ctermbg == ""
                let ctermbg = "NONE"
            endif
        endif

        let hiCmd = printf("hi Lf_hl_LineNr cterm=%s ctermbg=%s gui=%s guibg=%s", attr, ctermbg, attr, guibg)
        exec hiCmd
    endif
endfunction

function! s:AddPropType() abort
    silent! highlight def link Lf_hl_cursor Cursor
    silent! call prop_type_add("Lf_hl_popup_cursor", {'highlight': "Lf_hl_cursor", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_window", {'highlight': "Lf_hl_popup_window", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_prompt", {'highlight': "Lf_hl_popup_prompt", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_spin", {'highlight': "Lf_hl_popup_spin", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_inputText", {'highlight': "Lf_hl_popup_inputText", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_normalMode", {'highlight': "Lf_hl_popup_normalMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_inputMode", {'highlight': "Lf_hl_popup_inputMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_category", {'highlight': "Lf_hl_popup_category", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_nameOnlyMode", {'highlight': "Lf_hl_popup_nameOnlyMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_fullPathMode", {'highlight': "Lf_hl_popup_fullPathMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_fuzzyMode", {'highlight': "Lf_hl_popup_fuzzyMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_regexMode", {'highlight': "Lf_hl_popup_regexMode", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_cwd", {'highlight': "Lf_hl_popup_cwd", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_blank", {'highlight': "Lf_hl_popup_blank", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_lineInfo", {'highlight': "Lf_hl_popup_lineInfo", 'priority': 20})
    silent! call prop_type_add("Lf_hl_popup_total", {'highlight': "Lf_hl_popup_total", 'priority': 20})
    silent! call prop_type_add("Lf_hl_gitDiffAdd", {'highlight': "Lf_hl_gitDiffAdd", 'priority': 20})
    silent! call prop_type_add("Lf_hl_gitDiffDelete", {'highlight': "Lf_hl_gitDiffDelete", 'priority': 20})
    silent! call prop_type_add("Lf_hl_gitDiffChange", {'highlight': "Lf_hl_gitDiffChange", 'priority': 21})
    silent! call prop_type_add("Lf_hl_gitDiffText", {'highlight': "Lf_hl_gitDiffText", 'priority': 22})
    silent! call prop_type_add("Lf_hl_LineNr", {'highlight': "Lf_hl_LineNr", 'priority': 20})
    silent! call prop_type_add("Lf_hl_gitTransparent", {'highlight': "Lf_hl_gitTransparent", 'priority': -2000})
    silent! call prop_type_add("Lf_hl_gitInlineBlame", {'highlight': "Comment", 'priority': 20})
endfunction

"
" let g:Lf_PopupPalette = {
"   \ 'light': {
"       \ 'Lf_hl_match': {
"           \       'gui': 'NONE',
"           \       'font': 'NONE',
"           \       'guifg': 'NONE',
"           \       'guibg': '#303136',
"           \       'cterm': 'NONE',
"           \       'ctermfg': 'NONE',
"           \       'ctermbg': '236'
"           \ },
"       \ 'Lf_hl_match0': {
"           \       'gui': 'NONE',
"           \       'font': 'NONE',
"           \       'guifg': 'NONE',
"           \       'guibg': '#303136',
"           \       'cterm': 'NONE',
"           \       'ctermfg': 'NONE',
"           \       'ctermbg': '236'
"           \ },
"   \ },
"   \ 'dark': {
"           ...
"           ...
"   \ }
" \ }
"
function! s:LoadFromPalette() abort
    let popup_palette = get(g:, "Lf_PopupPalette", {})
    let palette = get(popup_palette, &background, {})

    for [name, dict] in items(palette)
        let highlightCmd = printf("hi %s", name)
        for [k, v] in items(dict)
            let highlightCmd .= printf(" %s=%s", k, v)
        endfor
        exec highlightCmd
    endfor
endfunction

function! leaderf#colorscheme#popup#load(category, name)
    exec 'runtime autoload/leaderf/colorscheme/popup/'.a:name.'.vim'
    " in case a:name does not exist
    if a:name != "default"
        exec 'runtime autoload/leaderf/colorscheme/popup/default.vim'
    endif

    call s:hiDefineLineNr()
    if !has("nvim")
        call s:AddPropType()
    endif
    call s:LoadFromPalette()
    call s:HighlightSeperator(a:category)
endfunction

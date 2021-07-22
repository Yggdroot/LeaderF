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
            \   'Fuzzy': 'Lf_hl_popup_fuzzyMode',
            \   'Regex': 'Lf_hl_popup_regexMode'
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
        let left_guibg = synIDattr(sid_left, "bg", "gui")
        let left_ctermbg = synIDattr(sid_left, "bg", "cterm")
        let right_guibg = synIDattr(sid_right, "bg", "gui")
        let right_ctermbg = synIDattr(sid_right, "bg", "cterm")
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
        let left_guibg = synIDattr(sid_left, "bg", "gui")
        let left_ctermbg = synIDattr(sid_left, "bg", "cterm")
        let right_guibg = synIDattr(sid_right, "bg", "gui")
        let right_ctermbg = synIDattr(sid_right, "bg", "cterm")
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

" https://github.com/vim/vim/issues/5227
" same as `hi link` but filter out the `reverse` attribute
function! leaderf#colorscheme#popup#link_no_reverse(from, to) abort
    let sid = synIDtrans(hlID(a:to))
    if synIDattr(sid, "reverse") || synIDattr(sid, "inverse")
        let guibg = synIDattr(sid, "fg", "gui")
        let guifg = synIDattr(sid, "bg", "gui")
        let ctermbg = synIDattr(sid, "fg", "cterm")
        let ctermfg = synIDattr(sid, "bg", "cterm")
    else
        let guibg = synIDattr(sid, "bg", "gui")
        let guifg = synIDattr(sid, "fg", "gui")
        let ctermbg = synIDattr(sid, "bg", "cterm")
        let ctermfg = synIDattr(sid, "fg", "cterm")
    endif
    let bold = synIDattr(sid, "bold") ? "bold" : ""
    let italic = synIDattr(sid, "italic") ? "italic" : ""
    if bold == "" && italic == ""
        let attr = "gui=NONE cterm=NONE"
    elseif bold == "bold" && italic == "italic"
        let attr = "gui=bold,italic cterm=bold,italic"
    elseif bold == "bold"
        let attr = "gui=bold cterm=bold"
    else
        let attr = "gui=italic cterm=italic"
    endif
    let hiCmd = printf("hi def %s %s", a:from, attr)
    let hiCmd .= printf(" guifg=%s guibg=%s", guifg == '' ? 'NONE': guifg, guibg == '' ? 'NONE': guibg)
    let hiCmd .= printf(" ctermfg=%s ctermbg=%s", ctermfg == '' ? 'NONE': ctermfg, ctermbg == '' ? 'NONE': ctermbg)
    exec hiCmd
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
    let guibg = synIDattr(sid, "bg", "gui")
    let ctermbg = synIDattr(sid, "bg", "cterm")
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
    let guibg = synIDattr(sid, "bg", "gui")
    let ctermbg = synIDattr(sid, "bg", "cterm")
    exec printf("hi link Lf_hl_popup_%s_matchMode %s", a:category, s:matchModeMap[a:mode])
    exec printf("hi Lf_hl_popup_%s_sep1 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep1 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_popup_%s_sep2 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_popup_%s_sep2 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
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
    if !has("nvim")
        call s:AddPropType()
    endif
    call s:LoadFromPalette()
    call s:HighlightSeperator(a:category)
    call g:LfDefineDefaultColors()
endfunction

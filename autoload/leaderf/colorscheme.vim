" ============================================================================
" File:        colorscheme.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

function! leaderf#colorscheme#mergePalette(palette)
    return a:palette
endfunction

let s:modeMap = {
            \   'NameOnly': 'Lf_hl_stlNameOnlyMode',
            \   'FullPath': 'Lf_hl_stlFullPathMode',
            \   'Fuzzy': 'Lf_hl_stlFuzzyMode',
            \   'Regex': 'Lf_hl_stlRegexMode',
            \   'Live': 'Lf_hl_stlFuzzyMode'
            \ }

let s:leftSep = {
            \   'stlSeparator0': {
            \       'left': 'stlName',
            \       'right': 'stlCategory'
            \   },
            \   'stlSeparator1': {
            \       'left': 'stlCategory',
            \       'right': 'stlMode'
            \   },
            \   'stlSeparator2': {
            \       'left': 'stlMode',
            \       'right': 'stlCwd'
            \   },
            \   'stlSeparator3': {
            \       'left': 'stlCwd',
            \       'right': 'stlBlank'
            \   }
            \ }

let s:rightSep = {
            \   'stlSeparator4': {
            \       'left': 'stlBlank',
            \       'right': 'stlLineInfo'
            \   },
            \   'stlSeparator5': {
            \       'left': 'stlLineInfo',
            \       'right': 'stlTotal'
            \   }
            \ }

function! s:HighlightGroup(category, name) abort
    if a:name == 'stlMode'
        return printf("Lf_hl_%s_%s", a:category, a:name)
    else
        return printf("Lf_hl_%s", a:name)
    endif
endfunction

function! s:LoadFromPalette() abort
    let palette = get(g:, "Lf_StlPalette", {})

    for [name, dict] in items(palette)
        let hiCmd = printf("hi Lf_hl_%s", name)
        for [k, v] in items(dict)
            let hiCmd .= printf(" %s=%s", k, v)
        endfor
        exec hiCmd
    endfor
endfunction

function! leaderf#colorscheme#highlight(category, bufnr)
    try
        let s:palette = g:leaderf#colorscheme#{g:Lf_StlColorscheme}#palette
    catch /^Vim\%((\a\+)\)\=:E121/
        try
            let s:palette = g:leaderf#colorscheme#{g:colors_name}#palette
        catch /^Vim\%((\a\+)\)\=:E121/
            "echohl WarningMsg
            "try
            "    echo "Could not load colorscheme '".g:colors_name."', use 'default'."
            "catch /^Vim\%((\a\+)\)\=:E121/
            "    echo "Could not load colorscheme, use 'default'."
            "    let g:colors_name = "default"
            "endtry
            "echohl None

            let s:palette = g:leaderf#colorscheme#default#palette
        endtry
    endtry

    let palette = copy(s:palette)
    for [name, dict] in items(palette)
        let hiCmd = printf("hi def Lf_hl_%s", name)
        for [k, v] in items(dict)
            let hiCmd .= printf(" %s=%s", k, v)
        endfor
        exec hiCmd
    endfor

    call s:LoadFromPalette()

    exec printf("hi link Lf_hl_%s_stlMode %s", a:category, s:modeMap[g:Lf_DefaultMode])
    for [sep, dict] in items(s:leftSep)
        let sid_left = synIDtrans(hlID(s:HighlightGroup(a:category, dict.left)))
        let sid_right = synIDtrans(hlID(s:HighlightGroup(a:category, dict.right)))
        let left_guibg = synIDattr(sid_left, "bg", "gui")
        let left_ctermbg = synIDattr(sid_left, "bg", "cterm")
        let right_guibg = synIDattr(sid_right, "bg", "gui")
        let right_ctermbg = synIDattr(sid_right, "bg", "cterm")
        let hiCmd = printf("hi Lf_hl_%s_%s", a:category, sep)
        let hiCmd .= printf(" guifg=%s guibg=%s", left_guibg == '' ? 'NONE': left_guibg, right_guibg == '' ? 'NONE': right_guibg)
        let hiCmd .= printf(" ctermfg=%s ctermbg=%s", left_ctermbg == '' ? 'NONE': left_ctermbg, right_ctermbg == '' ? 'NONE': right_ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let hiCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec hiCmd
    endfor

    for [sep, dict] in items(s:rightSep)
        let sid_left = synIDtrans(hlID(s:HighlightGroup(a:category, dict.left)))
        let sid_right = synIDtrans(hlID(s:HighlightGroup(a:category, dict.right)))
        let left_guibg = synIDattr(sid_left, "bg", "gui")
        let left_ctermbg = synIDattr(sid_left, "bg", "cterm")
        let right_guibg = synIDattr(sid_right, "bg", "gui")
        let right_ctermbg = synIDattr(sid_right, "bg", "cterm")
        let hiCmd = printf("hi Lf_hl_%s_%s", a:category, sep)
        let hiCmd .= printf(" guifg=%s guibg=%s", right_guibg == '' ? 'NONE': right_guibg, left_guibg == '' ? 'NONE': left_guibg)
        let hiCmd .= printf(" ctermfg=%s ctermbg=%s", right_ctermbg == '' ? 'NONE': right_ctermbg, left_ctermbg == '' ? 'NONE': left_ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let hiCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec hiCmd
    endfor

    exec printf("hi link Lf_hl_%s_stlBlank Lf_hl_stlBlank", a:category)
    redrawstatus
endfunction

function! leaderf#colorscheme#highlightMode(category, mode)
    let sid = synIDtrans(hlID(s:modeMap[a:mode]))
    let guibg = synIDattr(sid, "bg", "gui")
    let ctermbg = synIDattr(sid, "bg", "cterm")
    exec printf("hi link Lf_hl_%s_stlMode %s", a:category, s:modeMap[a:mode])
    exec printf("hi Lf_hl_%s_stlSeparator1 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator1 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_%s_stlSeparator2 guifg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator2 ctermfg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    redrawstatus
endfunction

function! leaderf#colorscheme#highlightBlank(category, bufnr)
    let mod = getbufvar(a:bufnr, "&modified")
    if getbufvar(a:bufnr, "lf_buffer_changed") == mod
        return
    endif

    call setbufvar(a:bufnr, "lf_buffer_changed", mod)

    if getbufvar(a:bufnr, "&modified") == 1
        let blank = "DiffChange"
    else
        let blank = "Lf_hl_stlBlank"
    endif
    let sid = synIDtrans(hlID(blank))
    if synIDattr(sid, "reverse") || synIDattr(sid, "inverse")
        let guibg = synIDattr(sid, "fg", "gui")
        let ctermbg = synIDattr(sid, "fg", "cterm")
    else
        let guibg = synIDattr(sid, "bg", "gui")
        let ctermbg = synIDattr(sid, "bg", "cterm")
    endif
    exec printf("hi link Lf_hl_%s_stlBlank %s", a:category, blank)
    exec printf("hi Lf_hl_%s_stlSeparator3 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator3 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    exec printf("hi Lf_hl_%s_stlSeparator4 guibg=%s", a:category, guibg == '' ? 'NONE': guibg)
    exec printf("hi Lf_hl_%s_stlSeparator4 ctermbg=%s", a:category, ctermbg == '' ? 'NONE': ctermbg)
    redrawstatus
endfunction

function! leaderf#colorscheme#setStatusline(bufnr, stl)
    for n in range(1, winnr('$'))
        if winbufnr(n) == a:bufnr
            call setwinvar(n, '&statusline', a:stl)
        endif
    endfor
endfunction

" ============================================================================
" File:        colorscheme.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

function! leaderf#colorscheme#mergePalette(palette)
    let palette = a:palette
    for key in keys(g:Lf_StlPalette)
        try
            for [k, v] in items(g:Lf_StlPalette[key])
                let palette[key][k] = v
            endfor
        catch
            echohl Error
            echo printf("Error: invalid key '%s' in 'g:Lf_StlPalette'.", key)
            sleep 1
            echohl None
        endtry
    endfor
    return palette
endfunction

let s:modeMap = {
            \   'NameOnly': 'stlNameOnlyMode',
            \   'FullPath': 'stlFullPathMode',
            \   'Fuzzy': 'stlFuzzyMode',
            \   'Regex': 'stlRegexMode'
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

function! leaderf#colorscheme#highlight(category)
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
        let highlightCmd = printf("hi def Lf_hl_%s_%s", a:category, name)
        for [k, v] in items(dict)
            let highlightCmd .= printf(" %s=%s", k, v)
        endfor
        exec highlightCmd
    endfor

    let palette.stlMode = palette[s:modeMap[g:Lf_DefaultMode]]

    for [sep, dict] in items(s:leftSep)
        let highlightCmd = printf("hi def Lf_hl_%s_%s", a:category, sep)
        let highlightCmd .= printf(" guifg=%s guibg=%s", palette[dict.left].guibg, palette[dict.right].guibg)
        let highlightCmd .= printf(" ctermfg=%s ctermbg=%s", palette[dict.left].ctermbg, palette[dict.right].ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let highlightCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec highlightCmd
    endfor

    for [sep, dict] in items(s:rightSep)
        let highlightCmd = printf("hi def Lf_hl_%s_%s", a:category, sep)
        let highlightCmd .= printf(" guifg=%s guibg=%s", palette[dict.right].guibg, palette[dict.left].guibg)
        let highlightCmd .= printf(" ctermfg=%s ctermbg=%s", palette[dict.right].ctermbg, palette[dict.left].ctermbg)
        if get(g:Lf_StlSeparator, "font", "") != ""
            let highlightCmd .= printf(" font='%s'", g:Lf_StlSeparator["font"])
        endif
        exec highlightCmd
    endfor
    redrawstatus
endfunction

function! leaderf#colorscheme#highlightMode(category, mode)
    exec printf("hi link Lf_hl_%s_stlMode Lf_hl_%s_%s", a:category, a:category, s:modeMap[a:mode])
    exec printf("hi Lf_hl_%s_stlSeparator1 guibg=%s", a:category, s:palette[s:modeMap[a:mode]].guibg)
    exec printf("hi Lf_hl_%s_stlSeparator1 ctermbg=%s", a:category, s:palette[s:modeMap[a:mode]].ctermbg)
    exec printf("hi Lf_hl_%s_stlSeparator2 guifg=%s", a:category, s:palette[s:modeMap[a:mode]].guibg)
    exec printf("hi Lf_hl_%s_stlSeparator2 ctermfg=%s", a:category, s:palette[s:modeMap[a:mode]].ctermbg)
    redrawstatus
endfunction

function! leaderf#colorscheme#setStatusline(bufnr, stl)
    for n in range(1, winnr('$'))
        if winbufnr(n) == a:bufnr
            call setwinvar(n, '&statusline', a:stl)
        endif
    endfor
endfunction

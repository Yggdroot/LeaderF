" ============================================================================
" File:        default.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

" due to https://github.com/vim/vim/issues/5227,
" if aim to link to another highlight group,
" it is better to use leaderf#colorscheme#popup#link_no_reverse()
" instead of `hi link`. Because some BAD colorscheme such as solarized8_flat
" like using `reverse` attribute.

if &background ==? 'dark'
    " Lf_hl_popup_inputText is the wincolor of input window
    highlight Lf_hl_popup_inputText guifg=#87ceeb guibg=#4d4d4d gui=NONE ctermfg=117 ctermbg=239 cterm=NONE

    " Lf_hl_popup_window is the wincolor of content window
    highlight Lf_hl_popup_window guifg=#eeeeee guibg=#404040 gui=NONE ctermfg=255 ctermbg=237 cterm=NONE

    " Lf_hl_popup_blank is the wincolor of statusline window
    highlight Lf_hl_popup_blank guifg=NONE guibg=#4b4e50 gui=NONE ctermbg=239 cterm=NONE

    highlight! link Lf_hl_popup_cursor Cursor
    highlight Lf_hl_popup_prompt guifg=#ffcd4a guibg=NONE gui=NONE ctermfg=221 ctermbg=NONE cterm=NONE
    highlight Lf_hl_popup_spin guifg=#e6e666 guibg=NONE gui=NONE ctermfg=185 ctermbg=NONE cterm=NONE
    highlight Lf_hl_popup_normalMode guifg=#333300 guibg=#c1ce96 gui=bold ctermfg=58 ctermbg=187 cterm=bold
    highlight Lf_hl_popup_inputMode guifg=#003333 guibg=#98b3a5 gui=bold ctermfg=23 ctermbg=109 cterm=bold
    highlight Lf_hl_popup_category guifg=#ecebf0 guibg=#636769 gui=NONE ctermfg=255 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_nameOnlyMode guifg=#14212b guibg=#cbb370 gui=NONE ctermfg=234 ctermbg=179 cterm=NONE
    highlight Lf_hl_popup_fullPathMode guifg=#14212b guibg=#aab3b6 gui=NONE ctermfg=234 ctermbg=249 cterm=NONE
    highlight Lf_hl_popup_fuzzyMode guifg=#14212b guibg=#aab3b6 gui=NONE ctermfg=234 ctermbg=249 cterm=NONE
    highlight Lf_hl_popup_regexMode guifg=#14212b guibg=#a0b688 gui=NONE ctermfg=234 ctermbg=108 cterm=NONE
    highlight Lf_hl_popup_cwd guifg=#f2ebc7 guibg=#6e7476 gui=NONE ctermfg=230 ctermbg=243 cterm=NONE
    highlight Lf_hl_popup_lineInfo guifg=#353129 guibg=#dce6da gui=NONE ctermfg=236 ctermbg=254 cterm=NONE
    highlight Lf_hl_popup_total guifg=#353129 guibg=#b8ccbb gui=NONE ctermfg=236 ctermbg=151 cterm=NONE


    " the color of the cursorline
    highlight Lf_hl_cursorline guifg=Yellow guibg=NONE gui=NONE ctermfg=226 ctermbg=NONE cterm=NONE

    " the color of matching character
    highlight Lf_hl_match  guifg=SpringGreen guibg=NONE gui=bold ctermfg=85 ctermbg=NONE cterm=bold

    " the color of matching character in `And mode`
    highlight Lf_hl_match0 guifg=SpringGreen guibg=NONE gui=bold ctermfg=85 ctermbg=NONE cterm=bold
    highlight Lf_hl_match1 guifg=#FE8019 guibg=NONE gui=bold ctermfg=208 ctermbg=NONE cterm=bold
    highlight Lf_hl_match2 guifg=#3FF5D1 guibg=NONE gui=bold ctermfg=50 ctermbg=NONE cterm=bold
    highlight Lf_hl_match3 guifg=#FF7272 guibg=NONE gui=bold ctermfg=203 ctermbg=NONE cterm=bold
    highlight Lf_hl_match4 guifg=#43B9F0 guibg=NONE gui=bold ctermfg=74 ctermbg=NONE cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight Lf_hl_matchRefine gui=bold guifg=Magenta cterm=bold ctermfg=201

    " the color of help in normal mode when <F1> is pressed
    highlight! link Lf_hl_help               comment
    highlight! link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight Lf_hl_selection guifg=Black guibg=#A5EB84 gui=NONE ctermfg=Black ctermbg=156 cterm=NONE

    " the color of `Leaderf buffer`
    highlight! link Lf_hl_bufNumber          Constant
    highlight! link Lf_hl_bufIndicators      Statement
    highlight! link Lf_hl_bufModified        String
    highlight! link Lf_hl_bufNomodifiable    Comment
    highlight! link Lf_hl_bufDirname         Directory

    " the color of `Leaderf tag`
    highlight! link Lf_hl_tagFile            Directory
    highlight! link Lf_hl_tagType            Type
    highlight! link Lf_hl_tagKeyword         Keyword

    " the color of `Leaderf bufTag`
    highlight! link Lf_hl_buftagKind         Title
    highlight! link Lf_hl_buftagScopeType    Keyword
    highlight! link Lf_hl_buftagScope        Type
    highlight! link Lf_hl_buftagDirname      Directory
    highlight! link Lf_hl_buftagLineNum      Constant
    highlight! link Lf_hl_buftagCode         Comment

    " the color of `Leaderf function`
    highlight! link Lf_hl_funcKind           Title
    highlight! link Lf_hl_funcReturnType     Type
    highlight! link Lf_hl_funcScope          Keyword
    highlight! link Lf_hl_funcName           Function
    highlight! link Lf_hl_funcDirname        Directory
    highlight! link Lf_hl_funcLineNum        Constant

    " the color of `Leaderf line`
    highlight! link Lf_hl_lineLocation       Comment

    " the color of `Leaderf self`
    highlight! link Lf_hl_selfIndex          Constant
    highlight! link Lf_hl_selfDescription    Comment

    " the color of `Leaderf help`
    highlight! link Lf_hl_helpTagfile        Comment

    " the color of `Leaderf rg`
    highlight! link Lf_hl_rgFileName         Directory
    highlight! link Lf_hl_rgLineNumber       Constant
    " the color of line number if '-A' or '-B' or '-C' is in the options list
    " of `Leaderf rg`
    highlight! link Lf_hl_rgLineNumber2      Folded
    " the color of column number if '--column' in g:Lf_RgConfig
    highlight! link Lf_hl_rgColumnNumber     Constant
    highlight Lf_hl_rgHighlight guifg=#000000 guibg=#CCCC66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    " the color of `Leaderf gtags`
    highlight! link Lf_hl_gtagsFileName      Directory
    highlight! link Lf_hl_gtagsLineNumber    Constant
    highlight Lf_hl_gtagsHighlight guifg=#000000 guibg=#CCCC66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    highlight! link Lf_hl_previewTitle       Statusline
else
    highlight Lf_hl_match  guifg=#1540AD guibg=NONE gui=bold ctermfg=26 ctermbg=NONE cterm=bold
    highlight Lf_hl_match0 guifg=#1540AD guibg=NONE gui=bold ctermfg=26 ctermbg=NONE cterm=bold
    highlight Lf_hl_match1 guifg=#A52A2A guibg=NONE gui=bold ctermfg=124 ctermbg=NONE cterm=bold
    highlight Lf_hl_match2 guifg=#B52BB0 guibg=NONE gui=bold ctermfg=127 ctermbg=NONE cterm=bold
    highlight Lf_hl_match3 guifg=#02781A guibg=NONE gui=bold ctermfg=28 ctermbg=NONE cterm=bold
    highlight Lf_hl_match4 guifg=#F70505 guibg=NONE gui=bold ctermfg=196 ctermbg=NONE cterm=bold
    highlight Lf_hl_matchRefine guifg=Magenta guibg=NONE gui=bold ctermfg=201 ctermbg=NONE cterm=bold
endif

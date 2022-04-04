" ============================================================================
" File:        gruvbox_default.vim
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
    highlight def Lf_hl_popup_inputText guifg=#dfebb2 guibg=#413d39 gui=NONE ctermfg=187 ctermbg=237 cterm=NONE

    " Lf_hl_popup_window is the wincolor of content window
    highlight def Lf_hl_popup_window guifg=#ebdbb2 guibg=#323232 gui=NONE ctermfg=187 ctermbg=236 cterm=NONE

    " Lf_hl_popup_blank is the wincolor of statusline window
    highlight def Lf_hl_popup_blank guifg=NONE guibg=#413d39 gui=NONE ctermbg=237 cterm=NONE

    highlight def link Lf_hl_popup_cursor Cursor
    highlight def Lf_hl_popup_prompt guifg=#fabd2f guibg=NONE gui=NONE ctermfg=214 ctermbg=NONE cterm=NONE
    highlight def Lf_hl_popup_spin guifg=#e6e666 guibg=NONE gui=NONE ctermfg=185 ctermbg=NONE cterm=NONE
    highlight def Lf_hl_popup_normalMode guifg=#282828 guibg=#a89984 gui=bold ctermfg=235 ctermbg=137 cterm=bold
    highlight def Lf_hl_popup_inputMode guifg=#504945 guibg=#83a598 gui=bold ctermfg=239 ctermbg=109 cterm=bold
    highlight def Lf_hl_popup_category guifg=#d5c4a1 guibg=#665c54 gui=NONE ctermfg=187 ctermbg=59 cterm=NONE
    highlight def Lf_hl_popup_nameOnlyMode guifg=#bdae93 guibg=#504945 gui=NONE ctermfg=144 ctermbg=239 cterm=NONE
    highlight def Lf_hl_popup_fullPathMode guifg=#bdae93 guibg=#504945 gui=NONE ctermfg=144 ctermbg=239 cterm=NONE
    highlight def Lf_hl_popup_fuzzyMode guifg=#bdae93 guibg=#504945 gui=NONE ctermfg=144 ctermbg=239 cterm=NONE
    highlight def Lf_hl_popup_regexMode guifg=#bdae93 guibg=#504945 gui=NONE ctermfg=144 ctermbg=239 cterm=NONE
    highlight def Lf_hl_popup_cwd guifg=#a89984 guibg=#413b39 gui=NONE ctermfg=144 ctermbg=237 cterm=NONE
    highlight def Lf_hl_popup_lineInfo guifg=#d5c4a1 guibg=#6a635c gui=NONE ctermfg=187 ctermbg=241 cterm=NONE
    highlight def Lf_hl_popup_total guifg=#282828 guibg=#a89984 gui=NONE ctermfg=234 ctermbg=102 cterm=NONE

    " the color of the cursorline
    highlight def Lf_hl_cursorline guifg=#cdcf2a guibg=NONE gui=NONE ctermfg=184 ctermbg=NONE cterm=NONE

    " the color of matching character
    highlight def Lf_hl_match guifg=#87d37c guibg=NONE gui=bold ctermfg=114 ctermbg=NONE cterm=bold

    " the color of matching character in `And mode`
    highlight def Lf_hl_match0 guifg=#87d37c guibg=NONE gui=bold ctermfg=114 cterm=bold
    highlight def Lf_hl_match1 guifg=#fe8019 guibg=NONE gui=bold ctermfg=208 cterm=bold
    highlight def Lf_hl_match2 guifg=#3ff5d1 guibg=NONE gui=bold ctermfg=50 cterm=bold
    highlight def Lf_hl_match3 guifg=#ff7272 guibg=NONE gui=bold ctermfg=203 cterm=bold
    highlight def Lf_hl_match4 guifg=#43b9f0 guibg=NONE gui=bold ctermfg=74 cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight def Lf_hl_matchRefine guifg=#d3869b gui=bold ctermfg=175 cterm=bold

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guifg=#282828 guibg=#8ec07c gui=NONE ctermfg=235 ctermbg=107 cterm=NONE

    " the color of `Leaderf buffer`
    highlight def link Lf_hl_bufNumber          Constant
    highlight def link Lf_hl_bufIndicators      Statement
    highlight def link Lf_hl_bufModified        String
    highlight def link Lf_hl_bufNomodifiable    Comment
    highlight def link Lf_hl_bufDirname         Directory

    " the color of `Leaderf tag`
    highlight def link Lf_hl_tagFile            Directory
    highlight def link Lf_hl_tagType            Type
    highlight def link Lf_hl_tagKeyword         Keyword

    " the color of `Leaderf bufTag`
    highlight def link Lf_hl_buftagKind         Title
    highlight def link Lf_hl_buftagScopeType    Keyword
    highlight def link Lf_hl_buftagScope        Type
    highlight def link Lf_hl_buftagDirname      Directory
    highlight def link Lf_hl_buftagLineNum      Constant
    highlight def link Lf_hl_buftagCode         Comment

    " the color of `Leaderf function`
    highlight def link Lf_hl_funcKind           Title
    highlight def link Lf_hl_funcReturnType     Type
    highlight def link Lf_hl_funcScope          Keyword
    highlight def link Lf_hl_funcName           Function
    highlight def link Lf_hl_funcDirname        Directory
    highlight def link Lf_hl_funcLineNum        Constant

    " the color of `Leaderf line`
    highlight def link Lf_hl_lineLocation       Comment

    " the color of `Leaderf self`
    highlight def link Lf_hl_selfIndex          Constant
    highlight def link Lf_hl_selfDescription    Comment

    " the color of `Leaderf help`
    highlight def link Lf_hl_helpTagfile        Comment

    " the color of `Leaderf rg`
    highlight def link Lf_hl_rgFileName         Directory
    highlight def link Lf_hl_rgLineNumber       Constant
    " the color of line number if '-A' or '-B' or '-C' is in the options list
    " of `Leaderf rg`
    highlight def link Lf_hl_rgLineNumber2      Folded
    " the color of column number if '--column' in g:Lf_RgConfig
    highlight def link Lf_hl_rgColumnNumber     Constant
    highlight def Lf_hl_rgHighlight guifg=#000000 guibg=#cccc66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    " the color of `Leaderf gtags`
    highlight def link Lf_hl_gtagsFileName      Directory
    highlight def link Lf_hl_gtagsLineNumber    Constant
    highlight def Lf_hl_gtagsHighlight guifg=#000000 guibg=#cccc66 gui=NONE ctermfg=16 ctermbg=185 cterm=NONE

    highlight def link Lf_hl_previewTitle       Statusline
    highlight def link Lf_hl_popupBorder        VertSplit

    highlight def link Lf_hl_winNumber          Constant
    highlight def link Lf_hl_winIndicators      Statement
    highlight def link Lf_hl_winModified        String
    highlight def link Lf_hl_winNomodifiable    Comment
    highlight def link Lf_hl_winDirname         Directory
    highlight def link Lf_hl_quickfixFileName   Directory
    highlight def link Lf_hl_quickfixLineNumber Constant
    highlight def link Lf_hl_quickfixColumnNumber Constant
    highlight def link Lf_hl_loclistFileName    Directory
    highlight def link Lf_hl_loclistLineNumber  Constant
    highlight def link Lf_hl_loclistColumnNumber Constant
else
    " Lf_hl_popup_inputText is the wincolor of input window
    highlight def Lf_hl_popup_inputText guifg=#504945 guibg=#faefb2 gui=NONE ctermfg=239 ctermbg=253 cterm=NONE

    " Lf_hl_popup_window is the wincolor of content window
    highlight def Lf_hl_popup_window guifg=#665c54 guibg=#fcf4cf gui=NONE ctermfg=59 ctermbg=230 cterm=NONE

    " Lf_hl_popup_blank is the wincolor of statusline window
    highlight def Lf_hl_popup_blank guifg=NONE guibg=#faefb2 gui=NONE ctermbg=253 cterm=NONE

    highlight def link Lf_hl_popup_cursor Cursor
    highlight def Lf_hl_popup_prompt guifg=#c77400 guibg=NONE gui=NONE ctermfg=172 cterm=NONE
    highlight def Lf_hl_popup_spin guifg=#f12d2d guibg=NONE gui=NONE ctermfg=196 cterm=NONE
    highlight def Lf_hl_popup_normalMode guifg=#fbf1c7 guibg=#a89984 gui=bold ctermfg=230 ctermbg=137 cterm=bold
    highlight def Lf_hl_popup_inputMode guifg=#808000 guibg=#f0e68c gui=bold ctermfg=100 ctermbg=186 cterm=bold
    highlight def Lf_hl_popup_category guifg=#504945 guibg=#d5c4a1 gui=NONE ctermfg=239 ctermbg=187 cterm=NONE
    highlight def Lf_hl_popup_nameOnlyMode guifg=#665c54 guibg=#e4d9c3 gui=NONE ctermfg=59 ctermbg=251 cterm=NONE
    highlight def Lf_hl_popup_fullPathMode guifg=#665c54 guibg=#e4d9c3 gui=NONE ctermfg=59 ctermbg=251 cterm=NONE
    highlight def Lf_hl_popup_fuzzyMode guifg=#665c54 guibg=#e4d9c3 gui=NONE ctermfg=59 ctermbg=251 cterm=NONE
    highlight def Lf_hl_popup_regexMode guifg=#665c54 guibg=#e4d9c3 gui=NONE ctermfg=59 ctermbg=251 cterm=NONE
    highlight def Lf_hl_popup_cwd guifg=#7c6f64 guibg=#faefb2 gui=NONE ctermfg=243 ctermbg=253 cterm=NONE
    highlight def Lf_hl_popup_lineInfo guifg=#665c54 guibg=#e4d9c3 gui=NONE ctermfg=59 ctermbg=187 cterm=NONE
    highlight def Lf_hl_popup_total guifg=#504945 guibg=#d5c4a1 gui=NONE ctermfg=239 ctermbg=186 cterm=NONE


    " the color of the cursorline
    highlight def Lf_hl_cursorline guifg=#b57614 guibg=NONE gui=NONE ctermfg=172 cterm=NONE

    " the color of matching character
    highlight def Lf_hl_match guifg=#d65d0e guibg=NONE gui=bold ctermfg=166 cterm=bold

    " the color of matching character in `And mode`
    highlight def Lf_hl_match0 guifg=#d65d0e guibg=NONE gui=bold ctermfg=166 cterm=bold
    highlight def Lf_hl_match1 guifg=#006bc2 guibg=NONE gui=bold ctermfg=25 cterm=bold
    highlight def Lf_hl_match2 guifg=#b52bb0 guibg=NONE gui=bold ctermfg=127 cterm=bold
    highlight def Lf_hl_match3 guifg=#ff7100 guibg=NONE gui=bold ctermfg=202 cterm=bold
    highlight def Lf_hl_match4 guifg=#248888 guibg=NONE gui=bold ctermfg=30 cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight def Lf_hl_matchRefine guifg=#8f3f71 guibg=NONE gui=bold ctermfg=126 cterm=bold

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guifg=#665c54 guibg=#a5eb84 gui=NONE ctermfg=59 ctermbg=156 cterm=NONE

    " the color of `Leaderf buffer`
    highlight def link Lf_hl_bufNumber          Constant
    highlight def link Lf_hl_bufIndicators      Statement
    highlight def link Lf_hl_bufModified        String
    highlight def link Lf_hl_bufNomodifiable    Comment
    highlight def link Lf_hl_bufDirname         Directory

    " the color of `Leaderf tag`
    highlight def link Lf_hl_tagFile            Directory
    highlight def link Lf_hl_tagType            Type
    highlight def link Lf_hl_tagKeyword         Keyword

    " the color of `Leaderf bufTag`
    highlight def link Lf_hl_buftagKind         Title
    highlight def link Lf_hl_buftagScopeType    Keyword
    highlight def link Lf_hl_buftagScope        Type
    highlight def link Lf_hl_buftagDirname      Directory
    highlight def link Lf_hl_buftagLineNum      Constant
    highlight def link Lf_hl_buftagCode         Comment

    " the color of `Leaderf function`
    highlight def link Lf_hl_funcKind           Title
    highlight def link Lf_hl_funcReturnType     Type
    highlight def link Lf_hl_funcScope          Keyword
    highlight def link Lf_hl_funcName           Function
    highlight def link Lf_hl_funcDirname        Directory
    highlight def link Lf_hl_funcLineNum        Constant

    " the color of `Leaderf line`
    highlight def link Lf_hl_lineLocation       Comment

    " the color of `Leaderf self`
    highlight def link Lf_hl_selfIndex          Constant
    highlight def link Lf_hl_selfDescription    Comment

    " the color of `Leaderf help`
    highlight def link Lf_hl_helpTagfile        Comment

    " the color of `Leaderf rg`
    highlight def link Lf_hl_rgFileName         Directory
    highlight def link Lf_hl_rgLineNumber       Constant
    " the color of line number if '-A' or '-B' or '-C' is in the options list
    " of `Leaderf rg`
    highlight def link Lf_hl_rgLineNumber2      Folded
    " the color of column number if '--column' in g:Lf_RgConfig
    highlight def link Lf_hl_rgColumnNumber     Constant
    highlight def Lf_hl_rgHighlight guifg=#4d4d4d guibg=#cccc66 gui=NONE ctermfg=239 ctermbg=185 cterm=NONE

    " the color of `Leaderf gtags`
    highlight def link Lf_hl_gtagsFileName      Directory
    highlight def link Lf_hl_gtagsLineNumber    Constant
    highlight def Lf_hl_gtagsHighlight guifg=#4d4d4d guibg=#cccc66 gui=NONE ctermfg=239 ctermbg=185 cterm=NONE

    highlight def link Lf_hl_previewTitle       Statusline
    highlight def link Lf_hl_popupBorder        VertSplit

    highlight def link Lf_hl_winNumber          Constant
    highlight def link Lf_hl_winIndicators      Statement
    highlight def link Lf_hl_winModified        String
    highlight def link Lf_hl_winNomodifiable    Comment
    highlight def link Lf_hl_winDirname         Directory
    highlight def link Lf_hl_quickfixFileName   Directory
    highlight def link Lf_hl_quickfixLineNumber Constant
    highlight def link Lf_hl_quickfixColumnNumber Constant
    highlight def link Lf_hl_loclistFileName    Directory
    highlight def link Lf_hl_loclistLineNumber  Constant
    highlight def link Lf_hl_loclistColumnNumber Constant
endif

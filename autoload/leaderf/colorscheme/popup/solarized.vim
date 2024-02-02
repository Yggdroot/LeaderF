if &background ==? 'dark'
    highlight def Lf_hl_popup_inputText    guifg=#839496 ctermfg=102 guibg=#002b36 ctermbg=17
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_window", "Normal")
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_blank", "StatusLineNC")
    highlight def Lf_hl_popup_cursor       guifg=#657b83 ctermfg=66  guibg=#93a1a1 ctermbg=109
    call leaderf#colorscheme#popup#link_two("Lf_hl_popupBorder", "Normal", "VertSplit", 1)
    highlight def Lf_hl_popup_prompt       guifg=#b58900 ctermfg=136 guibg=#002b36 ctermbg=17   gui=bold cterm=bold
    highlight def Lf_hl_popup_spin         guifg=#fdf6e3 ctermfg=230 guibg=#002b36 ctermbg=17
    highlight def Lf_hl_popup_normalMode   guifg=#fdf6e3 ctermfg=230 guibg=#93a1a1 ctermbg=109  gui=bold cterm=bold
    highlight def Lf_hl_popup_inputMode    guifg=#fdf6e3 ctermfg=230 guibg=#b58900 ctermbg=136  gui=bold cterm=bold
    highlight def Lf_hl_popup_category     guifg=#eee8d5 ctermfg=224 guibg=#657b83 ctermbg=66
    highlight def Lf_hl_popup_nameOnlyMode guifg=#eee8d5 ctermfg=224 guibg=#268bd2 ctermbg=32
    highlight def Lf_hl_popup_fullPathMode guifg=#eee8d5 ctermfg=224 guibg=#586e75 ctermbg=60
    highlight def Lf_hl_popup_fuzzyMode    guifg=#eee8d5 ctermfg=224 guibg=#586e75 ctermbg=60
    highlight def Lf_hl_popup_regexMode    guifg=#eee8d5 ctermfg=224 guibg=#dc322f ctermbg=166
    highlight def Lf_hl_popup_cwd          guifg=#93a1a1 ctermfg=109 guibg=#073642 ctermbg=23
    highlight def Lf_hl_popup_lineInfo     guifg=#eee8d5 ctermfg=224 guibg=#657b83 ctermbg=66
    highlight def Lf_hl_popup_total        guifg=#fdf6e3 ctermfg=230 guibg=#93a1a1 ctermbg=109

    highlight def Lf_hl_cursorline         guifg=#fdf6e3 ctermfg=230

    highlight def Lf_hl_match              guifg=#b58900 ctermfg=136 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match0             guifg=#d33682 ctermfg=168 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match1             guifg=#6c71c4 ctermfg=62  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match2             guifg=#268bd2 ctermfg=32  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match3             guifg=#2aa198 ctermfg=36  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match4             guifg=#859900 ctermfg=100 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_matchRefine        guifg=#cb4b16 ctermfg=166

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guifg=#4d4d4d guibg=#a5eb84 gui=NONE ctermfg=239 ctermbg=156 cterm=NONE

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

    highlight def link Lf_hl_jumpsTitle         Title
    highlight def link Lf_hl_jumpsNumber        Number
    highlight def link Lf_hl_jumpsLineCol       String
    highlight def link Lf_hl_jumpsIndicator     Type
else
    highlight def Lf_hl_popup_inputText    guifg=#657b83 ctermfg=66  guibg=#fdf6e3 ctermbg=230
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_window", "Normal")
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_blank", "StatusLineNC")
    highlight def Lf_hl_popup_cursor       guifg=#b58900 ctermfg=136 guibg=#586e75 ctermbg=60
    call leaderf#colorscheme#popup#link_two("Lf_hl_popupBorder", "Normal", "VertSplit", 1)
    highlight def Lf_hl_popup_prompt       guifg=#073642 ctermfg=23  guibg=#fdf6e3 ctermbg=230  gui=bold cterm=bold
    highlight def Lf_hl_popup_spin         guifg=#002b36 ctermfg=17  guibg=#fdf6e3 ctermbg=230
    highlight def Lf_hl_popup_normalMode   guifg=#fdf6e3 ctermfg=230 guibg=#586e75 ctermbg=60   gui=bold cterm=bold
    highlight def Lf_hl_popup_inputMode    guifg=#fdf6e3 ctermfg=230 guibg=#b58900 ctermbg=136  gui=bold cterm=bold
    highlight def Lf_hl_popup_category     guifg=#eee8d5 ctermfg=224 guibg=#839496 ctermbg=102
    highlight def Lf_hl_popup_nameOnlyMode guifg=#eee8d5 ctermfg=224 guibg=#268bd2 ctermbg=32
    highlight def Lf_hl_popup_fullPathMode guifg=#eee8d5 ctermfg=224 guibg=#93a1a1 ctermbg=109
    highlight def Lf_hl_popup_fuzzyMode    guifg=#eee8d5 ctermfg=224 guibg=#93a1a1 ctermbg=109
    highlight def Lf_hl_popup_regexMode    guifg=#eee8d5 ctermfg=224 guibg=#dc322f ctermbg=166
    highlight def Lf_hl_popup_cwd          guifg=#586e75 ctermfg=60  guibg=#eee8d5 ctermbg=224
    highlight def Lf_hl_popup_lineInfo     guifg=#eee8d5 ctermfg=224 guibg=#839496 ctermbg=102
    highlight def Lf_hl_popup_total        guifg=#fdf6e3 ctermfg=230 guibg=#586e75 ctermbg=60

    highlight def Lf_hl_cursorline         guifg=#002b36 ctermfg=17

    highlight def Lf_hl_match              guifg=#b58900 ctermfg=136 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match0             guifg=#d33682 ctermfg=168 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match1             guifg=#6c71c4 ctermfg=62  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match2             guifg=#268bd2 ctermfg=32  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match3             guifg=#2aa198 ctermfg=36  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match4             guifg=#859900 ctermfg=100 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_matchRefine        guifg=#cb4b16 ctermfg=166 guibg=NONE    ctermbg=NONE gui=bold cterm=bold

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guifg=#4d4d4d guibg=#a5eb84 gui=NONE ctermfg=239 ctermbg=156 cterm=NONE

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

    highlight def link Lf_hl_jumpsTitle         Title
    highlight def link Lf_hl_jumpsNumber        Number
    highlight def link Lf_hl_jumpsLineCol       String
    highlight def link Lf_hl_jumpsIndicator     Type
endif

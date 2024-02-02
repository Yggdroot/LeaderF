if &background ==? 'dark'
    highlight def Lf_hl_popup_inputText    guifg=#ABB2BF ctermfg=145 guibg=#3B4048 ctermbg=238
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_window", "Normal")
    call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_blank", "StatusLineNC")
    highlight def Lf_hl_popup_cursor       guifg=#657b83 ctermfg=66  guibg=#98C379 ctermbg=114
    call leaderf#colorscheme#popup#link_two("Lf_hl_popupBorder", "Normal", "VertSplit", 1)
    highlight def Lf_hl_popup_prompt       guifg=#D19A66 ctermfg=173 guibg=#3B4048 ctermbg=238  gui=bold cterm=bold
    highlight def Lf_hl_popup_spin         guifg=#ABB2BF ctermfg=145 guibg=#3B4048 ctermbg=238
    highlight def Lf_hl_popup_normalMode   guifg=#2C323C ctermfg=236 guibg=#98C379 ctermbg=114  gui=bold cterm=bold
    highlight def Lf_hl_popup_inputMode    guifg=#2C323C ctermfg=236 guibg=#61AFEF ctermbg=39   gui=bold cterm=bold
    highlight def Lf_hl_popup_category     guifg=#2C323C ctermfg=236 guibg=#ABB2BF ctermbg=145
    highlight def Lf_hl_popup_nameOnlyMode guifg=#2C323C ctermfg=236 guibg=#C678DD ctermbg=170
    highlight def Lf_hl_popup_fullPathMode guifg=#2C323C ctermfg=236 guibg=#E5C07B ctermbg=180
    highlight def Lf_hl_popup_fuzzyMode    guifg=#2C323C ctermfg=236 guibg=#56B6C2 ctermbg=38
    highlight def Lf_hl_popup_regexMode    guifg=#2C323C ctermfg=236 guibg=#E06C75 ctermbg=204
    highlight def Lf_hl_popup_cwd          guifg=#ABB2BF ctermfg=145 guibg=#3E4452 ctermbg=237
    highlight def Lf_hl_popup_lineInfo     guifg=#ABB2BF ctermfg=145 guibg=#3E4452 ctermbg=237
    highlight def Lf_hl_popup_total        guifg=#2C323C ctermfg=236 guibg=#ABB2BF ctermbg=145

    highlight def Lf_hl_cursorline         guifg=#ABB2BF ctermfg=145 guibg=NONE    ctermbg=NONE

    highlight def Lf_hl_match              guifg=#E06C75 ctermfg=204 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match0             guifg=#E06C75 ctermfg=204 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match1             guifg=#D19A66 ctermfg=173 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match2             guifg=#61AFEF ctermfg=39  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match3             guifg=#98C379 ctermfg=114 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match4             guifg=#56B6C2 ctermfg=38  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_matchRefine        guifg=#D19A66 ctermfg=173

    highlight def Lf_hl_selection          guifg=#2C323C ctermfg=236 guibg=#E5C07B ctermbg=180  gui=NONE cterm=NONE

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

if &background ==? 'dark'
    highlight def Lf_hl_popup_inputText    guifg=#839496 ctermfg=102 guibg=#002b36 ctermbg=17
    highlight def Lf_hl_popup_window       guifg=#839496 ctermfg=102 guibg=#002b36 ctermbg=17
    highlight def Lf_hl_popup_blank        guibg=#073642 ctermbg=23
    highlight def Lf_hl_popup_cursor       guifg=#657b83 ctermfg=66  guibg=#93a1a1 ctermbg=109
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

    highlight def link Lf_hl_popupBorder   Normal

    highlight def Lf_hl_cursorline         guifg=#fdf6e3 ctermfg=230

    highlight def Lf_hl_match              guifg=#b58900 ctermfg=136 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match0             guifg=#d33682 ctermfg=168 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match1             guifg=#6c71c4 ctermfg=62  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match2             guifg=#268bd2 ctermfg=32  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match3             guifg=#2aa198 ctermfg=36  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match4             guifg=#859900 ctermfg=100 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_matchRefine        guifg=#cb4b16 ctermfg=166
else
    highlight def Lf_hl_popup_inputText    guifg=#657b83 ctermfg=66  guibg=#fdf6e3 ctermbg=230
    highlight def Lf_hl_popup_window       guifg=#657b83 ctermfg=66  guibg=#fdf6e3 ctermbg=230
    highlight def Lf_hl_popup_blank        guibg=#eee8d5 ctermbg=224
    highlight def Lf_hl_popup_cursor       guifg=#b58900 ctermfg=136 guibg=#586e75 ctermbg=60
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

    highlight def link Lf_hl_popupBorder   Normal

    highlight def Lf_hl_cursorline         guifg=#002b36 ctermfg=17

    highlight def Lf_hl_match              guifg=#b58900 ctermfg=136 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match0             guifg=#d33682 ctermfg=168 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match1             guifg=#6c71c4 ctermfg=62  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match2             guifg=#268bd2 ctermfg=32  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match3             guifg=#2aa198 ctermfg=36  guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_match4             guifg=#859900 ctermfg=100 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
    highlight def Lf_hl_matchRefine        guifg=#cb4b16 ctermfg=166 guibg=NONE    ctermbg=NONE gui=bold cterm=bold
endif

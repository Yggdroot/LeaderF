" ============================================================================
" File:        autoload/leaderf/colorscheme/popup/gruvbox_material.vim
" Description: Gruvbox with Material Palette
" Author:      Sainnhe Park <sainnhe@gmail.com>
" Website:     https://github.com/sainnhe/gruvbox-material/
" Note:
" License:     MIT, Anti-996
" ============================================================================

if &background ==# 'dark'
    if get(g:, 'gruvbox_material_background', 'medium') ==# 'hard'
        highlight Lf_hl_popup_inputText guifg=#ddc7a1 guibg=#3c3836 gui=NONE ctermfg=223 ctermbg=237 cterm=NONE
        highlight Lf_hl_popup_window guifg=#ddc7a1 guibg=#3c3836 gui=NONE ctermfg=223 ctermbg=237 cterm=NONE
    elseif get(g:, 'gruvbox_material_background', 'medium') ==# 'medium'
        highlight Lf_hl_popup_inputText guifg=#ddc7a1 guibg=#504945 gui=NONE ctermfg=223 ctermbg=239 cterm=NONE
        highlight Lf_hl_popup_window guifg=#ddc7a1 guibg=#504945 gui=NONE ctermfg=223 ctermbg=239 cterm=NONE
    elseif get(g:, 'gruvbox_material_background', 'medium') ==# 'soft'
        highlight Lf_hl_popup_inputText guifg=#ddc7a1 guibg=#504945 gui=NONE ctermfg=223 ctermbg=239 cterm=NONE
        highlight Lf_hl_popup_window guifg=#ddc7a1 guibg=#504945 gui=NONE ctermfg=223 ctermbg=239 cterm=NONE
    endif

    highlight Lf_hl_popup_prompt guifg=#89b482 ctermfg=108
    highlight Lf_hl_popup_spin guifg=#d8a657 ctermfg=214
    highlight Lf_hl_popup_normalMode guifg=#282828 guibg=#a89984 gui=bold ctermfg=235 ctermbg=246 cterm=bold
    highlight Lf_hl_popup_inputMode guifg=#282828 guibg=#a89984 gui=bold ctermfg=235 ctermbg=246 cterm=bold
    highlight Lf_hl_popup_category guifg=#ddc7a1 guibg=#7c6f64 gui=NONE ctermfg=223 ctermbg=243 cterm=NONE
    highlight Lf_hl_popup_nameOnlyMode guifg=#ddc7a1 guibg=#665c54 gui=NONE ctermfg=223 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_fullPathMode guifg=#ddc7a1 guibg=#665c54 gui=NONE ctermfg=223 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_fuzzyMode guifg=#ddc7a1 guibg=#665c54 gui=NONE ctermfg=223 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_regexMode guifg=#ddc7a1 guibg=#665c54 gui=NONE ctermfg=223 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_cwd guifg=#ddc7a1 guibg=#504945 gui=NONE ctermfg=223 ctermbg=239 cterm=NONE
    " Lf_hl_popup_blank is the wincolor of statusline window
    highlight! link Lf_hl_popup_blank Lf_hl_popup_window
    highlight Lf_hl_popup_lineInfo guifg=#ddc7a1 guibg=#665c54 gui=NONE ctermfg=223 ctermbg=241 cterm=NONE
    highlight Lf_hl_popup_total guifg=#282828 guibg=#a89984 gui=NONE ctermfg=235 ctermbg=246 cterm=NONE

    highlight def link Lf_hl_popup_cursor Cursor
    " the color of the cursorline
    highlight def Lf_hl_cursorline guifg=#d4be98 guibg=NONE gui=NONE ctermfg=223 ctermbg=NONE cterm=NONE

    " the color of matching character
    highlight def Lf_hl_match  guifg=#a9b665 guibg=NONE gui=bold ctermfg=142 ctermbg=NONE cterm=bold

    " the color of matching character in `And mode`
    highlight def Lf_hl_match0 guifg=#a9b665 guibg=NONE gui=bold ctermfg=142 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match1 guifg=#89b482 guibg=NONE gui=bold ctermfg=108 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match2 guifg=#7daea3 guibg=NONE gui=bold ctermfg=109 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match3 guifg=#d3869b guibg=NONE gui=bold ctermfg=175 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match4 guifg=#e78a4e guibg=NONE gui=bold ctermfg=208 ctermbg=NONE cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight def Lf_hl_matchRefine gui=bold guifg=#ea6962 cterm=bold ctermfg=167

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guibg=#34381b gui=NONE ctermbg=22 cterm=NONE

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
else
    if get(g:, 'gruvbox_material_background', 'medium') ==# 'hard'
        highlight Lf_hl_popup_inputText guifg=#4f3829 guibg=#f2e5bc gui=NONE ctermfg=237 ctermbg=228 cterm=NONE
        highlight Lf_hl_popup_window guifg=#4f3829 guibg=#f2e5bc gui=NONE ctermfg=237 ctermbg=228 cterm=NONE
    elseif get(g:, 'gruvbox_material_background', 'medium') ==# 'medium'
        highlight Lf_hl_popup_inputText guifg=#4f3829 guibg=#ebdbb2 gui=NONE ctermfg=237 ctermbg=223 cterm=NONE
        highlight Lf_hl_popup_window guifg=#4f3829 guibg=#ebdbb2 gui=NONE ctermfg=237 ctermbg=223 cterm=NONE
    elseif get(g:, 'gruvbox_material_background', 'medium') ==# 'soft'
        highlight Lf_hl_popup_inputText guifg=#4f3829 guibg=#d5c4a1 gui=NONE ctermfg=237 ctermbg=250 cterm=NONE
        highlight Lf_hl_popup_window guifg=#4f3829 guibg=#d5c4a1 gui=NONE ctermfg=237 ctermbg=250 cterm=NONE
    endif

    highlight Lf_hl_popup_prompt guifg=#4c7a5d ctermfg=165
    highlight Lf_hl_popup_spin guifg=#b47109 ctermfg=136
    highlight Lf_hl_popup_normalMode guifg=#ebdbb2 guibg=#7c6f64 gui=bold ctermfg=235 ctermbg=243 cterm=bold
    highlight Lf_hl_popup_inputMode guifg=#ebdbb2 guibg=#7c6f64 gui=bold ctermfg=235 ctermbg=243 cterm=bold
    highlight Lf_hl_popup_category guifg=#4f3829 guibg=#a89984 gui=NONE ctermfg=237 ctermbg=246 cterm=NONE
    highlight Lf_hl_popup_nameOnlyMode guifg=#4f3829 guibg=#bdae93 gui=NONE ctermfg=237 ctermbg=248 cterm=NONE
    highlight Lf_hl_popup_fullPathMode guifg=#4f3829 guibg=#bdae93 gui=NONE ctermfg=237 ctermbg=248 cterm=NONE
    highlight Lf_hl_popup_fuzzyMode guifg=#4f3829 guibg=#bdae93 gui=NONE ctermfg=237 ctermbg=248 cterm=NONE
    highlight Lf_hl_popup_regexMode guifg=#4f3829 guibg=#bdae93 gui=NONE ctermfg=237 ctermbg=248 cterm=NONE
    highlight Lf_hl_popup_cwd guifg=#4f3829 guibg=#d5c4a1 gui=NONE ctermfg=237 ctermbg=250 cterm=NONE
    " Lf_hl_popup_blank is the wincolor of statusline window
    highlight! link Lf_hl_popup_blank Lf_hl_popup_window
    highlight Lf_hl_popup_lineInfo guifg=#4f3829 guibg=#bdae93 gui=NONE ctermfg=237 ctermbg=248 cterm=NONE
    highlight Lf_hl_popup_total guifg=#ebdbb2 guibg=#7c6f64 gui=NONE ctermfg=235 ctermbg=243 cterm=NONE

    highlight def link Lf_hl_popup_cursor Cursor
    " the color of the cursorline
    highlight def Lf_hl_cursorline guifg=#654735 guibg=NONE gui=NONE ctermfg=237 ctermbg=NONE cterm=NONE

    " the color of matching character
    highlight def Lf_hl_match  guifg=#6c782e guibg=NONE gui=bold ctermfg=100 ctermbg=NONE cterm=bold

    " the color of matching character in `And mode`
    highlight def Lf_hl_match0 guifg=#6c782e guibg=NONE gui=bold ctermfg=100 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match1 guifg=#4c7a5d guibg=NONE gui=bold ctermfg=165 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match2 guifg=#45707a guibg=NONE gui=bold ctermfg=24 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match3 guifg=#945e80 guibg=NONE gui=bold ctermfg=96 ctermbg=NONE cterm=bold
    highlight def Lf_hl_match4 guifg=#c35e0a guibg=NONE gui=bold ctermfg=130 ctermbg=NONE cterm=bold

    " the color of matching character in nameOnly mode when ';' is typed
    highlight def Lf_hl_matchRefine gui=bold guifg=#c14a4a cterm=bold ctermfg=88

    " the color of help in normal mode when <F1> is pressed
    highlight def link Lf_hl_help               Comment
    highlight def link Lf_hl_helpCmd            Identifier

    " the color when select multiple lines
    highlight def Lf_hl_selection guibg=#daf0a7 gui=NONE ctermbg=194 cterm=NONE

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
endif


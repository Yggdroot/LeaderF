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
" like use `reverse` attribute.

" Lf_hl_popup_inputText is the wincolor of input window
highlight Lf_hl_popup_inputText guifg=#87ceeb guibg=#4d4d4d gui=NONE ctermfg=117 ctermbg=239 cterm=NONE

" Lf_hl_popup_window is the wincolor of content window
call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_window", "Pmenu")

call leaderf#colorscheme#popup#link_no_reverse("Lf_hl_popup_cursor", "Cursor")
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
" Lf_hl_popup_blank is the wincolor of statusline window
highlight Lf_hl_popup_blank guifg=NONE guibg=#4b4e50 gui=NONE ctermbg=239 cterm=NONE
highlight Lf_hl_popup_lineInfo guifg=#353129 guibg=#dce6da gui=NONE ctermfg=236 ctermbg=254 cterm=NONE
highlight Lf_hl_popup_total guifg=#353129 guibg=#b8ccbb gui=NONE ctermfg=236 ctermbg=151 cterm=NONE

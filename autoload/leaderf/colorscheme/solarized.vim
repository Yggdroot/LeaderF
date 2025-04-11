if &background ==? 'dark'
    let s:palette = {
                \ 'match':           { 'guifg': '#b58900', 'ctermfg': '136'   },
                \ 'match0':          { 'guifg': '#d33682', 'ctermfg': '168'   },
                \ 'match1':          { 'guifg': '#6c71c4', 'ctermfg': '62'    },
                \ 'match2':          { 'guifg': '#268bd2', 'ctermfg': '32'    },
                \ 'match3':          { 'guifg': '#2aa198', 'ctermfg': '36'    },
                \ 'match4':          { 'guifg': '#859900', 'ctermfg': '100'   },
                \ 'matchRefine':     { 'guifg': '#cb4b16', 'ctermfg': '166'   },
                \ 'cursorline':      { 'guifg': '#fdf6e3', 'ctermfg': '230'   },
                \ 'stlName':         { 'guifg': '#fdf6e3', 'ctermfg': '230',  'guibg': '#b58900', 'ctermbg': '136', 'gui': 'bold,nocombine', 'cterm': 'bold,nocombine' },
                \ 'stlCategory':     { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#657b83', 'ctermbg': '66',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlNameOnlyMode': { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#268bd2', 'ctermbg': '32',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFullPathMode': { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#586e75', 'ctermbg': '60',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFuzzyMode':    { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#586e75', 'ctermbg': '60',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlRegexMode':    { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#dc322f', 'ctermbg': '166', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlCwd':          { 'guifg': '#93a1a1', 'ctermfg': '109',  'guibg': '#073642', 'ctermbg': '23',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlBlank':        { 'guifg': '#93a1a1', 'ctermfg': '109',  'guibg': '#073642', 'ctermbg': '23',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlLineInfo':     { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#657b83', 'ctermbg': '66',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlTotal':        { 'guifg': '#fdf6e3', 'ctermfg': '230',  'guibg': '#93a1a1', 'ctermbg': '109', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ }
else
    let s:palette = {
                \ 'match':           { 'guifg': '#b58900', 'ctermfg': '136'   },
                \ 'match0':          { 'guifg': '#d33682', 'ctermfg': '168'   },
                \ 'match1':          { 'guifg': '#6c71c4', 'ctermfg': '62'    },
                \ 'match2':          { 'guifg': '#268bd2', 'ctermfg': '32'    },
                \ 'match3':          { 'guifg': '#2aa198', 'ctermfg': '36'    },
                \ 'match4':          { 'guifg': '#859900', 'ctermfg': '100'   },
                \ 'matchRefine':     { 'guifg': '#cb4b16', 'ctermfg': '166'   },
                \ 'cursorline':      { 'guifg': '#002b36', 'ctermfg': '17'    },
                \ 'stlName':         { 'guifg': '#fdf6e3', 'ctermfg': '230',  'guibg': '#b58900', 'ctermbg': '136', 'gui': 'bold,nocombine', 'cterm': 'bold,nocombine' },
                \ 'stlCategory':     { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#839496', 'ctermbg': '102', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlNameOnlyMode': { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#268bd2', 'ctermbg': '32',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFullPathMode': { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#93a1a1', 'ctermbg': '109', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFuzzyMode':    { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#93a1a1', 'ctermbg': '109', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlRegexMode':    { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#dc322f', 'ctermbg': '166', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlCwd':          { 'guifg': '#586e75', 'ctermfg': '60',   'guibg': '#eee8d5', 'ctermbg': '224', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlBlank':        { 'guifg': '#586e75', 'ctermfg': '60',   'guibg': '#eee8d5', 'ctermbg': '224', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlLineInfo':     { 'guifg': '#eee8d5', 'ctermfg': '224',  'guibg': '#839496', 'ctermbg': '102', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlTotal':        { 'guifg': '#fdf6e3', 'ctermfg': '230',  'guibg': '#586e75', 'ctermbg': '60',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ }
endif

let g:leaderf#colorscheme#solarized#palette = leaderf#colorscheme#mergePalette(s:palette)

if &background ==? 'dark'
    let s:palette = {
                \ 'match':           { 'guifg': '#E06C75', 'ctermfg': '204'   },
                \ 'match0':          { 'guifg': '#E06C75', 'ctermfg': '204'   },
                \ 'match1':          { 'guifg': '#D19A66', 'ctermfg': '173'   },
                \ 'match2':          { 'guifg': '#61AFEF', 'ctermfg': '39'    },
                \ 'match3':          { 'guifg': '#98C379', 'ctermfg': '114'   },
                \ 'match4':          { 'guifg': '#56B6C2', 'ctermfg': '38'    },
                \ 'matchRefine':     { 'guifg': '#D19A66', 'ctermfg': '173'   },
                \ 'cursorline':      { 'guifg': '#ABB2BF', 'ctermfg': '145'   },
                \ 'stlName':         { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#98C379', 'ctermbg': '114', 'gui': 'bold', 'cterm': 'bold' },
                \ 'stlCategory':     { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#ABB2BF', 'ctermbg': '145', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlNameOnlyMode': { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#C678DD', 'ctermbg': '170', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlFullPathMode': { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#E5C07B', 'ctermbg': '180', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlFuzzyMode':    { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#56B6C2', 'ctermbg': '38',  'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlRegexMode':    { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#E06C75', 'ctermbg': '204', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlCwd':          { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#3E4452', 'ctermbg': '237', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlBlank':        { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#282C34', 'ctermbg': '235', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlLineInfo':     { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#3E4452', 'ctermbg': '237', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlTotal':        { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#98C379', 'ctermbg': '114', 'gui': 'NONE', 'cterm': 'NONE' },
                \ 'stlSpin':         { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#282C34', 'ctermbg': '235', 'gui': 'NONE', 'cterm': 'NONE' },
                \ }
endif

let g:leaderf#colorscheme#onedark#palette = leaderf#colorscheme#mergePalette(s:palette)

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
                \ 'stlName':         { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#98C379', 'ctermbg': '114', 'gui': 'bold,nocombine', 'cterm': 'bold,nocombine' },
                \ 'stlCategory':     { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#ABB2BF', 'ctermbg': '145', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlNameOnlyMode': { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#C678DD', 'ctermbg': '170', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFullPathMode': { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#E5C07B', 'ctermbg': '180', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlFuzzyMode':    { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#56B6C2', 'ctermbg': '38',  'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlRegexMode':    { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#E06C75', 'ctermbg': '204', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlCwd':          { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#3E4452', 'ctermbg': '237', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlBlank':        { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#282C34', 'ctermbg': '235', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlLineInfo':     { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#3E4452', 'ctermbg': '237', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlTotal':        { 'guifg': '#2C323C', 'ctermfg': '236',  'guibg': '#98C379', 'ctermbg': '114', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ 'stlSpin':         { 'guifg': '#ABB2BF', 'ctermfg': '145',  'guibg': '#282C34', 'ctermbg': '235', 'gui': 'nocombine', 'cterm': 'nocombine' },
                \ }
endif

let g:leaderf#colorscheme#onedark#palette = leaderf#colorscheme#mergePalette(s:palette)

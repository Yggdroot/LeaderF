" ============================================================================
" File:        Any.vim
" Description:
" Author:      Yggdroot <archofortune@gmail.com>
" Website:     https://github.com/Yggdroot
" Note:
" License:     Apache License, Version 2.0
" ============================================================================

if leaderf#versionCheck() == 0  " this check is necessary
    finish
endif

exec g:Lf_py "from leaderf.anyExpl import *"

function! leaderf#Any#Maps(category)
    let b:Lf_AnyExplManager = "anyHub._managers['".a:category."']."
    nmapclear <buffer>
    nnoremap <buffer> <silent> <CR>          :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> o             :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> <2-LeftMouse> :exec g:Lf_py b:Lf_AnyExplManager."accept()"<CR>
    nnoremap <buffer> <silent> x             :exec g:Lf_py b:Lf_AnyExplManager."accept('h')"<CR>
    nnoremap <buffer> <silent> v             :exec g:Lf_py b:Lf_AnyExplManager."accept('v')"<CR>
    nnoremap <buffer> <silent> t             :exec g:Lf_py b:Lf_AnyExplManager."accept('t')"<CR>
    nnoremap <buffer> <silent> q             :exec g:Lf_py b:Lf_AnyExplManager."quit()"<CR>
    " nnoremap <buffer> <silent> <Esc>         :exec g:Lf_py b:Lf_AnyExplManager."quit()"<CR>
    nnoremap <buffer> <silent> i             :exec g:Lf_py b:Lf_AnyExplManager."input()"<CR>
    nnoremap <buffer> <silent> <Tab>         :exec g:Lf_py b:Lf_AnyExplManager."input()"<CR>
    nnoremap <buffer> <silent> <F1>          :exec g:Lf_py b:Lf_AnyExplManager."toggleHelp()"<CR>
    if has_key(g:Lf_NormalMap, a:category)
        for i in g:Lf_NormalMap[a:category]
            exec 'nnoremap <buffer> <silent> '.i[0].' '.i[1]
        endfor
    endif
endfunction

let g:Lf_Helps = {
            \ "file":           "search files",
            \ "buffer":         "search buffers",
            \ "mru":            "search most recently used files",
            \ "tag":            "navigate tags using the tags file",
            \ "bufTag":         "navigate tags in the buffer",
            \ "function":       "navigate functions or methods in the buffer",
            \ "line":           "search a line in the buffer",
            \ "cmdHistory":     "execute the command in the history",
            \ "searchHistory":  "execute the search command in the history",
            \ "help":           "navigate the help tags",
            \ "colorscheme":    "switch between colorschemes",
            \ "self":           "execute the commands of itself",
            \ "rg":             "grep using rg",
            \ }

let g:Lf_Arguments = {
            \ "file":[
            \           [
            \               {"name": ["directory"], "nargs": "?", "help": "serarch files under <directory>"},
            \               {"name": ["--file"], "nargs": "+", "help": "read file list from the specified file."},
            \           ],
            \           {"name": ["--no-ignore"], "nargs": 0, "help": "don't respect ignore files (.gitignore, .ignore, etc.)."},
            \   ],
            \ "buffer":[
            \           {"name": ["--all"], "nargs": 0, "help": "search all buffers in addition to the listed buffers"},
            \           {"name": ["--tabpage"], "nargs": 0, "help": "search buffers in current tabpage"},
            \   ],
            \ "mru":[
            \           {"name": ["--cwd"], "nargs": 0, "help": "search MRU in current working directory"},
            \   ],
            \ "tag":[],
            \ "bufTag":[
            \           {"name": ["--all"], "nargs": 0, "help": "search bufTag in all opening buffers"},
            \   ],
            \ "function":[
            \           {"name": ["--all"], "nargs": 0, "help": "search functions in all opening buffers"},
            \   ],
            \ "line":[
            \           {"name": ["--all"], "nargs": 0, "help": "search lines in all opening buffers"},
            \   ],
            \ "cmdHistory":[],
            \ "searchHistory":[],
            \ "help":[],
            \ "colorscheme":[],
            \ "self":[],
            \ "rg":[
            \           {"name": ["-e", "--regexp"], "action": "append", "metavar": "<PATTERN>...",
            \               "help": "A pattern to search for. This option can be provided multiple times, where all patterns given are searched."},
            \           {"name": ["-F", "--fixed-strings"], "nargs": 0, "help": "Treat the pattern as a literal string instead of a regular expression."},
            \           {"name": ["-i", "--ignore-case"], "nargs": 0, "help": "Searches case insensitively."},
            \           {"name": ["-L", "--follow"], "nargs": 0, "help": "Follow symbolic links while traversing directories."},
            \           {"name": ["-P", "--pcre2"], "nargs": 0, "help": "When this flag is present, rg will use the PCRE2 regex engine instead of its default regex engine."},
            \           {"name": ["-S", "--smart-case"], "nargs": 0, "help": "Searches case insensitively if the pattern is all lowercase, case sensitively otherwise."},
            \           {"name": ["-s", "--case-sensitive"], "nargs": 0, "help": "Searches case sensitively."},
            \           {"name": ["-v", "--invert-match"], "nargs": 0, "help": "Invert matching. Show lines that do not match the given patterns."},
            \           {"name": ["-w", "--word-regexp"], "nargs": 0, "help": "Only show matches surrounded by word boundaries. This is roughly equivalent to putting \\b before and after all of the search patterns."},
            \           {"name": ["-x", "--line-regexp"], "nargs": 0, "help": "Only show matches surrounded by line boundaries."},
            \           {"name": ["--hidden"], "nargs": 0, "help": "Search hidden files and directories. By default, hidden files and directories are skipped."},
            \           {"name": ["--no-config"], "nargs": 0, "help": "Never read configuration files. When this flag is present, rg will not respect the RIPGREP_CONFIG_PATH environment variable."},
            \           {"name": ["--no-ignore"], "nargs": 0, "help": "Don't respect ignore files (.gitignore, .ignore, etc.). This implies --no-ignore-parent and --no-ignore-vcs."},
            \           {"name": ["--no-ignore-global"], "nargs": 0,
            \               "help": "Don't respect ignore files that come from 'global' sources such as git's `core.excludesFile` configuration option (which defaults to `$HOME/.config/git/ignore`)."},
            \           {"name": ["--no-ignore-parent"], "nargs": 0, "help": "Don't respect ignore files (.gitignore, .ignore, etc.) in parent directories."},
            \           {"name": ["--no-ignore-vcs"], "nargs": 0, "help": "Don't respect version control ignore files (.gitignore, etc.)."},
            \           {"name": ["-E", "--encoding"], "nargs": 1, "metavar": "<ENCODING>", "help": "Specify the text encoding that rg will use on all files searched."},
            \           {"name": ["-M", "--max-columns"], "nargs": 1, "metavar": "<NUM>", "help": "Don't print lines longer than this limit in bytes."},
            \           {"name": ["-m", "--max-count"], "nargs": 1, "metavar": "<NUM>", "help": "Limit the number of matching lines per file searched to NUM."},
            \           {"name": ["--max-depth"], "nargs": 1, "metavar": "<NUM>", "help": "Limit the depth of directory traversal to NUM levels beyond the paths given."},
            \           {"name": ["--max-filesize"], "nargs": 1, "metavar": "<NUM+SUFFIX?>", "help": "Ignore files larger than NUM in size. This does not apply to directories."},
            \           {"name": ["-g", "--glob"], "action": "append", "metavar": "<GLOB>...",
            \               "help": "Include or exclude files and directories for searching that match the given glob.(This option can be provided multiple times.)"},
            \           {"name": ["--iglob"], "action": "append", "metavar": "<GLOB>...",
            \               "help": "Include or exclude files and directories for searching that match the given glob. Globs are matched case insensitively.(This option can be provided multiple times.)"},
            \           {"name": ["--ignore-file"], "action": "append", "metavar": "<PATH>...",
            \               "help": "Specifies a path to one or more .gitignore format rules files."},
            \           {"name": ["-t", "--type"], "action": "append", "metavar": "<TYPE>...",
            \               "help": "Only search files matching TYPE. Multiple type flags may be provided."},
            \           {"name": ["-T", "--type-not"], "action": "append", "metavar": "<TYPE>...",
            \               "help": "Do not search files matching TYPE. Multiple type-not flags may be provided."},
            \           {"name": ["PATH"], "nargs": "*", "metavar": "<PATH>",
            \               "help": "A file or directory to search. Directories are searched recursively. Paths specified on the command line override glob and ignore rules."},
            \           [
            \               {"name": ["--current-buffer"], "nargs": 0, "help": "Searches in current buffer."},
            \               {"name": ["--all-buffers"], "nargs": 0, "help": "Searches in all listed buffers."},
            \           ],
            \   ],
            \}

let g:Lf_CommonArguments = [
            \ {"name": ["--reverse"], "nargs": 0, "help": "show results in bottom-up order"},
            \ {"name": ["--stayOpen"], "nargs": 0, "help": "don't quit LeaderF after accepting an entry"},
            \ [
            \   {"name": ["--input"], "nargs": 1, "help": "specifies INPUT as the pattern inputted in advance"},
            \   {"name": ["--cword"], "nargs": 0, "help": "current word under cursor is inputted in advance"},
            \ ],
            \ [
            \   {"name": ["--top"],        "nargs": 0, "help": "the LeaderF window is at the top of the screen"},
            \   {"name": ["--bottom"],     "nargs": 0, "help": "the LeaderF window is at the bottom of the screen"},
            \   {"name": ["--left"],       "nargs": 0, "help": "the LeaderF window is at the left of the screen"},
            \   {"name": ["--right"],      "nargs": 0, "help": "the LeaderF window is at the right of the screen"},
            \   {"name": ["--belowright"], "nargs": 0, "help": "the LeaderF window is at the belowright of the screen"},
            \   {"name": ["--aboveleft"],  "nargs": 0, "help": "the LeaderF window is at the aboveleft of the screen"},
            \   {"name": ["--fullScreen"], "nargs": 0, "help": "the LeaderF window takes up the full screen"},
            \ ],
            \ [
            \   {"name": ["--nameOnly"], "nargs": 0, "help": "LeaderF is in NameOnly mode by default"},
            \   {"name": ["--fullPath"], "nargs": 0, "help": "LeaderF is in FullPath mode by default"},
            \   {"name": ["--fuzzy"],    "nargs": 0, "help": "LeaderF is in Fuzzy mode by default"},
            \   {"name": ["--regexMode"],    "nargs": 0, "help": "LeaderF is in Regex mode by default"},
            \ ],
            \]

" arguments is something like g:Lf_CommonArguments
" return something like
" [
"   ["--input", "--cword"],
"   ["--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"],
"   ["--nameOnly", "--fullPath", "--fuzzy", "--regexMode"],
" ]
function! s:Lf_Refine(arguments)
    let result = []
    for arg in a:arguments
        if type(arg) == type([])
            let sublist = []
            for i in arg
                let sublist += i["name"]
            endfor
            call add(result, sublist)
        else
            call extend(result, arg["name"])
        endif
    endfor
    return result
endfunction

function! leaderf#Any#parseArguments(argLead, cmdline, cursorPos)
    let argList = split(a:cmdline[:a:cursorPos-1], '[ \t!]\+')
    let argNum = len(argList)
    if argNum == 1  " Leaderf
        return keys(g:Lf_Arguments) + keys(g:Lf_Extensions)
    elseif argNum == 2 && a:cmdline[a:cursorPos-1] !~ '\s'  " 'Leaderf b'
        return filter(keys(g:Lf_Arguments) + keys(g:Lf_Extensions), "v:val =~? '^".a:argLead."'")
    else
        let existingOptions = a:cmdline[a:cursorPos-1] !~ '\s' ? argList[2:-2] : argList[2:]
        let options = []
        if has_key(g:Lf_Extensions, argList[1])
            let arguments = get(g:Lf_Extensions[argList[1]], "arguments", [])
        elseif has_key(g:Lf_Arguments, argList[1])
            let arguments = g:Lf_Arguments[argList[1]]
        else
            let arguments = []
        endif
        for opt in s:Lf_Refine(arguments + g:Lf_CommonArguments)
            if type(opt) == type([])
                if len(filter(copy(opt), "index(".string(existingOptions).", v:val) >= 0")) == 0
                    let options += opt
                endif
            elseif index(existingOptions, opt) == -1
                call add(options, opt)
            endif
        endfor
        return filter(filter(copy(options), "v:val =~? '^".a:argLead."'"), "v:val =~ '^-'")
    endif
endfunction

function! leaderf#Any#start(bang, args)
    if a:args == ""

    else
        call leaderf#LfPy("anyHub.start(r''' ".a:args." ''', bang=".a:bang.")")
    endif
endfunction


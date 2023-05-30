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
    nnoremap <buffer> <silent> p             :exec g:Lf_py b:Lf_AnyExplManager."_previewResult(True)"<CR>
    nnoremap <buffer> <silent> j             j:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    nnoremap <buffer> <silent> k             k:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Up>          <Up>:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    nnoremap <buffer> <silent> <Down>        <Down>:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageUp>      <PageUp>:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    nnoremap <buffer> <silent> <PageDown>    <PageDown>:exec g:Lf_py b:Lf_AnyExplManager."_previewResult(False)"<CR>
    if has("nvim")
        nnoremap <buffer> <silent> <C-Up>    :exec g:Lf_py b:Lf_AnyExplManager."_toUpInPopup()"<CR>
        nnoremap <buffer> <silent> <C-Down>  :exec g:Lf_py b:Lf_AnyExplManager."_toDownInPopup()"<CR>
        nnoremap <buffer> <silent> <Esc>     :exec g:Lf_py b:Lf_AnyExplManager."_closePreviewPopup()"<CR>
    endif
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
            \ "gtags":          "navigate tags using the gtags",
            \ "filetype":       "navigate the filetype",
            \ "command":        "execute built-in/user-defined Ex commands",
            \ "window":         "search windows",
            \ "quickfix":       "navigate quickfix",
            \ "loclist":        "navigate location list",
            \ "jumps":          "navigate jumps list",
            \ }

let g:Lf_Arguments = {
            \ "file":[
            \           [
            \               {"name": ["directory"], "nargs": "*", "help": "serarch files under <directory>"},
            \               {"name": ["--file"], "nargs": "+", "help": "read file list from the specified file."},
            \           ],
            \           {"name": ["--no-ignore"], "nargs": 0, "help": "don't respect ignore files (.gitignore, .ignore, etc.)."},
            \   ],
            \ "buffer":[
            \           {"name": ["--all"], "nargs": 0, "help": "search all buffers in addition to the listed buffers"},
            \           {"name": ["--tabpage"], "nargs": 0, "help": "search buffers in current tabpage"},
            \   ],
            \ "mru":[
            \           [
            \               {"name": ["--cwd"], "nargs": 0, "help": "search MRU in current working directory"},
            \               {"name": ["--project"], "nargs": 0, "help": "search MRU in the project"},
            \           ],
            \           {"name": ["--no-split-path"], "nargs": 0, "help": "do not split the path"},
            \           {"name": ["--absolute-path"], "nargs": 0, "help": "show absolute path"},
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
            \           {"name": ["-A", "--after-context"], "nargs": 1, "metavar": "<NUM>", "help": "Show NUM lines after each match."},
            \           {"name": ["-B", "--before-context"], "nargs": 1, "metavar": "<NUM>", "help": "Show NUM lines before each match."},
            \           {"name": ["-C", "--context"], "nargs": 1, "metavar": "<NUM>", "help": "Show NUM lines before and after each match."},
            \           {"name": ["--context-separator"], "nargs": 1, "metavar": "<SEPARATOR>", "help": "The string used to separate non-contiguous context lines in the output."},
            \           {"name": ["--crlf"], "nargs": 0, "help": "ripgrep will treat CRLF ('\r\n') as a line terminator instead of just '\n'."},
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
            \           {"name": ["--binary"], "nargs": 0, "help": "Enabling this flag will cause ripgrep to search binary files."},
            \           {"name": ["--column"], "nargs": 0, "help": "Show column numbers (1-based). This only shows the column numbers for the first match on each line."},
            \           {"name": ["--hidden"], "nargs": 0, "help": "Search hidden files and directories. By default, hidden files and directories are skipped."},
            \           {"name": ["--heading"], "nargs": 0, "help": "Prints the file path above clusters of matches from each file instead of printing the file path as a prefix for each matched line."},
            \           {"name": ["--no-config"], "nargs": 0, "help": "Never read configuration files. When this flag is present, rg will not respect the RIPGREP_CONFIG_PATH environment variable."},
            \           {"name": ["--no-ignore"], "nargs": 0, "help": "Don't respect ignore files (.gitignore, .ignore, etc.). This implies --no-ignore-parent and --no-ignore-vcs."},
            \           {"name": ["--no-ignore-global"], "nargs": 0,
            \               "help": "Don't respect ignore files that come from 'global' sources such as git's `core.excludesFile` configuration option (which defaults to `$HOME/.config/git/ignore`)."},
            \           {"name": ["--no-ignore-parent"], "nargs": 0, "help": "Don't respect ignore files (.gitignore, .ignore, etc.) in parent directories."},
            \           {"name": ["--no-ignore-vcs"], "nargs": 0, "help": "Don't respect version control ignore files (.gitignore, etc.)."},
            \           {"name": ["--no-messages"], "nargs": 0, "help": "Suppress all error messages related to opening and reading files."},
            \           {"name": ["--no-pcre2-unicode"], "nargs": 0, "help": "When PCRE2 matching is enabled, this flag will disable Unicode mode, which is otherwise enabled by default."},
            \           {"name": ["-E", "--encoding"], "nargs": 1, "metavar": "<ENCODING>", "help": "Specify the text encoding that rg will use on all files searched."},
            \           {"name": ["-M", "--max-columns"], "nargs": 1, "metavar": "<NUM>", "help": "Don't print lines longer than this limit in bytes."},
            \           {"name": ["-m", "--max-count"], "nargs": 1, "metavar": "<NUM>", "help": "Limit the number of matching lines per file searched to NUM."},
            \           {"name": ["-U", "--multiline"], "nargs": 0, "help": "Enable matching across multiple lines."},
            \           {"name": ["--multiline-dotall"], "nargs": 0, "help": "This flag enables 'dot all' in your regex pattern, which causes '.' to match newlines when multiline searching is enabled."},
            \           {"name": ["--max-depth"], "nargs": 1, "metavar": "<NUM>", "help": "Limit the depth of directory traversal to NUM levels beyond the paths given."},
            \           {"name": ["--max-filesize"], "nargs": 1, "metavar": "<NUM+SUFFIX?>", "help": "Ignore files larger than NUM in size. This does not apply to directories."},
            \           {"name": ["--path-separator"], "nargs": 1, "metavar": "<SEPARATOR>", "help": "Set the path separator to use when printing file paths."},
            \           {"name": ["--sort"], "nargs": 1, "metavar": "<SORTBY>", "help": "This flag enables sorting of results in ascending order."},
            \           {"name": ["--sortr"], "nargs": 1, "metavar": "<SORTBY>", "help": "This flag enables sorting of results in descending order."},
            \           {"name": ["-f", "--file"], "action": "append", "metavar": "<PATTERNFILE>...",
            \               "help": "Search for patterns from the given file, with one pattern per line.(This option can be provided multiple times.)"},
            \           {"name": ["-g", "--glob"], "action": "append", "metavar": "<GLOB>...",
            \               "help": "Include or exclude files and directories for searching that match the given glob.(This option can be provided multiple times.)"},
            \           {"name": ["--iglob"], "action": "append", "metavar": "<GLOB>...",
            \               "help": "Include or exclude files and directories for searching that match the given glob. Globs are matched case insensitively.(This option can be provided multiple times.)"},
            \           {"name": ["--ignore-file"], "action": "append", "metavar": "<PATH>...",
            \               "help": "Specifies a path to one or more .gitignore format rules files."},
            \           {"name": ["--type-add"], "action": "append", "metavar": "<TYPE_SPEC>...",
            \               "help": "Add a new glob for a particular file type."},
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
            \           {"name": ["--append"], "nargs": 0, "help": "Append to the previous search results."},
            \           {"name": ["--match-path"], "nargs": 0, "help": "Match the file path when fuzzy searching."},
            \           {"name": ["--wd-mode"], "nargs": 1, "metavar": "<MODE>", "help": "Specify the working directory mode, value has the same meaning as g:Lf_WorkingDirectoryMode."},
            \   ],
            \ "gtags":[
            \           [
            \              {"name": ["--update"], "nargs": 0, "help": "Create tag files if tag files do not exist, update the tag files otherwise."},
            \              {"name": ["--remove"], "nargs": 0, "help": "Remove the tag files generated."},
            \           ],
            \           {"name": ["--accept-dotfiles"], "nargs": 0, "help": "Accept files and directories whose names begin with a dot.  By default, gtags ignores them."},
            \           {"name": ["--skip-unreadable"], "nargs": 0, "help": "Skip unreadable files."},
            \           {"name": ["--gtagsconf"], "nargs": 1, "metavar": "<FILE>", "help": "Set environment variable GTAGSCONF to <FILE>."},
            \           {"name": ["--gtagslabel"], "nargs": 1, "metavar": "<LABEL>", "help": "Set environment variable GTAGSLABEL to <LABEL>."},
            \           {"name": ["--skip-symlink"], "nargs": "?", "metavar": "<TYPE>", "help": "Skip symbolic links. If type is 'f' then skip only symbolic links for file, else if 'd' then skip only symbolic links for directory. The default value of type is 'a' (all symbolic links)."},
            \           {"name": ["--gtagslibpath"], "nargs": "+", "metavar": "<PATH>", "help": "Specify the paths to search for library functions."},
            \           [
            \               {"name": ["-d", "--definition"], "nargs": 1, "metavar": "<PATTERN>", "help": "Show locations of definitions."},
            \               {"name": ["-r", "--reference"], "nargs": 1, "metavar": "<PATTERN>", "help": "Show reference to a symbol which has definitions."},
            \               {"name": ["-s", "--symbol"], "nargs": 1, "metavar": "<PATTERN>", "help": "Show reference to a symbol which has no definition."},
            \               {"name": ["-g", "--grep"], "nargs": 1, "metavar": "<PATTERN>", "help": "Show all lines which match to the <PATTERN>."},
            \               {"name": ["--by-context"], "nargs": 0, "help": "Decide tag type by context at cursor position. If the context is a definition of the pattern then use -r, else if there is at least one definition of the pattern then use -d, else use -s. Regular expression is not allowed for pattern."},
            \           ],
            \           {"name": ["-i", "--ignore-case"], "nargs": 0, "help": "Ignore case distinctions in the pattern."},
            \           {"name": ["--literal"], "nargs": 0, "help": "Execute literal search instead of regular expression search."},
            \           {"name": ["--path-style"], "nargs": 1, "choices": ["relative", "absolute", "shorter", "abslib", "through"], "metavar": "<FORMAT>", "help": "Show path names using <FORMAT>, which may be one of: `relative`, `absolute`, `shorter`, `abslib` or `through`. `relative` means relative path.  `absolute`  means  absolute path.  `shorter` means the shorter one of relative and absolute path.  `abslib` means absolute path for libraries (GTAGSLIBPATH) and relative path for the rest.  `through` means the relative path from the project root directory (internal format of GPATH).  The default is `relative`."},
            \           {"name": ["-S", "--scope"], "nargs": 1, "metavar": "<DIR>", "help": "Show only tags which exist under <DIR> directory."},
            \           {"name": ["--match-path"], "nargs": 0, "help": "Match the file path when fuzzy searching."},
            \           [
            \               {"name": ["--append"], "nargs": 0, "help": "Append to the previous search results."},
            \               {"name": ["--current-buffer"], "nargs": 0, "help": "Show tags in current buffer."},
            \               {"name": ["--all-buffers"], "nargs": 0, "help": "Show tags in all listed buffers."},
            \               {"name": ["--all"], "nargs": 0, "help": "Show tags in the whole project."},
            \           ],
            \           {"name": ["--result"], "nargs": 1, "choices": ["ctags", "ctags-x", "ctags-mod"], "metavar": "<FORMAT>", "help": "Show result using format, which may be one of: `ctags`(default), `ctags-x`,  `ctags-mod`."},
            \           {"name": ["--auto-jump"], "nargs": "?", "metavar": "<TYPE>", "help": "Jump to the tag directly when there is only one match. <TYPE> can be 'h', 'v' or 't', which mean jump to a horizontally, vertically split window, or a new tabpage respectively. If <TYPE> is omitted, jump to a position in current window."},
            \           {"name": ["--debug"], "nargs": 0, "help": "debug mode, some useful messages will be printed."},
            \   ],
            \ "filetype": [],
            \ "command": [
            \           {"name": ["--run-immediately"], "nargs": 0, "help": "Immediately execute the command on the current line in the result window"},
            \   ],
            \ "window": [],
            \ "quickfix": [],
            \ "loclist": [],
            \ "jumps": [],
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
            \   {"name": ["--popup"],      "nargs": 0, "help": "the LeaderF window is a popup window or floating window"},
            \ ],
            \ [
            \   {"name": ["--nameOnly"], "nargs": 0, "help": "LeaderF is in NameOnly mode by default"},
            \   {"name": ["--fullPath"], "nargs": 0, "help": "LeaderF is in FullPath mode by default"},
            \   {"name": ["--fuzzy"],    "nargs": 0, "help": "LeaderF is in Fuzzy mode by default"},
            \   {"name": ["--regexMode"],    "nargs": 0, "help": "LeaderF is in Regex mode by default"},
            \ ],
            \ {"name": ["--nowrap"], "nargs": 0, "help": "long lines in the LeaderF window won't wrap"},
            \ [
            \   {"name": ["--next"], "nargs": 0, "help": "Jump to the next result."},
            \   {"name": ["--previous"], "nargs": 0, "help": "Jump to the previous result."},
            \ ],
            \ {"name": ["--recall"], "nargs": 0, "help": "Recall last search. If the result window is closed, reopen it."},
            \ {"name": ["--popup-height"], "nargs": 1, "help": "specifies the maximum height of popup window, only available in popup mode."},
            \ {"name": ["--popup-width"], "nargs": 1, "help": "specifies the width of popup window, only available in popup mode."},
            \ {"name": ["--no-sort"], "nargs": 0, "help": "do not sort the result."},
            \ {"name": ["--case-insensitive"], "nargs": 0, "help": "fuzzy search case insensitively."},
            \ {"name": ["--auto-preview"], "nargs": 0, "help": "open preview window automatically."},
            \]

" arguments is something like g:Lf_CommonArguments
" return something like
" [
"   "--reverse",
"   "--stayOpen",
"   ["--input", "--cword"],
"   ["--top", "--bottom", "--left", "--right", "--belowright", "--aboveleft", "--fullScreen"],
"   ["--nameOnly", "--fullPath", "--fuzzy", "--regexMode"],
" ]
function! s:Lf_Refine(arguments) abort
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

" arguments is something like g:Lf_CommonArguments
" return something like
" {
"   "--reverse":  {"name": ["--reverse"], "nargs": 0, "help": "show results in bottom-up order"},
"   "--stayOpen": {"name": ["--stayOpen"], "nargs": 0, "help": "don't quit LeaderF after accepting an entry"},
"   "--input":    {"name": ["--input"], "nargs": 1, "help": "specifies INPUT as the pattern inputted in advance"},
"   "--cword":    {"name": ["--cword"], "nargs": 0, "help": "current word under cursor is inputted in advance"},
"   ...
" }
function! s:Lf_GenDict(arguments) abort
    let result = {}
    for arg in a:arguments
        if type(arg) == type([])
            for a in arg
                for i in a["name"]
                    let result[i] = a
                endfor
            endfor
        else
            for i in arg["name"]
                let result[i] = arg
            endfor
        endif
    endfor
    return result
endfunction

function! s:Lf_FuzzyMatch(pattern, str) abort
    let i = 0
    let pattern_len = len(a:pattern)
    let j = 0
    let str_len = len(a:str)
    while i < pattern_len && j < str_len
        if a:pattern[i] ==? a:str[j]
            let i += 1
        endif
        let j += 1
    endwhile
    return i >= pattern_len
endfunction

function! leaderf#Any#parseArguments(argLead, cmdline, cursorPos) abort
    let argList = split(a:cmdline[:a:cursorPos-1], '[ \t!]\+')
    let argNum = len(argList)
    if argNum == 1  " Leaderf
        return keys(g:Lf_Arguments) + keys(g:Lf_Extensions) + keys(g:Lf_PythonExtensions) + ['--recall', '--next', '--previous']
    elseif argNum == 2 && a:cmdline[a:cursorPos-1] !~ '\s'  " 'Leaderf b'
        return filter(keys(g:Lf_Arguments) + keys(g:Lf_Extensions) + keys(g:Lf_PythonExtensions) + ['--recall', '--next', '--previous'], "s:Lf_FuzzyMatch(a:argLead, v:val)")
    else
        let existingOptions = a:cmdline[a:cursorPos-1] !~ '\s' ? argList[2:-2] : argList[2:]
        if argList[1] == "gtags"
            if get(existingOptions, -1, "") == "--path-style"
                return ["relative", "absolute", "shorter", "abslib", "through"]
            elseif get(existingOptions, -1, "") == "--result"
                return ["ctags", "ctags-x", "ctags-mod"]
            endif
        endif
        let options = []
        if has_key(g:Lf_Extensions, argList[1])
            let arguments = get(g:Lf_Extensions[argList[1]], "arguments", [])
        elseif has_key(g:Lf_PythonExtensions, argList[1])
            let arguments = get(g:Lf_PythonExtensions[argList[1]], "arguments", [])
        elseif has_key(g:Lf_Arguments, argList[1])
            let arguments = g:Lf_Arguments[argList[1]]
        else
            let arguments = []
        endif
        let argDict = s:Lf_GenDict(arguments + g:Lf_CommonArguments)
        for opt in s:Lf_Refine(arguments + g:Lf_CommonArguments)
            if type(opt) == type([])
                let existingOpt = filter(copy(opt), "index(".string(existingOptions).", v:val) >= 0")
                if len(existingOpt) == 0
                    let options += opt
                elseif get(argDict[existingOpt[0]], "action", "") == "append"
                    let options += argDict[existingOpt[0]].name
                endif
            elseif index(existingOptions, opt) == -1 || get(argDict[opt], "action", "") == "append"
                call add(options, opt)
            endif
        endfor
        return filter(filter(copy(options), "v:val =~? '^".a:argLead."'"), "v:val =~ '^-'")
    endif
endfunction

function! leaderf#Any#start(bang, args) abort
    if a:args == ""

    else
        call leaderf#LfPy("anyHub.start(r''' ".a:args." ''', bang=".a:bang.")")
    endif
endfunction


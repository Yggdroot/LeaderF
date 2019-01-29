LeaderF
=======

This plugin is mainly used for locating files, buffers, mrus, tags in large project.

 - Written in Python.
 - Support fuzzy and regex searching.
 - Manage buffers and mrus.
 - Open multiple files at once.
 - [Extensible](https://github.com/Yggdroot/LeaderF-marks).

Changelog
---------

Please see the [CHANGELOG](https://github.com/Yggdroot/LeaderF/blob/master/CHANGELOG.md) for a release history.

Screenshots
-----------

![NameOnly Mode][1]

![FullPath Mode][2]

Requirements
------------

 - vim7.3 or higher. Only support vim7.4.330 or higher after [v1.01](https://github.com/Yggdroot/LeaderF/releases/tag/v1.01).
 - vim compiled with Python support, you can check by using `echo has('python')` or `echo has('python3')` to see if the result is `1`; Make sure that your python2 version is Python **2.7** or higher and python3 version is Python **3.1** or higher.

Installation
------------

To install this plugin just put the plugin files in your `~/.vim` (Linux) or `~/vimfiles` (Windows).<br>
For [Vundle][3] user, just add `Plugin 'Yggdroot/LeaderF'` to your `.vimrc`.

Performance
-----------

LeaderF is already very fast. If you want better performance, install the C extension of the fuzzy matching algorithm, which is more than 10 times faster.  
To install the C extension, follow the below:

 - On Linux/Unix/MacOS:

    First, make sure `python2` and/or `python3` commands are available.  
    Then run the installation script:

    ```sh
    cd ~/.vim/bundle/LeaderF
    ./install.sh
    ```
    Uninstall the C extension:

        ./install.sh --reverse

    If you are using [vim-plug][5]:

        Plug 'Yggdroot/LeaderF', { 'do': './install.sh' }

 - On Windows:

    First, make sure `py -2` and/or `py -3` commands are available.  
    Then run the installation script:

    ```sh
    cd ~\.vim\bundle\LeaderF
    .\install.bat
    ```
    There may be some error during the installation, please google the error messages to resolve it.  
    For example, `"error: Unable to find vcvarsall.bat"`, you can turn to [here][6] for help.

    Uninstall the C extension:

        .\install.bat --reverse

    If you are using [vim-plug][5]:

        Plug 'Yggdroot/LeaderF', { 'do': '.\install.bat' }

After running any command of LeaderF, check the value of `echo g:Lf_fuzzyMatch_C`, if the value is 1, it means the C extension is loaded sucessfully.

Usage
-----

```
usage: Leaderf[!] [-h] [--reverse] [--stayOpen] [--input <INPUT> | --cword]
                  [--top | --bottom | --left | --right | --belowright | --aboveleft | --fullScreen]
                  [--nameOnly | --fullPath | --fuzzy | --regexMode] [--nowrap]
                  {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,self,bufTag,buffer,rg}
                  ...

optional arguments:
  -h, --help            show this help message and exit
  --reverse             show results in bottom-up order
  --stayOpen            don't quit LeaderF after accepting an entry
  --input <INPUT>       specifies INPUT as the pattern inputted in advance
  --cword               current word under cursor is inputted in advance
  --top                 the LeaderF window is at the top of the screen
  --bottom              the LeaderF window is at the bottom of the screen
  --left                the LeaderF window is at the left of the screen
  --right               the LeaderF window is at the right of the screen
  --belowright          the LeaderF window is at the belowright of the screen
  --aboveleft           the LeaderF window is at the aboveleft of the screen
  --fullScreen          the LeaderF window takes up the full screen
  --nameOnly            LeaderF is in NameOnly mode by default
  --fullPath            LeaderF is in FullPath mode by default
  --fuzzy               LeaderF is in Fuzzy mode by default
  --regexMode           LeaderF is in Regex mode by default
  --nowrap              long lines in the LeaderF window won't wrap

subcommands:

  {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,self,bufTag,buffer,rg}
    file                search files
    tag                 navigate tags using the tags file
    function            navigate functions or methods in the buffer
    mru                 search most recently used files
    searchHistory       execute the search command in the history
    cmdHistory          execute the command in the history
    help                navigate the help tags
    line                search a line in the buffer
    colorscheme         switch between colorschemes
    self                execute the commands of itself
    bufTag              navigate tags in the buffer
    buffer              search buffers
    rg                  grep using rg(ripgrep)

If [!] is given, enter normal mode directly.
```

use `:Leaderf <subcommand> -h` to get specific help of subcommand, e.g., `:Leaderf rg -h`

```
usage: Leaderf[!] rg [-h] [-A <NUM>] [-B <NUM>] [-C <NUM>]
                     [--context-separator <SEPARATOR>] [-e <PATTERN>...] [-F]
                     [-i] [-L] [-P] [-S] [-s] [-v] [-w] [-x] [--hidden]
                     [--no-config] [--no-ignore] [--no-ignore-global]
                     [--no-ignore-parent] [--no-ignore-vcs]
                     [--no-pcre2-unicode] [-E <ENCODING>] [-M <NUM>]
                     [-m <NUM>] [--max-depth <NUM>] [--max-filesize <NUM+SUFFIX?>]
                     [--path-separator <SEPARATOR>] [--sort <SORTBY>]
                     [--sortr <SORTBY>] [-f <PATTERNFILE>...] [-g <GLOB>...]
                     [--iglob <GLOB>...] [--ignore-file <PATH>...]
                     [--type-add <TYPE_SPEC>...] [-t <TYPE>...] [-T <TYPE>...]
                     [--current-buffer | --all-buffers] [--recall] [--append]
                     [--match-path] [--reverse] [--stayOpen] [--input <INPUT> | --cword]
                     [--top | --bottom | --left | --right | --belowright | --aboveleft | --fullScreen]
                     [--nameOnly | --fullPath | --fuzzy | --regexMode] [--nowrap]
                     [<PATH> [<PATH> ...]]

optional arguments:
  -h, --help            show this help message and exit

specific arguments:
  -A <NUM>, --after-context <NUM>
                        Show NUM lines after each match.
  -B <NUM>, --before-context <NUM>
                        Show NUM lines before each match.
  -C <NUM>, --context <NUM>
                        Show NUM lines before and after each match.
  --context-separator <SEPARATOR>
                        The string used to separate non-contiguous context lines in the output.
  -e <PATTERN>..., --regexp <PATTERN>...
                        A pattern to search for. This option can be provided multiple times, where all
                        patterns given are searched.
  -F, --fixed-strings   Treat the pattern as a literal string instead of a regular expression.
  -i, --ignore-case     Searches case insensitively.
  -L, --follow          Follow symbolic links while traversing directories.
  -P, --pcre2           When this flag is present, rg will use the PCRE2 regex engine instead of its
                        default regex engine.
  -S, --smart-case      Searches case insensitively if the pattern is all lowercase, case sensitively
                        otherwise.
  -s, --case-sensitive  Searches case sensitively.
  -v, --invert-match    Invert matching. Show lines that do not match the given patterns.
  -w, --word-regexp     Only show matches surrounded by word boundaries. This is roughly equivalent to
                        putting \b before and after all of the search patterns.
  -x, --line-regexp     Only show matches surrounded by line boundaries.
  --hidden              Search hidden files and directories. By default, hidden files and directories
                        are skipped.
  --no-config           Never read configuration files. When this flag is present, rg will not respect
                        the RIPGREP_CONFIG_PATH environment variable.
  --no-ignore           Don't respect ignore files (.gitignore, .ignore, etc.). This implies
                        --no-ignore-parent and --no-ignore-vcs.
  --no-ignore-global    Don't respect ignore files that come from 'global' sources such as git's
                        `core.excludesFile` configuration option (which defaults to
                        `$HOME/.config/git/ignore`).
  --no-ignore-parent    Don't respect ignore files (.gitignore, .ignore, etc.) in parent directories.
  --no-ignore-vcs       Don't respect version control ignore files (.gitignore, etc.).
  --no-pcre2-unicode    When PCRE2 matching is enabled, this flag will disable
                        Unicode mode, which is otherwise enabled by default.
  -E <ENCODING>, --encoding <ENCODING>
                        Specify the text encoding that rg will use on all files searched.
  -M <NUM>, --max-columns <NUM>
                        Don't print lines longer than this limit in bytes.
  -m <NUM>, --max-count <NUM>
                        Limit the number of matching lines per file searched to NUM.
  --max-depth <NUM>     Limit the depth of directory traversal to NUM levels beyond the paths given.
  --max-filesize <NUM+SUFFIX?>
                        Ignore files larger than NUM in size. This does not apply to directories.
  --path-separator <SEPARATOR>
                        Set the path separator to use when printing file paths.
  --sort <SORTBY>       This flag enables sorting of results in ascending order.
  --sortr <SORTBY>      This flag enables sorting of results in descending order.
  -f <PATTERNFILE>..., --file <PATTERNFILE>...
                        Search for patterns from the given file, with one pattern per line.
                        (This option can be provided multiple times.)
  -g <GLOB>..., --glob <GLOB>...
                        Include or exclude files and directories for searching that match the given
                        glob.(This option can be provided multiple times.)
  --iglob <GLOB>...     Include or exclude files and directories for searching that match the given glob.
                        Globs are matched case insensitively.(This option can be provided multiple times.)
  --ignore-file <PATH>...
                        Specifies a path to one or more .gitignore format rules files.
  --type-add <TYPE_SPEC>...
                        Add a new glob for a particular file type.
  -t <TYPE>..., --type <TYPE>...
                        Only search files matching TYPE. Multiple type flags may be provided.
  -T <TYPE>..., --type-not <TYPE>...
                        Do not search files matching TYPE. Multiple type-not flags may be provided.
  <PATH>                A file or directory to search. Directories are searched recursively. Paths
                        specified on the command line override glob and ignore rules.
  --current-buffer      Searches in current buffer.
  --all-buffers         Searches in all listed buffers.
  --recall              Recall last search. If the result window is closed, reopen it.
  --append              Append to the previous search results.
  --match-path          Match the file path when fuzzy searching.

common arguments:
  --reverse             show results in bottom-up order
  --stayOpen            don't quit LeaderF after accepting an entry
  --input <INPUT>       specifies INPUT as the pattern inputted in advance
  --cword               current word under cursor is inputted in advance
  --top                 the LeaderF window is at the top of the screen
  --bottom              the LeaderF window is at the bottom of the screen
  --left                the LeaderF window is at the left of the screen
  --right               the LeaderF window is at the right of the screen
  --belowright          the LeaderF window is at the belowright of the screen
  --aboveleft           the LeaderF window is at the aboveleft of the screen
  --fullScreen          the LeaderF window takes up the full screen
  --nameOnly            LeaderF is in NameOnly mode by default
  --fullPath            LeaderF is in FullPath mode by default
  --fuzzy               LeaderF is in Fuzzy mode by default
  --regexMode           LeaderF is in Regex mode by default
  --nowrap              long lines in the LeaderF window won't wrap

If [!] is given, enter normal mode directly.
```

You can customize some handy maps, e.g.,

```vim
" search word under cursor, the pattern is treated as regex, and enter normal mode directly
noremap <C-F> :<C-U><C-R>=printf("Leaderf! rg -e %s ", expand("<cword>"))<CR>
" search word under cursor, the pattern is treated as regex,
" append the result to previous search results.
noremap <C-G> :<C-U><C-R>=printf("Leaderf! rg --append -e %s ", expand("<cword>"))<CR>
" search word under cursor literally only in current buffer
noremap <C-B> :<C-U><C-R>=printf("Leaderf! rg -F --current-buffer -e %s ", expand("<cword>"))<CR>
" search visually selected text literally, don't quit LeaderF after accepting an entry
xnoremap gf :<C-U><C-R>=printf("Leaderf! rg -F --stayOpen -e %s ", leaderf#Rg#visual())<CR>
" recall last search. If the result window is closed, reopen it.
noremap go :<C-U>Leaderf! rg --stayOpen --recall<CR>
```
Once LeaderF is launched:

| Command                    | Description
| -------                    | -----------
| `<C-C>`<br>`<ESC>`         | quit from LeaderF
| `<C-R>`                    | switch between fuzzy search mode and regex mode
| `<C-F>`                    | switch between full path search mode and name only search mode
| `<Tab>`                    | switch to normal mode
| `<C-V>`<br>`<S-Insert>`    | paste from clipboard
| `<C-U>`                    | clear the prompt
| `<C-J>`                    | move the cursor downward in the result window
| `<C-K>`                    | move the cursor upward in the result window
| `<Up>`/`<Down>`            | recall last/next input pattern from history
| `<2-LeftMouse>`<br>`<CR>`  | open the file under cursor or selected(when multiple files are selected)
| `<C-X>`                    | open in horizontal split window
| `<C-]>`                    | open in vertical split window
| `<C-T>`                    | open in new tabpage
| `<F5>`                     | refresh the cache
| `<C-LeftMouse>`<br>`<C-S>` | select multiple files
| `<S-LeftMouse>`            | select consecutive multiple files
| `<C-A>`                    | select all files
| `<C-L>`                    | clear all selections
| `<BS>`                     | delete the preceding character in the prompt
| `<Del>`                    | delete the current character in the prompt
| `<Home>`                   | move the cursor to the begin of the prompt
| `<End>`                    | move the cursor to the end of the prompt
| `<Left>`                   | move the cursor one character to the left in the prompt
| `<Right>`                  | move the cursor one character to the right in the prompt
| `<C-P>`                    | preview the result

Input formats:

 * In **NameOnly** mode (*fuzzy mode*)

    If the first character you input is `';'`, then the searching will be the same as in **FullPath** mode.<br>
    If you input string as `'abc;def'`, then `'abc'` will match the file name and `'def'` will match the directory name.

 * In **FullPath** mode (*fuzzy mode*)

    Same as in **NameOnly** mode except that the pattern will match the full path but not the file name only.

 * In **Regexp** mode

    The input string is the same as the Vim's regexp.

Smart Case:

 * If the characters in search pattern are all lowercase, the matching is case-insensitive. If the search pattern contains uppercase characters, all lowercase characters still are matched case-insensitively, the uppercase characters can only match upper case. So uppercase characters can speed up the narrowing down of the searching result.  

    e.g., input `abcDef`，it can match the following strings:
    ```
    abcDef
    AbcDef
    abcDEf
    aBcDeF
    ```
    but can not match the strings such as:
    ```
    abcdef
    Abcdef
    ```
    Note: `abc` and `ef` are still case-insensitive.

And operator:

 * In fuzzy mode, using `' '`(space) as the **and** operator, the candidate lines should fuzzily match all the substrings separated by space.

    e.g., input `abc def gh`，it can match the following strings:
    ```
    ...a.b.c...d.e.f...g.h...
    ...a.b.c...g.h...d.e.f...
    ...a.d..e.g.b.c...h..f...
    ...gh...def...abc...
    ```

Customization
-------------

 * Change key bindings

    By default, `<Up>` and `<Down>` are used to recall last/next input pattern from history. If you want to use them to navigate the result list just like `<C-K>` and `<C-J>` :

    `let g:Lf_CommandMap = {'<C-K>': ['<Up>'], '<C-J>': ['<Down>']}`

    for more detail, please refer to `:h g:Lf_CommandMap`.

 * Customize the statusline

    Please refer to [here][4].

 * Change the highlight of matched string

    ```vim
    highlight Lf_hl_match gui=bold guifg=Blue cterm=bold ctermfg=21
    highlight Lf_hl_matchRefine  gui=bold guifg=Magenta cterm=bold ctermfg=201
    ```

 * Change the default mapping of searching files command

    e.g. `let g:Lf_ShortcutF = '<C-P>'`

License
-------

This plugin is released under the Apache License, Version 2.0 (the "License").


  [1]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_1.gif
  [2]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_2.gif
  [3]: https://github.com/gmarik/Vundle.vim
  [4]: https://github.com/Yggdroot/LeaderF/blob/master/doc/leaderf.txt#L189-L349
  [5]: https://github.com/junegunn/vim-plug
  [6]: https://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat  

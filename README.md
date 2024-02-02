LeaderF
=======

An efficient fuzzy finder that helps to locate files, buffers, mrus, gtags, etc. on the fly.

 - Written in Python.
 - Support fuzzy and regex searching.
 - Full-featured.
 - Well-designed fuzzy matching algorithm.
 - [Extensible](https://github.com/Yggdroot/LeaderF/wiki/Extensions).

Changelog
---------

Please see the [CHANGELOG](https://github.com/Yggdroot/LeaderF/blob/master/CHANGELOG.md) for a release history.

Wiki
----

[Wiki](https://github.com/Yggdroot/LeaderF/wiki).

Extensions
----------

A list of community extensions can be found in the [Extensions](https://github.com/Yggdroot/LeaderF/wiki/Extensions) wiki.

Screenshots
-----------

![Popup Mode][1]

![And Mode][2]

Requirements
------------

 - vim7.3 or higher. Only support 7.4.1126+ after [v1.01](https://github.com/Yggdroot/LeaderF/releases/tag/v1.01).
 - Python2.7+ or Python3.1+.
 - To use the popup mode, neovim 0.5.0+ or vim 8.1.1615+ are required.

Installation
------------

For [vim-plug][5] user:

```vim
Plug 'Yggdroot/LeaderF', { 'do': ':LeaderfInstallCExtension' }
```

Performance
-----------

LeaderF is already very fast. If you'd like better performance, install the C extension of the fuzzy matching algorithm, which is more than 10 times faster.  
To install the C extension, firstly, make sure `python2` and/or `python3` commands are available on Linux/Unix/MacOS and `py -2` and/or `py -3` commands are available on Windows.

 - Install the C extension
    ```vim
    :LeaderfInstallCExtension
    ```
    There may be some errors during the installation, please google the error messages to resolve it.  
    For example, `"error: Unable to find vcvarsall.bat"`, you can turn to [here][6] for help.


- Uninstall the C extension
    ```vim
    :LeaderfUninstallCExtension
    ```

After running any command of LeaderF, check the value of `echo g:Lf_fuzzyEngine_C`, if the value is 1, it means the C extension is loaded sucessfully.

Usage
-----

```
usage: Leaderf[!] [-h] [--reverse] [--stayOpen] [--input <INPUT> | --cword]
                  [--top | --bottom | --left | --right | --belowright | --aboveleft | --fullScreen | --popup]
                  [--nameOnly | --fullPath | --fuzzy | --regexMode] [--nowrap] [--next | --previous]
                  [--recall] [--popup-height <POPUP_HEIGHT>] [--popup-width <POPUP_WIDTH>] [--no-sort]
                  [--case-insensitive] [--auto-preview | --no-auto-preview]
                  
                  {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,gtags,
                      self,bufTag,buffer,rg,filetype,command,window,quickfix,loclist,jumps}
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
  --popup               the LeaderF window is a popup window or floating window
  --nameOnly            LeaderF is in NameOnly mode by default
  --fullPath            LeaderF is in FullPath mode by default
  --fuzzy               LeaderF is in Fuzzy mode by default
  --regexMode           LeaderF is in Regex mode by default
  --nowrap              long lines in the LeaderF window won't wrap
  --next                Jump to the next result.
  --previous            Jump to the previous result.
  --recall              Recall last search. If the result window is closed, reopen it.
  --popup-height <POPUP_HEIGHT>
                        specifies the maximum height of popup window, only available in popup mode.
  --popup-width <POPUP_WIDTH>
                        specifies the width of popup window, only available in popup mode.
  --no-sort             do not sort the result.
  --case-insensitive    fuzzy search case insensitively.
  --auto-preview        open preview window automatically.
  --no-auto-preview     don't open preview window automatically.

subcommands:

  {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,gtags,
      self,bufTag,buffer,rg,filetype,command,window,quickfix,loclist,jumps}
    file                search files
    tag                 navigate tags using the tags file
    function            navigate functions or methods in the buffer
    mru                 search most recently used files
    searchHistory       execute the search command in the history
    cmdHistory          execute the command in the history
    help                navigate the help tags
    line                search a line in the buffer
    colorscheme         switch between colorschemes
    gtags               navigate tags using the gtags
    self                execute the commands of itself
    bufTag              navigate tags in the buffer
    buffer              search buffers
    rg                  grep using rg
    filetype            navigate the filetype
    command             execute built-in/user-defined Ex commands.
    window              search windows.
    quickfix            navigate the quickfix.
    loclist             navigate the location list.

If [!] is given, enter normal mode directly.
```

use `:Leaderf <subcommand> -h` to get specific help of subcommand, e.g., `:Leaderf rg -h`.

Once LeaderF is launched:

| Command                    | Description
| -------                    | -----------
| `<C-C>`<br>`<ESC>`         | quit from LeaderF
| `<C-R>`                    | switch between fuzzy search mode and regex mode
| `<C-F>`                    | switch between full path search mode and name only search mode
| `<Tab>`                    | switch to normal mode
| `<C-V>`<br>`<S-Insert>`    | paste from clipboard
| `<C-U>`                    | clear the prompt
| `<C-W>`                    | delete the word before the cursor in the prompt
| `<C-J>`                    | move the cursor downward in the result window
| `<C-K>`                    | move the cursor upward in the result window
| `<Up>`/`<Down>`            | recall last/next input pattern from history
| `<2-LeftMouse>`<br>`<CR>`  | open the file under cursor or selected(when multiple files are selected)
| `<C-X>`                    | open in horizontal split window
| `<C-]>`                    | open in vertical split window
| `<C-T>`                    | open in new tabpage
| `<C-\>`                    | show a prompt enable to choose split window method: vertical, horizontal, tabpage, etc
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
| `<C-Up>`                   | scroll up in the popup preview window
| `<C-Down>`                 | scroll down in the popup preview window

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

Popup Mode
----------

Popup Mode is to open LeaderF in a popup window(vim 8.1.1615+) or floating window(nvim 0.4.2+). 

To enable popup mode:  
```vim
let g:Lf_WindowPosition = 'popup'
```  
or add `--popup` after each subcommand, e.g.,  
```
Leaderf file --popup
```

Customization
-------------

 * Change key bindings

    By default, `<Up>` and `<Down>` are used to recall last/next input pattern from history. If you want to use them to navigate the result list just like `<C-K>` and `<C-J>` :

    `let g:Lf_CommandMap = {'<C-K>': ['<Up>'], '<C-J>': ['<Down>']}`

    for more detail, please refer to `:h g:Lf_CommandMap`.

 * Change the colors used in LeaderF

    ```vim
    let g:Lf_PopupPalette = {
        \  'light': {
        \      'Lf_hl_match': {
        \                'gui': 'NONE',
        \                'font': 'NONE',
        \                'guifg': 'NONE',
        \                'guibg': '#303136',
        \                'cterm': 'NONE',
        \                'ctermfg': 'NONE',
        \                'ctermbg': '236'
        \              },
        \      'Lf_hl_cursorline': {
        \                'gui': 'NONE',
        \                'font': 'NONE',
        \                'guifg': 'NONE',
        \                'guibg': '#303136',
        \                'cterm': 'NONE',
        \                'ctermfg': 'NONE',
        \                'ctermbg': '236'
        \              },
        \      },
        \  'dark': {
        \         ...
        \         ...
        \      }
        \  }
    ```
    All the highlight groups supported are defined in
    [LeaderF/autoload/leaderf/colorscheme/popup/default.vim](https://github.com/Yggdroot/LeaderF/blob/master/autoload/leaderf/colorscheme/popup/default.vim).

 * Change the default mapping of searching files command

    e.g. `let g:Lf_ShortcutF = '<C-P>'`

 * Show icons (should install fonts from https://github.com/ryanoasis/nerd-fonts)

    Support commands: buffer,file,mru,window

    ```vim
    " Show icons, icons are shown by default
    let g:Lf_ShowDevIcons = 1
    " For GUI vim, the icon font can be specify like this, for example
    let g:Lf_DevIconsFont = "DroidSansM Nerd Font Mono"
    " If needs
    set ambiwidth=double
    ```

    
Configuration examples
----------------------

```vim
" don't show the help in normal mode
let g:Lf_HideHelp = 1
let g:Lf_UseCache = 0
let g:Lf_UseVersionControlTool = 0
let g:Lf_IgnoreCurrentBufferName = 1
" popup mode
let g:Lf_WindowPosition = 'popup'
let g:Lf_StlSeparator = { 'left': "\ue0b0", 'right': "\ue0b2", 'font': "DejaVu Sans Mono for Powerline" }
let g:Lf_PreviewResult = {'Function': 0, 'BufTag': 0 }

let g:Lf_ShortcutF = "<leader>ff"
noremap <leader>fb :<C-U><C-R>=printf("Leaderf buffer %s", "")<CR><CR>
noremap <leader>fm :<C-U><C-R>=printf("Leaderf mru %s", "")<CR><CR>
noremap <leader>ft :<C-U><C-R>=printf("Leaderf bufTag %s", "")<CR><CR>
noremap <leader>fl :<C-U><C-R>=printf("Leaderf line %s", "")<CR><CR>

noremap <C-B> :<C-U><C-R>=printf("Leaderf! rg --current-buffer -e %s ", expand("<cword>"))<CR>
noremap <C-F> :<C-U><C-R>=printf("Leaderf! rg -e %s ", expand("<cword>"))<CR>
" search visually selected text literally
xnoremap gf :<C-U><C-R>=printf("Leaderf! rg -F -e %s ", leaderf#Rg#visual())<CR>
noremap go :<C-U>Leaderf! rg --recall<CR>

" should use `Leaderf gtags --update` first
let g:Lf_GtagsAutoGenerate = 0
let g:Lf_Gtagslabel = 'native-pygments'
noremap <leader>fr :<C-U><C-R>=printf("Leaderf! gtags -r %s --auto-jump", expand("<cword>"))<CR><CR>
noremap <leader>fd :<C-U><C-R>=printf("Leaderf! gtags -d %s --auto-jump", expand("<cword>"))<CR><CR>
noremap <leader>fo :<C-U><C-R>=printf("Leaderf! gtags --recall %s", "")<CR><CR>
noremap <leader>fn :<C-U><C-R>=printf("Leaderf gtags --next %s", "")<CR><CR>
noremap <leader>fp :<C-U><C-R>=printf("Leaderf gtags --previous %s", "")<CR><CR>
```

FAQ
---

https://github.com/Yggdroot/LeaderF/issues?q=label%3AFAQ+

License
-------

This plugin is released under the Apache License, Version 2.0 (the "License").

:heart: Sponsor
-------

If you like this software, please consider buying me a coffee.  
https://github.com/Yggdroot/SponsorMe/blob/main/README.md#donate
(捐赠的朋友最好备注一下自己的ID）

  [1]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_popup.gif
  [2]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_2.gif
  [3]: https://github.com/gmarik/Vundle.vim
  [4]: https://github.com/Yggdroot/LeaderF/blob/master/doc/leaderf.txt#L189-L349
  [5]: https://github.com/junegunn/vim-plug
  [6]: https://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat  

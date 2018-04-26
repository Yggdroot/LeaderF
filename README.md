LeaderF
=======

This plugin is mainly used for locating files, buffers, mrus, tags in large project.

 - Written in Python.
 - Support fuzzy and regex searching.
 - Manage buffers and mrus.
 - Open multiple files at once.
 - [Extensible](https://github.com/Yggdroot/LeaderF-marks).

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

    First, make sure `python` and/or `python3` commands are available.  
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

| Command                    | Description
| -------                    | -----------
| `:LeaderfFile`<br> `<leader>f`| search files
| `:LeaderfFile [directory]` | search files under the `directory` specified
| `:LeaderfFileFullScreen`   | search files, LeaderF window take up full screen
| `:LeaderfFilePattern <pattern>` | like `LeaderfFile`, with `pattern` inputted in advance
| `:LeaderfFileCword`        | like `LeaderfFile`, with word under the cursor as pattern inputted in advance
| `:LeaderfBuffer`<br> `<leader>b`| search listed buffers
| `:LeaderfBufferAll`        | search all buffers
| `:LeaderfTabBuffer`        | search listed buffers in current tabpage
| `:LeaderfTabBufferAll`     | search all buffers in current tabpage
| `:LeaderfBufferPattern <pattern>` | like `LeaderfBuffer`, with `pattern` inputted in advance
| `:LeaderfBufferCword`      | like `LeaderfBuffer`, with word under the cursor as pattern inputted in advance
| `:LeaderfMru`              | search most recently used files
| `:LeaderfMruCwd`           | search MRU in current working directory
| `:LeaderfMruPattern <pattern>` | like `LeaderfMru`, with `pattern` inputted in advance
| `:LeaderfMruCword`         | like `LeaderfMru`, with word under the cursor as pattern inputted in advance
| `:LeaderfMruCwdPattern <pattern>` | like `LeaderfMruCwd`, with `pattern` inputted in advance
| `:LeaderfMruCwdCword`      | like `LeaderfMruCwd`, with word under the cursor as pattern inputted in advance
| `:LeaderfTag`              | navigate tags using the tags file
| `:LeaderfTagPattern <pattern>` | like `LeaderfTag`, with `pattern` inputted in advance
| `:LeaderfTagCword`         | like `LeaderfTag`, with word under the cursor as pattern inputted in advance
| `:LeaderfBufTag`           | navigate tags in current buffer
| `:LeaderfBufTagAll`        | navigate tags in all listed buffers
| `:LeaderfBufTagPattern <pattern>` | like `LeaderfBufTag`, with `pattern` inputted in advance
| `:LeaderfBufTagCword`      | like `LeaderfBufTag`, with word under the cursor as pattern inputted in advance
| `:LeaderfBufTagAllPattern <pattern>` | like `LeaderfBufTagAll`, with `pattern` inputted in advance
| `:LeaderfBufTagAllCword`   | like `LeaderfBufTagAll`, with word under the cursor as pattern inputted in advance
| `:LeaderfFunction`         | navigate functions or methods in current buffer
| `:LeaderfFunctionAll`      | navigate functions or methods in all listed buffers
| `:LeaderfFunctionPattern <pattern>` | like `LeaderfFunction`, with `pattern` inputted in advance
| `:LeaderfFunctionCword`    | like `LeaderfFunction`, with word under the cursor as pattern inputted in advance
| `:LeaderfFunctionAllPattern <pattern>` | like `LeaderfFunctionAll`, with `pattern` inputted in advance
| `:LeaderfFunctionAllCword` | like `LeaderfFunctionAll`, with word under the cursor as pattern inputted in advance
| `:LeaderfLine`             | search a line in current buffer
| `:LeaderfLineAll`          | search a line in all listed buffers
| `:LeaderfLinePattern <pattern>` | like `LeaderfLine`, with `pattern` inputted in advance
| `:LeaderfLineCword`        | like `LeaderfLine`, with word under the cursor as pattern inputted in advance
| `:LeaderfLineAllPattern <pattern>` | like `LeaderfLineAll`, with `pattern` inputted in advance
| `:LeaderfLineAllCword`     | like `LeaderfLineAll`, with word under the cursor as pattern inputted in advance
| `:LeaderfHistoryCmd`       | execute the command in the history
| `:LeaderfHistorySearch`    | execute the search command in the history
| `:LeaderfSelf`             | execute the commands of itself
| `:LeaderfHelp`             | navigate the help tags
| `:LeaderfHelpPattern <pattern>` | like `LeaderfHelp`, with `pattern` inputted in advance
| `:LeaderfHelpCword`        | like `LeaderfHelp`, with word under the cursor as pattern inputted in advance
| `:LeaderfColorscheme`      | switch between colorschemes


Once LeaderF is launched:

| Command                    | Description
| -------                    | -----------
| `<C-C>`<br>`<ESC>`         | quit from LeaderF
| `<C-R>`                    | switch between fuzzy search mode and regex mode
| `<C-F>`                    | switch between full path search mode and name only search mode
| `<Tab>`                    | switch to normal mode
| `<C-V>`<br>`<S-Insert>`    | paste from clipboard
| `<C-U>`                    | clear the prompt
| `<C-J>`<br>`<Down>`        | move the cursor downward in the result window
| `<C-K>`<br>`<Up>`          | move the cursor upward in the result window
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

 * In **NameOnly** mode (*fuzzy*)

    `'abc'` is interpreted as vim's regexp `'a.\{-}b.\{-}c'`.<br>
    If the first character you input is `';'`, then the searching will be the same as in **FullPath** mode.<br>
    If you input string as `'abc;def'`, then `'abc'` will match the file name and `'def'` will match the directory name.

 * In **FullPath** mode (*fuzzy*)

    Same as in **NameOnly** mode except that the pattern will match the full path but not the file name only.

 * In **Regexp** mode

    The input string is the same as the Vim's regexp.

Smart Case:

 * If the characters in search pattern are all lowercase, the matching is case-insensitive. If the search pattern contains uppercase characters, all lowercase characters still are matched case-insensitively, the uppercase characters can only match upper case. So uppercase characters can speed up the narrowing down of the searching result.  

    e.g., input `abcDef`，it can match the following string:
    ```
    abcDef
    AbcDef
    abcDEf
    aBcDeF
    ```
    but can not match the string such as:
    ```
    abcdef
    Abcdef
    ```
    Note: `abc` and `ef` are still case-insensitive.

Customization
-------------

 * Change key bindings

    By default, `<Tab>` is the shortcut key to switch to normal mode, if you want to change the key into `<ESC>`:

    `let g:Lf_CommandMap = {'<Tab>': ['<ESC>']}`

    for more detail, please refer to [here][7].

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
  [7]: https://github.com/Yggdroot/LeaderF/blob/master/doc/leaderf.txt#L476-L481

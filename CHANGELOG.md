v1.21 (2019-10-15)
==================

**BREAKING CHANGES**:

* Let `Leaderf rg {pattern}` work

Feature enhancements:

* [Feature #293](https://github.com/Yggdroot/LeaderF/issues/293):  
  Let `--recall` support all leaderf cmd.  
  `Leaderf --recall` to recall last Leaderf command
* [Feature #360](https://github.com/Yggdroot/LeaderF/issues/360):  
  Find file based on the current buffer  
  Add g:Lf_IgnoreCurrentBufferName
* Enhance the ability to write extension for nvim
* Add support for `Leaderf! file`
* Add "--auto-jump" support for `Leaderf[!] gtags --by-context`
* Add "--no-messages" for Leaderf rg
* Add g:Lf_Debug_Gtags

Bug fixes:

* [BUG #366](https://github.com/Yggdroot/LeaderF/issues/366)
* [BUG #361](https://github.com/Yggdroot/LeaderF/issues/361)
* [BUG #359](https://github.com/Yggdroot/LeaderF/issues/359)
* [BUG #349](https://github.com/Yggdroot/LeaderF/issues/349)
* [BUG #335](https://github.com/Yggdroot/LeaderF/issues/335)
* [BUG #332](https://github.com/Yggdroot/LeaderF/issues/332)
* [BUG #329](https://github.com/Yggdroot/LeaderF/issues/329)
* [BUG #327](https://github.com/Yggdroot/LeaderF/issues/327)
* [BUG #326](https://github.com/Yggdroot/LeaderF/issues/326)
* [BUG #325](https://github.com/Yggdroot/LeaderF/issues/325)
* [BUG #320](https://github.com/Yggdroot/LeaderF/issues/320)

v1.20 (2019-5-8)
================

Feature enhancements:

* [Feature #191](https://github.com/Yggdroot/LeaderF/issues/191):
  add support for GNU Global(`Leaderf gtags`)  
  For more details: `Leaderf gtags -h`
* [Feature #254](https://github.com/Yggdroot/LeaderF/issues/254):
  Add rg option `--type-add`.
* Add `--no-split-path` for "Leaderf mru"
* Add mouse wheel support for terminal vim
* Add rg options `--no-pcre2-unicode`, `--path-separator`, `--sort`, `--sortr`, `-f`, `--match-path`
* Add g:Lf_RgConfig and g:Lf_MaxCount
* [Feature #266](https://github.com/Yggdroot/LeaderF/issues/266):
  Add "-A", "-B" and "-C" options for `Leaderf rg`
* [Feature #274](https://github.com/Yggdroot/LeaderF/issues/274):
  Add g:Lf_NoChdir
* [Feature #277](https://github.com/Yggdroot/LeaderF/issues/277):
  Add `--wd-mode` support for `Leaderf rg`
* Add preview support for `Leaderf file`
* Add preview support for `Leaderf mru`
* Use tab drop to open buffer
* `--wd-mode` use the value of `g:Lf_WorkingDirectoryMode` by default
* Optimize the asyncExecutor
* Add `--next` and `--previous` to navigate the results

Bug fixes:

* [BUG #257](https://github.com/Yggdroot/LeaderF/issues/257)
* [BUG #261](https://github.com/Yggdroot/LeaderF/issues/261)
  Never read configuration files.
* [BUG #267](https://github.com/Yggdroot/LeaderF/issues/267)
* [BUG #272](https://github.com/Yggdroot/LeaderF/issues/272)
* [BUG #273](https://github.com/Yggdroot/LeaderF/issues/273)
* [BUG #278](https://github.com/Yggdroot/LeaderF/issues/278)
* [BUG #280](https://github.com/Yggdroot/LeaderF/issues/280)
* [BUG #283](https://github.com/Yggdroot/LeaderF/issues/283)
* [BUG #297](https://github.com/Yggdroot/LeaderF/issues/297)
* [BUG #302](https://github.com/Yggdroot/LeaderF/issues/302)
* [BUG #304](https://github.com/Yggdroot/LeaderF/issues/304)
* [BUG #307](https://github.com/Yggdroot/LeaderF/issues/307)
* [BUG #310](https://github.com/Yggdroot/LeaderF/issues/310)
* [BUG #315](https://github.com/Yggdroot/LeaderF/issues/315)
* Fix the hang issue if `silent`

v1.19 (2018-12-7)
=================

**BREAKING CHANGES**:

* `<Up>` and  `<Down>` is changed. [issue #236](https://github.com/Yggdroot/LeaderF/issues/236)  
  from: `navigate the result list.`  
  to:   `recall last/next input pattern from history.`

Feature enhancements:

* [Feature #57](https://github.com/Yggdroot/LeaderF/issues/57):
  Add support for rg(`Leaderf rg`)  
  For more details: `Leaderf rg -h`
* [Feature #130](https://github.com/Yggdroot/LeaderF/issues/130):
  Add Changelog file.
* [Feature #208](https://github.com/Yggdroot/LeaderF/issues/208):
  Add support for input file list.  
  Add `--file` option for `Leaderf file`.
* [Feature #213](https://github.com/Yggdroot/LeaderF/issues/213):
  Add support for input history.  
  Use `<UP>` and `<Down>` to loop the input history.
* Add `one-dark` colorscheme.
* Add `--nowrap` option for LeaderF.

Bug fixes:

* [BUG #220](https://github.com/Yggdroot/LeaderF/issues/220)
* [BUG #227](https://github.com/Yggdroot/LeaderF/issues/227):
  `autocmd filetype leaderf set nonumber` is broken after this commit
* [BUG #233](https://github.com/Yggdroot/LeaderF/issues/233)
* [BUG #234](https://github.com/Yggdroot/LeaderF/issues/234)
* [BUG #241](https://github.com/Yggdroot/LeaderF/issues/241)
* [BUG #245](https://github.com/Yggdroot/LeaderF/issues/245)
* Restore original sizes only if windows count no change.

v1.18 (2018-10-7)
=================

Feature enhancements:

* Add support for `and mode`.  
  In fuzzy mode, using `' '`(space) as the **and** operator(`g:Lf_AndDelimiter`), the
  candidate lines should fuzzily match all the substrings separated by space.

    e.g., input `abc def gh`，it can match the following strings:
    ```
    ...a.b.c...d.e.f...g.h...
    ...a.b.c...g.h...d.e.f...
    ...a.d..e.g.b.c...h..f...
    ...gh...def...abc...
    ```

v1.17 (2018-10-3)
=================

Feature enhancements:

* Add a new thread to read output of AsyncExecutor.
* [Feature #222](https://github.com/Yggdroot/LeaderF/issues/222):
  Allow for bottom-up ordering of results.

Bug fixes:

* Fix a critical latent bug introduced by PR #131.
* [BUG #223](https://github.com/Yggdroot/LeaderF/issues/223):
  NameOnly bug when searching directories.
* [BUG #224](https://github.com/Yggdroot/LeaderF/issues/224)
* [BUG #225](https://github.com/Yggdroot/LeaderF/issues/225):
  install.sh failed on Windows10(msys64).

v1.16 (2018-9-20)
=================

**BREAKING CHANGES**:

* `<Esc>` in normal mode does not quit LeaderF any more, because there is a bug
  in vim that all the function keys can not work correctly if `<Esc>` is mapped.

Feature enhancements:

* Optimize the fuzzy matching algorithm.
* Add fuzzyEngine to fully take advantage of the cpu cores.
* [Feature #202](https://github.com/Yggdroot/LeaderF/issues/202):
  Add `g:Lf_CtagsFuncOpts`.
* [Feature #205](https://github.com/Yggdroot/LeaderF/issues/205):
  Allow LeaderF to work with Git submodules. Add `g:Lf_RecurseSubmodules`.
* Add "need_exit": funcref (line, arguments)
* [Feature #194 #217](https://github.com/Yggdroot/LeaderF/issues/194):
  Add '--no-ignore'.

Bug fixes:

* [BUG #192](https://github.com/Yggdroot/LeaderF/issues/192):
  Swapping mapping of `<Tab>` and `<CR>` doesn't work in commandmap.
* Fix a **huge** bug.
* [BUG #197](https://github.com/Yggdroot/LeaderF/issues/197)
* Don't support ag on Windows because of issue #190 and #198.
* [BUG #206](https://github.com/Yggdroot/LeaderF/issues/206):
  No module named leaderf.
* [BUG #209](https://github.com/Yggdroot/LeaderF/issues/209)
* [BUG #210](https://github.com/Yggdroot/LeaderF/issues/210):
  Undefined variable: g:Lf_MruCacheFileName when calling LeaderfMru.
* [BUG #218](https://github.com/Yggdroot/LeaderF/issues/218):
  Add if python is present in system.

v1.15 (2018-7-13)
=================

Feature enhancements:

* Optimize the fuzzy matching algorithm.

Bug fixes:

* There is a bug if `let g:Lf_WorkingDirectoryMode = "Ac"`
* [BUG #138](https://github.com/Yggdroot/LeaderF/issues/138):
  DeprecationWarning with python 3.7 on Windows 10.
* [BUG #176](https://github.com/Yggdroot/LeaderF/issues/176):
  Slow start in neovim.
* [BUG #180](https://github.com/Yggdroot/LeaderF/issues/180):
  Leaderf ignore Lf_WildIgnore.
* [BUG #181](https://github.com/Yggdroot/LeaderF/issues/181):
  Search dir is same when two tabpage's work dir is different.
* A bug because of https://github.com/neovim/neovim/issues/8690.

v1.14 (2018-6-19)
=================

Feature enhancements:

* Beautify the display of bufTag.
* [Feature #144](https://github.com/Yggdroot/LeaderF/issues/144):
  Add the capability to search everything. Support writing extensions in vimscript.   
  Add a universal command line interface for LeaderF.
    ```
    usage: Leaderf[!] [-h] [--reverse] [--stayOpen] [--input INPUT | --cword]
                      [--top | --bottom | --left | --right | --belowright | --aboveleft | --fullScreen]
                      [--nameOnly | --fullPath | --fuzzy | --regex]
                      {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,self,bufTag,buffer}
                      ...

    optional arguments:
      -h, --help            show this help message and exit
      --reverse             show results in bottom-up order
      --stayOpen            don't quit LeaderF after accepting an entry
      --input INPUT         specifies INPUT as the pattern inputted in advance
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
      --regex               LeaderF is in Regex mode by default

    subcommands:

      {file,tag,function,mru,searchHistory,cmdHistory,help,line,colorscheme,self,bufTag,buffer}
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

    If [!] is given, enter normal mode directly.
    ```
  use `:Leaderf <subcommand> -h` to get specific help of subcommand, e.g., `:Leaderf mru -h`.

* [Feature #160](https://github.com/Yggdroot/LeaderF/issues/160):
  Search result window auto closed after choose a item add "--stayOpen".
* [Feature #162](https://github.com/Yggdroot/LeaderF/issues/162):
  Add `<PageUp>` and `<PageDown>` support.


Bug fixes:

* [BUG #164](https://github.com/Yggdroot/LeaderF/issues/164):
  LeaderfLine can't work after syntax off
* [BUG #165](https://github.com/Yggdroot/LeaderF/issues/165):
  LeaderfLine have UnicodeEncodeError in some file by use vim binary mode.
* Fix an issue that Popen.poll always returns None.
* [BUG #175](https://github.com/Yggdroot/LeaderF/issues/175)

v1.13 (2018-5-17)
==================

**BREAKING CHANGES**:

* `<ESC>` is changed into 'quit from LeaderF', use `<Tab>` as the key 'switch to normal mode'.

Feature enhancements:

* Add `g:Lf_StlSeparator.font`.
* [Feature #105](https://github.com/Yggdroot/LeaderF/issues/105):
  List all buffers in current tab.
  Add `LeaderfTabBuffer` and `LeaderfTabBufferAll`.
* [Feature #127](https://github.com/Yggdroot/LeaderF/issues/127):
  Add new option `g:Lf_HideHelp` to hide "Press F1 for help".
* Add ISSUE_TEMPLATE.md
* [Feature #143](https://github.com/Yggdroot/LeaderF/issues/143):
  Add bang support for `LeadfFunction`, `LeaderfBufTag` to enter normal mode directly.
  (Add support for `LeaderfFunction!`, `LeaderfBufTag!`)
* Add `g:Lf_Debug_Cmd` to help debug issue.
* LeaderfFunction: Support Rust and OCaml
* Add command p(preview the result) in normal mode.
* Add `g:Lf_ShowHidden`.
* [Feature #149](https://github.com/Yggdroot/LeaderF/issues/149):
  Add `g:Lf_MruWildIgnore`.
* [Feature #158](https://github.com/Yggdroot/LeaderF/issues/158):
  Use `<Tab>` to go back to "input" mode.

Bug fixes:

* [BUG #94](https://github.com/Yggdroot/LeaderF/issues/94):
  Utf-8 error.
* [BUG #95](https://github.com/Yggdroot/LeaderF/issues/95):
  LeaderfBufferAll doesn't list all buffers.
* [BUG #97](https://github.com/Yggdroot/LeaderF/issues/97):
  Long startup time when using NeoVim.
* [BUG #98](https://github.com/Yggdroot/LeaderF/issues/98):
  LeaderfFile does not work properly when using with lcd.
* Update the installation script.
* [BUG #102](https://github.com/Yggdroot/LeaderF/issues/102):
  Using LeaderF while having a quickfix window open is pushing splits up.
* [BUG #103](https://github.com/Yggdroot/LeaderF/issues/103):
  `let g:Lf_StlSeparator = { 'left': '', 'right': '' }` if encoding is not UTF-8.
* [BUG #121](https://github.com/Yggdroot/LeaderF/issues/121):
  `:LeaderfFile ~` outputs "No content!"
* Fix a bug open more than 10 buffers, then close some buffers until number of buffers less than 10, launch `LeaderfBuffer`, something goes wrong
* Fix hang when the instance buffer is wiped
* [BUG #129](https://github.com/Yggdroot/LeaderF/issues/129):
  Error: Key not present in Dictionary: font.
* [BUG #132](https://github.com/Yggdroot/LeaderF/issues/132):
  Error after reload vimrc.
* [BUG #137](https://github.com/Yggdroot/LeaderF/issues/137):
  Python os.chdir() takes no effect for NeoVim(https://github.com/neovim/neovim/issues/8336).
  Using `vim.chdir` as workaround.
* [BUG #141](https://github.com/Yggdroot/LeaderF/issues/141):
  Absurd height of the LeaderF window after resizing GVim while LeaderF is opening.
* [BUG #147](https://github.com/Yggdroot/LeaderF/issues/147):
  Don't show file name for current buffer.
* [BUG #155](https://github.com/Yggdroot/LeaderF/issues/155):
  Add augroup for autocmds.
* Fix an issue can not change directory correctly if buffer name has non-ascii characters.
* [BUG #155](https://github.com/Yggdroot/LeaderF/issues/155):
  Change VimLeave to VimLeavePre.
* [BUG #156](https://github.com/Yggdroot/LeaderF/issues/156):
  Error reported if encoding missing in tempfile.NamedTemporaryFile.
* [BUG #157](https://github.com/Yggdroot/LeaderF/issues/157):
  Keep selection when changing mode.
* [BUG #159](https://github.com/Yggdroot/LeaderF/issues/159):
  Error occurs if buffer list empty.

v1.12 (2017-11-11)
==================

**BREAKING CHANGES**:

* Change the default value of `g:Lf_WildIgnore`

  From
  ```vim
  let g:Lf_WildIgnore = {
            \ 'dir': ['.svn','.git','.hg'],
            \ 'file': ['*.sw?','~$*','*.bak','*.exe','*.o','*.so','*.py[co]']
            \}
  ```
  to
  ```vim
  let g:Lf_WildIgnore = {
            \ 'dir': ['.svn','.git','.hg'],
            \ 'file': []
            \}
  ```

Feature enhancements:

* Refactor the code to make LeaderF extensible.
* Better `asynchronous` experience.
* Add **helpExpl**.
* Add **colorschemeExpl**.
* Optimize the fuzzy matching algorithm.
* Make history editable.
* [Feature #43](https://github.com/Yggdroot/LeaderF/issues/43):
  Add `g:Lf_RootMarkers` and `g:Lf_WorkingDirectoryMode`.
* [Feature #54](https://github.com/Yggdroot/LeaderF/issues/54):
  Change the keys in normal mode.
* Add fuzzy matching algorithm written in **C**.
* [Feature #62](https://github.com/Yggdroot/LeaderF/issues/62):
  Add `g:Lf_RememberLastSearch` to remember last search.
* Set the default color of light background.
* [Feature #64](https://github.com/Yggdroot/LeaderF/issues/64):
  Add `g:Lf_UseCache`.
* Add window position `aboveleft` and `belowright`.
* Add support for `*.pyw` file
* [Feature #83](https://github.com/Yggdroot/LeaderF/issues/83):
  Add the following commands.
  
    | Command                    | Description
    | ---                        | -----------
    | `:LeaderfFilePattern <pattern>` | like `LeaderfFile`, with `pattern` inputted in advance
    | `:LeaderfFileCword`        | like `LeaderfFile`, with word under the cursor as pattern inputted in advance
    | `:LeaderfBufferPattern <pattern>` | like `LeaderfBuffer`, with `pattern` inputted in advance
    | `:LeaderfBufferCword`      | like `LeaderfBuffer`, with word under the cursor as pattern inputted in advance
    | `:LeaderfMruPattern <pattern>` | like `LeaderfMru`, with `pattern` inputted in advance
    | `:LeaderfMruCword`         | like `LeaderfMru`, with word under the cursor as pattern inputted in advance
    | `:LeaderfMruCwdPattern <pattern>` | like `LeaderfMruCwd`, with `pattern` inputted in advance
    | `:LeaderfMruCwdCword`      | like `LeaderfMruCwd`, with word under the cursor as pattern inputted in advance
    | `:LeaderfTagPattern <pattern>` | like `LeaderfTag`, with `pattern` inputted in advance
    | `:LeaderfTagCword`         | like `LeaderfTag`, with word under the cursor as pattern inputted in advance
    | `:LeaderfBufTagPattern <pattern>` | like `LeaderfBufTag`, with `pattern` inputted in advance
    | `:LeaderfBufTagCword`      | like `LeaderfBufTag`, with word under the cursor as pattern inputted in advance
    | `:LeaderfBufTagAllPattern <pattern>` | like `LeaderfBufTagAll`, with `pattern` inputted in advance
    | `:LeaderfBufTagAllCword`   | like `LeaderfBufTagAll`, with word under the cursor as pattern inputted in advance
    | `:LeaderfFunctionPattern <pattern>` | like `LeaderfFunction`, with `pattern` inputted in advance
    | `:LeaderfFunctionCword`    | like `LeaderfFunction`, with word under the cursor as pattern inputted in advance
    | `:LeaderfFunctionAllPattern <pattern>` | like `LeaderfFunctionAll`, with `pattern` inputted in advance
    | `:LeaderfFunctionAllCword` | like `LeaderfFunctionAll`, with word under the cursor as pattern inputted in advance
    | `:LeaderfLinePattern <pattern>` | like `LeaderfLine`, with `pattern` inputted in advance
    | `:LeaderfLineCword`        | like `LeaderfLine`, with word under the cursor as pattern inputted in advance
    | `:LeaderfLineAllPattern <pattern>` | like `LeaderfLineAll`, with `pattern` inputted in advance
    | `:LeaderfLineAllCword`     | like `LeaderfLineAll`, with word under the cursor as pattern inputted in advance
    | `:LeaderfHelpPattern <pattern>` | like `LeaderfHelp`, with `pattern` inputted in advance
    | `:LeaderfHelpCword`        | like `LeaderfHelp`, with word under the cursor as pattern inputted in advance

Bug fixes:

* Fix issue that git can not list untracked files.
* Suppress error messages of rg.
* Fix Esc delay issue.
* [BUG #48](https://github.com/Yggdroot/LeaderF/issues/48):
  Typing in the prompt is slow for Macvim.
* [BUG #53](https://github.com/Yggdroot/LeaderF/issues/53)
* [BUG #56](https://github.com/Yggdroot/LeaderF/issues/56):
  "NameError: global name 'FileNotFoundError' is not defined".
* [BUG #59](https://github.com/Yggdroot/LeaderF/issues/59):
  Sometimes g:Lf_CommandMap did not take effect.
* [BUG #61](https://github.com/Yggdroot/LeaderF/issues/61):
  :LeaderfHistorySearch error.
* Refactor the highlight functions fix a crash when text = 'shF一.txt' pattern = 'sf'
  solution: `pattern_mask[tolower(c)]` => `pattern_mask[(uint8_t)tolower(c)]`
* Fix an issue that if `set guicursor=a:block-blinkon0`, the cursor disappears after launching and quitting LeaderF
* [BUG #81](https://github.com/Yggdroot/LeaderF/issues/81):
  Error when searching using `;`.
* [BUG #82](https://github.com/Yggdroot/LeaderF/issues/82):
  Can't open file in directory with `+` as first character of directory name.
* [BUG #88](https://github.com/Yggdroot/LeaderF/issues/88):
  Suppress the error message.
* [BUG #89](https://github.com/Yggdroot/LeaderF/issues/89)

v1.11 (2017-7-6)
================

Feature enhancements:

* [FEATURE #35](https://github.com/Yggdroot/LeaderF/issues/35):
  Add async support.
* Add preview support for bufTagExpl
* Add preview support for functionExpl
* Make preview available in normal mode
* Add **SelfExpl**

Bug fixes:

* Minor bug fixed.

v1.10 (2017-6-16)
=================

Only supports `vim7.4.330+` from this version release.

**BREAKING CHANGES**:

* Change the default value of `g:Lf_PreviewCode` from 1 to 0.

Feature enhancements:

* Enhance the UI of bufExplorer and mruExplorer.
* Replace vim.command with lfCmd, replace vim.eval with lfEval.
* Beautify the statusline.
* [FEATURE #8](https://github.com/Yggdroot/LeaderF/issues/8):
  Add navigating tags support.
* Add navigating tags of opening buffers.
* Add "autocmd BufWipeout" to clear useless cache.
* Add `LeaderfFunction` and `LeaderfFunctionAll`.
* Add `LeaderfLine` and `LeaderfLineAll`.
* Add `LeaderfHistoryCmd` and `LeaderfHistorySearch`.
* A little optimization of fuzzy match algorithm.
* Add async support and execute command in parallel
* Add support for external command use '`rg`', '`pt`', '`ag`', '`find`' by default
* Add `g:Lf_DefaultExternalTool`, `g:Lf_UseVersionControlTool`

Bug fixes:

* Fix an issue that highlight is wrong when `g:Lf_ShowRelativePath` is 0 e.g. c:\abc.txt
* Fix an issue that it will get stuck if select too many files
* Fix https://github.com/SpaceVim/SpaceVim/issues/52
* '`modifiable`' attribute must have a Boolean value
* [BUG #41](https://github.com/Yggdroot/LeaderF/issues/41):
  High cup usage.
* [BUG #44](https://github.com/Yggdroot/LeaderF/issues/44):
  Install error on OSX.
* Fix the issue that <CR> can not open file, the issue is caused by 47d340a.
* [BUG #46](https://github.com/Yggdroot/LeaderF/issues/46):
  `<leader>` is not always '`,`'.
* Some workarounds for neovim.
* Do not show "Type  :quit<Enter>  to exit Nvim"
* [BUG #48](https://github.com/Yggdroot/LeaderF/issues/48):
  Typing in the prompt is slow.
* Fix an issue that can not terminate the python subprocess launched with shell=True.
* [BUG vim #1738](https://github.com/vim/vim/issues/1738)
* subprocess 'shell=False' can not use pipe e.g. `find . -type f | sed 's#\./##'`
* fix a bug that if g:Lf_WildIgnore has '.' in it
* [BUG #50](https://github.com/Yggdroot/LeaderF/issues/50)

v1.01 (2016-12-16)
==================

This is the last version release that supports vim7.3.

* Optimize the fuzzy matching algorithm.
* Fix many bugs.
* Change license to Apache License, Version 2.0.

v1.00 (2013-12-29)
==================

Initial commit.


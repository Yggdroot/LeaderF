LeaderF
=======

This plugin is mainly used for locating files, buffers, mrus in large project.

 - Written in Python.
 - Support for fuzzy and regex searching.
 - Manage buffers and mrus.
 - Open multiple files at once.
 - Extensible.

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

Usage
-----

 - `:LeaderfFile` or `:LeaderfFile [directory]` or `,f`<br>
 Launch LeaderF to search files.

 - `:LeaderfBuffer` or `,b`<br>
 Launch LeaderF to search buffers.

 - `:LeaderfMru`<br>
 Launch LeaderF to search Mru.
 
 - `:LeaderfMruCwd`<br>
 Launch LeaderF to search Mru in current working directory.

 - `:LeaderfTag`<br>
 Launch LeaderF to navigate tags.

Once LeaderF is launched:

 - `<C-C>` : quit from LeaderF.
 - `<C-R>` : switch between fuzzy search mode and regex mode.
 - `<C-F>` : switch between full path search mode and name only search mode.
 - `<ESC>` : switch to normal mode.
 - `<C-V>`, `<S-Insert>` : paste from clipboard.
 - `<C-U>` : clear the prompt.
 - `<C-J>`, `<Down>`, `<C-K>`, `<Up>` : navigate the result list.
 - `<2-LeftMouse>` or `<CR>` : open the file under cursor or selected(when multiple files are selected).
 - `<C-X>` : open in horizontal split window.
 - `<C-]>` : open in vertical split window.
 - `<C-T>` : open in new tabpage.
 - `<F5>`  : refresh the cache.
 - `<C-LeftMouse>` or `<C-S>` : select multiple files.
 - `<S-LeftMouse>` : select consecutive multiple files.
 - `<C-A>` : select all files.
 - `<C-L>` : clear all selections.
 - `<BS>`  : delete the preceding character in the prompt.
 - `<Del>` : delete the current character in the prompt.
 - `<Home>`: move the cursor to the begin of the prompt.
 - `<End>` : move the cursor to the end of the prompt.
 - `<Left>`: move the cursor one character to the left.
 - `<Right>` : move the cursor one character to the right.

Input formats:

 - In **NameOnly** mode (*fuzzy*)

 `'abc'` is interpreted as vim's regexp `'a.\{-}b.\{-}c'`.<br>
 If the first character you input is `';'`, then the searching will be the same as in **FullPath** mode.<br>
 If you input string as `'abc;def'`, then `'abc'` will match the file name and `'def'` will match the directory name.

 - In **FullPath** mode (*fuzzy*)

 Same as in **NameOnly** mode except that the pattern will match the full path but not the file name only.

 - In **Regexp** mode

 The input string is the same as the Vim's regexp.

Related works
-------------

 - [ctrlp][4] is a great plugin. Some ideas of my plugin come from it.

Advantages over ctrlp
---------------------

The only advantage over ctrlp is performance. If you are smart enough, perhaps you can find more.


License
-------

This plugin is released under the Apache License, Version 2.0 (the "License").


  [1]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_1.gif
  [2]: https://github.com/Yggdroot/Images/blob/master/leaderf/leaderf_2.gif
  [3]: https://github.com/gmarik/Vundle.vim
  [4]: https://github.com/kien/ctrlp.vim

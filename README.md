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

![enter image description here][1]

![enter image description here][2]

Requirements
------------

 - vim7.0 or higher.
 - vim compiled with Python support, you can check by using `echo has('python')` or `echo has('python3')` to see if the result is `1`.

Installation
------------

To install this plugin just put the plugin files in your `~/.vim` (Linux) or `~/vimfiles` (Windows).<br>
For [Vundle][3] user, just add `Bundle 'Yggdroot/LeaderF'` to your `.vimrc`.

Usage
----- 

 - `:Leaderf` or `:Leaderf [directory]` or `,f`<br>
 Launch LeaderF to search files.

 - `:LeaderfBuffer` or `,b`<br>
 Launch LeaderF to search buffers.

 - `:LeaderfMru`<br>
 Launch LeaderF to search Mru.

Once LeaderF is launched:

 - `<C-C>`, `<C-Q>` : quit from LeaderF.
 - `<C-R>` : switch between fuzzy search mode and regex mode.
 - `<C-F>` : switch between full path search mode and name only search mode.
 - `<ESC>` : switch to normal mode.
 - `<C-V>` : paste from clipboard.
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

Input formats:

 - In **NameOnly** mode (*fuzzy*)

 `'abc'` is interpreted as vim's regexp `'a.\{-}b.\{-}c'`.<br>
 If the first character you input is `'/'`, then the searching will be the same as in **FullPath** mode.<br>
 If you input string as `'abc/def/gh'`, then `'abc'` will match the file name and `'def/gh'` will match the directory name as in **FullPath** mode.

 - In **FullPath** mode (*fuzzy*)
 
 `'ab'` is interpreted as vim's regexp `'a[^/]\{-}b'`.<br>
 `'/'` is interpreted as vim's regexp `'[/].\{-}'`.<br>
 `'ab/c'` is interpreted as vim's regexp `'a[^/]\{-}b[^/]\{-}[/].\{-}[^/]\{-}c'`.<br>
 If you want to search `'/example/full/path/mode/filename.txt'`, you must input like this: `'ex/fu/pa/mo/file'` (**NOTE** that `'/'` is essential in the input), and `'exfupamofile'` won't match.<br>
 The purpose for this restriction is to decrease the number of matches.

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

This plugin is released under the Vim License.


  [1]: http://imageshack.com/a/img802/1026/iei.gif
  [2]: http://imageshack.com/a/img809/2369/mnu.gif
  [3]: https://github.com/gmarik/Vundle.vim
  [4]: https://github.com/kien/ctrlp.vim

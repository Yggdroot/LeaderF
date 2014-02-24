LeaderF
=======

This plugin is mainly used for searching files, buffers, mrus in large project.

 - Written in Python.
 - Support for fuzzy and regex searching.
 - Manage buffers and mrus.
 - Open multiple files at once.
 - Extensible.

Screenshots
-----------

Requirements
------------

 - vim7.0 or higher.
 - vim compiled with Python support, check by using `echo has('python')` or `echo has('python3')` to see if the result is `1`.

Installation
------------

To install this plugin just put the plugin files in your `~/.vim` (Linux) or `~/vimfiles` (Windows).<br>
For [Vundle][1] user, just add `Bundle 'Yggdroot/LeaderF'` to your `.vimrc`.

Usage
-----



Related works
-------------

 - [ctrlp][2] is a great plugin. Some ideas of my plugin come from it. 

Advantages over ctrlp
---------------------

The only advantage over ctrlp is performance. If you are smart enough, perhaps you can find more.

License
-------

This plugin is released under the Vim License.

  [1]: https://github.com/gmarik/Vundle.vim
  [2]: https://github.com/kien/ctrlp.vim

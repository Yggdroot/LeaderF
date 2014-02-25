#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


#*****************************************************
# Explorer
#*****************************************************
class Explorer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getContent(self, *args, **kwargs):
        pass

    @abstractmethod
    def acceptSelection(self, *args, **kwargs):
        pass

    @abstractmethod
    def getStlFunction(self):
        pass

    def getFreshContent(self, *args, **kwargs):
        pass

    def getStlCurDir(self):
        return ''

    def supportsMulti(self):
        return False

    def supportsFullPath(self):
        return False

    def supportsSort(self):
        return False



#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob



def fun(path, parent, Id, jsonstr):


    for i, fn in enumerate(glob.glob(path + os.sep + '*')):

        if os.path.isdir(fn):
            jsonstr += '''{"attributes":{"id":"''' + str(Id) + '''''"},"parent":"''' + str(
                parent) + '''","state":{"opened":false},"text":"''' + os.path.basename(fn) + '''","children":['''
            parent = Id
            Id += 1
            jsonstr = fun(fn, parent, Id, jsonstr)

            jsonstr += "]}"
            if i < len(glob.glob(path + os.sep + '*')) - 1:
                jsonstr += ","

        else:

            jsonstr += '''{"attributes":{"id":"''' + str(Id) + '''''"},"parent":"''' + str(
                parent) + '''","state":{"opened":false},"text":"''' + os.path.basename(
                fn) + '''","icon":"fa fa-file-text-o"}'''
            Id += 1
            if i < len(glob.glob(path + os.sep + '*')) - 1:
                jsonstr += ","

    return jsonstr
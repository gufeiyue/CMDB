#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import glob
import sys

parent = 0
Id = 0


def fun(path,parent):
    global Id  
    global jsonstr

    for i,fn in enumerate(glob.glob(path + os.sep + '*' )):  
         
        if os.path.isdir(fn):  
            jsonstr+='''{"attributes":{"id":"'''+ str(Id)+'''''"},"parent":"'''+str(parent)+'''","state":{"opened":false},"text":"'''+os.path.basename(fn)+'''","children":['''  
            parent=Id  
            Id+=1  
            for j,li in enumerate(glob.glob(fn + os.sep + '*' )):  
                  
                if os.path.isdir(li):  
                    jsonstr+='''{"attributes":{"id":"'''+ str(Id)+'''''"},"parent":"'''+str(parent)+'''","state":{"opened":false},"text":"'''+os.path.basename(li)+'''","children":['''  
                    parent=Id  
                    Id+=1  
                    fun(li,parent)  
                    jsonstr+="]}"  
                    if j<len(glob.glob(fn + os.sep + '*' ))-1:  
                        jsonstr+=","                        
                                
                else:  
                    jsonstr+='''{"attributes":{"id":"'''+ str(Id)+'''''"},"parent":"'''+str(parent)+'''","state":{"opened":false},"text":"'''+os.path.basename(li)+'''","icon":"fa fa-file-text-o"}'''  
                    Id+=1  
                    if j<len(glob.glob(fn + os.sep + '*' ))-1:  
                        jsonstr+=","  
            jsonstr+="]}"  
            if i<len(glob.glob(path + os.sep + '*' ))-1:  
                        jsonstr+=","  
            
        else:  
              
            jsonstr+='''{"attributes":{"id":"'''+ str(Id)+'''''"},"parent":"'''+str(parent)+'''","state":{"opened":false},"text":"'''+os.path.basename(fn)+'''","icon":"fa fa-file-text-o"}'''  
            Id+=1              
            if i<len(glob.glob(path + os.sep + '*' ))-1:  
               jsonstr+=","

    return jsonstr


def get_json(jsonstr):
    return jsonstr

if __name__ == '__main__':

    path = sys.argv[1]
    #file_path = sys.argv[2]

    #path="/Users/gufy/Desktop/config/prod"

    jsonstr="["
    jsonstr=fun(path,0)
    jsonstr+="]"
    get_json(jsonstr)
    # file_object = open(file_path, 'w')
    # file_object.write(jsonstr)
    # file_object.close()

# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 17:06:17 2019

@author: Ale
"""

c1 = [("a", [1,2,3]), ("f", [3]), ("x", [4,2])] 
c2 = [("a", [1,2]), ("h", [1]), ("s", [2]), ("w", [4]), ("r", [7,3])]

def foo(cc):    
    
    if cc == []:
        return []
    
    if len(cc) == 1:        
        allperms = []
        for i in cc[0][1]:
            allperms.append([(cc[0][0],i)])
        return allperms
        
    
    head = cc[0]
    body = cc[1:]
    
    
    allperms = []
    
    for e in head[1]:
        ret = foo(body)
        for r in ret:
            allperms.append([(head[0],e)]+r)
            
            
    return allperms

aaa = foo(c1)
print(aaa)
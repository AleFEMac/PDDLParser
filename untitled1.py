# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 10:58:31 2019

@author: Ale
"""

from utils import take_enclosed_data
import boolean as b

def partition_recursively(string):
    
    ss = string[1:-1]
    
    if '(' not in ss:
        return {ss.split()[0]: ss.split()[1:]}
    
    head = ss.split()[0]
    
    res = {head:[]}
    
    data_l = take_enclosed_data(ss.replace(head, '', 1).strip())
    
    for d in data_l:        
        out = partition_recursively(d)
        
        res[head].append(out)
    
    return res

def classify_parameter(p, level):
    
    assert p[0] == '?'
    
    label = set()
    
    for i in level:
        found = False
        ii = level[i]
        for j in ii:
            if type(j) != dict:
                if j == p:
                    label.add(i)
                    found = True
                    break
            else:
                out = classify_parameter(p, j)
                label |= out
                
            if found:
                break
    return label

params1 = "?obj1 ?room1 ?gripper1"
prec1 = "(and (ball ?obj1) (room ?room1) (gripper ?gripper1) (at ?obj1 ?room1) (at-robby ?room1) (free ?gripper1))"
effect1 = "(and (carry ?obj1 ?gripper1) (not (at ?obj1 ?room1)) (not (free ?gripper1)))"
params2 = "?obj ?room ?gripper"
prec2 = "(and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))"
effect2 = "(and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))"

pl = params1.split()
p2 = params2.split()

p_effect1 = partition_recursively(effect1)
p_effect2 = partition_recursively(effect2)

print(pl)
print(p2)
print(p_effect1)
print(p_effect2)

classes1 = {}
classes2 = {}

for p in pl:
    classes1[p] = classify_parameter(p, p_effect1)
    
for p in p2:
    classes2[p] = classify_parameter(p, p_effect2)

print(classes1)
print(classes2)


    

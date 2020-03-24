# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:35:14 2020

@author: Ale
"""

def classify_parameter(p, level, classes=[], neglevel=0):
    
    assert p[0] == '?'
    
    # Set of labels possessed by the parameter on this level
    label = set()
    
    # Check every argument of the current operator
    for i in level:
        found = False           # Variable to record if the parameter was found
        ii = level[i]           # Check the contents of the argument
        for j in ii:            # Check all of said contents (sub-arguments)
            
            # If the sub-argument is not a dictionary, it must be a predicate
            if type(j) != dict:
                
                # Check if one of the sub-argument is the parameter we were
                # looking for, it was the only sub-argument, it's not being
                # negated and either it's one of the desired classes or there
                # are no desired classes
                if j == p and len(ii) == 1 and neglevel%2 == 0 and (classes == [] or i in classes):
                    label.add(i)
                    found = True
                    break
            
            # If the sub-argument is a dictionary, it must be an AND, OR, NOT
            # statement
            else:
                out = classify_parameter(p, j, classes)
                label |= out
                
            if found:
                break
    return label

def max_similitude_coup(ap):
    
    occ_dict = {}
    
    for d in ap:
        cur_empty = 0
        for i in d:
            if d[i] == '':
                cur_empty += 1
        if cur_empty not in occ_dict:
            occ_dict[cur_empty] = []
        if d not in occ_dict[cur_empty]:
            occ_dict[cur_empty].append(d)
    
    return occ_dict[min(list(occ_dict.keys()))]


def find_min_empty(ap):
    
    min_empty = len(ap[0])
    min_dict = {}
    
    for d in ap:
        cur_empty = 0
        for i in d:
            if d[i] == '':
                cur_empty += 1
        if cur_empty < min_empty:
            min_dict = d
            min_empty = cur_empty
    
    return min_dict

def find_negatives(level, params, classes, neg=False):
    
    op = list(level.keys())[0]
    tbr = set()
    
    print(level)
    
    if op == "and" or op == "or":
        for a in level[op]:
            res = find_negatives(a, params, classes)
            tbr |= res
            
    elif op == "not":        
        tbr |= find_negatives(level[op][0], params, classes, not neg)
    
    else:
        if op in classes and neg:
            for a in level[op]:
                if a[1:] in params:                    
                    tbr.add((a[1:],op))
    
    return tbr
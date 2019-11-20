# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd, collection_copy, align
import boolean as bb

# =============================================================================
# Make couplings of the parameters from two different actions
# =============================================================================
def couple_params(ac1, ac2):
    
    matches = {}
    matched = []

    for p in ac1:
        matches[p] = []
        for pp in ac2:
            if ac2[pp].issubset(ac1[p]):                    
                matches[p].append(pp)
                matched.append(pp)
                
    return matches

def check_action_compat(a1, a2):
    

    bool_alg = bb.BooleanAlgebra()      
        
    t1 = to_boolean(partition_recursively(a1['precondition'].replace('-', '___')))
    t2 = to_boolean(partition_recursively(a1['effect'].replace('-', '___')))
    t3 = to_boolean(partition_recursively(a2['precondition'].replace('-', '___')))

    ex1 = bool_alg.parse('(' + t1 + ')').simplify()
    ex2 = bool_alg.parse('(' + t2 + ')' + ' & (' + t3 + ')').simplify()
    
    if not (ex1 != False and ex2 != False):
        return False
    else:
        return True
        
        
# =============================================================================
# Check that the preconditions of an action are not always false
# =============================================================================
def check_action_precs(act):
        
    ba = bb.BooleanAlgebra()
    
    # If the parametric preconditions are False, the action will never be
    # performable
    if ba.parse(to_boolean(partition_recursively(act['precondition'].replace('-', '___')))).simplify() == False:
        return False
    else:
        return True 

def combine_actions(a1, a2, par_dict, hascost=True):
    
    ea1 = a1['effect']
    ea2 = a2['effect']
    
    ne1 = compose_partition(partition_recursively(ea1))
    ne2 = compose_partition(partition_recursively(ea2))
        
    a12 = {
        'parameters': list(par_dict.keys()),
        'precondition': "(or " + a1['precondition'] + " (and " + a1['effect'] + ' ' + a2['precondition'] + ") )",
        'effect': '(and ' + ne1.replace("  ", " ") + "   " + ne2.replace("  ", " ") + " )"
    }
    
    if hascost:
        tot_cost = a1['cost'] + a2['cost']
        a12['cost'] = tot_cost
        a12['effect'] = a12['effect'][:-1]  + "(increase (total-cost) " + str(tot_cost) + ") )"
    
    return a12

def assign_perms(level):
    
    if len(level) == 0:
        return [{}]
    
    level_copy = collection_copy(level)
    
    all_perms = []

    level_copy = collection_copy(level)
    
    for par in level_copy:
        
        par_level = collection_copy(level_copy)
        cur_values = par_level.pop(par)
        
        if cur_values == []:
                        
            ret = assign_perms(par_level)            
            for poss in ret:
                poss[par] = ''
                all_perms.append(poss)
        
        else:
            
            for val in cur_values:
                
                val_level = collection_copy(par_level)
                
                for oth in val_level:
                    if val in val_level[oth]:
                        val_level[oth].remove(val)
                
                ret = assign_perms(val_level)
                for poss in ret:
                    poss[par] = val
                    all_perms.append(poss)
    return all_perms

def partition_recursively(string, remove_increase=True):
    
    ss = string.strip()[1:-1].strip()
    
    if '(' not in ss:
        return {ss.split()[0]: ss.split()[1:]}
    
    head = ss.split()[0]
    
    if head == 'increase' and remove_increase:
        return ""
    
    res = {head:[]}
    
    data_l = take_enclosed_data(ss.replace(head, '', 1).strip())
    
    for d in data_l:        
        out = partition_recursively(d)
        
        if out != "":
            res[head].append(out)
    
    return res

def compose_partition(level):
    
    comp = ""
    op = list(level.keys())[0]
    
    if op == "and":
        comp += "(and "
        for arg in level[op]:
            ret = compose_partition(arg)
            comp += ret + ' '
        comp += ")"
        return comp
    elif op == "or":
        comp += "(or "
        for arg in level[op]:
            ret = compose_partition(arg)
            comp += ret + ' '
        comp += ")"
        return comp
    elif op == "not":
        comp += "(not " + compose_partition(level[op][0]) + ")"
        return comp
    else:
        comp += "(" + str(op) + ' '
        for arg in level[op]:
            comp += arg + ' '
        comp += ")"        
        return comp

def classify_parameter(param, exprs, classes=[]):
    
    if param[0] == '?':
        param = param[1:]
    
    param_classes = set()
    
    for exp in exprs:                       # Cycle on the OR-separated statements                
        
        for item in exp:                    # Cycle on every item of a statement
                        
            # Get predicate/operator, there is only one per dictionary
            key = list(item.keys())[0]     
            
            if key == 'not':                # NOT operator case
                
                kkey = item[key][0]         # Take the class being NOT-ed
                
                # It's an acceptable class
                if kkey in classes:
                    param_classes.add(kkey) # Add the class to the set
            
            else:
                
                # It's an acceptable class
                if key in classes:                
                    param_classes.add(key)           
                    
    return param_classes

# =============================================================================
# TO BE SCRAPPED
# =============================================================================
def classify_parameter_old(p, level, classes=[], neglevel=0):
    
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
# =============================================================================
# 
# =============================================================================

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


def to_boolean(level):
    
    op = list(level.keys())[0]
    expression = ""
    
    if op == "and":
        helpme = []
        for idx, a in enumerate(level[op]):
            new_a = to_boolean(a)
            helpme.append(new_a)
            expression += "(" + new_a + ")"
            if idx < len(level[op])-1:
                expression += " & "
        
    elif op == "or":
        for idx, a in enumerate(level[op]):
            new_a = to_boolean(a)
            expression += "(" + new_a + ")"
            if idx < len(level[op])-1:
                expression += " | "
    
    elif op == "not":
        new_a = to_boolean(level[op][0])
        expression += "!(" + new_a + ")"
    
    else:
        expression += str(op)
        for a in level[op]:
            expression += "_" + str(a[1:])     
    
    return expression  
    
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

def apply_negative(col):
    
    assert type(col) == list
    
    res = []
    
    for c in col:
        op = list(c.keys())[0]
        if op == 'not':
            res.append(c[op])
        else:
            res.append({'not':{op:c[op]}})
        
    return res 
        

def toDNF(level, params={}):
    
    op = list(level.keys())[0]
    
    
    if op == "and":
        
        # Create the collection of and-clauses to return
        lvl = [[]]
        
        # Arguments of the current operator
        for a in level[op]:
            
            # Current return
            new_lvl = []
            
            # Deep copy of collection returned from successive recursive step
            res_og = toDNF(a, params)
            res = collection_copy(res_og)            
            
            for r in res:
                for rr in lvl:
                    new_lvl.append(rr+r)
            lvl = new_lvl
        
        return lvl
        
    elif op == "or":
        # Create the collection of and-clauses to return
        lvl = []
        
        # Arguments of the current operator
        for a in level[op]:
            
            # Current return
            new_lvl = []
            
            # Deep copy of collection returned from successive recursive step
            res_og = toDNF(a, params)
            res = collection_copy(res_og)            
            
            for r in res:
                new_lvl.append(r)
            lvl = lvl + new_lvl
        
        return lvl
        
    elif op == "not":
        # Create the collection of and-clauses to return
        lvl = []        
        
        a = level[op][0]    # NOT operator can only have a single argument        
        new_lvl = []        # Initialize current return
        
        # Deep copy of collection returned from successive recursive step
        res_og = toDNF(a, params)
        res = collection_copy(res_og)
        
        pos_al = align(res)
        neg_al = []
        for p in pos_al:
            neg = apply_negative(p)
            neg_al.append(neg)
        
        return neg_al
        
    else:        
        return [[level]]
    
    return


# =============================================================================
# TESTING PORTION
# =============================================================================


actions = {
        'test': {'parameters': ['p1', 'p2'], 
                 'precondition': '(not (and (pr1 p1) (pr2 p1 p2)))', 
                 'effect': '(and (at-robby ?to) (not (at-robby ?from)))'}, 
        'move': {'parameters': ['from', 'to'], 
                 'precondition': '(and (room ?from) (room ?to) (at-robby ?from))', 
                 'effect': '(and (at-robby ?to) (not (at-robby ?from)))'}, 
        'pick': {'parameters': ['obj', 'room', 'gripper'], 
                 'precondition': '(and (ball ?obj) (room ?room) (gripper ?gripper) (at ?obj ?room) (at-robby ?room) (free ?gripper))', 
                 'effect': '(and (carry ?obj ?gripper) (not (at ?obj ?room)) (not (free ?gripper)))'}, 
        'drop': {'parameters': ['obj', 'room', 'gripper'], 
                 'precondition': '(and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))', 
                 'effect': '(and (at ?obj ?room) (free ?gripper) (not (carry ?obj ?gripper)))'}
        }

pr1 = partition_recursively(actions['test']['precondition'])
pr2 = partition_recursively(actions['pick']['precondition'])
ef1 = partition_recursively(actions['test']['effect'])
ef2 = partition_recursively(actions['pick']['effect'])

p1 = toDNF(pr1)
p2 = toDNF(pr2)
e1 = toDNF(ef1)
e2 = toDNF(ef2)

print("p1", p1)
# =============================================================================
# print("p2", p2)
# print("e1", e1)
# print("e2", e2)
# =============================================================================

# =============================================================================
# poss_classes = ['obj', 'ball', 'gripper']
# 
# 
# 
# pr1 = "(or (and (room ?par_0) (room ?par_1) (at-robby ?par_0)) (and (and (at-robby ?par_1) (not (at-robby ?par_0))) (and (room ?par_0) (room ?par_1) (at-robby ?par_0))) )"
# pp1 = partition_recursively(pr1)
# pe1 = "(and (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) )   (and (at-robby ?par_1 ) (not (at-robby ?par_0 )) ) )"
# pq1 = partition_recursively(pe1)
# a = toDNF(pp1)
# e = toDNF(pq1)
# 
# print("\na", a)
# =============================================================================

# =============================================================================
# tt = '?par_0'
# pc = classify_parameter(tt, a, poss_classes)
# print(pc)
# 
# =============================================================================


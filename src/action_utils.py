# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd, collection_copy
import boolean as bb
import itertools

# =============================================================================
# Make couplings of the parameters from two different actions
# =============================================================================
def couple_params(ac1, ac2):
    
    matches = {}
    matched = []

    for p in ac1:
        matches[p] = []
        for pp in ac2:
            
# =============================================================================
# Check if the parameter from the second action wasn't selected already,
# if all of its tags are shared with the parameter of the first action
# and vice versa            
# =============================================================================
            if ac2[pp].issubset(ac1[p]):                    
                matches[p].append(pp)
                matched.append(pp)
    
    for pp in ac2:
        if pp not in matched:
            matches[pp] = []
                
    return matches

def check_action_compat(a1, a2, bool_alg=None):
    
    if bool_alg == None:
        bool_alg = bb.BooleanAlgebra()      
        
    t1 = to_boolean(partition_recursively(a1['precondition'].replace('-', '___')))
    t2 = to_boolean(partition_recursively(a1['effect'].replace('-', '___')))
    t3 = to_boolean(partition_recursively(a2['precondition'].replace('-', '___')))
    
    ex1 = bool_alg.parse('(' + t2 + ')' + ' & (' + t3 + ')').simplify()
    ex2 = bool_alg.parse('(' + t1 + ')' + ' & (' + t3 + ')').simplify()
    
    if not (ex1 != False and ex2 != False):
        return False
    else:
        return True
        
        
        
def check_action_precs(act):
        
    ba = bb.BooleanAlgebra()
    
    if ba.parse(to_boolean(partition_recursively(act['precondition'].replace('-', '___')))).simplify() == False:
        return False
    else:
        return True 

def combine_actions(a1, a2, par_dict):
    
    ea1 = a1['effect']
    ea2 = a2['effect']
    tot_cost = a1['cost'] + a2['cost']
    
    ne1 = compose_partition(partition_recursively(ea1))
    ne2 = compose_partition(partition_recursively(ea2))
    
    a12 = {
        'parameters': list(par_dict.keys()),
        'precondition': "(or (and " + a1['precondition'] + ' ' + a2['precondition'] + ") (and " + a1['effect'] + ' ' + a2['precondition'] + ") )",
        'effect': '(and (' + ne1.replace("  ", " ") + " ) ( " + ne2.replace("  ", " ") + " )" + "(increase (total-cost) " + str(tot_cost) + ") )",
        'cost': tot_cost
    }
    
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

def classify_parameter(p, level, classes, neglevel=0):
    
    assert p[0] == '?'
    
    label = set()
    
    for i in level:
        found = False
        ii = level[i]
        for j in ii:
            if type(j) != dict:
                if j == p and len(ii) == 1 and neglevel%2==0 and i in classes:
                    label.add(i)
                    found = True
                    break
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


def to_boolean(level):
    
    op = list(level.keys())[0]
    expression = ""
    
    if op == "and":
        for a in level[op]:
            new_a = to_boolean(a)
            expression += "(" + new_a + ")"
            if a != level[op][-1]:
                expression += " & "
    elif op == "or":
        for a in level[op]:
            new_a = to_boolean(a)
            expression += "(" + new_a + ")"
            if a != level[op][-1]:
                expression += " || "
    
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
    
    if op == "and" or op == "and":
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
# =============================================================================
# 
# a1 = {
#       'name':'pick',
#       'parameters': ['obj1', 'room', 'gripper'],
#       'precondition': '(and (ball ?obj1) (room ?room) (gripper ?gripper) (at ?obj1 ?room) (at-robby ?room) (free ?gripper))',
#       'effect': '(and (carry ?obj1 ?gripper) (not (at ?obj1 ?room)) (not (free ?gripper)) (increase (total-cost) 1))',
#       'cost': 3
#       }
# 
# a3 = {
#       'name':'drop',
#       'parameters': ['obj', 'room', 'gripper'],
#       'precondition': '(and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))',
#       'effect': '(and (at ?obj ?room) (free ?gripper)   (not (carry ?obj ?gripper))(increase (total-cost) 3))',
#       'cost': 1
#       }
# 
# a2 = {
#       'name':'move',
#       'parameters': ['from', 'to'],
#       'precondition': '(and (room ?from) (room ?to) (at-robby ?from))',
#       'effect': '(and (at-robby ?to) (not (at-robby ?from)) (increase (total-cost) 6))',
#       'cost': 6
#       }
# 
# poss_classes = ['room', 'ball', 'gripper']
# 
# pp1 = partition_recursively(a1['precondition'])
# pe1 = partition_recursively(a1['effect'])
# 
# pp2 = partition_recursively(a2['precondition'])
# pe2 = partition_recursively(a2['effect'])
# 
# pp3 = partition_recursively(a3['precondition'])
# pe3 = partition_recursively(a3['effect'])
# 
# p1 = a1['parameters']
# p2 = a2['parameters']
# p3 = a3['parameters']
# 
# pr1 = {}
# pr2 = {}
# pr3 = {}
# 
# for p in a1['parameters']:
#     pr1[p] = classify_parameter('?'+p, pp1, poss_classes)    
# print("pr1:" + str(pr1))
# 
# for p in a2['parameters']:
#     pr2[p] = classify_parameter('?'+p, pp2, poss_classes)    
# print("pr2:" + str(pr2))
# 
# for p in a3['parameters']:
#     pr3[p] = classify_parameter('?'+p, pp3, poss_classes)    
# print("pr3:" + str(pr3))
# 
# print("===================")
# 
# actions = [a1, a2, a3]
# action_names = [x['name'] for x in actions]
# perms = []
# perms_names = []
# 
# for i in range(len(actions)):
#     for j in range(i+1, len(actions)):
#         if i == j:
#             break
#         perms.append((actions[i], actions[j]))
#         perms_names.append((actions[i]['name'], actions[j]['name']))
#         
# print("pena:", perms_names)
# 
# print("===================")
# 
# matches = {}
# matched = []
# 
# ac1 = pr1
# ac2 = pr2
# 
# print("ac1:", ac1)
# print("ac2:", ac2)
# 
# for p in ac1:
#     for pp in ac2:
#         if pp not in matched and ac1[p] == ac2[pp]:
#             label = 'v_'+str(len(matches))
#             matches[label] = (p, pp)
#             matched.append(pp)
#             break
# 
# print("mtch:", matches)
# 
# print("====================")
# 
# print(pe1)
# 
# 
# 
# fn1 = find_negatives(pe1, p1, poss_classes)
# fn2 = find_negatives(pe2, p2, poss_classes)
# 
# print("fn1:", fn1)
# print("fn2:", fn2)
# 
# print("=================")
# 
# for i in fn1:
#     ac1[i[0]].remove(i[1])
# 
# cp = couple_params(ac1, ac2)
# print("cp:", cp)
# 
# eap = assign_perms(cp)
# ap = []
# for p in eap:
#     if p not in ap:
#         ap.append(p)
# for p in ap:
#     print("p:", p)
# 
# min_dict = find_min_empty(ap)
# min_dicts = max_similitude_coup(ap)
# 
# print("md:", min_dict)
# print("mds:", min_dicts)
# 
# print("=================")
# 
# par_dict_list = []
# act_new_pars_list = []
# 
# for ii, x in enumerate(min_dicts):
#     
#     idx = 0
#     
#     aux1  = {}
#     aux2 = [{}, {}]
#     
#     pairing = min_dicts[ii]
#     
#     for i in x:
#         par_name = "par_" + str(idx)
#         aux1[par_name] = [i]
#         aux2[0][i] = par_name
#         if pairing[i] != '':
#             aux1[par_name].append(pairing[i])
#             aux2[1][pairing[i]] = par_name
#         idx += 1
#     
#     for p in a2['parameters']:
#         if p not in aux2[1]:
#             par_name = "par_" + str(idx)
#             aux1[par_name] = str(p)
#             aux2[1][str(p)] = par_name
#             idx += 1
#             
#     par_dict_list.append(aux1)
#     act_new_pars_list.append(aux2)
# 
# print("\n>pdl>", par_dict_list, "\n\n>anpl>", act_new_pars_list)
# 
# merged_actions = []
# name_count = {}
# 
# 
# for idx in range(len(par_dict_list)):
#     
#     na1 = collection_copy(a1)
#     na2 = collection_copy(a2)
#     
#     act_new_pars = act_new_pars_list[idx]
#     
#     nas = [na1, na2]
#     
#     for i, na in enumerate(nas):        
#         na['precondition'] = na['precondition'].replace(')', ') ').replace('(', ' (')
#         na['effect'] = na['effect'].replace(')', ') ').replace('(', ' (')
#         for p in act_new_pars[i]:
#             na['precondition'] = na['precondition'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
#             na['effect'] = na['effect'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
#     
#     ba = bb.BooleanAlgebra()
#     
#     ret = check_action_compat(a1, a2, ba)
#     
#     if not ret:
#         print("Actions are incompatible")
#     
#     a12 = combine_actions(a1, a2, par_dict_list[ii])    
#     name = na1['name'] + '_' + na2['name']
#     
#     if name in name_count:
#         name_count[name] += 1
#         a12['name'] = name + '_' + str(name_count[name])
#     else:
#         name_count[name] = 0
#         a12['name'] = name
#     
#     merged_actions.append(a12)   
#         
# =============================================================================

# =============================================================================
# for ma in merged_actions:
#     printd(ma)
# =============================================================================


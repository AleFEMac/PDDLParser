# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd
import boolean as bb

# =============================================================================
# Make couplings of the parameters from two different actions
# =============================================================================
def couple_params(ac1, ac2):
    
    matches = {}
    matched = []
    
    for p in ac1:
        for pp in ac2:
            
# =============================================================================
# Check if the parameter from the second action wasn't selected already,
# if all of its tags are shared with the parameter of the first action
# and vice versa            
# =============================================================================
            if pp not in matched and ac2[pp].issubset(ac1[p]) or ac1[p].issubset(ac2[pp]):
                if p not in matches:
                    matches[p] = []
                matches[p].append(pp)
                
    return matches

def check_action_precs(act):
        
    ba = bb.BooleanAlgebra()
    
    if ba.parse(to_boolean(partition_recursively(act['precondition'].replace('-', '___')))).simplify() == False:
        return False
    else:
        return True 

def combine_actions(a1, a2, par_dict):
    
    ea1 = a1['effect']
    ea2 = a2['effect']
    
    
    pe1 = partition_recursively(ea1)
    print("ea1:", pe1)
    
    a12 = {
        'parameters': list(par_dict.keys()),
        'precondition': a1['precondition'],
        'effect': '(and (' + a1['effect'].replace("  ", " ") + " ) ( " + a2['effect'].replace("  ", " ") + " ) )",
        'cost': a1['cost'] + a2['cost']
    }
    
    return a12

def assign_perms(level):
        
    lk = list(level.keys())
    
    if len(lk) == 0:
        return None
    
    par = lk[0]
    poss = []
    
    if len(level[par]) > 0:
        for x in level[par]:
            cur = {}
            
            for j in lk[1:]:
                aux = level[j].copy()
                if x in level[j]:  
                    aux.remove(x)
                cur[j] = aux
            
            res = assign_perms(cur)
            
            if res != None:
                for sub_dict in res:
                    sub_dict[par] = x
                    poss.append(sub_dict)
            else:
                poss.append({par:x})
    else:
        
        cur = level.copy()
        cur.pop(par)
        
        res = assign_perms(cur)
            
        if res != None:
            for sub_dict in res:
                sub_dict[par] = ''
                poss.append(sub_dict)
        else:
            poss.append({par:''})
                    
            
    
    return poss

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
        comp += "(" + str(op)
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
# a2 = {
#       'name':'drop',
#       'parameters': ['obj', 'room', 'gripper'],
#       'precondition': '(and (ball ?obj) (room ?room) (gripper ?gripper) (carry ?obj ?gripper) (at-robby ?room))',
#       'effect': '(and (at ?obj ?room) (free ?gripper)   (not (carry ?obj ?gripper))(increase (total-cost) 3))',
#       'cost': 1
#       }
# 
# a3 = {
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
# ap = assign_perms(cp)
# print("ap:", ap)
# 
# min_empty = len(ap[0])
# min_dict = {}
# 
# for d in ap:
#     cur_empty = 0
#     for i in d:
#         if d[i] == '':
#             cur_empty += 1
#     if cur_empty < min_empty:
#         min_dict = d
#         min_empty = cur_empty
# 
# min_dict = find_min_empty(ap)
# 
# print("md:", min_dict)
# 
# print("=================")
# 
# par_dict = {}
# act_new_pars = [{}, {}]
# 
# idx = 0
# for i in min_dict:
#     par_name = "par_" + str(idx)
#     par_dict[par_name] = [i]
#     act_new_pars[0][i] = par_name
#     if min_dict[i] != '':
#         par_dict[par_name].append(min_dict[i])
#         act_new_pars[1][min_dict[i]] = par_name
#     idx += 1
# 
# print("pd:", par_dict)
# print("anp:", act_new_pars)
#     
# na1 = a1.copy()
# na2 = a2.copy()
# 
# nas = [na1, na2]
# 
# for i, na in enumerate(nas):
#     napa = [act_new_pars[i][x] for x in na['parameters']]
#     na['precondition'] = na['precondition'].replace(')', ') ').replace('(', ' (')
#     na['effect'] = na['effect'].replace(')', ') ').replace('(', ' (')
#     for p in act_new_pars[i]:
#         na['precondition'] = na['precondition'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
#         na['effect'] = na['effect'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
# 
# print("=================")
# 
# ba = bb.BooleanAlgebra()
# 
# t1 = to_boolean(partition_recursively(a1['precondition'].replace('-', '___')))
# t2 = to_boolean(partition_recursively(a1['effect'].replace('-', '___')))
# t3 = to_boolean(partition_recursively(a2['precondition'].replace('-', '___')))
# 
# ex1 = ba.parse('(' + t2 + ')' + ' & (' + t3 + ')').simplify()
# ex2 = ba.parse('(' + t1 + ')' + ' & (' + t3 + ')').simplify()
# 
# print("ex1:", ex1)
# print("ex2:", ex2)
# 
# if ex1 == False or ex2 == False:
#     print("Actions are incompatible")
#     
# print("=================")
# 
# a12 = {
#       'name':na1['name'] + '_' + na2['name'],
#       'parameters': list(par_dict.keys()),
#       'precondition': na1['precondition'],
#       'effect': '(and (' + na1['effect'].replace("  ", " ") + " ) ( " + na2['effect'].replace("  ", " ") + " ) )",
#       'cost': na1['cost'] + na2['cost']
#       }
# 
# printd(a12)
# 
# print("=================")
# 
# tt = to_boolean(partition_recursively(a3['precondition'].replace('-', '___')))
# 
# if ba.parse(tt).simplify() == False:
#     print("Action '" + a3['name'] + "' has conflicting preconditions and will be removed")
# 
# 
# =============================================================================

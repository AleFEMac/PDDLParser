# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 18:05:37 2019

@author: Ale
"""

from utils import collection_copy
from action_utils import partition_recursively, find_negatives, classify_parameter, combine_actions, couple_params, assign_perms, check_action_compat, max_similitude_coup, to_boolean

HASCOST = False

poss_classes = ['room', 'ball', 'gripper']
name_count = {}

coup = ('move', 'pick')

actions = {
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

act1 = collection_copy(actions[coup[0]])
act2 = collection_copy(actions[coup[1]])

t1 = to_boolean(partition_recursively(act1['precondition'].replace('-', '___')))
# =============================================================================
# print(t1)
# =============================================================================

pp1 = partition_recursively(act1['precondition'])
pe1 = partition_recursively(act1['effect'])

pp2 = partition_recursively(act2['precondition'])

p1 = act1['parameters']

pr1 = {}
pr2 = {}

for p in act1['parameters']:
    pr1[p] = classify_parameter('?'+p, pp1, poss_classes)

for p in act2['parameters']:
    pr2[p] = classify_parameter('?'+p, pp2, poss_classes) 

fn = find_negatives(pe1, p1, poss_classes)

for i in fn:
    pr1[i[0]].remove(i[1])

cp = couple_params(pr1, pr2)        
ap = assign_perms(cp)

min_dict_list = max_similitude_coup(ap)

par_dict_list = []
act_new_pars_list = []

for ii, x in enumerate(min_dict_list):
    
    idx = 0
    
    aux1  = {}
    aux2 = [{}, {}]
    
    pairing = min_dict_list[ii]
    
    for i in x:
        
        par_name = "par_" + str(idx)
        aux1[par_name] = [i]
        aux2[0][i] = par_name
        if pairing[i] != '':
            aux1[par_name].append(pairing[i])
            aux2[1][pairing[i]] = par_name
        idx += 1
        
    
    
    for p in act2['parameters']:
        if p not in aux2[1]:
            par_name = "par_" + str(idx)
            aux1[par_name] = [str(p)]
            aux2[1][str(p)] = par_name
            idx += 1
    
    par_dict_list.append(aux1)
    act_new_pars_list.append(aux2)
    
    

for idx in range(len(par_dict_list)):
    
    na1 = collection_copy(act1)
    na2 = collection_copy(act2)
    
    act_new_pars = act_new_pars_list[idx]
    
    nas = [na1, na2]
    
    for i, na in enumerate(nas):        
        na['precondition'] = na['precondition']
        na['effect'] = na['effect']
        for p in act_new_pars[i]:
            na['precondition'] = na['precondition'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
            na['effect'] = na['effect'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
                    
    ret = check_action_compat(act1, act2)
    
    if not ret:
        print("Actions", str(coup[0]), "and", str(coup[1]), "are incompatible")
    
    a12 = combine_actions(na1, na1, par_dict_list[ii], HASCOST)
    name = str(coup[0]) + '_' + str(coup[1])
    
    if name in name_count:
        name_count[name] += 1
        name += '_' + str(name_count[name])
    else:
        name_count[name] = 0                
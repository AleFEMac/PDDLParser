# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:35:14 2020

@author: Ale
"""

# =============================================================================
#         merged_actions = {}
#         name_count = {x:0 for x in arg_data['domain']['actions']}
#         
#         for coup in action_couples:
#             
#             act1 = collection_copy(arg_data['domain']['actions'][coup[0]])
#             act2 = collection_copy(arg_data['domain']['actions'][coup[1]])
#             
#             pp1 = partition_recursively(act1['precondition'])
#             pe1 = partition_recursively(act1['effect'])
#             
#             pp2 = partition_recursively(act2['precondition'])
#             
#             p1 = act1['parameters']
#             
#             pr1 = {}
#             pr2 = {}
#             
#             for p in act1['parameters']:
#                 pr1[p] = classify_parameter('?'+p, pp1, poss_classes)
#             
#             for p in act2['parameters']:
#                 pr2[p] = classify_parameter('?'+p, pp2, poss_classes) 
#             
#             fn = find_negatives(pe1, p1, poss_classes)
#             
#             for i in fn:
#                 pr1[i[0]].remove(i[1])
#             
#             cp = couple_params(pr1, pr2)        
#             ap = assign_perms(cp)
#             
#             min_dict_list = max_similitude_coup(ap)
#             
#             par_dict_list = []
#             act_new_pars_list = []
#             
#             for ii, x in enumerate(min_dict_list):
#                 
#                 idx = 0
#                 
#                 aux1  = {}
#                 aux2 = [{}, {}]
#                 
#                 pairing = min_dict_list[ii]
#                 
#                 for i in x:
#                     
#                     par_name = "par_" + str(idx)
#                     aux1[par_name] = [i]
#                     aux2[0][i] = par_name
#                     if pairing[i] != '':
#                         aux1[par_name].append(pairing[i])
#                         aux2[1][pairing[i]] = par_name
#                     idx += 1
#                     
#                 
#                 
#                 for p in act2['parameters']:
#                     if p not in aux2[1]:
#                         par_name = "par_" + str(idx)
#                         aux1[par_name] = [str(p)]
#                         aux2[1][str(p)] = par_name
#                         idx += 1
#                 
#                 par_dict_list.append(aux1)
#                 act_new_pars_list.append(aux2)
#                 
#                 
#             
#             for idx in range(len(par_dict_list)):
#                 
#                 na1 = collection_copy(act1)
#                 na2 = collection_copy(act2)
#                 
#                 act_new_pars = act_new_pars_list[idx]
#                 
#                 nas = [na1, na2]
#                 
#                 for i, na in enumerate(nas):        
#                     na['precondition'] = na['precondition']
#                     na['effect'] = na['effect']
#                     for p in act_new_pars[i]:
#                         na['precondition'] = na['precondition'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
#                         na['effect'] = na['effect'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
#                                 
#                 ret = check_action_compat(act1, act2)
#                 
#                 if not ret:
#                     print("Actions", str(coup[0]), "and", str(coup[1]), "are incompatible")
#                 
#                 a12 = combine_actions(na1, na1, par_dict_list[ii], HASCOST)
#                 name = str(coup[0]) + '_' + str(coup[1])
#                 
#                 if name in name_count:
#                     name_count[name] += 1
#                     name += '_' + str(name_count[name])
#                 else:
#                     name_count[name] = 0                
#                 
#                 merged_actions[name] = a12
#             
#         for a in merged_actions:
#             arg_data['domain']['actions'][a] = merged_actions[a]
#             
#         
#         print("Action merging complete\n")    
# =============================================================================

def check_action_compat(a1, a2):    

    bool_alg = bb.BooleanAlgebra()      
        
    t1 = to_boolean(partition_recursively(a1['precondition'].replace('-', '___')))
    t2 = to_boolean(partition_recursively(a1['effect'].replace('-', '___')))
    t3 = to_boolean(partition_recursively(a2['precondition'].replace('-', '___')))

    ex1 = bool_alg.parse('(' + t1 + ')').simplify()
    ex2 = bool_alg.parse('(' + t2 + ') & (' + t3 + ')').simplify()    
    
    return (ex1 and ex2)

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
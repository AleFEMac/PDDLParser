# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd, collection_copy, align, align_dictionary, permutations
from utils import remove_duplicates, nthkey
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

def check_action_compat(exp1, exp2): 
    
    for ex2 in exp2:        
        admissible = False
        
        for ex1 in exp1:            
            exp_admissible = True
            
            for stat2 in ex2:                    
                pos2 = True
                
                nstat2 = collection_copy(stat2)
                if nthkey(nstat2) == 'not':
                    nstat2 = nstat2['not'][0]
                    pos2 = False
                
                for stat1 in ex1:                    
                    pos1 = True
                    
                    nstat1 = collection_copy(stat1)
                    if nthkey(nstat1) == 'not':
                        nstat1 = nstat1['not'][0]
                        pos1 = False
                    
                    if nstat2 == nstat1 and not (pos1 and pos2):
                        exp_admissible = False
                        break
                
                if not exp_admissible:
                    break
            
            if exp_admissible:
                admissible = True
        
        if admissible:
            return True
    
    return False

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
    
    if string == '':
        return {}
    
    ss = string.strip()[1:-1].strip()
    
    if '(' not in ss:
        return {ss.split()[0]: ss.split()[1:]}
    
    head = ss.split()[0]
    
    if head == 'increase' and remove_increase:
        return ""
    
    assert head != ""
    
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
        comp += "(and"
        for arg in level[op]:
            ret = compose_partition(arg)
            comp += ' ' + ret
        comp += ")"
        return comp
    elif op == "or":
        comp += "(or"
        for arg in level[op]:
            ret = compose_partition(arg)
            comp += ' ' + ret
        comp += ")"
        return comp
    elif op == "not":
        comp += "(not " + compose_partition(level[op][0]) + ")"
        return comp
    else:
        comp += "(" + str(op)
        for arg in level[op]:
            comp += ' ' + arg
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
                
                # Take the class being NOT-ed
                kkey = list(item[key].keys())[0]
                
                # It's an acceptable class
                if kkey in classes:
                    param_classes.add(kkey) # Add the class to the set
            
            else:
                
                # It's an acceptable class
                if key in classes:                
                    param_classes.add(key)           
                    
    return param_classes

def to_boolean(level):
    
    if level == {}:
        return {}
    
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

def apply_negative(col):
    
    assert type(col) == list
    
    res = []
    
    for c in col:
        op = list(c.keys())[0]
        if op == 'not':
            res.append(c[op])
        else:
            res.append({'not':[{op:c[op]}]})
        
    return res 
        

def toDNF(level, params={}):
    
    if level == {}:
        return []

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

def assemble_DNF(or_clauses):
    
    if len(or_clauses) == 0:
        return {}     
    
    expression = {'or':[]}
    
    for clause in or_clauses:
        if len(clause) > 1:
            expression['or'].append({'and':collection_copy(clause)})
        elif len(clause) == 1:
            expression['or'].append(clause[0])
        else:
            return {}
        
    if len(or_clauses) == 1:
        expression = expression['or'][0]
    
    return expression

def apply_effect(prec, eff):
    
    or_clause_list = []
    
    # Copy the effect and differentiate between different predicates under an
    # AND operator and a single effect clause
    actual_eff = collection_copy(eff)
    if list(actual_eff.keys())[0] == 'and':
        actual_eff = actual_eff['and']
    else:
        actual_eff = [actual_eff]
    
    for and_clause in prec:
        and_clause_list = []
        
        eff_copy = collection_copy(actual_eff)
        
        # Cicle on all elements of the AND clause
        for prec_clause in and_clause:
            
            prec_clause_operator = list(prec_clause.keys())[0]
            prec_clause_content = prec_clause[prec_clause_operator]
            
            added_effect = False         
            
            if prec_clause_operator == 'not':
                prec_clause_operator = list(prec_clause_content[0].keys())[0]
                prec_clause_content = prec_clause_content[0][prec_clause_operator]
                        
            for eff_clause in actual_eff:
                
                eff_clause_operator = list(eff_clause.keys())[0]
                eff_clause_content = eff_clause[eff_clause_operator]                
                
                if eff_clause_operator == 'not':
                    eff_clause_operator = list(eff_clause_content[0].keys())[0]
                    eff_clause_content = eff_clause_content[0][eff_clause_operator]
                
                
                if eff_clause_operator == prec_clause_operator and eff_clause_content == prec_clause_content:
                    and_clause_list.append(eff_clause)
                    eff_copy.remove(eff_clause)
                    added_effect = True
                    break
        
                
            if not added_effect:
                and_clause_list.append(prec_clause)
         
        # Add remaining effects to the clause
        for eff_clause in eff_copy:
            and_clause_list.append(eff_clause)
        
        # Add an AND statement if there are multiple effects
        if len(and_clause_list) > 1:
            or_clause_list.append({'and':and_clause_list})
        else:
            or_clause_list.append(and_clause_list)
    
    if len(or_clause_list) > 1:
        return {'or':or_clause_list}
    elif len(or_clause_list) == 1:
        return or_clause_list[0]
    else:
        return {}


def associate_parameter(param, expression):
    
    # We don't need the "number" of associations a parameter has, so we use
    # a set instead of a list
    associations = set()
    
    if len(expression) == 0:    # Actions may not have preconditions
        return associations
    
    c_param = str('?' + param)              # Add the '?' to the parameter
    operator = list(expression.keys())[0]   # Header of the level
    level = expression[operator]            # Arguments of the level parameter
    
    # Iterate over all arguments of the level parameter
    for stat in level:
        
        if type(stat) != dict:              # Parameter case
            if stat == c_param and operator.split('_')[0] == "type":
                associations.add(operator)
                break
        else:                                           # Next level 
            ret = associate_parameter(param, stat)      # Recursive step
            associations.update(ret)        
    
    return associations

# Wrapper to iterate associate_parameter over multiple parameters
def associate_parameters(params, expression):
    associations = {}
    
    for param in params:
        ret = associate_parameter(param, expression)
        associations[param] = ret
    
    return associations
        
def pick_max_matches(inters):
    
    threshold = 0
    out = []
    
    for i in inters:
        if len(i) == threshold:
            out.append(i)
        elif len(i) > threshold:
            threshold = len(i)
            out = [i]
    return out

# Replace parameters of an action with generic 'par_n' names, which will be
# used in the final combined action
def replace_params(level, par_maps, middlemen={}):
    
    assert type(level) == dict
    
    if len(level) == 0:
        return
        
    operator = list(level.keys())[0]
    content = level[operator]
    
    if operator in ['or', 'and', 'not']:
        for i in content:
            replace_params(i, par_maps, middlemen)
    else:
        new_content = []
        for i in content:
            if i[1:] in par_maps:
                new_content.append(str('?' + str(par_maps[i[1:]])))
            else:
                new_content.append(str('?' + str(par_maps[middlemen[i[1:]]])))
        level[operator] = new_content
        return
            
# Checks if the parameters expressed by the precondition/effect of an action
# are actually defined
def action_cons_check(level, params, predics):
    
    def action_cons_check_in(level, params, predics):
        
        if len(level) == 0:
            return False, 0, ()       
        
        head = list(level.keys())[0]
        body = level[head]
        
        if head not in ['and', 'or', 'not']:
            if head not in predics:
                return False, 1, (head)
            elif head in predics and len(predics[head]) != len(body):
                return False, 2, (head, str(len(predics[head])), str(len(body)))
            else:
                for par in body:
                    if par[1:] not in params:
                        return False, 3, (head, par[1:])
        else:
            for subc in body:
                ret, rerr, rpar = action_cons_check_in(subc, params, predics)
                if not ret:
                    return False, rerr, rpar
        
        return True, None, None
    
    assert len(params) > 0
    
    prt_level = partition_recursively(level)
    dnf_level = assemble_DNF(toDNF(prt_level, params))
    if len(dnf_level) == 0:
        return False

    return action_cons_check_in(dnf_level, params, predics)

# =============================================================================
# Check action preconditions without using the boolean module
# =============================================================================
def check_action_precs(act):
    
    prec = collection_copy(act['precondition'])
    prec_dnf = toDNF(partition_recursively(prec))
    
    acceptable = True
    
    for or_clause in prec_dnf:
        memory = []
        
        for predicate in or_clause:
            struc = ()
            pos = True
            
            head = nthkey(predicate)
            body = predicate[head]
            
            if head == 'not':
                pos = False
                
                head = nthkey(body[0])
                body = body[0][head]
                
            struc = (head, body, pos)
            
            if (head, body, not pos) in memory:
                acceptable = False
                break
            else:
                memory.append(struc)
        
        if acceptable:
            return True
        
    return False

def check_pointlessness(act1, act2):
    
        
    
    return True
    
    
# =============================================================================
# TESTING PORTION
# =============================================================================


actions = {
        'start': {'parameters': ['r', 'b'], 
                 'precondition': '(and (type_robot ?r) (type_battery ?b) (or (on ?r) (and (not (on ?r)) (charged ?b))))', 
                 'effect': '(and (on ?r) (active ?b) (not (disabled ?r)))'},
        'move': {'parameters': ['rob', 'to'], 
                 'precondition': '(and (type_robot ?rob) (type_position ?to) (on ?rob) (not (at ?rob ?to)))', 
                 'effect': '(at ?rob ?to)'},
        'scream': {'parameters': ['r'],
                   'precondition': '(and (type_robot ?r) (silent ?r))',
                   'effect': '(not (silent ?r))'},
        'a1': {'parameters': ['rob'],
                   'precondition': '(type_robot ?rob)',
                   'effect': '(a_1 ?rob)'},
        'a2': {'parameters': ['r'],
                   'precondition': '(type_robot ?r)',
                   'effect': '(type_robot ?r)'},
        'a3': {'parameters': ['rob', 'to'], 
                 'precondition': '(and (type_robot ?rob) (type_position ?to) (not (on ?rob)) (not (at ?rob ?to)))', 
                 'effect': '(at ?rob ?to)'},
        'a4': {'parameters': ['rob', 'to'], 
                 'precondition': '(and (type_robot ?rob) (type_position ?to) (not (on ?rob)) (not (at ?rob ?to)))', 
                 'effect': '(at ?rob ?to)'}        
        }
        
# =============================================================================
# a = toDNF(partition_recursively(actions['a4']['precondition']))
# print(check_action_precs_2(actions['a4']))
# =============================================================================
       
# =============================================================================
# names = [list(actions.keys())[3], list(actions.keys())[4]]
# pa1 = actions[names[0]]['parameters']
# pa2 = actions[names[1]]['parameters']
# pr1 = partition_recursively(actions[names[0]]['precondition'])
# pr2 = partition_recursively(actions[names[1]]['precondition'])
# ef1 = partition_recursively(actions[names[0]]['effect'])
# ef2 = partition_recursively(actions[names[1]]['effect'])
# 
# p1 = toDNF(pr1)
# p2 = toDNF(pr2)
# 
# ae = apply_effect(p1, ef1)
# a1 = associate_parameters(actions[names[0]]['parameters'], ae)
# a2 = associate_parameters(actions[names[1]]['parameters'], assemble_DNF(p2))
# 
# intersections = {}
# for i in a1:
#     intersections[i] = []
#     for j in a2:
#         if a1[i].intersection(a2[j]) != set():
#             intersections[i].append(j)
# 
# 
# inter_permutations = permutations(intersections)
# aligned_dictionaries = []
# for perm in inter_permutations:
#     aligned_dictionaries += align_dictionary(perm)
# max_matches = pick_max_matches(aligned_dictionaries)
# 
# 
# 
# max_matches = remove_duplicates(max_matches)
# all_parametrizations = []
# all_inv_parametrizations  = []
# generated_actions = {}
# for a_idx, match in enumerate(max_matches):
#     idx = 0
#     used = []
#     parametrization = {}
#     inv_parametrization = {}
#     
#     inv_match = {}
#     for key in match:
#         inv_match[match[key]] = key
#         print(">", key)
#     
#     for couple in match:
#         par = "par_" + str(idx)
#         parametrization[par] = couple
#         inv_parametrization[couple] = par
#         used.append(match[couple])
#         idx += 1
#         
#     for par1 in pa1:
#         if par1 not in inv_parametrization:
#             par = "par_" + str(idx)
#             parametrization[par] = par1
#             inv_parametrization[par1] = par
#             idx += 1
#             
#     for par2 in pa2:
#         if par2 not in used:
#             par = "par_" + str(idx)
#             parametrization[par] = par2
#             inv_parametrization[par2] = par
#             used.append(par2)
#             idx += 1
#     
#     all_parametrizations.append(parametrization)
#     all_inv_parametrizations.append(inv_parametrization)
#     
#     copy_ae = collection_copy(ae)
#     replace_params(copy_ae, inv_parametrization)
#     copy_prec1 = collection_copy(pr1)
#     replace_params(copy_prec1, inv_parametrization)
#     copy_prec1 = toDNF(copy_prec1)
#     copy_prec2 = collection_copy(pr2)
#     replace_params(copy_prec2, inv_parametrization, inv_match)
#     copy_prec2 = toDNF(copy_prec2)
#     
#     copy_eff1 = collection_copy(ef1)
#     replace_params(copy_eff1, inv_parametrization)
#     copy_eff1 = toDNF(copy_eff1)
#     
#     copy_eff2 = collection_copy(ef2)
#     replace_params(copy_eff2, inv_parametrization, inv_match)
#     copy_eff2 = toDNF(copy_eff2)
#     
#     # Doability check
#     action_compat = check_action_compat(toDNF(copy_ae), copy_prec2)
#     
#     copy_ae_cont = toDNF(copy_ae)
#         
#     
#     for clause in copy_prec2:       # OR clause 
#         for stat in clause:         # statement in clause
#             
#             # Check now if the statement is entailed by the effect of the
#             # first action. AE has necessarily the same amount of clauses
#             # as the precondition of the first action
#             for idx, ae_clause in enumerate(copy_ae_cont):  
#                 # ae_clause_cont = ae_clause['and']
#                 if stat not in ae_clause and stat not in copy_prec1[idx]:
#                     copy_prec1[idx].append(stat)
#         
#     if len(copy_eff2[0]) > 1:
#         copy_eff2 = {'and':copy_eff2[0]}
#     else:
#         copy_eff2 = copy_eff2[0][0]
#     
#     final_prec = collection_copy(copy_prec1)
#     final_effect = apply_effect(copy_eff1, copy_eff2)
#     
#     print(">>>", final_prec)
#     
#     combined_action = {'parameters':list(parametrization.keys()),
#                        'precondition':assemble_DNF(final_prec), 
#                        'effect':final_effect}
#     
#     generated_actions[str(names[0] + '_' + names[1] + '_' + str(a_idx))] = combined_action
# 
# printd(generated_actions)
#     
# =============================================================================
        
    
    
        
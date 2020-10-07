# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd, collection_copy, align, align_dictionary, permutations
from utils import remove_duplicates, nthkey
# =============================================================================
# Make couplings of the parameters from two different actions
# ## DEPRECATED ##
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

def check_action_compat(expression_1, expression_2):
    
    for ex2 in expression_2:    # OR-clauses in expression_2  
        admissible = False
        
        for ex1 in expression_1:    # OR-clauses in expression_1
            exp_admissible = True
            expression_match_found = False
            
            # Statements in OR-clause from expression_2
            for stat2 in ex2:             
                positivity_2 = True     # Statement positivity
                
                # The statement might be under a "not": recover it and change
                # the statement's positivity                
                nstat2 = collection_copy(stat2)
                if nthkey(nstat2) == 'not':
                    nstat2 = nstat2['not'][0]
                    positivity_2 = False
                
                # Statements in OR-clause from expression_1
                for stat1 in ex1:                    
                    positivity_1 = True     # Statement positivity
                    
                    # The statement might be under a "not": recover it and change
                    # the statement's positivity
                    nstat1 = collection_copy(stat1)
                    if nthkey(nstat1) == 'not':
                        nstat1 = nstat1['not'][0]
                        positivity_1 = False
                    
                    # If a match between predicates is found but they have
                    # different positivity, return an incompatibility
                    if nstat2 == nstat1 and not (positivity_1 and positivity_2):
                        exp_admissible = False
                        break
                    
                    # If a match is found and the positivities are the same,
                    # return a compatibility
                    elif nstat2 == nstat1 and (positivity_1 and positivity_2):
                        expression_match_found = True
                        break
                
                # Incompatibilities due to lack of appearance of a statement
                # from the second precondition in the world of the first
                # action can only happen when the statement is positive
                # (due to the closed world assumption)
                if not positivity_2 and not expression_match_found:
                    expression_match_found = True
                
                # If a conflict was found or a positive statement wasn't included
                # in the world, return an incompatibility
                if not exp_admissible or (not expression_match_found and positivity_2):
                    break
            
            # The OR-clause from the second expression is acceptable only if
            # there were no problems
            if exp_admissible and expression_match_found:
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
    
    if len(ss) == 0:
        return {}
    
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
    
    op = nthkey(level)  #list(level.keys())[0]
    
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
            key = nthkey(item) #list(item.keys())[0]     
            
            if key == 'not':                # NOT operator case
                
                # Take the class being NOT-ed
                kkey = nthkey(item[key]) #list(item[key].keys())[0]
                
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
    
    op = nthkey(level)  #list(level.keys())[0]
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
        op = nthkey(c)  #list(c.keys())[0]
        if op == 'not':
            res.append(c[op])
        else:
            res.append({'not':[{op:c[op]}]})
        
    return res 
        

def toDNF(level, params={}):
    
    if level == {}:
        return []

    op = nthkey(level)  #list(level.keys())[0]
    
    
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

# Turns a non-partitioned DNF to a partitioned DNF
# or_clauses: non-partitioned DNF list of lists of clauses
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


# Applies an effect to an existing world
# prec: non-partitioned DNF
# eff: partitioned form
# return: partitioned DNF
def apply_effect(prec, eff):
    # Initialize a new list of or-clauses for the new world
    or_clause_list = []
    
    # Copy the effect and differentiate between different predicates under an
    # AND operator and a single effect clause (effects can't have ORs)
    actual_eff = collection_copy(eff)
    if nthkey(actual_eff) == 'and':
        actual_eff = actual_eff['and']
    else:
        actual_eff = [actual_eff]
    
    for and_clause in prec:
        and_clause_list = []
        
        eff_copy = collection_copy(actual_eff)
        
        # Cicle on all elements of the AND clause (predicates)
        for prec_clause in and_clause:
            
            # Take the name of the predicate and its parameters
            prec_clause_operator = nthkey(prec_clause)  #list(prec_clause.keys())[0]
            prec_clause_content = prec_clause[prec_clause_operator]
            
            added_effect = False         
            
            # The predicate might be inside of a NOT operator
            if prec_clause_operator == 'not':
                prec_clause_operator = nthkey(prec_clause_content[0])   #list(prec_clause_content[0].keys())[0]
                prec_clause_content = prec_clause_content[0][prec_clause_operator]
                        
            for eff_clause in actual_eff:
                
                eff_clause_operator = nthkey(eff_clause)    #list(eff_clause.keys())[0]
                eff_clause_content = eff_clause[eff_clause_operator]
                
                if eff_clause_operator == 'not':
                    eff_clause_operator = nthkey(eff_clause_content[0]) #list(eff_clause_content[0].keys())[0]
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
        if type(or_clause_list[0]) == list:
            return or_clause_list[0][0]
        elif type(or_clause_list[0]) == dict:
            return or_clause_list[0]
        else:
            print("Error during effect application")
            return {}
    else:
        return {}


def associate_parameter(param, expression):
    
    # We don't need the "number" of associations a parameter has, so we use
    # a set instead of a list
    associations = set()
    
    if len(expression) == 0:    # Actions may not have preconditions
        return associations
    
    c_param = str('?' + param)              # Add the '?' to the parameter
    operator = nthkey(expression)           # Header of the level
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
        
    operator = nthkey(level)    #list(level.keys())[0]
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
        
        head = nthkey(level)    #list(level.keys())[0]
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
        
# =============================================================================
#     assert len(params) > 0    
# =============================================================================
    
        
    partitioned_level = partition_recursively(level)
    dnf_level = assemble_DNF(toDNF(partitioned_level, params))

    return action_cons_check_in(dnf_level, params, predics)

# =============================================================================
# Check action preconditions without using the boolean module
# =============================================================================
def check_action_formula(act, formula):
    
    if formula not in act:
        if formula == "precondition":
            return True
        else:
            return False
    
    prec = collection_copy(act[formula])
    prec_dnf = toDNF(partition_recursively(prec, False))
    
    if len(prec_dnf) == 0:
        return True
    
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

def check_pointlessness(act1, act2, param_mapping, param_match):
    
    # Copy the actions to avoid side-effect related problems    
    copy_act1 = collection_copy(act1)
    copy_act2 = collection_copy(act2)
    
    # Extract preconditions and effects from actions    
    precondition_act1 = copy_act1["precondition"]
    effect_act1 = copy_act1["effect"]
    precondition_act2 = copy_act2["precondition"]
    effect_act2 = copy_act2["effect"]
    
    # Turn preconditions and effects in DNF
    dnf_precondition_act1 = toDNF(partition_recursively(precondition_act1))
    dnf_effect_act1 = toDNF(partition_recursively(effect_act1))
    dnf_precondition_act2 = toDNF(partition_recursively(precondition_act2))
    dnf_effect_act2 = toDNF(partition_recursively(effect_act2))
    
    # Obtain partitioned DNF of preconditions and effects
    pdnf_precondition_act1 = assemble_DNF(dnf_precondition_act1)
    pdnf_effect_act1 = assemble_DNF(dnf_effect_act1)
    pdnf_precondition_act2 = assemble_DNF(dnf_precondition_act2)
    pdnf_effect_act2 = assemble_DNF(dnf_effect_act2)
    
    # Replace all parameters with their general version
    replace_params(pdnf_precondition_act1, param_mapping, param_match)
    replace_params(pdnf_effect_act1, param_mapping, param_match)
    replace_params(pdnf_precondition_act2, param_mapping, param_match)
    replace_params(pdnf_effect_act2, param_mapping, param_match)
    
    # Apply the effect of the first action to its precondition, then convert
    # to DNF
    world_1 = apply_effect(dnf_precondition_act1, pdnf_effect_act1)
    world_1_dnf = toDNF(world_1)
    
    # Apply the effect of the second acitons to world 1, then convert to DNF
    world_2 = apply_effect(world_1_dnf, pdnf_effect_act2)
    world_2_dnf = toDNF(world_2)
    
    # Check if the end results of the merging of the 2 actions brings the world
    # 2 back to either world 0 (action 1 precondition) or to world 1, making
    # the merged action pointless
    world_0_independence = False
    world_1_independence = False
    
    # WORLD 0 TEST
    # Loop over OR-clauses of world 2
    for or_clause_2 in world_2_dnf:                
        
        clause_not_present = False
        
        for or_clause_0 in dnf_precondition_act1:
            
            if len(or_clause_2) != len(or_clause_0):
                clause_not_present = True
                break
            
            for statement_2 in or_clause_2:
                
                statement_found = False
                
                positivity_2 = True
                
                statement_2_head = nthkey(statement_2)
                statement_2_body = statement_2[statement_2_head]
                
                if statement_2_head == "not":
                    statement_2_head = nthkey(statement_2_body[0])
                    statement_2_body = statement_2_body[0][statement_2_head]
                    positivity_2 = False
                    
                final_statement_2 = {statement_2_head: statement_2_body}
                
                for statement_0 in or_clause_0:
                    
                    positivity_0 = True

                    statement_0_head = nthkey(statement_0)
                    statement_0_body = statement_0[statement_0_head]
                    
                    if statement_0_head == "not":
                        statement_0_head = nthkey(statement_0_body[0])
                        statement_0_body = statement_0_body[0][statement_0_head]
                        positivity_0 = False      
                        
                    final_statement_0 = {statement_0_head: statement_0_body}
                    
                    # Statement from world 2 found in world 0
                    if final_statement_2 == final_statement_0 and (positivity_0 == positivity_2):
                        statement_found = True
                    
                if not statement_found:
                    clause_not_present = True
                    break
            
            if clause_not_present:
                break
        
        if clause_not_present:
            world_0_independence = True
        
    
    # WORLD 1 TEST
    # Loop over OR-clauses of world 2
    for or_clause_2 in world_2_dnf:                
        
        clause_not_present = False
        
        for or_clause_1 in dnf_precondition_act1:
            
            if len(or_clause_2) != len(or_clause_1):
                clause_not_present = True
                break
            
            for statement_2 in or_clause_2:
                
                statement_found = False
                
                positivity_2 = True
                
                statement_2_head = nthkey(statement_2)
                statement_2_body = statement_2[statement_2_head]
                
                if statement_2_head == "not":
                    statement_2_head = nthkey(statement_2_body[0])
                    statement_2_body = statement_2_body[0][statement_2_head]
                    positivity_2 = False
                    
                final_statement_2 = {statement_2_head: statement_2_body}
                
                for statement_1 in or_clause_1:
                                    
                    positivity_1 = True

                    statement_1_head = nthkey(statement_1)
                    statement_1_body = statement_1[statement_1_head]
                    
                    if statement_1_head == "not":
                        statement_1_head = nthkey(statement_1_body[0])
                        statement_1_body = statement_1_body[0][statement_1_head]
                        positivity_1 = False      
                        
                    final_statement_1 = {statement_1_head: statement_1_body}
                    
                    # Statement from world 2 found in world 0
                    if final_statement_2 == final_statement_1 and (positivity_1 == positivity_2):
                        statement_found = True
                    
                if not statement_found:
                    clause_not_present = True
                    break
            
            if clause_not_present:
                break
        
        if clause_not_present:
            world_1_independence = True
    
    return (world_0_independence and world_1_independence)

    
    
    
        
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
                 'effect': '(at ?rob ?to)'},
        'a5': {'parameters': ['rob'], 
                 'precondition': '(and (type_robot ?rob) (not (on ?rob)))', 
                 'effect': '(on ?rob)'},
        'a6': {'parameters': ['r'], 
                 'precondition': '(and (type_robot ?r) (on ?r))', 
                 'effect': '(not (on ?r))'},
        }
           
# =============================================================================
# a = toDNF(partition_recursively(actions['a4']['precondition']))
# print(check_action_precs_2(actions['a4']))
# =============================================================================
       
# =============================================================================
# names = [list(actions.keys())[0], list(actions.keys())[1]]
# =============================================================================
# =============================================================================
# names = ['a5', 'a6']
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
#     copy_ae_cont = toDNF(copy_ae)
#     action_compat = check_action_compat(copy_ae_cont, copy_prec2)
#     
#     
#     check_pointlessness(actions[names[0]], actions[names[1]], inv_parametrization, inv_match)
#     
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
#     combined_action = {'parameters':list(parametrization.keys()),
#                        'precondition':assemble_DNF(final_prec), 
#                        'effect':final_effect}
#     
#     generated_actions[str(names[0] + '_' + names[1] + '_' + str(a_idx))] = combined_action
# =============================================================================

    
        
    
    
        
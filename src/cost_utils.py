# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 12:39:56 2019

@author: Ale
"""

from utils import take_enclosed_data, nthkey
from action_utils import toDNF, partition_recursively

def calculate_cost(data, params):
    
    data = data.strip()
    
    if data.count("(") == 1 and data.count(")") == 1:
        cost, operation= get_cost(data, params)
        return cost, operation
    
    data_l = take_enclosed_data(data)
    
    cost = -1
    operation = ''
    for d in data_l:
        out, operation = calculate_cost(d[1:-1], params)
        if out == -2:
            return -2, ''
        elif out < -2:
            return out, ''
        else:
            if cost != -1:
                return -2, ''
            cost = out
    
    return cost, operation

def get_cost(data, params):
    
    name = data.split()[0]
    
    if name in ['increase', 'decrease']:
        cost = data.split()[-1]
        try:
            cost = int(cost)
        except:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is not an integer or is fractional.\nPlease correct the error.")
            return -2, ''
        if cost < 1:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is non-positive.\nPlease correct the error.")
            return -2  , ''
        body = take_enclosed_data(data)[0]
        
        if body[0] != '(' or body[-1] != ')':
            print("\n[ERROR] Cost modification function\n'" + body + "'\nis not enclosed in parentheses.\nPlease enclose it in parentheses.")
            return -3, ''
        
        body = body[1:-1]
        
        if 'cost_function' in params['domain'] and params['domain']['cost_function'] != body:
            print("\n[ERROR] Found cost function\n'" + body + "'\nin an action, while previous cost function was defined as\n'" + params['domain']['cost_function']+ "'\nPlease correct one of the two.")
            return -3, ''
        else:
            params['domain']['cost_function'] = body        

        
        return cost, name
    
    return -1, ''

def merge_costs(action_1, action_2):
    
    # Grab each cost operation
    cost_operation_1 = action_1["cost_operation"]
    cost_operation_2 = action_1["cost_operation"]
    
    # Get costs, we use the absolute value in case the cost slipped through
    # the net and remained negative
    cost_1 = abs(action_1["cost"])
    cost_2 = abs(action_2["cost"])
    
    if cost_operation_1 == "decrease":
        cost_1 *= -1
    if cost_operation_2 == "decrease":
        cost_2 *= -1
        
    cost_result = cost_1 + cost_2
    operation_cost = "increase"
    
    if cost_result < 0:
        operation_cost = "decrease"
        cost_result = abs(cost_result)  
    
    return cost_result, operation_cost

def stringify_predicate(predicate):
    
    assert type(predicate) == dict
    
    predicate_head = nthkey(predicate)
    predicate_body = predicate[predicate_head]
    
    is_not_statement = False
    
    if predicate_head == "not":
        predicate_head = nthkey(predicate_body[0])
        predicate_body = predicate_body[0][predicate_head]
        is_not_statement = True    
    
    assert type(predicate_body) == list
    for par in predicate_body:
        assert type(par) == str
        
    predicate_string = '(' + str(predicate_head) + ' '
    
    for par in predicate_body:
        new_par = par
        if par[0] != '?':
            new_par = '?' + par
        predicate_string += new_par + ' '
        
    predicate_string = predicate_string[:-1] + ')'
        
    if is_not_statement:
        predicate_string = "(not " + predicate_string + ')'
    
    return predicate_string
    

def introduce_cost(action, cost_function):
    
    action_cost = action["cost"]
    action_operation = action["cost_operation"]
    action_effect = action["effect"]
    
    dnf_effect = toDNF(partition_recursively(action_effect))
    
    cost_string = '(' + action_operation + ' (' + cost_function + ") " + str(action_cost) + ')'
    
    final_effect = ""
    or_clauses = []
    
    for or_clause in dnf_effect:
        or_clause_string = "(and "
        or_clause_list = []
        for predicate in or_clause:
            predicate_string = stringify_predicate(predicate)
            or_clause_list.append(predicate_string)
        for predicate in or_clause_list:
            or_clause_string += predicate + " "
        or_clause_string += cost_string + ')'
        or_clauses.append(or_clause_string)
            
    if len(or_clauses) == 0:
        print("[ERROR] Error while adding cost to action\n'" + action["name"] + "'\nExiting")
        return action_effect
    elif len(or_clauses) == 1:
        final_effect = or_clauses[0]
    else:
        final_effect = "(or "
        for or_clause_string in or_clauses:
            final_effect += or_clause_string + " "
        final_effect = final_effect[:-1] + ')'
                
    return final_effect
    
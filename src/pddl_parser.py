# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 16:17:44 2018

@author: Ale
"""

import os
import boolean as bb
from utils import ischalnum, make_name, take_enclosed_data, dissect, remove_comments, printd
from cost_utils import get_cost, calculate_cost
from action_utils import check_action_precs, find_negatives, partition_recursively, classify_parameter, couple_params, assign_perms, find_min_empty, to_boolean, combine_actions

PDDLDIR = r"..\pddl_files"
UTILDIR = r"..\utilities"
OUTDIR  = r"..\out"
PDDLDOM = "domain.pddl"
PDDLPRB = "problem.pddl"
MSGFILE = "messages.txt"
PRDFILE = "predefined.txt"
ODOMFIL = "domain.pddl"
OPRBFIL = "problem.pddl"

LENIENT = True
PERMPUN = ['_', '-']
POSSCLASS = ['room', 'ball', 'gripper']


def write_domain(file, domain_struct):
    
    domain = "(define (domain "
    
    domain += domain_struct['name'] + ")\n\n\t"
    domain += "(:predicates"
    
    for pred in domain_struct['predicates']:
        domain += " (" + pred
        for arg in domain_struct['predicates'][pred]:
            domain += " " + arg
        domain += ")"
    domain += ")\n"
    
    for action in domain_struct['actions']:
        action_d = domain_struct['actions'][action]
        domain += "\n\t(:action " + action + "\n\t\t"
        
        if 'parameters' in action_d:
            domain += ":parameters ("
            for par in action_d['parameters']:
                domain += " " + par
            domain += " )\n\t\t"
        
        if 'precondition' in action_d:
            domain += ":precondition " + action_d['precondition'] + "\n\t\t"
        
        domain += ":effect " + action_d['effect'] + ")\n\t"       
    
    domain = domain[:-1] + ")"

    f = open(file, 'w')        
    f.write(domain)    
    f.close()
    
    return

def write_problem(file, problem_struct):
       
    # Define instruction and problem name
    problem = "(define (problem " + problem_struct['name'] + ")\n\n\t"
    
    # Domain this problem refers to
    problem += "(:domain " + problem_struct['domain'] + "\n\n\t"
    
    # Objects
    problem += "(:objects"
    for obj in problem_struct['objects']:
        problem += " " + obj
    problem += "\n\n\t"
    
    # Problem initialization
    problem += problem_struct['init'] + "\n\n\t"
    
    # Problem goal
    problem += problem_struct['goal'] + "\n)"   
    
    # Save problem on file
    f = open(file, 'w')    
    f.write(problem)
    f.close()
    
    return
    
def parse_element(element, arg_data, mode='domain'):
    
    lenient = arg_data['lenient']
    
    if mode == 'domain':
        if element[:len("(domain")] == "(domain":
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            if len(elem_list) < 2:
                print("\n[ERROR] Too few arguments in suspected domain element '", element + "'.\nDomain elements must have the format\n'domain domain_name'")
                return False
            elif len(elem_list) > 2:
                print("\n[ERROR] Too many arguments in suspected domain element '", element + "'.\nDomain elements must have the format\n'domain domain_name'")
                return False
            arg_data['visited']['domain'].append('domain')
            arg_data['domain']['name'] = elem_list[1]
            
        elif element[:len("(:predicates")] == "(:predicates":
            element2 = element[1:-1].strip()
            elem_list = take_enclosed_data(element2)
            elem_list = [element2.split()[0]] + elem_list
            
            if len(elem_list) < 2:
                print("\n[ERROR] Too few arguments in suspected predicates element\n'" + element + "'.\nPredicates elements must have the format\n'predicates ([predicate1]) ([predicate2]) ... ([predicateN])'")
                return False
            if elem_list[0] != ":predicates":
                first_statement = elem_list[0]
                print("\n[ERROR] Suspected predicate argument does not begin with a ':predicate' statement. Predicates elements must have the format\n'predicates ([predicate1]) ([predicate2]) ... ([predicateN])'\nwhile the program detected\n" + first_statement + ".\nas first statement.\nPlease correct the typo if present or add the statement itself if not inserted at all.")
                return False
            if not 'domain' in arg_data['visited']['domain']:
                print("\n[ERROR] Predicates argument found before the specification of the domain. Insert a domain statement with relative name first. The format of a domain file must be\n'(define (domain [name]) (:requirements :[requirement1] ... :[requirementN]) (:predicates [predicates1] ... [predicatesN]) (:action [action1] ...) ... (:action [actionN] ...))'")
                return False
            
            predicates = []
            for pred in elem_list:
                pred = pred.strip()
                if pred == ":predicates":
                    continue
                if ":" in pred:
                    print("\n[ERROR] String containing ':predicates' detected in Arguments of the predicates element must have the format\n':predicates ([predicate1]) ([predicate2]) ... ([predicateN])'\nwhile the program detected\n" + pred + ".\nPlease enclose every single predicate between parentheses.")
                    return False
                if pred[-1] != ")":
                    print("\n[ERROR] Arguments of the predicates element must have the format\n':predicates (predicate1) (predicate2) ... (predicateN)'\nwhile the program detected\n" + pred + ".\nPlease enclose every single predicate between parentheses.")
                    return False
                pred2 = pred[1:-1]
                if "(" in pred2 or ")" in pred2:
                    print("\n[ERROR] Parentheses detected in predicate \n'" + pred2 + "'\nParentheses are not allowed in the names of the parameter since they are used as separators.")
                    return False
                
                predicates.append(pred2)
            
            preds_with_params = {}
            for pred in predicates:
                pred_split = pred.split()
                pred_name = pred_split[0]
                if pred_name in preds_with_params:
                    if lenient:
                        print("\n[WARNING] Detected the duplicate predicate \n'" + pred_name + "'\nDuplicate ignored")
                        continue
                    else:
                        print("\n[ERROR] Detected the duplicate predicate \n'" + pred_name + "'\nPlease do not insert duplicate parameters in the domain.")
                        return False
                if not ischalnum(pred_name, PERMPUN) or pred_name[0].isnumeric():
                    print("\n[ERROR] the first character of a predicate must be a letter, while\n" + str(pred_split[0][0]) + "\nwas detected in the predicate\n" + pred)
                    return False
                
                pred_args = pred_split[1:]
                for arg in pred_args:
                    if arg[0] != "?":
                        print("\n[ERROR] Arguments of a parameter must be signaled by a '?' as first character, while \n" + arg +"\nwas detected in the predicate\n" + pred)
                        return False
                preds_with_params[pred_name] = pred_args
            
            arg_data['domain']['predicates'] = preds_with_params
            arg_data['visited']['domain'].append('predicates')
            
        elif element[:len("(:requirements")] == "(:requirements":
            
            if element[-1] != ")":
                print("\n[ERROR] Arguments of the requirements element must have the format\n':requirements :requirement1 :requirement2 ... :requirementN'\nwhile the program detected\n" + pred + ".\nPlease enclose every single predicate between parentheses.")
                return False
            
            element = element[1:-1].strip()
            
            elem_list = element.split()
            for idx, elem in enumerate(elem_list):
                
                elem_name = elem[1:]
                
                if elem[0] != ":":
                    print("\n[ERROR] All parameters of requirement statement must be preceded by semicolon, while it was not detected in\n'" + elem + "'\n")
                    return False
                    
                if elem_name == "requirements" and idx != 0:
                    print("\n[ERROR] Element 'requirements' was found in a position\n" + str(idx) + "\ndifferent from 0 in element\n'" + element + "'\nA ':requirements' statement may only appear once to signal the beginning of the element.")
                    return False
                
                if idx == 0 and elem_name != "requirements":
                    print("\n[ERROR] First statement of a 'requirements' element must be ':reuirements', while it was\n'" + elem_name + "'\nin\n'" + element + "'\nPlease put a ':requirement' statement before any of the requirements.")
                    return False
                
                if elem_name == "requirements":
                    continue
                
                if elem_name not in arg_data['requirements_list']:
                    print("\n[ERROR] Non-existant requirement\n'" + elem[1:] + "'\nwas passed. Make sure that the inserted name is correct.")
                    return False
                
                arg_data['requirements'].append(elem_name)
                
            arg_data['visited']['domain'].append('requirements')
            
        elif element[:len("(:action")] == "(:action":
            element2 = element[1:-1].strip()
            
            if "::" in element2:
                print("\n[ERROR] Multiple consecutive colons detected in action\n'" + element + "'\nUse a single colon to identify the single components of an action element.")
                return False
            
            if element2.split()[0] != ":action":
                print("\n[ERROR] First instruction found in suspected action element was\n'" + element2.split()[0] + "'\nwhile it should have been\n':action'.\nAction element format must be\n':action [action_name] :precondition ([sequence_of_preconditions]) :effect ([series_of_effects])'")
                return False
            
            elem_list = element2.split(":")
            while '' in elem_list:
                elem_list.remove('')
                
            if len(elem_list) > 4:
                print("[ERROR] Too many elements preceded by a semicolon. An action must have the format\n':action [action_name] :precondition ([sequence_of_preconditions]) :effect ([series_of_effects])'")
                return False
            
            action_struct = {}
            visited_action_comps = []
            
            for elem in elem_list:
                elem2 = elem.strip()
                elem_name = elem2.split()[0]
                    
                if elem_name in visited_action_comps:
                    if lenient:    
                        print("\n[WARNING] Element\n'" + elem_name + "'\nhas already been encountered in this action. Skipping it.")
                        return True
                    else:    
                        print("\n[ERROR] Element\n'" + elem_name + "'\nhas already been encountered in this action. Make sure to not repeat components of an action element.")
                        return False
                
                if elem_name == "action":
                    l = elem.split()
                    
                    if len(l) > 2:
                        print("\n[ERROR] Element\n'" + elem2 + "'\nhas been identified as an action statement, but contains too many words.\nRemember that an action must be named using the format\n':action [name_without_spaces]'.")
                        return lenient
                    
                    if l[1] in arg_data['domain']['actions']:
                        print("\n[ERROR] Action\n'" + l[1] + "'\nwas defined multiple times.\nRemember that action names are exclusive and cannot be shared by multiple actions.")
                        return lenient
                    
                    action_struct['name'] = l[1]
                    visited_action_comps.append('action')
                        
                elif elem_name == "parameters":
                    
                    if 'action' not in visited_action_comps:
                        print("\n[ERROR] Encountered a parameters definition without declaring the name of the action first in action\n'" + element + "'")
                        return False
                    
                    elem3 = elem2.replace("parameters", '', 1).strip()
                    out = take_enclosed_data(elem3, no_outliers=(not lenient))
                    if type(out) != list:
                        print("\n[ERROR] Out-of-parentheses character\n'" + out + "'\nidentified while parsing ':parameters' element\n':" + elem2 + "'\nThe required format is\n':parameters (?param1 ?param2 ... ?paramN)'\nMake sure that all of the parameters are included in the same set of parentheses.")
                        return False
                    
                    action_struct['parameters'] = []
                    
                    out = out[0][1:-1]
                    out = out.split()
                    
                    for param in out:
                        if param[0] != '?':
                            if not lenient:
                                print("\n[ERROR] Parameter\n'" + param + "'\nis not preceded by a '?' symbol in action" + element + "'\nThe required format is\n':parameters (?param1 ?param2 ... ?paramN)'\nMake sure that all of the parameters are preceded by a '?' symbol.")
                                return False
                        
                        if param[1:] in action_struct['parameters']:
                            print("\n[WARNING] Parameter\n'" + param + "'\nwas declared more than once in action\n'" + action_struct['name'] + "'\nThe program will skip the repetitions.")
                            continue
                        
                        action_struct['parameters'].append(param[1:])
                    
                        
                    visited_action_comps.append('parameters')
                        
                elif elem_name == "precondition":
                    
                    if 'action' not in visited_action_comps:
                        print("\n[ERROR] Encountered a precondition definition without declaring the name of the action first in action\n'" + element + "'")
                        return False
                    
                    elem3 = elem2.replace("precondition", '', 1).strip()  
                    
                    out = dissect(elem3, arg_data)
                    if not out:
                        return False
                    
                    action_struct['precondition'] = elem3
                    
                elif elem_name == "effect":
                    
                    if 'action' not in visited_action_comps:
                        print("\n[ERROR] Encountered an effect definition without declaring the name of the action first in action\n'" + element + "'")
                        return False
                    
                    elem3 = elem2.replace("effect", '', 1).strip()  
                    
                    out = dissect(elem3, arg_data)
                    if not out:
                        return False
                    
                    action_struct['effect'] = elem3
                    
                    cost = calculate_cost(elem3, arg_data)
                    
                    if cost == -1:
                        print("\n[ERROR] Could not calculate cost of the action\n'" + action_struct['name'] + "'\nPlease correct the error, as every action must have a positive cost.")
                        return False
                    elif cost == -2:
                        print("\n[ERROR] Action\n'" + action_struct['name'] + "'\nhad more than one specified cost. Actions must have one and only one cost definition.")
                        return False
                    
                    action_struct['cost'] = cost
                
                else:
                    print("\n[ERROR] Unrecognised element\n'" + elem_name + "'\nin action\n'" + element + "'\nAction element format must be\n':action [action_name] :precondition ([sequence_of_preconditions]) :effect ([series_of_effects])'")
                    return False
                
                visited_action_comps.append(elem_name)
            
            arg_data['domain']['actions'][action_struct['name']] = {}
            for key in action_struct:
                if key != 'name':
                    arg_data['domain']['actions'][action_struct['name']][key] = action_struct[key]
            
    
        else:
            print("\n[ERROR] Unrecognised element\n'" + element + "'\nNo such element is part of a domain.")
            return False
    
    elif mode == 'problem':
        
        if element[:len("(problem")] == "(problem":
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            if len(elem_list) != 2:
                print("\n[ERROR] Suspected 'problem' element\n'" + element + "'\nhas\n" + str(len(elem_list)) + "\narguments, while\n2\nwere expected.\nProblem elements must have the format\n'problem problem_name'")
                return False
            arg_data['problem']['name'] = elem_list[1]
            
        elif element[:len("(:domain")] == "(:domain":
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            if len(elem_list) < 2:
                print("\n[ERROR] Too few arguments in suspected 'domain' element '", element + "'.\nDomain elements must have the format\n'domain domain_name'")
                return False
            elif len(elem_list) > 2:
                print("\n[ERROR] Too many arguments in suspected 'domain' element '", element + "'.\nDomain elements must have the format\n'domain domain_name'")
                return False
            elif elem_list[1] != arg_data['domain']['name']:
                print("\n[ERROR] The problem was created for a domain different from the one passed to the parser.\nExpected domain was\n'" + arg_data['domain']['name'] + "'\nwhile the problem requires a\n'" + elem_list[1] + "'\ndomain")
                return False
                
            arg_data['visited']['problem'].append('domain')
            arg_data['problem']['domain'] = arg_data['domain']['name']
            
        elif element[:len("(:objects")] == "(:objects":
            
            if 'domain' not in arg_data['problem']:
                print("\n[ERROR] No domain specified.")
                return False
            
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            if len(elem_list) < 2:
                print("\n[ERROR] Too few arguments in suspected objects element '", element + "'.\nObjects elements must have the format\n':objects object1 ... objectN'")
                return False
            if elem_list[0] != ":objects":
                print("\n[ERROR] First statement of a 'objects' element must be ':objects', while it was\n'" + elem_list[0] + "'\nin\n'" + element + "'\nPlease put a ':objects' statement before any of the objects.")
                return False
            
            elem_list = elem_list[1:]
                        
            for obj in elem_list:
                if obj in arg_data['problem']['objects']:
                    
                    if lenient:
                        print("\n[WARNING]  Object\n'", obj + "'\nwas already defined in this problem file.\nObjects elements must be declared only once.")
                    
                    else:
                        print("\n[ERROR] Object\n'", obj + "'\nwas already defined in this problem file.\nObjects elements must be declared only once.")
                        return False
                    
                elif obj in arg_data['requirements_list']+list(arg_data['predefined'].keys()):
                    print("\n[ERROR] Object\n'", obj + "'\nhas an invalid name.\nDo not use names reserved for predefined operators or libraries.")
                    return False
                
                elif not ischalnum(obj, PERMPUN) or obj[0].isnumeric():
                    print("\n[ERROR] Object\n'", obj + "'\ncontains an invalid character.\nObject names may only contain numbers (albeit not in the first position) and letters, along with the characters\n" + str(PERMPUN) + "")
                    return False
                
                arg_data['problem']['objects'].append(obj)
                
        elif element[:len("(:init")] == "(:init":
            
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            
            if elem_list[0] != ":init":
                print("\n[ERROR] First statement of a ':init' element must be ':init', while it was\n'" + elem_list[0] + "'\nin\n'" + element + "'\nPlease put a ':init' statement before defining the starting conditions.")
                return False
            
            element2 = element[1:-1].strip()        
            elem3 = element2.replace(":init", '', 1).strip()
            
            out = dissect(elem3, arg_data)
            if not out:
                return False
                        
            arg_data['problem']['init'] = elem3
        
        elif element[:len("(:goal")] == "(:goal": 
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            
            if elem_list[0] != ":goal":
                print("\n[ERROR] First statement of a ':goal' element must be ':goal', while it was\n'" + elem_list[0] + "'\nin\n'" + element + "'\nPlease put a ':goal' statement before defining the goal of this problem.")
                return False
            
            element2 = element[1:-1].strip()        
            elem3 = element2.replace(":goal", '', 1).strip()  
            
            out = dissect(elem3, arg_data)
            if not out:
                return False
                
            arg_data['problem']['goal'] = elem3
        
        else:
            print("\n[ERROR] Unrecognised element\n'" + element + "'\nNo such element is part of a problem.")
            return False
    else:
        print("Unrecognized mode", mode)
        return False

    return True

def parse_domain(domain, arg_data):
    
    par = 0
    
    subelements = []
    
    domain = domain.strip()
    
    if domain[0:8] != "(define ":
        print("\n[ERROR] The domain was not formatted correctly; domains should begin with a '(define ' clause")
        return False
    if domain[-1] != ")":
        print("\n[ERROR] Extra characters at the end of the domain, found\n'" + domain.split(")")[-1] + "'\nafter the last closed parenthesis. Please remove any trailing elements.")
        return False
    
    n_domain = domain[8:-1].strip()
    current_subs = ""
    for idx, char in enumerate(n_domain):
        if char == "(":
            current_subs += char
            par += 1
        elif char == ")":
            par -= 1
            current_subs += char
            if par == 0:
                subelements.append(current_subs)
                current_subs = ""
        else:
            if current_subs != "":
                current_subs += char
            else:
                if char != " ":
                    print("\n[ERROR] The out-of-element character\n'" + char + "'\nin position\n"+ str(idx) +"\nhas been identified.\nPlease enclose all elements of the domain within parentheses.")
                    return False
            
    if par != 0:
        print("\n[ERROR] Unclosed parentheses")
        return False
    
    for i in subelements:
        status = parse_element(i, arg_data, 'domain')
        if not status:
            print("\n\nExecution has terminated with an error.")
            return False
        
    return True

def parse_problem(problem, arg_data):
            
    problem = problem.strip()
    
    if problem[0:8] != "(define ":
        print("\n[ERROR] The problem was not formatted correctly; domains should begin with a '(define ' clause")
        return False
    
    if problem[-1] != ")":
        print("\n[ERROR] Extra characters at the end of the problem, found\n'" + problem.split(")")[-1] + "'\nafter the last closed parenthesis. Please remove any trailing elements.")
        return False
    
    n_problem = problem[8:-1].strip()
    subelements = take_enclosed_data(n_problem, no_outliers=True)
    if type(subelements) != list:
        print("\n[ERROR] Out-of-element character\n'" + str(subelements) + "'\nhas been identified in the problem file.\nPlease enclose all elements of the problem within parentheses.")
        return False
    
    
    for se in subelements:
        status = parse_element(se, arg_data, 'problem')
        if not status:
            print("\n\nExecution has terminated with an error.")
            return False
    
    return True
    
def main():             
    f = open(make_name([PDDLDIR, PDDLDOM]), 'r')
    dom_list = f.readlines()
    f.close()
    
    f = open(make_name([PDDLDIR, PDDLPRB]), 'r')
    prb_list = f.readlines()
    f.close()
    
    arg_data = {'requirements_list':['strips', 'equality', 'typing', 'adl', 'action-costs'], 'visited':{'problem':[], 'domain':[]}}
    arg_data['predefined'] = {}
    arg_data['domain'] = {'requirements':[], 'actions':{}}
    arg_data['problem'] = {'objects':[], 'init':'', 'goal':''}
    arg_data['lenient'] = LENIENT
    
    f = open(make_name([UTILDIR, PRDFILE]), 'r')
    predef = f.readlines()
    f.close()
    
    for p in predef:
        pp = p.split()
        assert len(pp) == 4
        arg_data['predefined'][pp[0]] = {'min':int(pp[1]), 'max':int(pp[2]), 'req':pp[3]}
    
    dom_string = ""
    for s in dom_list:
        dom_string += s
    
    dom_string = remove_comments(dom_string)
        
    dom_string = dom_string.replace("\n", " ").replace("\t", " ").strip()
    
    print("\nStarting PDDL domain parsing...")
    
    out = parse_domain(dom_string, arg_data)
    if not out:
        return
    
    print("Parsing of the provided PDDL domain has terminated with success.\nStarting PDDL problem parsing...")
    
    prb_string = ""
    for s in prb_list:
        prb_string += s
        
    prb_string = remove_comments(prb_string)
        
    prb_string = prb_string.replace("\n", " ").replace("\t", " ").strip()

    out = parse_problem(prb_string, arg_data)
    if not out:
        return
    
# =============================================================================
#     print(arg_data['domain'])
#     
#     for act in arg_data['domain']['actions']:
#         print(act)
#         print(arg_data['domain']['actions'][act])
#         print("\n")
# =============================================================================

    print("Parsing of the provided PDDL problem has terminated with success.\n")
    
    print("Merging actions...")
    
    ok_actions = []
    
    for act in arg_data['domain']['actions']:
        ret = check_action_precs(arg_data['domain']['actions'][act])
        if ret:
            ok_actions.append(act)
        else:
            print("Precondition of action '" + act + "' is always false, the action has been removed")
        
    action_couples = []
    
    for act1 in ok_actions:
        for act2 in ok_actions:
            if act1 == act2:
                continue
            action_couples.append((act1, act2))
    
    poss_classes = POSSCLASS
    
    for coup in action_couples:
        
        act1 = arg_data['domain']['actions'][coup[0]].copy()
        act2 = arg_data['domain']['actions'][coup[1]].copy()
        
        pp1 = partition_recursively(act1['precondition'])
        pe1 = partition_recursively(act1['effect'])
        
        pp2 = partition_recursively(act2['precondition'])
        pe2 = partition_recursively(act2['effect'])
        
        p1 = act1['parameters']
        p2 = act2['parameters']
        
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
        
        min_dict = find_min_empty(ap)
        
        par_dict = {}
        act_new_pars = [{}, {}]
        
        idx = 0
        for i in min_dict:
            par_name = "par_" + str(idx)
            par_dict[par_name] = [i]
            act_new_pars[0][i] = par_name
            if min_dict[i] != '':
                par_dict[par_name].append(min_dict[i])
                act_new_pars[1][min_dict[i]] = par_name
            idx += 1
        
        
        na1 = act1.copy()
        na2 = act2.copy()
        
        nas = [na1, na2]
        
        for i, na in enumerate(nas):
            na['precondition'] = na['precondition'].replace(')', ') ').replace('(', ' (')
            na['effect'] = na['effect'].replace(')', ') ').replace('(', ' (')
            for p in act_new_pars[i]:
                na['precondition'] = na['precondition'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
                na['effect'] = na['effect'].replace(str('?' + p), str('?' + act_new_pars[i][p]))
                
        ba = bb.BooleanAlgebra()
                
        t1 = to_boolean(partition_recursively(na1['precondition'].replace('-', '___')))
        t2 = to_boolean(partition_recursively(na1['effect'].replace('-', '___')))
        t3 = to_boolean(partition_recursively(na2['precondition'].replace('-', '___')))
        
        ex1 = ba.parse('(' + t2 + ')' + ' & (' + t3 + ')').simplify()
        ex2 = ba.parse('(' + t1 + ')' + ' & (' + t3 + ')').simplify()
        
        if ex1 == False or ex2 == False:
            print("Actions '" + coup[0] + "' and '" + coup[1] + "' are incompatible")
        
        new_act = combine_actions(na1, na2, par_dict)
        
        idx = 1
        new_name = str(coup[0]) + "_" + str(coup[1])
        if str(new_name + str(idx)) in arg_data['domain']['actions']:
            while str(new_name + str(idx)) in arg_data['domain']['actions']:
                idx += 1
            new_name += '_' + str(idx)
        
        arg_data['domain']['actions'][new_name] = new_act
        
    
    
    print(arg_data['domain']['actions'].keys())
    
    print("Action merging complete\n")
    print("Saving new domain")
    write_domain(os.path.join(OUTDIR, ODOMFIL), arg_data['domain'])
    print("New domain saved")
    print("\nSaving new problem")
    write_problem(os.path.join(OUTDIR, OPRBFIL), arg_data['problem'])
    print("New problem saved")
    
if __name__ == "__main__":
    main()


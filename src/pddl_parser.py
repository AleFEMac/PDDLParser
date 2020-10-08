# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 16:17:44 2018

@author: Ale
"""

import os
from utils import ischalnum, make_name, take_enclosed_data, dissect, remove_comments, collection_copy
from utils import remove_duplicates, permutations
from cost_utils import calculate_cost, merge_costs, introduce_cost
from action_utils import partition_recursively, compose_partition, pick_max_matches
from action_utils import toDNF, apply_effect, associate_parameters, assemble_DNF
from action_utils import check_action_compat, align_dictionary, replace_params
from action_utils import check_action_formula, action_cons_check, check_pointlessness
from parser_utils import write_domain, write_problem

PDDLDIR = r"../pddl_files"
UTILDIR = r"../utilities"
OUTDIR  = r"../out"
PDDLDOM = "domain_0.pddl"
PDDLPRB = "problem_0.pddl"
MSGFILE = "messages.txt"
PRDFILE = "predefined.txt"
ODOMFIL = PDDLDOM #"domain_cost.pddl"    #"domain_output.pddl"
OPRBFIL = PDDLPRB #"problem_cost.pddl"   #"problem_output.pddl"

can_write = True
can_merge_actions = True
LENIENT = True
STRICT = False
HASCOST = True
GUARANTYPES = True
PERMPUN = ['_', '-']
RESVNAMES = ['action', 'define', 'domain', 'predicates', 'parameter', 'precondition', 'effect']


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
                if pred2[0] == "(" and pred2[-1] == ')':
                    print("\n[ERROR] Use of nested parentheses detected in\n'" + pred2 + "\nDo not use statements of the type (( xxx ))")
                    return False
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
                print("[ERROR] Too many elements preceded by a semicolon. An action must have the format\n':action [action_name] :parameters ([sequence_of_parameters]) :precondition ([sequence_of_preconditions]) :effect ([series_of_effects])'")
                return False

            action_struct = {}
            visited_action_comps = []

            for elem in elem_list:

                elem2 = elem.strip()
                elem_name = elem2.split()[0]

                if elem_name in visited_action_comps:
                    if lenient:
                        print("\n[WARNING] Element\n'" + elem_name + "'\nhas already been encountered in this action. Skipping it.")
                        continue
                        # return True
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


                    if len(out.strip()) > 0:
                        if out[0] == '(' or out[-1] == ')':
                            if lenient:
                                print("\n[WARNING] Multiple set of parentheses detected in the parameters definition of the action\n'" + action_struct['name'] + "'\nThe required format is\n':parameters (?param1 ?param2 ... ?paramN)'\nMake sure not to use multiple sets of parentheses.\n")
                                out = out.replace('(', '').replace(')', '')
                            else:
                                print("\n[WARNING] Multiple set of parentheses detected in the parameters definition of the action\n'" + action_struct['name'] + "'\nThe required format is\n':parameters (?param1 ?param2 ... ?paramN)'\nMake sure not to use multiple sets of parentheses.")
                                return False

                    out = out.split()

                    for param in out:

                        param_name = ""

                        if param[0] != '?':
                            if not lenient:
                                print("\n[ERROR] Parameter\n'" + param + "'\nis not preceded by a '?' symbol in action" + element + "'\nThe required format is\n':parameters (?param1 ?param2 ... ?paramN)'\nMake sure that all of the parameters are preceded by a '?' symbol.")
                                return False
                            param_name = param
                        else:
                            param_name = param[1:]

                        if param_name in action_struct['parameters']:
                            print("\n[WARNING] Parameter\n'" + param_name + "'\nwas declared more than once in action\n'" + action_struct['name'] + "'\nThe program will skip the repetitions.")
                            continue

                        action_struct['parameters'].append(param_name)


                    visited_action_comps.append('parameters')

                elif elem_name == "precondition":

                    initial_precondition = elem2

# =============================================================================
#                     if 'parameters' not in visited_action_comps:
#                         print("\n[ERROR] Encountered a precondition definition without declaring the parameters of the action first in action\n'" + element + "'")
#                         return False
# =============================================================================
                    # Leave an empty field for the parameters, even if not
                    # declared
                    if 'parameters' not in visited_action_comps:
                        action_struct['parameters'] = []

                    elem3 = elem2.replace("precondition", '', 1).strip()

                    # Preconditions could be empty
                    check_empty_precondition = False
                    no_parentheses_elem3 = elem3.strip().replace('(', '').replace(')', '').strip()
                    check_empty_precondition = len(no_parentheses_elem3) == 0

                    if check_empty_precondition:
                        pass
                    else:
                        out = dissect(elem3, arg_data)
                        if not out:
                            return False

                    par_cor, par_err, par_val = action_cons_check(elem3, action_struct['parameters'], arg_data['domain']['predicates'])

                    if not par_cor and par_err != 0:
                        if par_err == 0:
                            pass
                            #print("\n[ERROR] Error while checking the contents of action\n'" + action_struct['name'] + "'\nVerify that the action contains all of its components.")
                        elif par_err == 1:
                            print("\n[ERROR] The precondition of the action\n'" + action_struct['name'] + "'\nis using the predicate\n'" + par_val[0] + "'\nwhich was not defined in the 'predicates' section of the domain first.\nPlease define the predicate before using it.")
                        elif par_err == 2:
                            print("\n[ERROR] The precondition of the action\n'" + action_struct['name'] + "'\nis using the wrong amount of parameters for the predicate\n'" + par_val[0] + "'\nThe predicate has\n" + par_val[1] + "\nparameters, while it should have\n" + par_val[2])
                        elif par_err == 3:
                            print("\n[ERROR] The precondition of the action\n'" + action_struct['name'] + "'\nis using the parameter\n'" + par_val[1] + "'\nin the predicate\n'" + par_val[0] + "'\nwithout defining it first.\nPlease define all parameters of the action in the 'parameters' section of the action.")

                        return False

                    precondition_consistency= check_action_formula({"precondition":initial_precondition}, "precondition")
                    if not precondition_consistency:
                        if lenient:
                            print("[WARNING] The precondition of action\n'" + action_struct['name'] + "'\nis always false. Please check it.")
                        else:
                            print("[ERROR] The precondition of action\n'" + action_struct['name'] + "'\nis always false. Please check it.")
                            return False

                    action_struct['precondition'] = elem3

                    visited_action_comps.append('precondition')

                elif elem_name == "effect":

                    if 'action' not in visited_action_comps:
                        print("\n[ERROR] Encountered an effect definition without declaring the name of the action first in action\n'" + element + "'")
                        return False

                    if 'precondition' not in visited_action_comps:
                        action_struct['precondition'] = "()"

                    if 'parameters' not in visited_action_comps:
                        action_struct['parameters'] = []

                    initial_effect = elem2

                    elem3 = elem2.replace("effect", '', 1).strip()

                    out = dissect(elem3, arg_data)
                    if not out:
                        return False

                    par_cor, par_err, par_val = action_cons_check(elem3, action_struct['parameters'], arg_data['domain']['predicates'])

                    if not par_cor:
                        if par_err == 0:
                            print("\n[ERROR] Error while checking the contents of action\n'" + action_struct['name'] + "'\nVerify that the action contains all of its components.")
                        elif par_err == 1:
                            print("\n[ERROR] The effect of the action\n'" + action_struct['name'] + "'\nis using the predicate\n'" + par_val[0] + "'\nwhich was not defined in the 'predicates' section of the domain first.\nPlease define the predicate before using it.")
                        elif par_err == 2:
                            print("\n[ERROR] The effect of the action\n'" + action_struct['name'] + "'\nis using the wrong amount of parameters for the predicate\n'" + par_val[0] + "'\nThe predicate has\n" + par_val[1] + "\nparameters, while it should have\n" + par_val[2])
                        elif par_err == 3:
                            print("\n[ERROR] The effect of the action\n'" + action_struct['name'] + "'\nis using the parameter\n'" + par_val[1] + "'\nin the predicate\n'" + par_val[0] + "'\nwithout defining it first.\nPlease define all parameters of the action in the 'parameters' section of the action.")

                        return False

                    effect_consistency= check_action_formula({"effect":initial_effect}, "effect")
                    if not effect_consistency:
                        if lenient:
                            print("[WARNING] The effect of action\n'" + action_struct['name'] + "'\nis inconsistent. Please check it.")
                        else:
                            print("[ERROR] The effect of action\n'" + action_struct['name'] + "'\nis always false. Please check it.")
                            return False

                    action_struct['effect'] = elem3

                    if HASCOST:
                        cost, operation = calculate_cost(elem3, arg_data)

                        if operation not in ["increase", "decrease"]:
                            print("\n[ERROR] Action\n'" + action_struct['name'] + "'\nis using the operation\n'" + operation + "'\nwhich is not supported. Only use the operations 'increase' and 'decrease' when acting on cost.")
                            return False

                        action_struct['cost_operation'] = operation

                        if cost == -1:
                            print("\n[ERROR] Could not calculate cost of the action\n'" + action_struct['name'] + "'\nPlease correct the error, as every action must have a positive cost.")
                            return False
                        elif cost == -2:
                            print("\n[ERROR] Action\n'" + action_struct['name'] + "'\nhad more than one specified cost. Actions must have one and only one cost definition.")
                            return False
                        elif cost < -2:
                            return False

                        action_struct['cost'] = cost



                    visited_action_comps.append('effect')

                else:
                    print("\n[ERROR] Unrecognised element\n'" + elem_name + "'\nin action\n'" + element + "'\nAction element format must be\n':action [action_name] :precondition ([sequence_of_preconditions]) :effect ([series_of_effects])'")
                    return False


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

            # Check if the domain has already been analyzed; otherwise, many of
            # the problem checks won't work
            if 'domain' not in arg_data['problem']:
                print("\n[ERROR] No domain specified.")
                return False

            # Form the objects list, with the first element being ':objects'
            element2 = element[1:-1].strip()
            elem_list = element2.split()
            elem_list = [x.strip() for x in elem_list]

            # Having no objects means
            if len(elem_list) < 2:
                # print("\n[ERROR] Too few arguments in suspected objects element '", element + "'.\nObjects elements must have the format\n':objects object1 ... objectN'")
                #arg_data['problem']['objects']
                return True

            if elem_list[0] != ":objects":
                print("\n[ERROR] First statement of a 'objects' element must be ':objects', while it was\n'" + elem_list[0] + "'\nin\n'" + element + "'\nPlease put a ':objects' statement before any of the objects.")
                return False

            # Excise the ':objects' label
            elem_list = elem_list[1:]

            # Iterate on all objects
            for obj in elem_list:

                # Check if an objects with the same name has already been found;
                # if so, either skip it if lenient or fail and exit if not
                if obj in arg_data['problem']['objects']:

                    if lenient:
                        print("\n[WARNING]  Object\n'", obj + "'\nwas already defined in this problem file.\nObjects elements must be declared only once. The object has been skipped.")
                    else:
                        print("\n[ERROR] Object\n'", obj + "'\nwas already defined in this problem file.\nObjects elements must be declared only once.")
                        return False

                # Check if the name of the object is a reserved name (like 'and'
                # or 'action')
                elif obj in arg_data['requirements_list']+list(arg_data['predefined'].keys())+RESVNAMES:
                    print("\n[ERROR] Object\n'", obj + "'\nhas an invalid name.\nDo not use names reserved for predefined operators or libraries.")
                    return False

                # Check if the object name contains non permitted characters
                # (permitted characters are letters, numbers, the dash and
                # underscore)
                elif not ischalnum(obj, PERMPUN) or obj[0].isnumeric():
                    print("\n[ERROR] Object\n'" + obj + "'\ncontains an invalid character.\nObject names may only contain numbers (albeit not in the first position) and letters, along with the characters\n" + str(PERMPUN) + "")
                    return False

                # Save the objects
                arg_data['problem']['objects'].append(obj)

        elif element[:len("(:init")] == "(:init":

            element2 = element[1:-1].strip()
            elem_list = element2.split()

            if elem_list[0] != ":init":
                print("\n[ERROR] First statement of a ':init' element must be ':init', while it was\n'" + elem_list[0] + "'\nin\n'" + element + "'\nPlease put a ':init' statement before defining the starting conditions.")
                return False

            # Remove the ':init' label, then partition the string of predicates
            # into a list (can't use a simple 'split()' due to the parentheses
            # enclosing the predicate statements containing white spaces)
            element2 = element[1:-1].strip()
            elem3 = element2.replace(":init", '', 1).strip()
            init_stats = take_enclosed_data(elem3)

            # Iterate on all init predicates
            for inst in init_stats:
                inst_cln = inst[1:-1].strip()

                #print(inst_cln.split()[0])


                # Parentheses have already been removed, multiple sets of
                # concentric parentheses are an error
                if inst_cln.split()[0] not in ["not", '='] and ('(' in inst_cln or ')' in inst_cln):
                    print("\n[ERROR] Multiple sets of parentheses detected in the problem definition.\nThe init section must follow the format\n'(:init (predicate_1 parameter_1 ... parameter_N) ... (predicate_M parameter_1 ... parameter_N))'")
                    return False
                elif inst_cln[0] == '=':
                    if not HASCOST:
                        print("\n[ERROR] A metric was initialized without setting the HASCOST variable to True.\nRemember that this software can only detect cost metrics, and that the presence of cost must be specified first by setting the HASCOST variable to True.")
                        return False

                    # Remove the '=' operator
                    inst_cln_body = inst_cln.split()
                    if len(inst_cln_body) != 3:
                        print("\n[ERROR] Metric initialization has wrong format.\nThe metric format must be\n'(= (metric_name) init_value)\nPlease check your spelling.")
                        return False

                    cost_metric = inst_cln_body[1]

                    if cost_metric[0] != '(' or cost_metric[-1] != ')':
                        print("\n[ERROR] Metric name has wrong format.\nThe metric name must be enclosed within parentheses in the following format:\n'(metric_name)\nPlease check your spelling.")
                        return False

                    cost_metric = cost_metric[1:-1].strip()

                    if not len(cost_metric[0]) > 0:
                        print("\n[ERROR] Cost metric name has a zero-length name.\nPlease use an actual word.")
                        return False


                    if 'cost_metric' in arg_data['problem']:
                        print("\n[ERROR] Cost metric for the problem has already been defined.\nDiscarding latest one.")
                        if not lenient:
                            return False

                    arg_data['problem']['cost_metric'] = cost_metric


                # Init predicates have the format '(pred par1 .. parN)'
                pred = inst_cln.split()[0].strip()
                pars = inst_cln.split()[1:]

                if pred not in ['=', "not"]:
                    # Check if the predicate was defined in the domain
                    if pred not in arg_data['domain']['predicates']:
                        print("\n[ERROR] The init section of the problem is using the predicate\n'" + pred + "'\nwithout prior definition.\nCheck for spelling mistakes or define the predicate in the 'predicates' section of the domain.")
                        return False

                    # Check if the predicate has the correct amount of parameters
                    if '=' and len(pars) != len(arg_data['domain']['predicates'][pred]):
                        print("\n[ERROR] The init section of the problem is using the wrong amount of parameters for the predicate\n'" + pred + "'\nThe problem is using\n'" + str(len(pars)) + "'\nwhile\n'" + str(len(arg_data['domain']['predicates'][pred])) + "'\nwere expected.")
                        return False

                    # Check if any used parameter was not defined before
                    for par in pars:
                        if par not in arg_data['problem']['objects']:
                            print("\n[ERROR] The init section of the problem is using parameter\n'" + par + "'\nin predicate\n'" + pred + "'\nwithout prior definition.\nCheck for spelling mistakes or define the parameter in the 'objects' section of the problem.")
                            return False

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

            elem3_original = elem3

            if elem3.strip()[:len("(and")] == "(and":
                elem3_clean = elem3.strip()
                if elem3_clean[0] != '(' or elem3_clean[-1] != ')':
                    print("\n[ERROR] Incorrect enclosing in goal with AND operator.\nPlease make sure you follow the format\n'(:goal (and (predicate_1 parameter_1 ... parameter_N) ... (predicate_M parameter_1 ... parameter_N)))'")
                    return False

                elem3 = elem3_clean[len("(and"):-1]


            goal_stats = take_enclosed_data(elem3)
            for gost in goal_stats:
                gost_cln = gost[1:-1].strip()

                if gost_cln[:len("not")] != "not" and ('(' in gost_cln or ')' in gost_cln):
                    print("\n[ERROR] Multiple sets of parentheses detected in the problem definition.\nThe goal section must follow the format\n'(:goal (and (predicate_1 parameter_1 ... parameter_N) ... (predicate_M parameter_1 ... parameter_N)))'")
                    return False

                if gost_cln[len("not"):] == "not":
                    gost_cln = gost_cln[:len("not")].strip()

                    if gost_cln[0] != '(' or gost_cln[-1] != ')':
                        print("\n[ERROR] Predicate\n'" + gost_cln + "'\nincluded in a NOT operator isn't enclosed by parenheses.\nPlease make sure you follow the format\n'(not (predicate_1 parameter_1 ... parameter_N))'")
                        return False

                    gost_cln= gost_cln[1:-1]


                pred = gost_cln.split()[0]
                pars = gost_cln.split()[1:]

                if pred not in arg_data['domain']['predicates']:
                    print("\n[ERROR] The goal section of the problem is using the predicate\n'" + pred + "'\nwithout prior definition.\nCheck for spelling mistakes or define the predicate in the 'predicates' section of the domain.")
                    return False

                if len(pars) != len(arg_data['domain']['predicates'][pred]):
                    print("\n[ERROR] The goal section of the problem is using the wrong amount of parameters for the predicate\n'" + pred + "'\nThe problem is using\n'" + str(len(pars)) + "'\nwhile\n'" + str(len(arg_data['domain']['predicates'][pred])) + "'\nwere expected.")
                    return False

                for par in pars:
                    if par not in arg_data['problem']['objects']:
                        print("\n[ERROR] The goal section of the problem is using parameter\n'" + par + "'\nin predicate\n'" + pred + "'\nwithout prior definition.\nCheck for spelling mistakes or define the parameter in the 'objects' section of the problem.")
                        return False

            out = dissect(elem3, arg_data)
            if not out:
                return False

            arg_data['problem']['goal'] = elem3_original
        elif element[:len("(:metric")] == "(:metric": # TODO Maybe done
            element_cln = element.strip()

            if not HASCOST:
                print("\n[ERROR] A metric was defined without setting the HASCOST variable to True.\nRemember that this software can only detect cost metrics, and that the presence of cost must be specified first by setting the HASCOST variable to True.")
                return False

            if element_cln[0] != '(' or element_cln[-1] != ')':
                print("\n[ERROR] The goal section of the problem is using parameter\n'" + par + "'\nin predicate\n'" + pred + "'\nwithout prior definition.\nCheck for spelling mistakes or define the parameter in the 'objects' section of the problem.")
                return False

            element_cln = element_cln[1:-1].strip()

            element_cln_body = element_cln.split()

            if len(element_cln_body) != 3:
                print("\n[ERROR] Metric objective has wrong format.\nThe metric format must be\n'(:metric operation (metric_name))\nPlease check your spelling.")
                return False

            if element_cln_body[0] != ":metric":
                print("\n[ERROR] Metric objective element has name\n" + element_cln_body[0] + "\ninstead of ':metric'.\nThe metric format must be\n'(= (metric_name) init_value)\nPlease ensure that you used that format in you problem ':metric' section.")
                return False

            if element_cln_body[1] not in ["maximize", "minimize"]:
                print("\n[ERROR] Metric objective operation is unknown.\nThe metric found is\n" + element_cln_body[1] + "\nBut the only accepted metric operations are 'maximize' and 'minimize'\nPlease ensure that you use one of those in you problem ':metric' section.")
                return False

            used_metric = element_cln_body[2]

            if used_metric[0] != '(' or used_metric[-1] != ')':
                print("\n[ERROR] The metric name in the problem :metric section is not enclosed by parentheses.\nPlease ensure that you follow the format\n'(:metric operation (metric_name))")
                return False

            used_metric = used_metric[1:-1]

            if 'cost_metric' not in arg_data['problem']:
                print("\n[ERROR] No cost metric found in the initialization.\nPlease ensure that you define one in the :init section.")
                return False

            cost_metric = arg_data['problem']['cost_metric']

            if used_metric != cost_metric:
                print("\n[ERROR] The metric you are trying to act upon is different from the one defined in the :init section.\nThe one being used in the :metric section is\n" + used_metric + "\nwhile the one defined in the initialization is\n" + cost_metric + "\nPlease change one of the two to the other.")
                return False

            # Find the metric goal (maximize/minimize cost function)
            metric_goal = element_cln_body[1]

            # Metric goals shouldn't be enclosed in parentheses
            if metric_goal[0] == '(' or metric_goal[-1] == ')':
                print("\n[ERROR] The metric goal\n'" + metric_goal + "'\nis enclosed in parentheses.\nPlease ensure that you follow the format\n'(:metric operation (metric_name))")
                return False

            if metric_goal not in ["maximize", "minimize"]:
                print("\n[ERROR] The metric goal\n'" + metric_goal + "'\nhas an incorrect value.\nPlease ensure that you use either\n'maximize'\nor\n'minimize'\nas metric goals.")
                return False

            # Save the metric goal
            arg_data['problem']['metric_goal'] = metric_goal


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
        print("\n[ERROR] Parsing reached its end while not closing all parentheses")
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

    arg_data = {'requirements_list':['strips', 'equality', 'typing', 'adl', 'action-costs'],
                'visited':{'problem':[], 'domain':[]}}
    arg_data['predefined'] = {}
    arg_data['domain'] = {'requirements':[], 'actions':{}}
    arg_data['problem'] = {'objects':[], 'init':'', 'goal':''}
    arg_data['lenient'] = LENIENT
    arg_data['cost'] = HASCOST

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

    print("Parsing of the provided PDDL problem has terminated with success.\n")

# =============================================================================
# ACTION MERGING
# =============================================================================
    if can_merge_actions:
        print("Merging actions...")

        actions = collection_copy(arg_data['domain']['actions'])
        ok_actions = []

        # Save actions whose precondition isn't always false
        for act in actions:
            ret_precondition = check_action_formula(actions[act], "precondition")
            ret_effect = check_action_formula(actions[act], "effect")
            if ret_precondition and ret_effect:
                ok_actions.append(act)
            elif not ret_precondition:
                print("Precondition of action '" + act + "' is always false, the action has been removed")
            elif not ret_effect:
                print("Effect of action '" + act + "' is always false, the action has been removed")

        action_couples = []

        # Form action couples
        for act1 in ok_actions:
            for act2 in ok_actions:
                if act1 != act2:
                    action_couples.append((act1, act2))

        # List of action names
        name_list = [x for x in arg_data['domain']['actions']]

        all_merged_actions = {}

        for coup in action_couples:

            # Parameters of the two actions
            pa1 = actions[coup[0]]['parameters']
            pa2 = actions[coup[1]]['parameters']

            no_parameters_in_couple = False
            if len(pa1) == len(pa2) == 0:
                no_parameters_in_couple = True

            # Preconditions of the two actions
            pr1 = partition_recursively(actions[coup[0]]['precondition'])
            pr2 = partition_recursively(actions[coup[1]]['precondition'])

            # Effects of the two actions
            ef1 = partition_recursively(actions[coup[0]]['effect'])
            ef2 = partition_recursively(actions[coup[1]]['effect'])

            # Preconditions transformed in DNF
            p1 = toDNF(pr1)
            p2 = toDNF(pr2)

            # Apply the effect of the first action to its preconditions to
            # obtain the 'relative' state of the world post-execution
            ae = apply_effect(p1, ef1)

            # Create parameters associations; the associate_parameters
            # function matches parameters to 'type' predicates; this
            # operation is performed both on world state and the DNF
            # preconditions of the second action
            a1 = associate_parameters(actions[coup[0]]['parameters'], ae)
            a2 = associate_parameters(actions[coup[1]]['parameters'], assemble_DNF(p2))

            # Find parameter intersections: parameters of the second action are
            # associated to the parameters of the first action they share a
            # type-predicate with
            intersections = {}
            for i in a1:
                intersections[i] = []
                for j in a2:
                    if a1[i].intersection(a2[j]) != set():
                        intersections[i].append(j)

            # Permute all possible associations so that different parameters
            # can be selected as first (since the align_dictionary works in a
            # first-come-first-served fashion), then pick the assignments which
            # create the least parameters
            inter_permutations = permutations(intersections)
            aligned_dictionaries = []
            for perm in inter_permutations:
                aligned_dictionaries += align_dictionary(perm)
            max_matches = pick_max_matches(aligned_dictionaries)

            # Remove duplicates
            max_matches = remove_duplicates(max_matches)
            all_parametrizations = []
            all_inv_parametrizations  = []
            generated_actions = {}

            # Cycle on all maximal pairings
            for a_idx, match in enumerate(max_matches):

                # Actions can be merged with no matches only when they both
                # have no parameters
                if len(max_matches) == 0 and not no_parameters_in_couple:
                    break

                idx = 0
                used = []
                parametrization = {}
                inv_parametrization = {}

                # Map parameters of the second action to the ones of the first
                # as well
                inv_match = {}
                for key in match:
                    inv_match[match[key]] = key

                # Create the new parameters for the eventual combined action,
                # named par_N
                for couple in match:
                    par = "par_" + str(idx)
                    parametrization[par] = couple
                    inv_parametrization[couple] = par
                    used.append(match[couple])
                    idx += 1

                # Match the 'old' parameters with the new ones
                for par1 in pa1:
                    if par1 not in inv_parametrization:
                        par = "par_" + str(idx)
                        parametrization[par] = par1
                        inv_parametrization[par1] = par
                        idx += 1

                for par2 in pa2:
                    if par2 not in used:
                        par = "par_" + str(idx)
                        parametrization[par] = par2
                        inv_parametrization[par2] = par
                        used.append(par2)
                        idx += 1

                # ???
                all_parametrizations.append(parametrization)
                all_inv_parametrizations.append(inv_parametrization)

                # Replace the old parameters in the post-execution world,
                # preconditions of the first action and preconditions of the
                # second action with the new ones, then reduce to DNF base form
                # (ie. non compatible with PDDL yet) the last two
                copy_ae = collection_copy(ae)
                replace_params(copy_ae, inv_parametrization)
                copy_prec1 = collection_copy(pr1)
                replace_params(copy_prec1, inv_parametrization)
                copy_prec1 = toDNF(copy_prec1)
                copy_prec2 = collection_copy(pr2)
                replace_params(copy_prec2, inv_parametrization, inv_match)
                copy_prec2 = toDNF(copy_prec2)

                # Do the same with the two actions' effects
                copy_eff1 = collection_copy(ef1)
                replace_params(copy_eff1, inv_parametrization)
                copy_eff1 = toDNF(copy_eff1)
                copy_eff2 = collection_copy(ef2)
                replace_params(copy_eff2, inv_parametrization, inv_match)
                copy_eff2 = toDNF(copy_eff2)

                #TODO: SHOULD WORK NOW
                action_compat = check_action_compat(toDNF(copy_ae), copy_prec2, STRICT, GUARANTYPES)
                if not action_compat:
                    continue

                usefulness = check_pointlessness(actions[coup[0]], actions[coup[1]], inv_parametrization, inv_match)
                if not usefulness:
                    continue

                copy_ae_cont = toDNF(copy_ae)

                for clause in copy_prec2:       # OR clause
                    for stat in clause:         # statement in clause

                        # Check now if the statement is entailed by the effect
                        # of the first action. AE has necessarily the same
                        # amount of clauses as the precondition of the first
                        # action (effects can't contain or's)
                        for idx, ae_clause in enumerate(copy_ae_cont):
                            # ae_clause_cont = ae_clause['and']
                            if stat not in ae_clause and stat not in copy_prec1[idx]:
                                copy_prec1[idx].append(stat)

                if len(copy_eff2[0]) > 1:
                    copy_eff2 = {'and':copy_eff2[0]}
                else:
                    copy_eff2 = copy_eff2[0][0]

                final_prec = collection_copy(copy_prec1)
                final_effect = apply_effect(copy_eff1, copy_eff2)

                combined_action = {'parameters':list(parametrization.keys()),
                                   'precondition':compose_partition(assemble_DNF(final_prec)),
                                   'effect':compose_partition(final_effect)}


                # Add cost if the domain requires it
                if HASCOST:
                    combined_cost, combined_operation = merge_costs(actions[coup[0]], actions[coup[1]])
                    combined_action['cost'] = combined_cost
                    combined_action["cost_operation"] = combined_operation  # Increase/Decrease

                    # New effect, DNF, with the cost added
                    combined_action_new_effect = introduce_cost(combined_action, arg_data["problem"]["cost_metric"])
                    combined_action["effect"] = combined_action_new_effect

                # Create base name
                generated_name = str(coup[0] + '_' + coup[1])

                # If an action name is already used, append an index at the end
                # of it to differentiate
                if generated_name in name_list:
                    idx = 0
                    while idx >= 0:
                        final_name = generated_name + "_" + str(idx)
                        if final_name not in name_list:
                            break
                else:
                    final_name = generated_name


                generated_actions[final_name] = combined_action

            # Update the actions generated by the different merging of the
            # couple
            all_merged_actions.update(generated_actions)

        if len(all_merged_actions) > 0:
            arg_data['domain']['actions'].update(all_merged_actions)
            print("...actions merged succesfully!\n")
        else:
            print("...no possible merge found.\n")

# =============================================================================
# SAVE RESULTS
# =============================================================================
    if can_write:
        print("Saving new domain")
        write_domain(os.path.join(OUTDIR, ODOMFIL), arg_data['domain'])
        print("New domain saved")

        print("\nSaving new problem")
        write_problem(os.path.join(OUTDIR, OPRBFIL), arg_data['problem'])
        print("New problem saved")

if __name__ == "__main__":
    main()

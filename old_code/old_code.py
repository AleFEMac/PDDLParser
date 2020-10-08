# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 17:35:14 2020

@author: Ale
"""

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

def old_check_action_compat(expression_1, expression_2):

    for ex2 in expression_2:    # OR-clauses in expression_2
        admissible = False

        for ex1 in expression_1:    # OR-clauses in expression_1
            exp_admissible = True
            expression_match_found = False

            validated_params = 0

            # Statements in OR-clause from expression_2
            for stat2 in ex2:
                positivity_2 = True     # Statement positivity

                # The statement might be under a "not": recover it and change
                # the statement's positivity
                nstat2 = collection_copy(stat2)
                if nthkey(nstat2) == 'not':
                    nstat2 = nstat2['not'][0]
                    positivity_2 = False

                print("N2", nstat2, positivity_2)

                # Statements in OR-clause from expression_1
                for stat1 in ex1:
                    positivity_1 = True     # Statement positivity

                    # The statement might be under a "not": recover it and change
                    # the statement's positivity
                    nstat1 = collection_copy(stat1)
                    if nthkey(nstat1) == 'not':
                        nstat1 = nstat1['not'][0]
                        positivity_1 = False

                    print("N1", nstat1, positivity_1)

                    # If a match between predicates is found but they have
                    # different positivity, return an incompatibility
                    if nstat2 == nstat1 and not (positivity_1 and positivity_2):
                        exp_admissible = False
                        break

                    # If a match is found and the positivities are the same,
                    # return a compatibility
                    elif nstat2 == nstat1 and (positivity_1 and positivity_2):
                        expression_match_found = True
                        validated_params += 1
                        print("NN", nstat1, nstat2)
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
                    admissible = False
                    break

            # The OR-clause from the second expression is acceptable only if
            # there were no problems
            if exp_admissible and expression_match_found:
                admissible = True

        if not admissible:
            return False

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

# =============================================================================
# def check_action_compat(a1, a2):
#
#     bool_alg = bb.BooleanAlgebra()
#
#     t1 = to_boolean(partition_recursively(a1['precondition'].replace('-', '___')))
#     t2 = to_boolean(partition_recursively(a1['effect'].replace('-', '___')))
#     t3 = to_boolean(partition_recursively(a2['precondition'].replace('-', '___')))
#
#     ex1 = bool_alg.parse('(' + t1 + ')').simplify()
#     ex2 = bool_alg.parse('(' + t2 + ') & (' + t3 + ')').simplify()
#
#     return (ex1 and ex2)
# =============================================================================

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

# =============================================================================
# Check that the preconditions of an action are not always false
# =============================================================================
def check_action_precs_old(act):

    ba = bb.BooleanAlgebra()

    # If the parametric preconditions are False, the action will never be
    # performable
    if ba.parse(to_boolean(partition_recursively(act['precondition'].replace('-', '___')))).simplify() == False:
        return False
    else:
        return True

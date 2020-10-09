# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 09:24:47 2019

@author: Ale
"""

from utils import ischalnum, make_name, take_enclosed_data, dissect, printd, collection_copy, align, align_dictionary, permutations
from utils import remove_duplicates, nthkey



# Verifies that two actions can be logically fused. To do so, the effect of the
# first action is applied to its precondition, and the result is used to
# verify the precondition of the second action.
# @param expression_1 - list, DNF of the "world" after the first acton
# @param expression_2 - list, DNF of the precondition of the second action
# @param strict - boolean, the strictness; if set to True, two actions are
#   considered compatible iff every OR-clause of the second expression is
#   validated by every OR-clause of the first (ie. none of its predicates cause
#   conflicts with any predicate of the first). If set to False, two action
#   will be compatible if every OR-clause of the second is at validated by at
#   least one OR-clause from the first. The strict is extremely restrictive,
#   but should guarantee that no actions are fused with inconsistencies.
# @param guarantee_types - boolean, if set to True, type predicates (predicates
#   starting with the label "type_") are considered always found in the first
#   world. It helps with actions where the second action has more type predicates
#   than the first
def check_action_compat(expression_1, expression_2, strict, guarantee_types):

    # How many clauses of the first world validate each OR-clause of the
    # second precondition
    or_clause_validation_list = [0 for x in expression_2]

    # Loop over the OR-clauses of the secon precondition
    for idx, or_clause_2 in enumerate(expression_2):

        # How many OR-clauses from world 1 validate this clause
        complete_validation_num = 0

        # Loop over OR-clauses of the first world
        for or_clause_1 in expression_1:    # OR-clauses in expression_1

            # Number of validated predicates from the current OR-clause 2
            validated_statements = 0
            breakoff = False

            # Statements in OR-clause from expression_2
            for stat2 in or_clause_2:
                positivity_2 = True     # Statement positivity
                expression_match_found = False

                # The statement might be under a "not": recover it and change
                # the statement's positivity
                nstat2 = collection_copy(stat2)
                if nthkey(nstat2) == 'not':
                    nstat2 = nstat2['not'][0]
                    positivity_2 = False


                # Statements in OR-clause from expression_1
                for stat1 in or_clause_1:
                    positivity_1 = True     # Statement positivity

                    # Type guarantee
                    if guarantee_types and positivity_2 and nthkey(nstat2)[:len("type_")] == "type_":
                        expression_match_found = True
                        validated_statements += 1
                        break

                    # The statement might be under a "not": recover it and change
                    # the statement's positivity
                    nstat1 = collection_copy(stat1)
                    if nthkey(nstat1) == 'not':
                        nstat1 = nstat1['not'][0]
                        positivity_1 = False


                    # If a match between predicates is found but they have
                    # different positivity, return an incompatibility
                    if nstat2 == nstat1 and not (positivity_1 and positivity_2):
                        breakoff = True
                        break

                    # If a match is found and the positivities are the same,
                    # return a compatibility
                    elif nstat2 == nstat1 and (positivity_1 and positivity_2):
                        expression_match_found = True
                        validated_statements += 1
                        break

                # If a conflict was found, skip the rest of the OR-clause from
                # expression 1 (the clauses in an OR-clause are all in an AND
                # relation)
                if breakoff == True:
                    break

                # Incompatibilities due to lack of appearance of a statement
                # from the second precondition in the world of the first
                # action can only happen when the statement is positive
                # (due to the closed world assumption)
                if not positivity_2 and not expression_match_found:
                    expression_match_found = True
                    validated_statements += 1

                # If a conflict was found or a positive statement wasn't included
                # in the world, return an incompatibility
                if not expression_match_found and positivity_2:
                    breakoff = True
                    break

            # Breakoff: go to the next OR-clause
            if breakoff == True:
                continue

            # If all positive statements were found and no conflict arose, the
            # Or-clause 1 validated the OR-clause 2
            if validated_statements == len(or_clause_2):
                complete_validation_num += 1

        # Save the number of validating clauses
        or_clause_validation_list[idx] = complete_validation_num

    # Strictness check
    if strict:
        discrepancy_found = False
        for validations in or_clause_validation_list:
            if validations != len(expression_1):
                discrepancy_found = True
        return not discrepancy_found
    else:
        discrepancy_found = False
        for validations in or_clause_validation_list:
            if validations == 0 and len(expression_1) != 0:
                discrepancy_found = True
        return not discrepancy_found

    return False


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

# Partition a string recursively; used to create the tree of operators and
# predicates which makes up a PDDL formula; each node is represented as a
# dictionary: the only key is the operator/predicate, its value is a list,
# containing the dictionaries of the elements depending from the current one;
# parameters are strings.
# @param string - string, the current level of the formula
# @param remove_increase - boolean, whether to ignore the increase/decrease
#   operation for the cost
# @return - the dictionary of the current node
def partition_recursively(string, remove_increase=True):

    if string == '':
        return {}

    # Remove parentheses and external spaces
    ss = string.strip()[1:-1].strip()

    if len(ss) == 0:
        return {}

    # Predicate case, has the format 'operator predicate_1 ... predicate_N'
    if '(' not in ss:
        return {ss.split()[0]: ss.split()[1:]}

    # Save the operator
    head = ss.split()[0]

    # Cost removal step
    if head in ['increase', "decrease"] and remove_increase:
        return ""

    # Operator cannot be empty (this was prevented by the first two checks)
    assert head != ""

    res = {head:[]}

    # Obtain the list of elements depending on this one
    data_l = take_enclosed_data(ss.replace(head, '', 1).strip())

    # Properly insert said elements in the dependency list after partitioning
    # them as well
    for d in data_l:
        out = partition_recursively(d)

        if out != "":
            res[head].append(out)

    return res

# Make a PDDL compatible string aout of a boolean tree
# @param level - dictionary, the current node being processed
# @return - string, the string of the level
def compose_partition(level):

    comp = ""

    op = nthkey(level)  #list(level.keys())[0]

    # Various possible cases; self explanatory
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


# Makes a boolean formula out of a boolean tree
# Possibly DEPRECATED
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

# Used by the toDNF function to create a negative element
# @param col - list, the dependencies of a node
# @return - list of dependencies
def apply_negative(col):

    assert type(col) == list

    res = []

    # Loop checks if any element is already negative, in which case it removes
    # the NOT operator
    for c in col:
        op = nthkey(c)  #list(c.keys())[0]
        if op == 'not':
            res.append(c[op])
        else:
            res.append({'not':[{op:c[op]}]})

    return res

# Turns a boolean tree into a Disjunctive Normal Form (ie. a set of formulae
# containing only AND and NOT operators, gathered under a single OR operator)
# @param level - dictionary, the current node
# @param params - dictionary, optional parameters
# @return - list, list of list of predicates in an AND relation
def toDNF(level, params={}):

    # Base step
    if level == {}:
        return []

    op = nthkey(level)  #list(level.keys())[0]

    # Recursive steps
    if op == "and":
        # Create the collection of predicates to return
        lvl = [[]]

        # Arguments of the current operator
        for a in level[op]:

            # Current return
            new_lvl = []

            # Deep copy of collection returned from successive recursive step
            res_og = toDNF(a, params)
            res = collection_copy(res_og)

            # All returned predicates are put together in the same formulae
            for r in res:
                for rr in lvl:
                    new_lvl.append(rr+r)
            lvl = new_lvl

        return lvl

    elif op == "or":
        # Create the collection of predicates to return
        lvl = []

        # Arguments of the current operator
        for a in level[op]:

            # Current return
            new_lvl = []

            # Deep copy of collection returned from successive recursive step
            res_og = toDNF(a, params)
            res = collection_copy(res_og)

            # Join the disparate lists of parameters from the recursive steps
            # under a single OR macro-list
            for r in res:
                new_lvl.append(r)
            lvl = lvl + new_lvl

        return lvl

    elif op == "not":
        # Create the collection of predicates to return
        lvl = []

        a = level[op][0]    # NOT operator can only have a single argument
        new_lvl = []        # Initialize current return

        # Deep copy of collection returned from successive recursive step
        res_og = toDNF(a, params)
        res = collection_copy(res_og)

        # De Morgan
        pos_al = align(res)
        neg_al = []
        for p in pos_al:
            neg = apply_negative(p)
            neg_al.append(neg)

        return neg_al

    # Return predicates as nodes encased in double sets of parentheses (the inner
    # one is the AND-clause, the outer one is the OR-clause)
    else:
        return [[level]]

    return

# Turns a non-partitioned DNF to a partitioned DNF (boolean tree of a DNF)
# @param or_clauses - list, non-partitioned DNF list of lists of clauses
# @return - dictionary, the DNF formatted to a boolean tree
def assemble_DNF(or_clauses):

    if len(or_clauses) == 0:
        return {}

    expression = {'or':[]}

    # Every sublist of the OR-clause is put under and AND operator (if it has
    # more than one predicate) or simply saved by itself
    for clause in or_clauses:
        if len(clause) > 1:
            expression['or'].append({'and':collection_copy(clause)})
        elif len(clause) == 1:
            expression['or'].append(clause[0])
        else:
            return {}

    # Check if the tree was a single node
    if len(or_clauses) == 1:
        expression = expression['or'][0]

    return expression


# Applies an effect to a precondition, in order to obtain the state of the world
# after said application
# @param prec - list, DNF precondition
# @param eff - dictionary, binary tree of the effect to apply to the precondition
# @return - partitioned DNF of the post-effect world
def apply_effect(prec, eff):
    # Initialize a new list of or-clauses for the new world
    or_clause_list = []

    # Copy the effect and differentiate between different predicates under an
    # AND operator and a single effect clause (effects can't have ORs), then make
    # a list of the predicates in the effect
    actual_eff = collection_copy(eff)
    if nthkey(actual_eff) == 'and':
        actual_eff = actual_eff['and']
    else:
        actual_eff = [actual_eff]

    # Loop on every clause on the precondition
    for and_clause in prec:
        and_clause_list = []

        eff_copy = collection_copy(actual_eff)

        # Loop on all elements of the AND clause (predicates)
        for prec_clause in and_clause:

            # Take the name of the predicate and its parameters
            prec_clause_operator = nthkey(prec_clause)  #list(prec_clause.keys())[0]
            prec_clause_content = prec_clause[prec_clause_operator]

            added_effect = False

            # The predicate might be inside of a NOT operator
            if prec_clause_operator == 'not':
                prec_clause_operator = nthkey(prec_clause_content[0])   #list(prec_clause_content[0].keys())[0]
                prec_clause_content = prec_clause_content[0][prec_clause_operator]

            # Loop over the predicates of the effect
            for eff_clause in actual_eff:

                eff_clause_operator = nthkey(eff_clause)    #list(eff_clause.keys())[0]
                eff_clause_content = eff_clause[eff_clause_operator]

                # The effect predicate might be inside a NOT operator
                if eff_clause_operator == 'not':
                    eff_clause_operator = nthkey(eff_clause_content[0]) #list(eff_clause_content[0].keys())[0]
                    eff_clause_content = eff_clause_content[0][eff_clause_operator]

                # If the predicate is already in the precondition, overwrite it
                # with the effect one, then remove it from the list of effect
                # predicates to add
                if eff_clause_operator == prec_clause_operator and eff_clause_content == prec_clause_content:
                    and_clause_list.append(eff_clause)
                    eff_copy.remove(eff_clause)
                    added_effect = True
                    break

            # If the effect predicate wasn't found in the precondiion, add it
            # now to the final world
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

    # Format the result into a binary tree
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


# Function to match a parameter to its type predicates (predicates introduced
# by the characters 'type_'); they act as a sort of "class" to identify which
# kind of "object" param is. Used to merge actions.
# @param param - string, parameter to associate to type predicates
# @param expression - dictionary, (DNF) binary tree of a boolean formula
# @return - set, the list of individual type predicates param can be matched with
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
            # If the operator found is a type predicate, save it
            if stat == c_param and operator.split('_')[0] == "type":
                associations.add(operator)
                break
        else:                                           # Next level
            # Only go in the recursive step if the operator isn't a NOT
            # (since the expression is in DNF before the recursion starts,
            # the NOT operator can only contain a predicate: if it is a type
            # predicate, the parameter shouldn't be classified in that way
            # anyways)
            if nthkey(stat) != "not":
                ret = associate_parameter(param, stat)      # Recursive step
                associations.update(ret)

    return associations

# Wrapper to iterate associate_parameter over multiple parameters; it is for all
# intents and purposes its "initialization".
# @param param - string, parameter to associate to type predicates
# @param expression - dictionary, DNF binary tree of a boolean formula
# @return - dictionary, the dictionary linking every parameter to its associated
#   type predicates
def associate_parameters(params, expression):
    associations = {}

    # Perform the associate_parameter function on every predicate
    for param in params:
        ret = associate_parameter(param, expression)
        associations[param] = ret

    return associations

# The function takes the possible parameters intersections (parameters having
# the same type predicates) and only selects the ones which link the most of them
# @param inters - list, list of parameters matches
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
# @param level - dictionary, the current node of the binary tree
# @param par_maps - dictionary, maps each parameter to a generic one
# @param middlemen - dictionary, instead of creating a separate par_maps for
#   parameters of the second action in a merging, the mapping from parameters
#   of the second action and parameters of the first can be fed to be used as
#   middleman
def replace_params(level, par_maps, middlemen={}):

    assert type(level) == dict

    if len(level) == 0:
        return

    operator = nthkey(level)    #list(level.keys())[0]
    content = level[operator]

    # Operator, recursive step
    if operator in ['or', 'and', 'not']:
        for i in content:
            replace_params(i, par_maps, middlemen)
    else:   # Predicate found
        new_content = []
        for i in content:
            # par_maps saves parameters without the '?'
            if i[1:] in par_maps:
                new_content.append(str('?' + str(par_maps[i[1:]])))
            else:   # Middleman case
                new_content.append(str('?' + str(par_maps[middlemen[i[1:]]])))
        level[operator] = new_content
        return

# Checks if the parameters expressed by the precondition/effect of an action
# are actually defined
# @param level - dictionary, current node of the binary tree
# @param params - list, parameters defined by the action
# @param predics - dictionary, all of the domain predicates
# @return 0 - boolean, whether an error happened or not
# @return 1 - integer, code of the error
# @return 2 - what caused the error
def action_cons_check(level, params, predics):

    # Recursive operation
    def action_cons_check_in(level, params, predics):

        if len(level) == 0:
            return False, 0, ()

        head = nthkey(level)    #list(level.keys())[0]
        body = level[head]

        if head not in ['and', 'or', 'not']:    # Predicate case
            if head not in predics:
                return False, 1, (head) # Predicate not defined in the domain
            elif head in predics and len(predics[head]) != len(body):
                # Wrong amount of parameters wrt what was defined in the domain
                return False, 2, (head, str(len(predics[head])), str(len(body)))
            else:
                for par in body:
                    if par[1:] not in params: # Parameter not defined in domain
                        return False, 3, (head, par[1:])
        else:
            for subc in body:   # Recursive step
                ret, rerr, rpar = action_cons_check_in(subc, params, predics)
                if not ret:
                    return False, rerr, rpar

        return True, None, None


    partitioned_level = partition_recursively(level)
    dnf_level = assemble_DNF(toDNF(partitioned_level, params))

    return action_cons_check_in(dnf_level, params, predics)

# Function to check that a formula from an action is logcally correct; done by
# hand since the 'boolean' module doesn't seem to work correctly.
# @param act - structure, the action the formula belongs to
# @param formula - string, name of the formula to analyze
# @return - boolean, whether no errors were found or not
def check_action_formula(act, formula):

    if formula not in act:
        if formula == "precondition":   # An action may have no precondition
            return True
        else:           # An effect must be present though
            return False

    formula_copy = collection_copy(act[formula])
    formula_dnf = toDNF(partition_recursively(formula_copy, False))

    if len(formula_dnf) == 0:  # Formula is empty
        return True

    acceptable = True

    # Loop over OR-clauses
    for or_clause in formula_dnf:
        memory = [] # Remember the predicates found, with parameters and positivity

        # Loop over predicates in OR-clause (Or-clauses only contain NOT
        # operators and predicates)
        for predicate in or_clause:
            struc = ()
            pos = True

            head = nthkey(predicate)
            body = predicate[head]

            # Predicate might be
            if head == 'not':
                pos = False

                head = nthkey(body[0])
                body = body[0][head]

            struc = (head, body, pos)

            # If the predicate was found with the same parameters and opposite
            # positivity, return an error
            if (head, body, not pos) in memory:
                acceptable = False
                break
            else:
                memory.append(struc)

        # If at least one OR-clause is positive, the formula is consistent
        # (since they are tied by an OR relation, only one of them has to be
        # be positive for the whole formula to be)
        if acceptable:
            return True

    return False

# Function to check whether there is no need to merge two actions.
# @param act1 - dictionary, first action
# @param act2 - dictionary, second action
# @param param_mapping, dictionary, maps parameters of action 1 to generic
#   parameters
# @param param_match, dictionary, matches parameters of action 2 to parameters of
#   action 1
# @return - boolean, True if the action merging is not pointless, False otherwise
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
    replace_params(pdnf_precondition_act1, param_mapping) #, param_match)
    replace_params(pdnf_effect_act1, param_mapping) #, param_match)
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
    # 2 back to either world 0 (action 1 precondition) or to world 1 (application
    # of effect 1 to world 0), making the merged action pointless
    world_0_independence = False
    world_1_independence = False

    # WORLD 0 TEST
    # Loop over OR-clauses of world 2
    for or_clause_2 in world_2_dnf:

        clause_not_present = False

        # World 0 OR-clauses
        for or_clause_0 in dnf_precondition_act1:

            if len(or_clause_2) != len(or_clause_0):
                clause_not_present = True
                break

            # Predicates in world 2
            for statement_2 in or_clause_2:

                statement_found = False

                positivity_2 = True

                # Save predicate, parameters and positivity of statement
                statement_2_head = nthkey(statement_2)
                statement_2_body = statement_2[statement_2_head]

                if statement_2_head == "not":
                    statement_2_head = nthkey(statement_2_body[0])
                    statement_2_body = statement_2_body[0][statement_2_head]
                    positivity_2 = False

                final_statement_2 = {statement_2_head: statement_2_body}

                # Predicates in world 0
                for statement_0 in or_clause_0:

                    positivity_0 = True

                    # Save predicate, parameters and positivity of statement
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

                # Any clause not present ensure not poinlessness
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

        # Loop over OR-clauses of world 1
        for or_clause_1 in dnf_precondition_act1:

            if len(or_clause_2) != len(or_clause_1):
                clause_not_present = True
                break

            # Predicates in world 2
            for statement_2 in or_clause_2:

                statement_found = False

                positivity_2 = True

                # Save predicate, parameters and positivity of statement
                statement_2_head = nthkey(statement_2)
                statement_2_body = statement_2[statement_2_head]

                if statement_2_head == "not":
                    statement_2_head = nthkey(statement_2_body[0])
                    statement_2_body = statement_2_body[0][statement_2_head]
                    positivity_2 = False

                final_statement_2 = {statement_2_head: statement_2_body}

                # Predicates in world 1
                for statement_1 in or_clause_1:

                    positivity_1 = True

                    # Save predicate, parameters and positivity of statement
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

                # Any clause not present ensure not poinlessness
                if not statement_found:
                    clause_not_present = True
                    break

            if clause_not_present:
                break

        if clause_not_present:
            world_1_independence = True

    return (world_0_independence and world_1_independence)

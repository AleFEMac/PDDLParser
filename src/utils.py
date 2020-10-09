# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 12:14:58 2019

@author: Ale
"""

# Deep copy of a collection (works with simple types as collection elements)
# @param col - any, collection to be copied
# @return - same type as col, copy of col
def collection_copy(col):

    # Collections cases, simply recurse over all elements
    if type(col) == dict:
        copy = {}
        for c in col:
            ret = collection_copy(col[c])
            # No need to copy 'c', keys cannot be modified (so no lists)
            copy[c] = ret
        return copy
    elif type(col) == list:
        copy = []
        for c in col:
            ret = collection_copy(c)
            copy.append(ret)
        return copy
    # If 'col' is not a collection, it is one of its elements, so just return it
    else:
        return col

# Print dictionary, one element per line
# @param diction-  dictionary, the dictionary to print
def printd(diction):
    print("{")
    for i in diction:
        print(str(i) + ":", diction[i])
    print("}")

# Return if a string is only made up of letters, numbers and approved pieces of
# punctuation
# @param string - string, the string to analyze
# @param puncts - list, acceptable punctuation
# @return - boolean, True if the string is acceptable, False if it contains
#   characters outside from number, letters and approved punctuation
def ischalnum(string, puncts=['.']):
    for c in string:
        cc = ord(c)
        if not ((cc >= 48 and cc <= 57) or (cc >= 65 and cc <= 90) or (cc >= 97 and cc <= 122) or c in puncts):
            print(cc)
            return False
    return True

# Turn a list of directories/files in a parsable path
# @param directories - list, list of directories/files to make the file path
# @ return - string, the full file path
def make_name(directories):
    name = ""
    for directory in directories:
        name += directory + "/"

    return name[:-1]    # Remove the trailing '/'

# Takes all characters (aside from those in "ignore_inside") included between a
# set of a started and an ender and saves them in a list. Multiple sets of
#starters-enders generate multiple lists.
# @param data - string, the string to extract data from
# @param starter - string, the character which signals the start of a new segment
# @param ender- string, the character which signals the end of the segment
# @param ignore_inside - list, list of characters to ignore if found between a
#   starter and an ender
# @param no_outliers - boolean, signals whether to record characters outside of
#   a starter-ender pair (True) or not (False)
# @return - list, partitions extracted from string
def take_enclosed_data(data, starter="(", ender=")", ignore_inside=[], no_outliers=False):

    par = 0     # (number of starters found - number of enders found)
    data_l = [] # List of different partitions obtained (includes ender and starter)
    current_subs = ""   # Current partition

    # Loop over the characters in data
    for char in data:

        # Increase the starter counter
        if char == starter:
            par += 1
            current_subs += char
        elif char == ender:
            if current_subs != "":
                current_subs += char
                par -= 1

                # Declare a partition closed only when the amount of starters and
                # enders found is equal again (the first opened starter was closed)
                if par == 0:
                    data_l.append(current_subs)
                    current_subs = ""
        else:
            # Outlier case
            if par == 0 and char !=  " " and no_outliers:
                return char
            # Exclude the characters in 'ignore_inside' from insertion in the
            # current string
            if current_subs != "" and char not in ignore_inside:
                current_subs += char

    return data_l

# The actual error check for the 'dissect' function
# @param data - string, the string to check
# @return - boolean, True if there were no errors, False otherwise
def check_correctness(data, params):

    # Opened and closed parentheses must be equal in number (otherwise the
    # partition isn't reallay "enclosed" by them)
    if data.count('(') != data.count(')'):
        return False

    inside = data[1:-1].strip()

    # Elements shouldn't be inserted between multiple sets of parentheses
    if inside[0] == '(' and inside[-1] == ')':
        print("\n[ERROR] Use of nested parentheses detected in\n'" + data + "\nDo not use statements of the type (( xxx ))")
        return False

    name = inside.split()[0]

    # Save the arguments of a regular predicate/operator
    if data.count('(') == 1 and data.count(')') == 1:
        body = inside.split()[1:]
    # Special cost case, action effect
    elif name in ['increase', 'decrease']:

        inside_list = inside.split()

        # The following checks analyze the structure of a cost change operation
        if len(inside_list) != 3:
            print("[ERROR] The cost function " + name + " operation in one of the actions was incorrectly written.\nIt must follow the format\n'(increase (cost_function) amount)'\nor\n'(increase (cost_function) amount)'\nPlease correct the error.")
            return False

        cost = inside_list[-1]

        # Cost must be a positive integer
        try:
            cost = int(cost)
        except:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is not an integer.\nPlease correct the error.")
            return False
        if cost < 1:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is non-positive.\nPlease correct the error.")
            return False

        # Cost change step:
        # operation (cost_function) amount
        cost_function = inside_list[1]

        # Cost functions must be enclosed in parentheses
        if cost_function[0] != '(' or cost_function[-1] != ')':
            print("\n[ERROR] Cost modification function\n'" + body + "'\nis not enclosed in parentheses.\nPlease enclose it in parentheses.")
            return False

        cost_function = cost_function[1:-1]

        # The cost functions used by the domain and problem must be the same
        if 'cost_function' in params['domain'] and cost_function != params['domain']['cost_function']:
            print("\n[ERROR] Found cost function\n'" + cost_function + "'\nin an action, while previous cost function was defined as\n'" + params['domain']['cost_function']+ "'\nPlease correct one of the two.")
            return False
        else:
            params['domain']['cost_function'] = cost_function # TODO?

# =============================================================================
#         body = take_enclosed_data(inside)[0]
#         if body != '(total-cost)':
#             print("\n[ERROR] Expected\n'total-cost'\nin action cost definition\n'" + data + "'\ngot\n'" + body + "'\ninstead.\nPlease correct the error.")
#             return False
# =============================================================================
        return True
    elif name == '=':
        pass # The '=' in a cost initialization is a special case
    else:
        body = take_enclosed_data(data.replace(name, '', 1)[1:-1], no_outliers=True)
        if type(body) != list:
            print("\n[ERROR] Out-of-parentheses element\n'" + body + "'\nfound in statement\n'" + data + "'\nPlease encapsulate all arguments of a statement with their respective arguments in a set of parentheses.")
            return False

    # The operator is a predefined one (AND, OR, NOT):
    # Check if the requirements (unused), minimum and maximum amount of parameters
    # they can have is respected
    if name in params['predefined']:
        pred = params['predefined'][name]

        if pred['req'] != 'NONE' and not pred['req'] in params['requirements']:
            print("\n[ERROR] Instruction\n'" + name + "'\nhas the requirement\n'" + pred['req'] + "'\nwhich was not included.\nPlease remember to include it after the ':requirements' statement.")
            return False
        if pred['min'] != -1 and len(body) < pred['min']:
            print("\n[ERROR] Too few arguments for statement\n'" + name + "'\nMinimum is\n" + str(pred['min']) + "\nwhile the program encountered\n" + str(len(body)) + "")
            return False
        if pred['max'] != -1 and len(body) > pred['max']:
            print("\n[ERROR] Too many arguments for statement\n'" + name + "'\nMaximum is\n" + str(pred['max']) + "\nwhile the program encountered\n" + str(len(body)) + "")
            return False
    # Predicate case
    elif name in params['domain']['predicates']:
        pred = params['domain']['predicates'][name]

        if len(body) != len(pred):
            print("\n[ERROR] Predicate\n'" + name + "'\nexpected\n" + str(len(pred)) + "\nparameters, while\n" + str(len(body)) + "\nwere encountered in\n'" + data + "'")
            return False
    elif name == '=':
        pass # The '=' in a cost initialization is a special case
    else:
        # Cost function case: check if it was already declared and if the
        # previous declaration had the same name
        if 'cost_function' in params['domain']:
            data_inside = data[1:-1]
            if data_inside == params['domain']['cost_function']:
                return True

        # Unknown statement found
        print("\n[ERROR] Statement\n'" + name + "'\nencountered in\n'" + data + "'\nis unknown. Please check the spelling or, should it be a predicate, its inclusion in the ':predicates' statement.")
        return False

    return True

# Performs an initial shallow check on a string
# @param data - string, the string to check
# @param starter - string, the character which signals the start of a new segment
# @param ender- string, the character which signals the end of the segment
# @param ignore_inside - list, list of characters to ignore if found between a
#   starter and an ender
# @param no_outliers - boolean, signals whether to record characters outside of
#   a starter-ender pair (True) or not (False)
# @return - boolean, True if there were no errors, False otherwise
def dissect(data, params, starter="(", ender=")", ignore_inside=[], no_outliers=False):

    data_l = take_enclosed_data(data, starter, ender, ignore_inside, no_outliers)

    # Perform the check on every partition in the data string
    for d in data_l:
        out = check_correctness(d, params)
        if not out:
            return False
        # Recurse on partitions ofthe current partition
        out = dissect(d[1:-1], params, starter, ender, ignore_inside, no_outliers)
        if not out:
            return False
    return True

# Remove comments from a string; simply capture all characters between a ';' (the
# comment starter in PDDL) and a newline
# @param string - string, string to remove comments from
# @param comment_char - string, character initializing the comment (';' by default)
# @return - string, same string, without comments
def remove_comments(string, comment_char=';'):

    # Add a newline at the end so it's easier to check every line (the
    # 'take_enclosed_data' has an ender '\n' for sure)
    string += '\n'
    comments = take_enclosed_data(string, starter=';', ender='\n')

    # Automatically remove all comments; due to the inclusion of the ';'
    # character at the start, no non-comment strings will be removed
    for comment in comments:
        string = string.replace(comment[:-1], '')

    return string

# Align elements from list of lists. Example:
# [[1,3], [2,4]] -> [[1,2], [1,4], [2,3], [2,4]]
# @param cols - list, list of lists to align
# @return - list of aligned lists
def align(cols):

    assert type(cols) == list

    if len(cols) == 0:  # Base step
        return [[]]
    else:               # Recursive step
        res = []
        ccols = collection_copy(cols)   # Collection copy
        cur = ccols[0]                  # Current item to align
        ret = align(ccols[1:])          # Recursion

        # Take every item from the current collection and append it to
        # every result collection from the recursive operation
        for c in cur:
            for c1 in ret:
                aux = [c] + c1
                res.append(aux)

        return res

# Align the components of a dictionary of lists (same as the 'align', but for
# dictionaries). Example:
# {'a':[1,3], 'b':[2,4]} -> [{'b': 2, 'a': 1}, {'b': 4, 'a': 1}, {'b': 2, 'a': 3}, {'b': 4, 'a': 3}]
# @param d - dictionary, dictionary of lists to align
# @return - list of dictionaries, each of which is aligned
def align_dictionary(d):

    assert type(d) == dict          # Check the argument is a dictionary

    def iteration_step(d, used=[]):

        if d == {}:                 # Base step
            return [{}]

        out = []

        d_copy = collection_copy(d)     # Copy the dict to prevent side effect
        head = nthkey(d_copy)           # Recover parameter
        cont = d_copy.pop(head, None)   # Recover list of possible matches


        if cont != []:

            for i in cont:

                # Check if a match has not been used before
                if i not in used:
                    ret = iteration_step(d_copy, used + [i])    # Iterate
                    for r in ret:       # Attach the parameter to the return
                        r[head] = i
                        out.append(r)
                else:
                    out += iteration_step(d_copy, used)
            return out

        # Parameter may not have any possible matches
        else:
            return iteration_step(d_copy, used)

    return iteration_step(d)

# Permute elements in a collection
# @param col - dictionary/list, collection to be permuted
# @return - list/None, permutations
def permutations(col):

    # Dictionary case
    def permutations_d(col):

        assert type(col) == dict

        if len(col) == 0:   # Base step
            return [{}]

        out = []

        # Prevent side-effect from reference copy
        col_copy = collection_copy(col)

        # Extract the various elements of the dictionary and riassemble them in
        # a different order
        for elem in col_copy:
            cont = col_copy[elem]
            col_next = collection_copy(col_copy) # Side-effect risk: copy
            col_next.pop(elem, None)
            ret = permutations_d(col_next)
            for r in ret:
                r[elem] = cont
                out.append(r)

        return out

    # List case
    def permutations_l(col):

        assert type(col) == list

        if len(col) == 0:   # Base step
            return [[]]

        out = []

        # Side-effect risk, deep copy
        col_copy = collection_copy(col)

        # Reassemble elements in different order
        for elem in col_copy:
            ret = permutations_l(col_copy.remove(elem))
            for r in ret:
                out.append([elem] + r)

        return out

    if type(col) == dict:
        return permutations_d(col)
    elif type(col) == list:
        return permutations_l(col)
    else:
        return None

# Creates a list without duplicates
# @param col - list, list to purge duplicates from
# @return - list, new list, without duplicates
def remove_duplicates(col):

    assert type(col) == list

    ret = []

    for c in col:
        if c not in ret:
            ret.append(c)

    return ret

# Returns the Nth key of a dictionary (dicitonaries are unordered, but the
# function is still useful to extract the only key from a lenght-1 dictionary)
def nthkey(d, i=0):

    assert type(d) == dict
    assert len(list(d.keys())) >= i

    return list(d.keys())[i]

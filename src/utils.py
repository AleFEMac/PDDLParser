# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 12:14:58 2019

@author: Ale
"""

def collection_copy(col):
    
    if type(col) == dict:
        copy = {}
        for c in col:
            ret = collection_copy(col[c])
            copy[c] = ret
        return copy
    
    elif type(col) == list:
        copy = []
        for c in col:
            ret = collection_copy(c)
            copy.append(ret)
        return copy
    
    else:
        return col

def printd(diction):
    print("{")
    for i in diction:
        print(str(i) + ":", diction[i])
    print("}")

def ischalnum(string, puncts=['.']):
    for c in string:
        cc = ord(c)
        if not ((cc >= 48 and cc <= 57) or (cc >= 65 and cc <= 90) or (cc >= 97 and cc <= 122) or c in puncts):
            print(cc)
            return False
    return True

# Turn a list of directories/files in a parsable path
def make_name(directories):
    name = ""
    for directory in directories:
        name += directory + "/"
    
    return name[:-1]            

# Takes all characters (aside from those in "ignore_inside")included between a 
# set of a started and an ender and saves them in a list. Multiple sets of 
#starters-enders generate multiple lists.
def take_enclosed_data(data, starter="(", ender=")", ignore_inside=[], no_outliers=False):
    par = 0
    data_l = []
    current_subs = ""
    for char in data:        
        if char == starter:
            par += 1
            current_subs += char
        elif char == ender:
            if current_subs != "":
                current_subs += char
                par -= 1
                if par == 0:
                    data_l.append(current_subs)
                    current_subs = ""
        else:
            if par == 0 and char !=  " " and no_outliers:
                return char
            if current_subs != "" and char not in ignore_inside:
                current_subs += char
    
    return data_l
            
def check_correctness(data, params):
    
    
        
    if data.count('(') != data.count(')'):
        return False   
    
    inside = data[1:-1].strip()
    
    
        
    if inside[0] == '(' and inside[-1] == ')':
        print("\n[ERROR] Use of nested parentheses detected in\n'" + data + "\nDo not use statements of the type (( xxx ))")
        return False
    
    name = inside.split()[0]
    
    if data.count('(') == 1 and data.count(')') == 1:
        body = inside.split()[1:]
    elif name in ['increase', 'decrease']:
        
        inside_list = inside.split()
        
        if len(inside_list) != 3:
            print("[ERROR] The cost function " + name + " operation in one of the actions was incorrectly written.\nIt must follow the format\n'(increase (cost_function) amount)'\nor\n'(increase (cost_function) amount)'\nPlease correct the error.")
            return False
        
        cost = inside_list[-1]
        
        try:
            cost = int(cost)
        except:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is not an integer.\nPlease correct the error.")
            return False 
        if cost < 1:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is non-positive.\nPlease correct the error.")
            return False
        
        cost_function = inside_list[1]
        
        if cost_function[0] != '(' or cost_function[-1] != ')':
            print("\n[ERROR] Cost modification function\n'" + body + "'\nis not enclosed in parentheses.\nPlease enclose it in parentheses.")
            return False
        
        cost_function = cost_function[1:-1]
        
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
        pass # TODO? Not necessary to analyze, just skip it
    else:
        body = take_enclosed_data(data.replace(name, '', 1)[1:-1], no_outliers=True)
        if type(body) != list:
            print("\n[ERROR] Out-of-parentheses element\n'" + body + "'\nfound in statement\n'" + data + "'\nPlease encapsulate all arguments of a statement with their respective arguments in a set of parentheses.")
            return False
        
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
    elif name in params['domain']['predicates']:
        pred = params['domain']['predicates'][name]
        
        if len(body) != len(pred):
            print("\n[ERROR] Predicate\n'" + name + "'\nexpected\n" + str(len(pred)) + "\nparameters, while\n" + str(len(body)) + "\nwere encountered in\n'" + data + "'")
            return False
    elif name == '=':
        pass #TODO? Not necessary to analyze, just skip it
    else:        
        if 'cost_function' in params['domain']:
            data_inside = data[1:-1]
            if data_inside == params['domain']['cost_function']:
                return True
        
        print("\n[ERROR] Statement\n'" + name + "'\nencountered in\n'" + data + "'\nis unknown. Please check the spelling or, should it be a predicate, its inclusion in the ':predicates' statement.")
        return False
    
    return True

def dissect(data, params, starter="(", ender=")", ignore_inside=[], no_outliers=False):
    
    data_l = take_enclosed_data(data, starter, ender, ignore_inside, no_outliers)
    for d in data_l:
        out = check_correctness(d, params)
        if not out:
            return False
        out = dissect(d[1:-1], params, starter, ender, ignore_inside, no_outliers)
        if not out:
            return False
    return True

def remove_comments(string, comment_char=';'):
    
    string += '\n'
    comments = take_enclosed_data(string, starter=';', ender='\n')
    
    for comment in comments:
        string = string.replace(comment[:-1], '')
        
    return string
    
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

# Align the components of a dictionary of lists
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
    
def permutations(col):
    
    def permutations_d(col):
    
        assert type(col) == dict
        
        if len(col) == 0:   # Base step
            return [{}]
        
        out = []
        
        col_copy = collection_copy(col)
        
        for elem in col_copy:
            cont = col_copy[elem]        
            col_next = collection_copy(col_copy)
            col_next.pop(elem, None)
            ret = permutations_d(col_next)
            for r in ret:
                r[elem] = cont
                out.append(r)
        
        return out
    
    def permutations_l(col):       
    
        assert type(col) == list
        
        if len(col) == 0:   # Base step
            return [[]]
        
        out = []
        
        col_copy = collection_copy(col)
        
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

def remove_duplicates(col):
    
    assert type(col) == list
    
    ret = []
    
    for c in col:
        if c not in ret:
            ret.append(c)
    
    return ret

# =============================================================================
# Returns the nth  key of a dictionary
# =============================================================================
def nthkey(d, i=0):
    
    assert type(d) == dict
    assert len(list(d.keys())) >= i
    
    return list(d.keys())[i]


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
    print("(")
    for i in diction:
        print(str(i) + ":", diction[i])
    print(")")

def ischalnum(string, puncts=['.']):
    for c in string:
        cc = ord(c)
        if not ((cc >= 48 and cc <= 57) or (cc >= 65 and cc <= 90) or (cc >= 97 and cc <= 122) or c in puncts):
            print(cc)
            return False
    return True

def make_name(directories):
    name = ""
    for directory in directories:
        name += directory + "/"
    
    return name[:-1]            

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
    elif name == 'increase':
        cost = inside.split()[-1]
        try:
            cost = int(cost)
        except:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is not an integer.\nPlease correct the error.")
            return False 
        if cost < 1:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is non-positive.\nPlease correct the error.")
            return False  
        body = take_enclosed_data(inside)[0]
        if body != '(total-cost)':
            print("\n[ERROR] Expected\n'total-cost'\nin action cost definition\n'" + data + "'\ngot\n'" + body + "'\ninstead.\nPlease correct the error.")
            return False
        return True
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
    elif name == 'total-cost':
        return True
    else:
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
                aux = c1 + [c]
                res.append(aux)
        
        return res

print(align([[1]]))
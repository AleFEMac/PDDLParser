# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 12:14:58 2019

@author: Ale
"""

def ischalnum(string, puncts=['.']):
    for c in string:
        cc = ord(c)
        if not ((cc >= 65 and cc <= 90) or (cc >= 97 and cc <= 122) or c in puncts):
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
    
    inside = data[1:-1]
    name = inside.split()[0]    
    
    if data.count('(') == 1 and data.count(')') == 1:
        body = inside.split()[1:]
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
    elif name in params['predicates']:
        pred = params['predicates'][name]
        
        if len(body) != pred:
            print("\n[ERROR] Predicate\n'" + name + "'\nexpected\n" + str(len(pred)) + "\nparameters, while\n" + str(len(body)) + "\nwere encountered in\n'" + data + "'")
            return False
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

def check_parameter_pred(par1, actions):
    labels = []
    for action in actions:
        pass
    
    
    
    
    
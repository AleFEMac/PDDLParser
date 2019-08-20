# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 12:39:56 2019

@author: Ale
"""

from utils import take_enclosed_data

def calculate_cost(data, params):
    
    data = data.strip()
    
    if data.count("(") == 1 and data.count(")") == 1:
        cost = get_cost(data, params)
        return cost
    
    data_l = take_enclosed_data(data)
    
    cost = -1
    for d in data_l:
        out = calculate_cost(d[1:-1], params)
        if out == -2:
            return -2
        else:
            if cost != -1:
                return -2
            cost = out
    
    return cost

def get_cost(data, params):
    
    name = data.split()[0]
    
    if name == 'increase':
        cost = data.split()[-1]
        try:
            cost = int(cost)
        except:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is not an integer or is fractional.\nPlease correct the error.")
            return -2 
        if cost < 1:
            print("\n[ERROR] Cost error detected in\n'" + data + "'\nThe cost of the action is non-positive.\nPlease correct the error.")
            return -2  
        body = take_enclosed_data(data)[0]
        if body != '(total-cost)':
            print("\n[ERROR] Expected\n'total-cost'\nin action cost definition\n'" + data + "'\ngot\n'" + body + "'\ninstead.\nPlease correct the error.")
            return -2
        
        return cost
    
    return -1
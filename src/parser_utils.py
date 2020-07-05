# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:16:10 2019

@author: Ale
"""

from action_utils import toDNF, partition_recursively, assemble_DNF, compose_partition

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
                domain += " ?" + par
            domain += " )\n\t\t"
        
        if 'precondition' in action_d:
            domain += ":precondition " + action_d['precondition'] + "\n\t\t"
        
        domain += ":effect " + action_d['effect'] + "\n\t)\n\t"       
    
    domain = domain[:-1] + ")"

    f = open(file, 'w')        
    f.write(domain)    
    f.close()
    
    return

def write_problem(file, problem_struct):
       
    # Define instruction and problem name
    problem = "(define (problem " + problem_struct['name'] + ")\n\n\t"
    
    # Domain this problem refers to
    problem += "(:domain " + problem_struct['domain'] + ")\n\n\t"
    
    # Objects
    problem += "(:objects"
    for obj in problem_struct['objects']:
        problem += " " + obj
    problem += ")\n\n\t"
    
    # Problem initialization
    problem += "(:init " + problem_struct['init'] + ")\n\n\t"
    
    # Problem goal
    problem += "(:goal " + problem_struct['goal'] + ")\n)"   
    
    # Save problem on file
    f = open(file, 'w')    
    f.write(problem)
    f.close()
    
    return

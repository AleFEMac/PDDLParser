# -*- coding: utf-8 -*-
"""
Created on Mon Sep  9 11:16:10 2019

@author: Ale
"""

# Stringify the domain structure and put it on file
# @param file - string, path for the output file (file name included)
# @param domain_struct - dictionary structure containing all of the domain data
def write_domain(file, domain_struct):

    # Start the string
    domain = "(define (domain "

    domain += domain_struct['name'] + ")\n\n\t"
    domain += "(:predicates"

    # Insert predicates
    for pred in domain_struct['predicates']:
        domain += " (" + pred
        for arg in domain_struct['predicates'][pred]:
            domain += " " + arg
        domain += ")"
    domain += ")\n"

    # Actions
    for action in domain_struct['actions']:
        action_d = domain_struct['actions'][action]
        domain += "\n\t(:action " + action + "\n\t\t"

        # Action parameters (may not be present)
        if 'parameters' in action_d and len(action_d['parameters']) > 0:
            domain += ":parameters ("
            for par in action_d['parameters']:
                domain += " ?" + par
            domain += " )\n\t\t"

        # Actions preconditions (may not be present)
        if 'precondition' in action_d:
            domain += ":precondition " + action_d['precondition'] + "\n\t\t"

        # Effect (must be present)
        domain += ":effect " + action_d['effect'] + "\n\t)\n\t"

    domain = domain[:-1] + ")"

    # Save domain on file
    f = open(file, 'w')
    f.write(domain)
    f.close()

    return

# Stringify the problem structure and put it on file
# @param file - string, path for the output file (file name included)
# @param problem_struct - dictionary structure containing all of the problem data
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

    # If the problem has a cost, update the cost metric and function
    if "metric_goal" in problem_struct:
        problem = problem[:-1] + "\n\t"
        problem += "(:metric " + str(problem_struct["metric_goal"]) + " (" + problem_struct["cost_metric"] + "))\n)"

    # Save problem on file
    f = open(file, 'w')
    f.write(problem)
    f.close()

    return

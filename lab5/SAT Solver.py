#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys

sys.setrecursionlimit(10000)


# NO ADDITIONAL IMPORTS

def bool_works(formula, var, bool):
    '''
    :param formula: formula in traditional notation
    :param var:  string variable id
    :param bool: bool to check viability
    :return: True if variable with this bool returns valid solution, else False
    '''
    for clause in formula:
        for literal in clause:
            if literal[0] == var:
                if literal[1] == bool:
                    break
                elif len(clause) == 1:
                    return False
    return True


def trim_formula(formula, var, bool):
    '''
    :param formula: formula in given format
    :param var: string variable id
    :param bool: bool to trim based on matching
    :return: return formula trimmed based on given var, bool
    '''
    new_formula = []

    for clause in formula:

        new_clause = []
        append_clause = True

        for literal in clause:
            if literal[0] == var:
                if literal[1] == bool:
                    append_clause = False
                    break
            else:
                new_clause.append(literal)

        if append_clause:
            new_formula.append(new_clause)

    return new_formula


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    if len(formula) == 0:
        return {}

    shortest_clause = min(formula, key=lambda x: len(x))

    variable_id = shortest_clause[0][0]

    if bool_works(formula, variable_id, True):
        new_formula = trim_formula(formula, variable_id, True)

        if len(new_formula) == 0:
            return {variable_id: True}
        else:
            result = satisfying_assignment(new_formula)
            if result is not None:
                result.update({variable_id: True})
                return result

    if bool_works(formula, variable_id, False):
        new_formula = trim_formula(formula, variable_id, False)

        if len(new_formula) == 0:
            return {variable_id: False}
        else:
            result = satisfying_assignment(new_formula)
            if result is not None:
                result.update({variable_id: False})
                return result

    return None

def size_n_combinations(itemlist, n):
    '''
    used to break up the result of combo func. See docstring below for more details.
    '''
    result = combo_func(itemlist, n)
    return [result[i:i + n] for i in range(0, len(result), n)]

def combo_func(itemlist, n, current=[]):
    '''
    :param itemlist: list of items to sort
    :param n: length of desired combinations
    :param current: current list, used for recursive calls
    :return: given a list, return all unique length n combinations
    '''

    #print(itemlist, n, current)

    if len(current) == n:
        return current

    if itemlist == []:
        return []

    combinations = []

    item = [itemlist[0]]

    #with value
    combo = combo_func(itemlist[1:], n, current + item)
    #print(item, combo)
    combinations = combinations + combo

    #without value
    combo = combo_func(itemlist[1:], n, current)
    combinations = combinations + combo

    return combinations

def boolify_scheduling_problem(student_preferences, session_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of session names (strings) that work for that student
    session_capacities: a dictionary mapping each session name to a positive
                        integer for how many students can fit in that session

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up
    We assume no student or session names contain underscores.
    """
    to_return = []
    for student in student_preferences:  # assign students based on their preferences
        clause = []
        for room in student_preferences[student]:
            clause.append((student + '_' + room, True))
        to_return.append(clause)

    size_2_combos_rooms = size_n_combinations(list(session_capacities.keys()), 2)

    for student in student_preferences:
        for combo in size_2_combos_rooms:
            clause = []
            for room in combo:
                clause.append((student + '_' + room, False))
            to_return.append(clause)

    for room in session_capacities:
        if session_capacities[room] < len(student_preferences.keys()):
            size_n_combos_students = size_n_combinations(list(student_preferences.keys()), session_capacities[room] + 1)
        else:
            continue
        for combo in size_n_combos_students:
            clause = []
            for student in combo:
                clause.append((student + '_' + room, False))
            to_return.append(clause)

    return to_return
if __name__ == '__main__':
    pass
    # import doctest
    #
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)
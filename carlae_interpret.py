#!/usr/bin/env python3
"""6.009 Lab 7: carlae Interpreter"""

import doctest
import sys

# NO ADDITIONAL IMPORTS!


class EvaluationError(Exception):
    """
    Exception to be raised if there is an error during evaluation other than a
    NameError.
    """
    pass


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a carlae
                      expression
    """
    #  trim input to include only relevant characters
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890()!?@#$%^&*+-{}[]/\|.><='
    trimmed_string = []
    in_comment = False

    for character in source:  # iterate through each character in source
        if character == ';':
            in_comment = True  # flag that we are in comment upon sight of a ;

        if character == '\n' or character == ' ':  # semicolon to indicate that we need to cut here
            trimmed_string.append(';')
            if character == '\n':  # exit comment on newline
                in_comment = False

        if character in characters and not in_comment:  # only add if we are in comment
            trimmed_string.append(character)

    # group letter/number strings vs operators
    operators = '(); '
    to_return = []
    current_word = []

    for character in trimmed_string:
        if character in operators:  # if character not a word we can add the current word and reset it
            if ''.join(current_word) != '':
                to_return.append(''.join(current_word))
            current_word = []
            if character != ';':
                to_return.append(character)
        else:
            current_word.append(character)

    if ''.join(current_word) != '':
        to_return.append(''.join(current_word))
    return to_return


def is_legal(tokens):
    if tokens[0] != "(" and len(tokens) > 1:  # check if expression is and s expression if longer than len 1
        return False
    count = 0
    for token in tokens:  # checks matching on # of parentheses
        if token == '(':
            count += 1  # add 1 for each open
        if token == ')':
            count -= 1  # sub 1 for each close
        if count < 0:  # these should match
            return False

    if count == 0:
        return True
    return False


def find_end_list(index, sequence):
    '''
    :param tokens: list of symbols returned by tokenize function
    :return: index at which a clustering of symbols ends
    '''
    count = 1
    i = 1

    tokens = sequence[index:]

    while count != 0:
        if tokens[i] == '(':
            count += 1
        if tokens[i] == ')':
            count -= 1
        i += 1

    return i + index  # return the index beyond which list ends


def parse_expression(tokens):
    '''
    :param tokens: list of symbols returned by tokenize
    :return: lists of variables of correct type
    Tries conversion in order of int ==> float ==> string
    Upon detection of an expression initiaties a recursive call on that expression.
    '''
    to_return = []
    i = 0

    while i < len(tokens):
        if tokens[i] != '(' and tokens[i] != ')':  # if not an s expression
            try:  # try conversion to int, then float, then string
                to_return.append(int(tokens[i]))
            except ValueError:
                try:
                    to_return.append(float(tokens[i]))
                except ValueError:
                    to_return.append(str(tokens[i]))
        elif tokens[i] == '(':  # if s exp detected, find end index, use it to cut and recursively run on that part
            end_index = find_end_list(i, tokens)
            to_return.append(parse_expression(tokens[i + 1:end_index]))
            i = end_index - 1
        i += 1

    return to_return


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    if not is_legal(tokens):
        raise SyntaxError

    return parse_expression(tokens)[0]


def multiply(items):  # helper function for multiplication
    start = 1
    for item in items:
        start *= item
    return start


def divide(items):  # helper function for division
    start = items[0]
    for i in range(1, len(items)):
        start /= items[i]
    return start


def equal_to(items):  # helper for equality
    for item in items:
        if item != items[0]:
            return '#f'
    return '#t'


def greater_than(items):  # helper for >
    val = items[0]
    items = items[1:]
    for item in items:
        if val <= item:
            return '#f'
    return '#t'


def greater_than_eq_to(items):  # helper for >=
    val = items[0]
    items = items[1:]
    for item in items:
        if val < item:
            return '#f'
    return '#t'


def less_than(items):  # helper for <
    val = items[0]
    items = items[1:]
    for item in items:
        if val >= item:
            return '#f'
    return '#t'


def less_than_eq_to(items):  # helper for <=
    val = items[0]
    items = items[1:]
    for item in items:
        if val > item:
            return '#f'
    return '#t'

carlae_builtins = {
    '+': sum,
    '-': lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: multiply(args),
    "/": lambda args: divide(args),
    '=?': lambda args: equal_to(args),
    '>': lambda args: greater_than(args),
    '<': lambda args: less_than(args),
    '>=': lambda args: greater_than_eq_to(args),
    '<=': lambda args: less_than_eq_to(args),
    '#t': '#t',  # true
    '#f': '#f',  # false
    'nil': 'nil',  # None
    'not': lambda args: '#f' if args[0] == '#t' else '#t',
    'car': lambda args: get_car(args[0]),
    'cdr': lambda args: get_cdr(args[0]),
    'length': lambda args: length_list(args[0]),
    'elt-at-index': lambda args: elt_at_index(args[0], args[1]),
    'map': lambda args: map_(args[0], args[1]),
    'filter': lambda args: filter_(args[0], args[1]),
    'concat': lambda args: concatenate(args) if len(args) > 0 else concatenate([]),
    'reduce': lambda args: reduce(args[0], args[1], args[2]),
    'begin': lambda args: args[-1]
}

def evaluate(tree, env=None):
    """
    Evaluate the given syntax tree according to the rules of the carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if env is None:  # create env if there exists none upon function call
        env = Environment(builtins_env)

    if type(tree) is str:  # string indicates a variable is being referenced
        if tree in env:
            return env[tree]  # return variable from env, otherwise raise error
        else:
            raise NameError('Variable not defined in tree or any parent')

    if type(tree) is int or type(tree) is float:  # if number return number
        return tree

    if type(tree) is list:
        if len(tree) == 0:  # Tree can't be of len 0
            raise EvaluationError('Tree is of length 0')
        if type(tree[0]) is int or type(tree[0]) is float:  # must have operator to start s statement
            raise EvaluationError('Incorrectly structured s statement')

        if tree[0] == 'if':
            evaluated = evaluate(tree[1], env)  # check value of conditional
            if evaluated == '#t':
                return evaluate(tree[2], env)  # if true execute trueexp
            elif evaluated == '#f':
                return evaluate(tree[3], env)  # if false execute falseexp

        if tree[0] == 'and':
            for item in tree[1:]:  # check each item, if any false return false.
                evaluated = evaluate(item, env)
                if evaluated == '#f':
                    return '#f'
            return '#t'

        if tree[0] == 'or':
            for item in tree[1:]:  # check each item, if any true return true.
                evaluated = evaluate(item, env)
                if evaluated == '#t':
                    return '#t'
            return '#f'

        if tree[0] == 'cons':
            return Pair(evaluate(tree[1], env), evaluate(tree[2], env))

        if tree[0] == 'list':

            def list_(items):
                if len(items) == 0:
                    return 'nil'
                return Pair(evaluate(items[0], env), list_(items[1:]))

            return list_(tree[1:])

        if tree[0] == 'define':
            if len(tree) != 3:  # define must be of len 3
                raise EvaluationError
            if type(tree[1]) is list:  # restructure in case of shortened function definition
                tree = ['define', tree[1][0], ['lambda', tree[1][1:], tree[2]]] + tree[3:]
            env[tree[1]] = evaluate(tree[2], env)  # set value
            return env[tree[1]]  # return value set tot that variable

        if tree[0] == 'let':
            let_env = Environment(env)
            var_bindings = {}
            for assignment in tree[1]:  # create a new env and assign vars in there, then do calculation
                var_bindings[assignment[0]] = evaluate(assignment[1], let_env)
            let_env.items = var_bindings
            return evaluate(tree[2], let_env)

        if tree[0] == 'set!':
            if len(tree) != 3:
                raise EvaluationError('Set bang statement of length other than three')
            var = tree[1]
            var_env = env.setbanghelper(var)  # find var env using this helper
            return evaluate(['define', var, evaluate(tree[2], env)], var_env)  # set var value in var env

        if tree[0] == 'lambda':
            new_func = Function(tree[1], tree[2], env)
            return new_func

        if type(tree[0]) is list:  # evaluate first item if func
            func = evaluate(tree[0], env)
            return func([evaluate(item, env) for item in tree[1:]])

        try:  # we need try because in doesn't work for lists (un-hashable)
            func = env[tree[0]]
        except NameError:
            raise NameError
        except:
            raise EvaluationError('Unknown command given')

        to_eval = []
        for item in tree[1:]:  # run func on items after first if item 1 is a defined function
            if type(item) is not list:
                if item not in env:  # add variable val if pre-defined
                    to_eval.append(evaluate(item))
                else:
                    to_eval.append(env[item])
            else:
                to_eval.append(evaluate(item, env))  # if item is a list evaluate it before adding

        return func(to_eval)


def REPL(env=None):  # test env for carlae code
    raw_input = input('in>')
    if env is None:  # create new env if none exists
        env = Environment(builtins_env)

    while raw_input not in ['QUIT', 'quit']:
        try:
            evaluated = evaluate(parse(tokenize(raw_input)), env) # evaluated tokenized parsed input in env
            print('out>' + str(evaluated))
        except EvaluationError:  # prints the error
            print('EVALUATION ERROR')
        except NameError:
            print('NAME ERROR')
        raw_input = input('in>')  # accept next input


def result_and_env(tree, env=None):
    if env is None:
        env = Environment(builtins_env)
    return evaluate(tree, env), env


class Environment():
    def __init__(self, parent=None):
        self.parent = parent
        self.items = {}

    def __getitem__(self, item):
        if item in self.items:
            return self.items[item]
        elif item not in self.items and self.parent == None:
            raise NameError('Value not found in environment or any of its parents')

        return self.parent[item]

    def __setitem__(self, key, value):
        self.items[key] = value

    def __contains__(self, item):
        if item in self.items:
            return True
        elif item not in self.items and self.parent is None:
            return False
        else:
            return item in self.parent

    def setbanghelper(self, item):
        if item in self.items:
            return self
        elif self.parent is None:
            raise NameError('Set bang failed, var not defined in env or any of its parents')
        else:
            return self.parent.setbanghelper(item)

    def __str__(self):
        return str([(item, self.items[item]) for item in self.items])


class Function(object):
    def __init__(self, args, func, env):
        self.args = args  # the arguments of the function
        self.func = func  # what the function does
        self.env = env  # the environment in which the function operates

    def __call__(self, args):
        if len(args) != len(self.args):
            raise EvaluationError('Too many variables in function call')

        function_env = Environment(self.env)  # function must be evaluated in its own special environment

        for i in range(len(args)):
            function_env[self.args[i]] = args[i]  # assign variables by position in function call

        return evaluate(self.func, function_env)


class Pair(object):
    def __init__(self, car=None, cdr=None):
        self.car = car
        self.cdr = cdr


def get_car(cons):
    if type(cons) is Pair:
        return cons.car
    else:
        raise EvaluationError('car called on object that is not Pair')


def get_cdr(cons):
    if type(cons) is Pair:
        return cons.cdr
    else:
        raise EvaluationError('cdr called on object that is not Pair')


def length_list(linked_list):
    if linked_list == 'nil':
        return 0
    next_item = linked_list
    i = 1
    while get_cdr(next_item) != 'nil':
        i += 1
        next_item = get_cdr(next_item)
    return i


def elt_at_index(linked_list, index):
    if index == 0:
        return get_car(linked_list)
    elif length_list(linked_list) <= index:
        raise EvaluationError('list index out of range')
    elif type(get_cdr(linked_list)) == Pair:
        return elt_at_index(get_cdr(linked_list), index-1)
    else:
        raise EvaluationError('called elt_at_index on cons statement, not list')


def list_(items):
    if len(items) == 0:
        return 'nil'
    return Pair(items[0], list_(items[1:]))


def concatenate(lists):
    if len(lists) == 0:
        return 'nil'

    for item in lists:
        if type(item) != Pair and item != 'nil':
            raise EvaluationError('non pair type in list during concatenation')

    if len(lists) == 1:
        return lists[0]
    else:
        last = 'nil'  # final node is nil
        for linked_list in reversed(lists): # iterate thru lists in reverse
            for i in range(length_list(linked_list) - 1, -1, -1):  # for i in reversed range
                last = Pair(elt_at_index(linked_list, i), last)  # last one is this new pair that includes previous last

        return last


def map_(func, linked_list):

    if linked_list == 'nil':
        return 'nil'

    try:  # try to evaluate it as function call from known env
        last = 'nil'
        for i in range(length_list(linked_list) - 1, -1, -1):
            last = Pair(evaluate([func, elt_at_index(linked_list, i)], func.env), last)
    except:  # otherwise call as if it were another function
        last = 'nil'
        for i in range(length_list(linked_list) - 1, -1, -1):
            last = Pair(func([elt_at_index(linked_list, i)]), last)

    return last


def filter_(func, linked_list):
    if linked_list == 'nil':
        return 'nil'
    last = 'nil'  # similar to last func except only allow in if true rather than mutate val
    for i in range(length_list(linked_list) - 1, -1, -1):
        if func([elt_at_index(linked_list, i)]) == '#t':
            last = Pair(elt_at_index(linked_list, i), last)

    return last


def reduce(func, linked_list, initial):
    next = initial
    try:  # try to evaluate it as function call from known env
        for i in range(length_list(linked_list)):
            next = evaluate([func, next, elt_at_index(linked_list, i)], func.env)
    except:  # otherwise call as if it were another function
        for i in range(length_list(linked_list)):
            next = func([next, elt_at_index(linked_list, i)])
    return next


def evaluate_file(filename, env=None):
    if env is None:
        env = Environment(builtins_env)
    opened = open(filename)  # open file
    read = opened.read()  # read file
    return evaluate(parse(tokenize(read)), env)


builtins_env = Environment()
builtins_env.items = carlae_builtins
# arg_list = sys.argv  # info for pulling assignments from command line
# for arg in arg_list[1:]:
#     evaluate_file(arg, builtins_env)
# print(builtins_env)


if __name__ == '__main__':
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)
    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    a = tokenize('(define (call x) (x))')
    b = parse(a)
    print(b)
    my_env = Environment(builtins_env)
    print(evaluate(b, my_env))
    print(my_env)
    a = tokenize('(call)')
    b = parse(a)
    print(b)
    print(evaluate(b, my_env))
    print(b)
    print(my_env)
    # REPL()

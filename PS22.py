#!/usr/bin/env python
# Simple Daikon-style invariant checker
# Andreas Zeller, May 2012
# Complete the provided code, using your code from
# first exercise and adding ability to infer assertions
# for variable type, set and relations
# Modify only the classes Range and Invariants,
# if you need additional functions, make sure
# they are inside the classes.

import sys
import math
import random


def square_root(x, eps=0.00001):
    assert x >= 0
    y = math.sqrt(x)
    assert abs(square(y) - x) <= eps
    return y


def square(x):
    return x * x


def double(x):
    return abs(20 * x) + 10


# The Range class tracks the types and value ranges for a single variable.

class Range(object):
    def __init__(self):
        self.min = None  # Minimum value seen
        self.max = None  # Maximum value seen
        self.type = None  # Type of variable
        self.set = set()  # Set of values taken
        self.value = None

    # Invoke this for every value
    def track(self, value):
        if self.min > value or self.min == None:
            self.min = value
        if self.max < value or self.max == None:
            self.max = value
        self.set.add(value)
        self.type = type(value)
        self.value = value

    # YOUR CODE

    def __repr__(self):
        repr(self.type) + " " + repr(self.min) + ".." + repr(self.max) + " " + repr(self.set)


# The Invariants class tracks all Ranges for all variables seen.
class Invariants:
    def __init__(self):
        # Mapping (Function Name) -> (Event type) -> (Variable Name)
        # e.g. self.variables["sqrt"]["call"]["x"] = Range()
        # holds the range for the argument x when calling sqrt(x)
        self.variables = {}

    def track(self, frame, event, arg):
        if event == "call" or event == "return":
            if not self.variables.has_key(frame.f_code.co_name):
                self.variables[frame.f_code.co_name] = {}
            if not self.variables[frame.f_code.co_name].has_key(event):
                self.variables[frame.f_code.co_name][event] = {}
            for var, val in frame.f_locals.iteritems():
                if not self.variables[frame.f_code.co_name][event].has_key(var):
                    self.variables[frame.f_code.co_name][event][var] = Range()
                self.variables[frame.f_code.co_name][event][var].track(val)
            if event == 'return':
                if not self.variables[frame.f_code.co_name][event].has_key('ret'):
                    self.variables[frame.f_code.co_name][event]['ret'] = Range()
                self.variables[frame.f_code.co_name][event]['ret'].track(arg)

    # YOUR CODE HERE.
    # MAKE SURE TO TRACK ALL VARIABLES AND THEIR VALUES

    def __repr__(self):
        # Return the tracked invariants
        s = ""
        for function, events in self.variables.iteritems():
            for event, variables in events.iteritems():
                s += event + " " + function + ":\n"

                for var, range in variables.iteritems():
                    s += "    assert isinstance(" + var + ", type(" + str(range.value) + '))\n'  # YOUR CODE
                    s += "    assert " + var + ' in ' + repr(range.set)
                    s += "\n"
                    if min(range.set) == max(range.set):
                        s += '    assert ' + var + ' == ' + min(range.set) + '\n'
                    else:
                        s += '    assert ' + repr(min(range.set)) + ' <= ' + var + ' <= ' + repr(max(range.set)) + '\n'
                    # ADD HERE RELATIONS BETWEEN VARIABLES
                    # RELATIONS SHOULD BE ONE OF: ==, <=, >=
                    eq = False
                    moeq = False
                    loeq = False
                    for var2, range2 in variables.iteritems():
                        if var2 != var:
                            if range.set == range2.set:
                                eq = True
                            else:
                                eq = False
                            if all(i >= j for i in list(range.set) for j in list(range2.set)):
                                moeq = True
                            else:
                                moeq = False
                            if all(i <= j for i in list(range.set) for j in list(range2.set)):
                                loeq = True
                            else:
                                loeq = False
                        else:
                            eq = False
                            moeq = False
                            loeq = False
                        if eq:
                            s += "    assert " + var + " == " + var2 + "\n"
                        if moeq:
                            s += "    assert " + var + " >= " + var2 + "\n"
                        if loeq:
                            s += "    assert " + var + " <= " + var2 + "\n"

        return s


invariants = Invariants()


def traceit(frame, event, arg):
    invariants.track(frame, event, arg)
    return traceit


sys.settrace(traceit)
# Tester. Increase the range for more precise results when running locally
eps = 0.000001
test_vars = [3, 0, -10]
for i in test_vars:
    # for i in range(1, 10):
    z = double(i)
sys.settrace(None)
print invariants

# Example sample of a correct output:
"""
return double:
    assert isinstance(x, type(-293438.402))
    assert x in set([9.348, -293438.402, 34.6363])
    assert -293438.402 <= x <= 34.6363
    assert x <= ret
"""

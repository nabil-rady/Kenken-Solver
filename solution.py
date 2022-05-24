from collections import deque
from typing import Any, Callable, Optional

class Solution:
    def __init__(self, vars: dict, domains: dict, neighbors: dict):
        self.vars = vars
        self.domains = domains
        self.neighbors = neighbors
        self.current_domains = None

    def constraints(self, *args, **kwargs):
        raise NotImplementedError

    def get_domain(self, var):
        return (self.current_domains or self.domains)[var]

    def number_of_conflicts(self, var, val, assignment):
        def neighbour_is_conflicting(neighbour):  
            return (neighbour in assignment and
                    not self.constraints(var, val, neighbour, assignment[neighbour]))
        return [neighbour_is_conflicting(neighbour) for neighbour in self.neighbors[var]].count(True)

    def assign(self, var, val, assignment):
        assignment[var] = val

    def unassign(self, var, assignment):
        if var in assignment:
            del assignment[var]

    def copy_domains(self):
        if self.current_domains is None:
            self.current_domains = {var: list(self.domains[var]) for var in self.vars}

    def prune(self, var, value, removals):
        self.current_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def get_removals(self, var, value):
        self.copy_domains()
        removals = [(var, possible_value) for possible_value in self.current_domains[var] if possible_value != value]
        self.current_domains[var] = [value]
        return removals

    def restore_removed_paths(self, removals):
        for var, removed_values in removals:
            self.current_domains[var].append(removed_values)

def first_unassigned_variable(assignment, sol):
    return [x for x in sol.vars if x not in assignment][0]

def forward_checking(sol: Solution, var, value, assignment, removals):
    sol.copy_domains()
    for neighbour in sol.neighbors[var]:
        if neighbour not in assignment:
            for possible_value in sol.current_domains[neighbour][:]:
                if not sol.constraints(var, value, neighbour, possible_value):
                    sol.prune(neighbour, possible_value, removals)
            if not sol.current_domains[neighbour]:
                return False
    return True

def ac3(sol: Solution, queue, removals):
    sol.copy_domains()
    while queue:
        (Xi, Xj) = queue.pop()
        if remove_inconsistent_values(sol, Xi, Xj, removals):
            if not sol.current_domains[Xi]:
                return False
            for Xk in sol.neighbors[Xi]:
                if Xk != Xj:
                    queue.append((Xk, Xi))
    return True


def remove_inconsistent_values(sol: Solution, Xi, Xj, removals):
    removed = False
    for x in sol.current_domains[Xi][:]:
        if all(not sol.constraints(Xi, x, Xj, y) for y in sol.current_domains[Xj]):
            sol.prune(Xi, x, removals)
            removed = True
    return removed

def apply_ac3(sol: Solution, var, value, assignment, removals):
    return ac3(sol, deque([(X, var) for X in sol.neighbors[var]]), removals)

def backtracking_search(sol: Solution,
                        select_unassigned_variable=first_unassigned_variable,
                        inference_method: Optional[Callable[[Solution, dict, Any, dict], bool]]=None):
    def backtrack(assignment):
        if len(assignment) == len(sol.vars):
            return assignment
        var = select_unassigned_variable(assignment, sol)
        for value in sol.get_domain(var):
            if sol.number_of_conflicts(var, value, assignment) == 0:
                sol.assign(var, value, assignment)
                if inference_method:
                    removals = sol.get_removals(var, value)  
                if not inference_method or inference_method(sol, var, value, assignment, removals):    
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                if inference_method:
                    sol.restore_removed_paths(removals)
        sol.unassign(var, assignment)
        return None

    result = backtrack({})
    return result

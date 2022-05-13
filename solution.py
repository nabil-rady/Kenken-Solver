class Solution:
    def __init__(self, vars, domains, neighbors, constraints):
        self.vars = vars
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints

    def get_domain(self, var):
        return self.domains[var]

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


def first_unassigned_variable(assignment, sol):
    return [x for x in sol.vars if x not in assignment][0]

def backtracking_search(sol: Solution,
                        select_unassigned_variable=first_unassigned_variable):
    def backtrack(assignment):
        if len(assignment) == len(sol.vars):
            return assignment
        var = select_unassigned_variable(assignment, sol)
        for value in sol.get_domain(var):
            if sol.number_of_conflicts(var, value, assignment) == 0:
                sol.assign(var, value, assignment)
                result = backtrack(assignment)
                if result is not None:
                    return result
        sol.unassign(var, assignment)
        return None

    result = backtrack({})
    return result


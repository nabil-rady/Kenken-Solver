from functools import reduce
import random
import solution
from itertools import product, permutations
from time import perf_counter
from csv import writer

def operation(operator):
    if operator == '+':
        return lambda a, b: a + b
    elif operator == '-':
        return lambda a, b: a - b
    elif operator == '*':
        return lambda a, b: a * b
    elif operator == '/':
        return lambda a, b: a / b
    else:
        return None

def is_adjacent(cell_1, cell_2):
    # Adjancent in X or Y direction (not diagonal)
    x1, y1 = cell_1
    x2, y2 = cell_2

    return (x1 - x2 == 0 and abs(y1 - y2) == 1) or (y1 - y2 == 0 and abs(x1 - x2) == 1)

def generate(board_size):

    board = [[((i + j) % board_size) + 1 for i in range(board_size)] for j in range(board_size)]

    for _ in range(board_size):
        random.shuffle(board)

    for i in range(board_size):
        for j in range(board_size):
            if random.random() > 0.5:
                for k in range(board_size):
                    board[k][i], board[k][j] = board[k][j], board[k][i]

    board = {(j + 1, i + 1): board[i][j] for i in range(board_size) for j in range(board_size)}

    # This will contain all uncaged cells
    uncaged = sorted(board.keys(), key=lambda x: x[1])

    cages = []
    while uncaged:

        cages.append([])

        cage_size = random.randint(1, 4)

        cell = uncaged[0]

        uncaged.remove(cell)

        cages[-1].append(cell)

        for _ in range(cage_size - 1):

            adjs = [adj for adj in uncaged if is_adjacent(cell, adj)]

            cell = random.choice(adjs) if adjs else None

            if not cell:
                break

            uncaged.remove(cell)
            
            cages[-1].append(cell)
            
        cage_size = len(cages[-1])
        
        if cage_size == 1:
            cell = cages[-1][0]
            cages[-1] = ((cell, ), '.', board[cell])
            continue
        
        elif cage_size == 2:
            first, second = cages[-1][0], cages[-1][1]
            if board[first] / board[second] > 0 and not board[first] % board[second]:
                operator = "/" 
            else:
                operator = "-"
        
        else:
            operator = random.choice("+*")

        cage_val = reduce(operation(operator), [board[cell] for cell in cages[-1]])

        cages[-1] = (tuple(cages[-1]), operator, int(cage_val))

    return cages

def row_or_col_same(cell_1, cell_2):
    x1, y1 = cell_1
    x2, y2 = cell_2

    same_row = x1 == x2
    same_col = y1 == y2

    return same_row or same_col

# True if cage values are in conflict.
def cage_is_conflicting(cage, cell_values):
    for (cell1, cell_value1) in zip(cage, cell_values):
        for(cell2, cell_value2) in zip(cage ,cell_values):
            if row_or_col_same(cell1, cell2) and cell1 != cell2 and cell_value1 == cell_value2: # If 1) there is a common col or row 2) not the same cell (because of foor loop) 3) same number, then this solution for the cage is wrong.
                return True    
    return False

# True if kenken cage value is correct.
def satisfies_cage_value(values, operation, cage_value):
    return any([reduce(operation, permutation) == cage_value for permutation in permutations(values)])

# Generates possible solutions.
def generate_domains(size, cages):
    domains = {}
    for cage in cages:
        cage_cells, operator, cage_value = cage

        domains[cage_cells] = list(product(range(1, size + 1), repeat=len(cage_cells)))

        qualifies = lambda values: not cage_is_conflicting(cage_cells, values) and satisfies_cage_value(values, operation(operator), cage_value)

        domains[cage_cells] = list(filter(qualifies, domains[cage_cells]))

    return domains

# True if cage values could cause conflict
def probable_conflict_of_neighbours(cage_1, cage_2):
    for cell_1 in cage_1:
        for cell_2 in cage_2:
            if row_or_col_same(cell_1, cell_2):
                return True
    return False

def generate_neighbors(cages):
    # Generate all neigbhours to all cages
    neighbors = {}
    for members, _, _ in cages:
        neighbors[members] = []

    for cage_1, _, _ in cages:
        for cage_2, _, _ in cages:
            if cage_1 != cage_2 and cage_2 not in neighbors[cage_1]:
                if probable_conflict_of_neighbours(cage_1, cage_2):
                    neighbors[cage_1].append(cage_2)
                    neighbors[cage_2].append(cage_1)

    return neighbors

class Kenken(solution.Solution):
    def __init__(self, size, cages):    
        vars = [cage_cell for cage_cell, _, _ in cages]

        domains = generate_domains(size, cages)

        neighbors = generate_neighbors(cages)

        super().__init__(vars, domains, neighbors)

        self.size = size

    # True if no conflict between two cages.
    def constraints(self, cage_1, values_of_cage_1, cage_2, values_of_cage_2):
        if cage_1 == cage_2:
            return True
        for cell_1, value_in_cage_1 in zip(cage_1, values_of_cage_1):
            for cell_2, value_in_cage_2 in zip(cage_2,  values_of_cage_2):
                if row_or_col_same(cell_1, cell_2) and value_in_cage_1 == value_in_cage_2:
                    return False
        return True

def run_algorithm(kenken, algorithm):

        start_time = perf_counter()

        assignment = algorithm(kenken)

        completion_time = perf_counter() - start_time

        return assignment, round(completion_time, 3)

def evaluate(num_of_boards, out):
    
    bt         = lambda ken: solution.backtracking_search(ken)
    bt_fc         = lambda ken: solution.backtracking_search(ken, inference_method=solution.forward_checking)
    bt_arc     = lambda ken: solution.backtracking_search(ken, inference_method=solution.apply_ac3)
    

    algorithms = {
        "BT": bt,
        "BT+FC": bt_fc,
        "BT+ARC": bt_arc
    }

    with open(out, "w+") as file:

        out = writer(file)

        out.writerow(["Algorithm", "Size", "Average time"])

        for board_size in range(5, 10):

            avg_time_bt = 0

            avg_time_bt_fc = 0

            avg_time_bt_arc = 0

            
            for board_num in range(1, num_of_boards + 1):

                    
                cages = generate(board_size)
                
                for algorithm_name, algorithm in algorithms.items():

                    if algorithm_name == 'BT' and board_size > 7:
                        continue

                    assignment, completion_time = run_algorithm(Kenken(board_size, cages), algorithm)

                    print("Algorithm =",  algorithm_name, "Size =", board_size, "Board number =", board_num, "Completion_time =", completion_time , "Result =", "Success" if assignment else "Failure")

                    if algorithm_name == "BT":

                        avg_time_bt += completion_time

                    elif algorithm_name == "BT+FC":

                        avg_time_bt_fc += completion_time

                    elif algorithm_name == "BT+ARC":

                        avg_time_bt_arc += completion_time    
                    

            avg_time_bt /= num_of_boards

            avg_time_bt_fc /= num_of_boards

            avg_time_bt_arc /= num_of_boards

            avg_time_bt = round(avg_time_bt, 3)

            avg_time_bt_fc = round(avg_time_bt_fc, 3)

            avg_time_bt_arc = round(avg_time_bt_arc, 3)

            for algorithm_name, algorithm in algorithms.items():

                if algorithm_name == "BT" and board_size < 8:

                    out.writerow([algorithm_name, board_size, avg_time_bt])

                elif algorithm_name == "BT+FC":

                    out.writerow([algorithm_name, board_size, avg_time_bt_fc])

                elif algorithm_name == "BT+ARC":

                    out.writerow([algorithm_name, board_size, avg_time_bt_arc])

            if board_size < 8:

                print("Average time for backtracking algorithm to run for board size = ", board_size , " is " , avg_time_bt , "seconds")

            print("Average time for backtracking with forward checking algorithm to run for board size = ", board_size , " is " , avg_time_bt_fc , "seconds")

            print("Average time for backtracking with arc consistency algorithm to run for board size = ", board_size , " is " , avg_time_bt_arc , "seconds")

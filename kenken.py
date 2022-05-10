from functools import reduce
import random

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

    cliques = []
    while uncaged:

        cliques.append([])

        clique_size = random.randint(1, 4)

        cell = uncaged[0]

        uncaged.remove(cell)

        cliques[-1].append(cell)

        for _ in range(clique_size - 1):

            adjs = [adj for adj in uncaged if is_adjacent(cell, adj)]

            cell = random.choice(adjs) if adjs else None

            if not cell:
                break

            uncaged.remove(cell)
            
            cliques[-1].append(cell)
            
        clique_size = len(cliques[-1])
        
        if clique_size == 1:
            cell = cliques[-1][0]
            cliques[-1] = ((cell, ), '.', board[cell])
            continue
        
        elif clique_size == 2:
            first, second = cliques[-1][0], cliques[-1][1]
            if board[first] / board[second] > 0 and not board[first] % board[second]:
                operator = "/" 
            else:
                operator = "-"
        
        else:
            operator = random.choice("+*")

        clique_val = reduce(operation(operator), [board[cell] for cell in cliques[-1]])

        cliques[-1] = (((cliques[-1]), operator, int(clique_val)))

    return cliques

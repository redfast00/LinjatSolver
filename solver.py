from itertools import product
import z3


def solve_puzzle(p):
    height = len(p)
    width = len(p[0])

    possible_states = ['empty']
    for h, line in enumerate(p):
        for w, tile in enumerate(line):
            if tile not in (' ', '.'):
                possible_states.append(f'line_{h}_{w}_{tile}')

    TileState, (empty, *lines) = z3.EnumSort('TileState', possible_states)
    board = [[z3.Const(f'coord_{h}_{w}', TileState) for w in range(width)] for h in range(height)]

    solver = z3.Solver()
    enumlookup = {str(v): v for v in lines}

    # Dots must be filled by a line
    for h, line in enumerate(p):
        for w, tile in enumerate(line):
            if tile == '.':
                solver.add(board[h][w] != empty)

    def inboard(h, w):
        return (0 <= h < height) and (0 <= w < width)

    def orientations(location, size):
        h, w = location
        # vertical
        for begin in range(h - size + 1, h + 1):
            if inboard(begin, w) and inboard(begin + size - 1, w):
                yield {(hi, w) for hi in range(begin, begin + size)}
        # horizontal
        for begin in range(w - size + 1, w + 1):
            if inboard(h, begin) and inboard(h, begin + size - 1):
                yield {(h, wi) for wi in range(begin, begin + size)}

    def to_var(location):
        h, w = location
        return board[h][w]

    all_tiles = {(hi, wi) for hi, wi in product(range(height), range(width))}

    # Lines must be the correct length and not be anywhere they're not
    for h, line in enumerate(p):
        for w, tile in enumerate(line):
            if tile not in ('.', ' '):
                clauses = []
                occupy = enumlookup[f'line_{h}_{w}_{tile}']
                # Generate all possible positions of a line
                for occupied_tiles in orientations((h, w), int(tile)):
                    # Lines must occupy the tiles they occupy
                    occupy_clause = z3.And(
                        *(map((lambda location: to_var(location) == occupy),
                              occupied_tiles))
                    )
                    # Lines cannot occupy the tiles they don't occupy
                    not_occupy_clause = z3.And(
                        *(map((lambda location: to_var(location) != occupy),
                              all_tiles - occupied_tiles))
                    )
                    clauses.append(z3.And(occupy_clause, not_occupy_clause))
                # A position excludes other positions, so we can use Or
                #  (instead of AtLeast and AtMost)
                solver.add(z3.Or(*clauses))

    if solver.check() != z3.sat:
        raise ValueError("Puzzle not solvable")
    model = solver.model()
    solved_board = [['' for w in range(width)] for h in range(height)]
    for tile in model.decls():
        tilename = str(tile)
        valuename = str(model[tile])
        tileparts = tilename.split('_')
        h, w = int(tileparts[1]), int(tileparts[2])
        if valuename == 'empty':
            solved_board[h][w] = None
        else:
            valueparts = valuename.split('_')
            origin_h, origin_w = int(valueparts[1]), int(valueparts[2])
            solved_board[h][w] = (origin_h, origin_w)
    return solved_board

#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!

'''
refactored by creating get neighbor bombs, and valid neighbors.
'''


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def get_neighbor_bombs(num_rows, num_cols, bombs):
    '''
    :param num_rows: number of rows
    :param num_cols: number of columns
    :param bombs: tuples of bomb locations (down, right)
    :return: list of lists where each location is the amount of neighboring bombs
    '''
    number = 0

    bomb_numbers = [[0] * num_cols for i in range(num_rows)]

    for r in range(num_rows):
        for c in range(num_cols):
            if (r, c) in bombs:
                if 0 <= r - 1 < num_rows:
                    bomb_numbers[r - 1][c] += 1
                    if 0 <= c - 1 < num_cols:
                        bomb_numbers[r - 1][c - 1] += 1
                    if 0 <= c + 1 < num_cols:
                        bomb_numbers[r - 1][c + 1] += 1
                if 0 <= r + 1 < num_rows:
                    bomb_numbers[r + 1][c] += 1
                    if 0 <= c - 1 < num_cols:
                        bomb_numbers[r + 1][c - 1] += 1
                    if 0 <= c + 1 < num_cols:
                        bomb_numbers[r + 1][c + 1] += 1
                if 0 <= c - 1 < num_cols:
                    bomb_numbers[r][c - 1] += 1
                if 0 <= c + 1 < num_cols:
                    bomb_numbers[r][c + 1] += 1

    return bomb_numbers


def get_valid_neighbors(num_rows, num_cols):
    '''
    :param num_rows: integer number of rows
    :param num_cols: integer number of columns
    :return: Set of tuples of valid positions
    '''
    valid_locations = set()

    for r in range(num_rows):
        for c in range(num_cols):
            valid_locations.add((r, c))

    return valid_locations


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat
    """
    return dig_nd(game, (row, col))


def render_2d(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring bombs).
    game['mask'] indicates which squares should be visible.  If xray is True (the
    default is False), game['mask'] is ignored and all cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)


def render_ascii(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function 'render_2d(game)'.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> print(render_ascii({'dimensions': (2, 4),
    ...                     'state': 'ongoing',
    ...                     'board': [['.', 3, 1, 0],
    ...                               ['.', '.', 1, 0]],
    ...                     'mask':  [[True, True, True, False],
    ...                               [False, False, True, False]]}))
    .31_
    __1_
    """
    render = render_2d(game, xray)

    gamestring = ''

    for i in render:
        for j in i:
            gamestring += j
        gamestring += '\n'

    return gamestring[:-1]


# N-D IMPLEMENTATION

def initialize_nd_board(dimensions, val):
    '''
    :param dimensions: Tuple of list dimensions
    :return: n-dimensional array where all values are 0
    '''

    if len(dimensions[0:]) == 1:  # base case, when we are in 1d scenario
        return dimensions[0] * [val]  # add lists full of value of length of given dimension
    else:
        return [initialize_nd_board(dimensions[1:], val) for i in range(dimensions[0])]
        # recursive step. Create lists of len dimension[0] of whatever we get in n - 1 case.


def get_value_at_location(board, location):
    '''
    :param board: nd array
    :param location: coordinates in nd of location to check
    :return: value at given location
    '''
    if len(location) == 1:  # base case, return location here
        return board[location[0]]
    else:
        return get_value_at_location(board[location[0]], location[1:])  # otherwise get value at spot in next index


def replace_value_at_location(board, location, new_value):
    '''
    :param board: nd array
    :param location: coordinates of nd location to change
    :param new_value: string new value to set the board to
    :return: new board with value replaced
    '''

    if len(location) == 1:  # exact same function as above, only this time we are replacing the value.
        board[location[0]] = new_value
    else:
        return replace_value_at_location(board[location[0]], location[1:], new_value)


def get_valid_tiles(dimensions):
    '''
    :param dimensions: tuple of length n with dimension values.
    :return: list of lists of all possible coordinates in space.
    '''
    if len(dimensions) == 1:
        possible_coordinates = []  # base case. We generate 1 elt lists up to i to add to base subsequent lists.
        for i in range(dimensions[0]):
            possible_coordinates.append([i])
        return possible_coordinates

    else:
        possible_coordinates = []
        for i in range(dimensions[0]):  # recursive step. create lists by adding lists of up to current val to old lists
            for dimension in get_valid_tiles(dimensions[1:]):  # dimension includes all possible smaller lists
                possible_coordinates.append([i] + dimension)

    return possible_coordinates


def get_neighbors(dimensions, tile):
    '''
    :param dimensions: length n tuple corresponding to dimensions of the board
    :param tile: tuple of coordinates for tile whose neighbors we search
    :return: set of tuples of neighbor tile coordinates
    '''

    if len(tile) == 1:  # base case, simply add values from -1 to +1 of val at index to possibilities
        one_d_possibilities = []

        for neighbor in range(tile[0] - 1, tile[0] + 2):
            if 0 <= neighbor < dimensions[0]:
                one_d_possibilities.append([neighbor])

        return one_d_possibilities

    else:  # recursive step, add values at index to previous lists generated by this function
        neighbors = []
        for neighbor in range(tile[0] - 1, tile[0] + 2):
            if 0 <= neighbor < dimensions[0]:
                for previous_dimensions in get_neighbors(dimensions[1:], tile[1:]):
                    neighbors.append([neighbor] + previous_dimensions)
        return neighbors


def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing
    """
    board = initialize_nd_board(dimensions, 0)
    mask = initialize_nd_board(dimensions, False)

    for bomb in bombs:
        replace_value_at_location(board, bomb, '.')

    for bomb in bombs:
        for neighbor in get_neighbors(dimensions, bomb):
            val = get_value_at_location(board, neighbor)
            if val != '.':
                replace_value_at_location(board, neighbor, 1 + int(val))

    return {
        'dimensions': dimensions,
        'board': board,
        'mask': mask,
        'state': 'ongoing'}


def dig_nd(game, coordinates, tiles=None):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False], [False, False]],
    ...               [[False, False], [False, False], [False, False], [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    if tiles is None:
        tiles = get_valid_tiles(game['dimensions'])

    if game['state'] == 'defeat' or game['state'] == 'victory':  # keep the state the same
        return 0

    if get_value_at_location(game['board'], coordinates) == '.':  # case where bomb clicked
        replace_value_at_location(game['mask'], coordinates, True)
        game['state'] = 'defeat'
        return 1

    if get_value_at_location(game['mask'], coordinates) != True:  # if we cant see tile, reveal it
        replace_value_at_location(game['mask'], coordinates, True)
        revealed = 1

    else:
        return 0

    def dig(game, coordinates):  # helper function to dig around zeroes.
        dug = 0
        agenda = []

        if get_value_at_location(game['board'], coordinates) != 0:
            if get_value_at_location(game['mask'], coordinates) == False:
                replace_value_at_location(game['mask'], coordinates, True)
                return 1
            else:
                return 0

        else:  # if tile is 0, we can recursively check neighbors
            neighbors = get_neighbors(game['dimensions'], coordinates)
            for neighbor in neighbors:  # going thru neighbors. recall neighbor is a tuple.
                if get_value_at_location(game['board'], neighbor) != '.':
                    if get_value_at_location(game['mask'], neighbor) == False:
                        replace_value_at_location(game['mask'], neighbor, True)
                        agenda.append(neighbor)

        revealed = len(agenda)

        for neighbor in agenda:
            revealed += dig(game, neighbor)

        return revealed

    revealed += dig(game, coordinates)

    bombs = 0  # set number of bombs to 0
    covered_squares = 0

    for tile in tiles:
        if get_value_at_location(game['board'], tile) == '.':
            if get_value_at_location(game['mask'], tile):
                # if the game mask is True, and the board is '.', add 1 to
                # bombs
                bombs += 1

        elif get_value_at_location(game['mask'], tile) == False:
            covered_squares += 1

    bad_squares = bombs + covered_squares
    if bad_squares > 0:
        game['state'] = 'ongoing'
        return revealed
    else:
        game['state'] = 'victory'
        return revealed


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True], [True, True]],
    ...               [[False, False], [False, False], [True, True], [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    tiles = get_valid_tiles(game['dimensions'])
    to_return = initialize_nd_board(game['dimensions'], 0)
    if xray:
        mask = initialize_nd_board(game['dimensions'], True)
    else:
        mask = game['mask']

    for tile in tiles:
        if xray:
            val = str(get_value_at_location(game['board'], tile))
            if val == '0':
                replace_value_at_location(to_return, tile, ' ')
            else:
                replace_value_at_location(to_return, tile, val)
        else:
            if get_value_at_location(mask, tile) == False:
                replace_value_at_location(to_return, tile, '_')
            else:
                val = str(get_value_at_location(game['board'], tile))
                if val == '0':
                    replace_value_at_location(to_return, tile, ' ')
                else:
                    replace_value_at_location(to_return, tile, val)

    return to_return


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # a = {'dimensions': (2, 4), 'state': 'ongoing', 'board': [['.', 3, 1, 0], ['.', '.', 1, 0]], 'mask': [[False, True, False, True], [False, False, False, True]]}

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so, comment
    # out the above line, and uncomment the below line of code. This may be
    # useful as you write/debug individual doctests or functions.  Also, the
    # verbose flag can be set to True to see all test results, including those
    # that pass.
    # doctest.run_docstring_examples(new_game_nd, globals(), optionflags=_doctest_flags, verbose=0)
    # a = get_neighbors((3,3,3,3,3), (1,1,1,1,1))
    # print(len(a))
    # print(3**5)
    # a = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # print(a)

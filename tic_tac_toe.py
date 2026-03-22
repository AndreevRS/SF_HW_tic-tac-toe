import queue
import random

# A queue for storing turns
turns = queue.Queue()
turns.put('x')
turns.put('o')


def choose_mark() -> str:
    """Ask the user to choose a mark (x or o)."""
    user_choice = input('Choose your mark (x or o): ')
    test_error = None

    if user_choice in ['x', 'X', 'х', 'Х']:
        choice = 'x'
    elif user_choice in ['o', 'O', 'о', 'О', '0']:
        choice = 'o'
    else:
        test_error = True

    if test_error:
        print('Invalid choice. Try again.')
        choice = choose_mark()
    return choice


def get_next_turn() -> str:
    """Implements swapping turns for players' moves.
    Returns a symbol of whose turn to move is now (x or o)
    """
    global turns
    turn = turns.get()
    turns.put(turn)
    return turn


def get_opponent(turn: str) -> str:
    """Returns the opponent's symbol."""
    if turn == 'x':
        return 'o'
    else:
        return 'x'


def print_grid(grid: list[list[str]]) -> None:
    """Prints the grid."""
    headers = '  0 1 2\n'
    grid_body = '\n'.join([str(index)
                             + ' '
                             + ' '.join([str(cell) for cell in row])
                             for index, row in enumerate(grid)])
    print(headers + grid_body)


def count_marks_horizontally(grid: list[list[str]], turn: str) -> list[int]:
    """Counts the number of specified marks horizontally."""
    return [sum(1 for cell in row if cell == turn) for row in grid]


def count_marks_vertically(grid: list[list[str]], turn: str) -> list[int]:
    """Counts the number of specified marks vertically."""
    transposed_grid = list(zip(*grid))
    return [sum(1 for cell in row if cell == turn) for row in transposed_grid]


def count_marks_diagonally(grid: list[list[str]], turn: str) -> list[int]:
    """Counts the number of specified marks diagonally."""
    diagonals = [[grid[i][i] for i in range(3)],
                 [grid[3-1-i][i] for i in range(3-1, -1, -1)]]
    return [sum(1 for cell in row if cell == turn) for row in diagonals]


def is_win_check(grid: list[list[str]], turn: str) -> bool:
    """Checks if the current player has 3 marks in one of the rows, columns or diagonals."""
    full_horizontal = 3 in count_marks_horizontally(grid, turn)
    full_vertical = 3 in count_marks_vertically(grid, turn)
    full_diagonal = 3 in count_marks_diagonally(grid, turn)
    return any([full_horizontal, full_vertical, full_diagonal])


def find_winning_cell_horizontally(grid: list[list[str]], turn: str) -> tuple[int, int] | None:
    """Finds the cell where the winning (the third in a row) mark can be placed."""
    own_horizontal = count_marks_horizontally(grid, turn)
    empty_horizontal = count_marks_horizontally(grid, '-')
    win_rows = [index for index, (own, empty) in enumerate(zip(own_horizontal, empty_horizontal))
           if own == 2 and empty == 1 ]
    if win_rows:
        row = win_rows[0]
        cell = grid[row].index('-')
        return row, cell
    else:
        return None


def find_winning_cell_vertically(grid: list[list[str]], turn: str) -> tuple[int, int] | None:
    """Finds the cell where the winning (the third in a column) mark can be placed."""
    own_vertical = count_marks_vertically(grid, turn)
    empty_vertical = count_marks_vertically(grid, '-')
    transposed_grid = list(zip(*grid))
    win_cells = [index for index, (own, empty) in enumerate(zip(own_vertical, empty_vertical))
           if own == 2 and empty == 1 ]
    if win_cells:
        cell = win_cells[0]
        row = transposed_grid[cell].index('-')
        return row, cell
    else:
        return None


def find_winning_cell_diagonally(grid: list[list[str]], turn: str) -> tuple[int, int] | None:
    """Finds the cell where the winning (the third in a diagonal) mark can be placed."""
    own_diagonal = count_marks_diagonally(grid, turn)
    empty_diagonal = count_marks_diagonally(grid, '-')
    win_diagonals = [index for index, (own, empty) in enumerate(zip(own_diagonal, empty_diagonal))
           if own == 2 and empty == 1 ]
    if 0 in win_diagonals:  # diagonal  (0,0), (1,1), (2,2)
        index = [grid[0][0], grid[1][1], grid[2][2]].index('-')
        return index, index
    elif 1 in win_diagonals:  # diagonal  (0,2), (1,1), (2,0)
        row = [grid[0][2], grid[1][1], grid[2][0]].index('-')
        cell = 3 - 1 - row
        return row, cell
    else:
        return None


def get_winning_cell(grid: list[list[str]], turn: str) -> tuple[int, int] | None:
    """Gets the winning cell."""
    finding_functions = [find_winning_cell_horizontally, find_winning_cell_vertically, find_winning_cell_diagonally]
    winning_cell_list = [f(grid, turn) for f in finding_functions if f(grid, turn) is not None]
    if len(winning_cell_list) == 0:
        return None
    else:
        return winning_cell_list[0]


def random_move(grid: list[list[str]]) -> tuple[int, int]:
    '''Returns a random move for computer.'''
    empty_cells = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == '-']
    move = random.choice(empty_cells)
    return move


def computer_moves(grid: list[list[str]], turn: str) -> tuple[int, int]:
    '''Implements the computer moves algorithm.
    First it tries to find a winning cell, if any.
    If none, it tries to block an opponent's winning cell, if any.
    Otherwise makes a random move to one of the empty cells.
    '''
    winning_move = get_winning_cell(grid, turn)
    if winning_move is not None:
        return winning_move

    opponent = get_opponent(turn)
    blocking_move = get_winning_cell(grid, opponent)
    if blocking_move is not None:
        return blocking_move

    return random_move(grid)


def user_moves(grid: list[list[str]], turn: str) -> tuple[int, int]:
    """ Prompts the user for a move and validates input."""
    user_input = input('Enter row (0-2) and column (0-2) (eg. 2 1): ')
    two_digits = ''.join(c for c in user_input if c.isdigit())[0:2]
    try:
        row = int(two_digits[0])
    except IndexError:
        row = None
    try:
        col = int(two_digits[1])
    except IndexError:
        col = None

    test_1_failed, test_2_failed, test_3_failed = None, None, None
    if row is None or col is None:
        test_1_failed = True
        error_msg = 'Invalid input. Two numbers are expected. Please try again.'
    elif row not in [0, 1, 2] or col not in [0, 1, 2]:
        test_2_failed = True
        error_msg = 'Invalid input. Numbers must be from 0 to 2. Please try again.'
    elif grid[row][col] != '-':
        test_3_failed = True
        error_msg = 'This space is not empty. Please try again.'

    if any([test_1_failed, test_2_failed, test_3_failed]):
        print(error_msg)
        row, col = user_moves(grid, turn)
    return row, col


def put_mark_into_grid(grid: list[list[str]], turn: str, move: tuple[int, int]) -> list[list[str]]:
    grid[move[0]][move[1]] = turn
    return grid


def no_free_space_left(grid: list[list[str]]) -> bool:
    """Detects if no space is left in the grid."""
    free_space = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == '-']
    if len(free_space) == 0:
        return True
    else:
        return False


def __main__():
    print('Welcome to Tic-Tac-Toe!')
    print('')
    user_mark = choose_mark()
    print('')
    print("You are playing '" + user_mark + "'")
    print("Computer is playing '"  + get_opponent(user_mark) + "'")
    print('')

    # Create initial (empty) grid.
    grid = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
    print_grid(grid)

    while True:
        current_turn = get_next_turn()
        if current_turn == user_mark:
            current_move = user_moves(grid, current_turn)
            print(f'Your move is {current_move}')
        else:
            current_move = computer_moves(grid, current_turn)
            print(f'Computer move is {current_move}')
        grid = put_mark_into_grid(grid, current_turn, current_move)
        print_grid(grid)
        if is_win_check(grid, current_turn):
            print('')
            print(f"'{current_turn}' wins!")
            break
        if no_free_space_left(grid):
            print('')
            print("No free space left! A draw!")
            break


__main__()

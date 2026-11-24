def mvmt(x: float, y: float) -> tuple:
    """
    Args:
        x (float): x input in range [0.0, 100.0]
        y (float): y input in range [0.0, 100.0]
    Returns:
        (tuple) (left, right): left and right motor commands in range [-1, 1]
    """
    x = motor_to_working_values(x)
    y = motor_to_working_values(y)

    character = None
    if abs(x) >= abs(y):
        character = "more_horizontal"
    elif abs(y) > abs(x):
        character = "more_vertical"
    # elif abs(x) == abs(y):
    #     character = "diagonal"
    else: 
        assert False

    if x == y == 0.0:
        return (50.0, 50.0)
    
    # direction = (int(x//abs(x)), int(y//abs(y)))
    if x != 0:
        dx = int(x//abs(x))
    else:
        dx = 0
    if y != 0:
        dy = int(y//abs(y))
    else:
        dy = 0
    direction = (dx, dy)

    # print(f"dir: {direction}")
    corner = vec(direction)
    # print(f"corner: {corner}")

    # if character == "diagonal":
    #     return (x, y)

    if character == "more_vertical":
        side = vec((0, direction[1]))
    elif character == "more_horizontal":
        side = vec((direction[0], 0))
    else:
        assert False
    # print(f"side: {side}")

    # normalizing values and stuff to get standard right triangle setup
    if character == "more_horizontal":
        a = abs(x)
        b = abs(y)
    elif character == "more_vertical":
        a = abs(y)
        b = abs(x)
    else:
        assert False

    side_pct = a - b
    corner_pct = b
    # print(f"side_pct: {side_pct}, corner_pct: {corner_pct}")

    left = side[0]*side_pct + corner[0]*corner_pct
    right = side[1]*side_pct + corner[1]*corner_pct

    # print(f"left: {left}, right: {right}")
    left = working_to_motor_values(left)
    right = working_to_motor_values(right)
    return left, right

def vec(input: tuple) -> tuple:
    x = input[0]
    y = input[1]
    vector_table = [[(0, 1), (1, 1), (1, 0)], 
                    [(-1, 1), (0, 0), (1, -1)], 
                    [(-1, 0), (-1, -1), (0, -1)]]
    return vector_table[(-y)+1][x+1]

def motor_to_working_values(input: float) -> float:
    # maps values in range [0.0, 100.0] to range [-1.0, 1.0]
    return (input-50)/50

def working_to_motor_values(input: float) -> float:
    # maps values in range [-1.0, 1.0] to range [0.0, 100.0]
    return (input*50) + 50
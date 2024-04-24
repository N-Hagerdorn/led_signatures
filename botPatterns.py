import copy

patterns = {
    'x': [[0, 1, 0],
          [1, 1, 1],
          [0, 1, 0]],

    'y': [[1, 0, 1],
          [0, 1, 0],
          [0, 1, 0]],

    'h': [[1, 0, 1],
          [1, 1, 1],
          [1, 0, 1]],

    'stair': [[1, 0, 0],
              [1, 1, 0],
              [1, 1, 1]]
}


def getPattern(pattern_name):
    pattern = copy.deepcopy(patterns[pattern_name.lower()])
    return pattern

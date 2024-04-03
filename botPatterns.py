import copy

patterns = {
    'X': [[0, 1, 0],
          [1, 1, 1],
          [0, 1, 0]],

    'Y': [[1, 0, 1],
          [0, 1, 0],
          [0, 1, 0]],

    'H': [[1, 0, 1],
          [1, 1, 1],
          [1, 0, 1]]
}


def getPattern(pattern_name):
    pattern = copy.deepcopy(patterns[pattern_name.upper()])
    return pattern

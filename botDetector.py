import math


def groupNearbyPoints(points, threshold_distance):
    if len(points) < 1:
        return []

    groups = [[points[0]]]
    for point in points[1:]:
        eligible_groups = []

        for group_idx in range(len(groups)):

            group_copy = groups[group_idx].copy()

            for ref_point in group_copy:
                if distance(point, ref_point) <= threshold_distance:
                    eligible_groups.append(group_idx)

        if len(eligible_groups) < 1:
            groups.append([point])
        else:
            new_group = [point]
            for group_idx in eligible_groups:
                group = groups[group_idx]
                new_group += group.copy()
                groups[group_idx] = []
            groups.append(new_group)

    cleaned_groups = []
    for group in groups:
        print('Group prior to cleaning: ' + str(group))
        if len(group) < 1:
            continue
        cleaned_group = removeDuplicatePoints(group, 0.001)
        cleaned_groups.append(cleaned_group)
        print('Group after cleaning: ' + str(cleaned_group))

    return cleaned_groups

def removeDuplicatePoints(points, tolerance):
    if len(points) < 1:
        return []

    distinct_points = [points[0]]
    for point in points[1:]:
        duplicate = False
        checked_points = distinct_points.copy()

        for checked_point in checked_points:

            if distance(point, checked_point) < tolerance:
                duplicate = True
                break

        if not duplicate:
            distinct_points.append(point)

    return distinct_points



def consolidateGroups(groups):

    group_points = []
    for group in groups:
        if len(group) < 1:
            continue
        x_sum = 0
        y_sum = 0

        for point in group:
            x_sum += point[0]
            y_sum += point[1]

        x_mean = x_sum / len(group)
        y_mean = y_sum / len(group)

        group_point = (x_mean, y_mean)
        group_points.append(group_point)

    return group_points

def detectX(group, tolerance):
    if len(group) < 3:
        return []

    group_center = consolidateGroups([group])[0]

    remaining_points = group.copy()

    # Get the center point of the X
    min_distance = math.inf
    center_point = (0, 0)
    center_point_idx = -1
    for point_idx in range(len(group)):
        point = group[point_idx]

        point_distance = distance(group_center, point)
        if point_distance < min_distance:
            min_distance = point_distance
            center_point = point
            center_point_idx = point_idx

    print('Expected center point at ' + str(group_center))
    print('Center point at ' + str(center_point))

    if distance(center_point, group_center) > tolerance:
        print('Did not find the center point')
        return []

    remaining_points.pop(center_point_idx)
    print(str(remaining_points))

    # Find the closest outer point to the center
    min_distance = math.inf
    closest_point_idx = -1
    for point_idx in range(len(remaining_points)):
        point = remaining_points[point_idx]

        point_distance = distance(center_point, point)
        if point_distance < min_distance:
            min_distance = point_distance
            closest_point_idx = point_idx

    closest_point = remaining_points[closest_point_idx]

    print('Closest arm point at ' + str(closest_point))

    remaining_points.pop(closest_point_idx)
    print(str(remaining_points))

    opposite_point_expected = (2 * center_point[0] - closest_point[0], 2 * center_point[1] - closest_point[1])
    # Find the closest point to the expected position of the opposite
    min_distance = math.inf
    opposite_point_idx = -1
    for point_idx in range(len(remaining_points)):
        point = remaining_points[point_idx]

        point_distance = distance(opposite_point_expected, point)
        if point_distance < min_distance:
            min_distance = point_distance
            opposite_point_idx = point_idx

    opposite_point = remaining_points[opposite_point_idx]

    print('Expected opposite arm point at ' + str(opposite_point_expected))
    print('Actual opposite point at ' + str(opposite_point))

    if distance(opposite_point, opposite_point_expected) > tolerance:
        print('Did not find the opposite point')
        return []

    remaining_points.pop(opposite_point_idx)
    print(str(remaining_points))
    '''
    left_point_expected = (group_center[0] - closest_point[1], group_center[1] - closest_point[0])
    # Find the closest point to the expected position of the left
    min_distance = math.inf
    left_point = (0, 0)
    left_point_idx = -1
    for point_idx in range(len(remaining_points)):
        point = group(point_idx)

        point_distance = distance(left_point_expected, point)
        if point_distance < min_distance:
            min_distance = point_distance
            left_point = point
            left_point_idx = point_idx

    remaining_points.pop(left_point_idx)

    right_point_expected = (-group_center[0] + closest_point[1], -group_center[1] + closest_point[0])
    # Find the closest point to the expected position of the left
    min_distance = math.inf
    right_point = (0, 0)
    right_point_idx = -1
    for point_idx in range(len(remaining_points)):
        point = group(point_idx)

        point_distance = distance(right_point_expected, point)
        if point_distance < min_distance:
            min_distance = point_distance
            right_point = point
            right_point_idx = point_idx

    remaining_points.pop(right_point_idx)'''
    return [center_point, closest_point, opposite_point]#, left_point, right_point]


def distance(point1, point2):
    return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1], 2))

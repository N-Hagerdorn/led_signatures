import math
import botPatterns


def groupNearbyPoints(points, threshold_distance):
    """
    Group rectangular points together if they are closer than a given distance.
    :param points:                  A list of points to group as (x, y) tuples
    :param threshold_distance:      The maximum distance between two points to consider them a group
    :return:                        A list of groups, which are each a list of close points
    """

    # If there are no points, return no groups
    if len(points) < 1:
        return []

    # Start a group using the first point
    groups = [[points[0]]]

    # Group the rest of the points
    for point in points[1:]:

        # List all groups that the point is close enough to be part of
        eligible_groups = []

        # Check each existing group
        for group_idx in range(len(groups)):

            group = groups[group_idx]

            # Check the proximity of the current point to each point in the group
            for ref_point in group:

                # If the current point is close enough to any point in the group,
                # it is eligible to be a member of that group
                if distance(point, ref_point) <= threshold_distance:
                    eligible_groups.append(group_idx)
                    break

        # If there are no groups this point is eligible to be added to, make it its own new group
        if len(eligible_groups) < 1:
            groups.append([point])

        # Otherwise, make a new group and merge all the eligible groups together, since this point connects them all
        else:
            new_group = [point]

            for group_idx in eligible_groups:

                # Get the group, add a copy of it to the new group, and make the old group empty
                group = groups[group_idx]
                new_group += group.copy()
                groups[group_idx] = []

            groups.append(new_group)

    # Clean up the groups before returning them
    cleaned_groups = []
    for group in groups:

        # Remove all empty groups that were produced when groups were merged
        if len(group) < 1:
            continue

        # Remove duplicate points from each group
        cleaned_group = removeDuplicatePoints(group, 0.01)

        cleaned_groups.append(cleaned_group)

    return cleaned_groups


def removeDuplicatePoints(points, tolerance):
    """
    Remove duplicate points if they are within a given distance from one another.
    :param points:          The list of points as (x, y) tuples
    :param tolerance:       The maximum distance between points to consider them duplicates of one another
    :return:                The list of points with duplicates removed
    """

    # Return the original list if there are not enough points to check for duplicates (0 or 1 points)
    if len(points) < 2:
        return points

    # The first point is always distinct, since no others have been checked yet
    distinct_points = [points[0]]

    # Check all other points
    for point in points[1:]:

        # Assume the current point is not a duplicate
        duplicate = False

        # Make a copy of all points that are known to be unique
        checked_points = distinct_points.copy()

        # Check the current point against all points that have previously been checked
        for checked_point in checked_points:

            if distance(point, checked_point) < tolerance:
                duplicate = True
                break

        if not duplicate:
            distinct_points.append(point)

    return distinct_points


def groupCenters(groups):
    """
    Convert a list of point groups into a list of their center points.
    The center point of a group is the average (x, y) position of its member points.
    :param groups:          A list of groups of points
    :return:                A list of points which are the center points of each group
    """

    group_points = []
    for group in groups:

        # An empty group has no center
        if len(group) < 1:
            continue

        # Compute the arithmetic means of the x and y coordinates of the points in the group
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


def numPointsInPattern(pattern):
    """
    Return the number of points in a pattern.
    :param pattern:         A 2D list of numbers which represents a pattern of points
    :return:                The number of points in the pattern
    """
    count = 0

    for line in pattern:

        # Count the number of non-zero elements in the line
        for element in line:
            if element > 0:
                count += 1

    return count


def cartesianToPolar(cart_vector):
    """
    Convert a Cartesian vector (such as a point) to its polar form representation
    :param cart_vector:     The Cartesian vector to convert
    :return:                The converted polar vector
    """

    x, y = cart_vector

    r = math.sqrt(x**2 + y**2)
    theta = math.degrees(math.atan2(y, x))

    return r, theta


# The idea is to treat the LED board like a wheel.
# There is a center point and 8 spokes.
# Find the center point if it exists and the angles between each spoke.
def detectShape(group, pattern):
    """
    Evaluate how similar a group of given points is to a specified pattern of points.
    A lower score returned indicates a higher similarity.
    :param group:           The group of points to match to a pattern
    :param pattern:         The pattern (2D list of binary numbers) to match the points to
    :return:                A score indicating the similarity between the group and pattern
    """

    pattern_size = numPointsInPattern(pattern)

    # The group won't match the pattern if it doesn't contain as many LEDs as the pattern
    # Return the worst possible score
    if len(group) < pattern_size:
        return math.inf

    # Get the center of the group
    group_center = groupCenters([group])[0]

    remaining_points = group.copy()

    # If the pattern has a point in the center position,
    # find the point that is closest to the calculated center and use that as the group center
    center_point = group_center
    center_state = pattern[1][1]
    if center_state > 0:

        # Get the center point of the group
        min_distance = math.inf
        center_point_idx = -1
        for point_idx in range(len(group)):
            point = group[point_idx]

            point_distance = distance(group_center, point)
            if point_distance < min_distance:
                min_distance = point_distance
                center_point_idx = point_idx

        center_point = remaining_points.pop(center_point_idx)

    # Convert all the remaining points to polar coordinates
    # with the center point as the origin of the polar coordinate frame
    spoke_points = normalizeAngles(cartesianToPolarList(remaining_points, center_point))

    # Get the length of the shortest spoke in the wheel
    side_spoke_length = min([spoke[0] for spoke in spoke_points])

    pattern_spokes = pattern.copy()
    pattern_spokes[1][1] = 0

    expected_spokes = convertPatternToPoints(pattern, side_spoke_length)

    match_score = matchWheels(expected_spokes, spoke_points)

    return match_score


def matchWheels(pattern_wheel, seen_wheel):
    """

    :param pattern_wheel:
    :param seen_wheel:
    :return:
    """

    if len(pattern_wheel) < 1 or len(seen_wheel) < 1:
        return math.inf

    # Use the first spoke of the smaller wheel as the angle reference
    ref_spoke = pattern_wheel[0]

    best_match_score = math.inf

    # For each spoke in the larger wheel
    for seen_spoke in seen_wheel:

        # Get the angle difference between the spoke and the reference spoke
        phase = seen_spoke[1] - ref_spoke[1]
        angle_diff_sum = 0

        # Make a copy of the larger wheel and rotate it
        # to align the selected spoke with the smaller wheel's reference spoke
        seen_wheel_copy = seen_wheel.copy()
        for j in range(len(seen_wheel_copy)):
            seen_wheel_copy[j] = seen_wheel_copy[j][0], seen_wheel_copy[j][1] - phase

        # Normalize all the angles of the spokes to [0, 360)
        seen_wheel_copy = normalizeAngles(seen_wheel_copy)

        # Try and match each spoke in the pattern wheel
        for pattern_wheel_spoke in pattern_wheel:
            matching_spoke_idx = -1
            min_angle_diff = math.inf

            # Find the spoke in the seen wheel that has the closest angle to the selected pattern spoke
            for j in range(len(seen_wheel_copy)):
                seen_wheel_copy_spoke = seen_wheel_copy[j]
                angle_diff = abs(seen_wheel_copy_spoke[1] - pattern_wheel_spoke[1])

                if angle_diff < min_angle_diff:
                    matching_spoke_idx = j
                    min_angle_diff = angle_diff

            best_match_spoke = seen_wheel_copy.pop(matching_spoke_idx)

            angle_diff_sum += min_angle_diff

        # The match score is the average angle error per spoke
        match_score = angle_diff_sum / len(pattern_wheel)

        if match_score < best_match_score:
            best_match_score = match_score

    return best_match_score


def normalizeAngles(polar_points):
    """
    Given a list of 2D points in polar coordinates, normalize their angles to [0, 360)
    :param polar_points:    The list of points to normalize
    :return:                The list of points with normalized angles
    """

    normalized_points = []
    for point in polar_points:
        new_point = point[0], point[1] % 360
        normalized_points.append(new_point)

    return normalized_points


def convertPatternToPoints(pattern, distance):
    """
    Convert a pattern into a set of points given the expected distance between points.
    :param pattern:         A 3x3 2D list of bits representing the presence of a point at that location
    :param distance:        The distance between any two horizontally or vertically adjacent points
    :return:                A list of points in polar form representing the outside points in the pattern.
    """

    # Make a copy of the pattern with the center point empty to represent only the outside points of the pattern
    pattern_points = pattern.copy()
    pattern_points[1][1] = 0

    expectedPoints = []

    for row_idx in range(len(pattern_points)):
        row = pattern_points[row_idx]
        for spoke_idx in range(len(row)):

            # If there is a 1 in the spoke's position in the pattern list, there should be a spoke there
            # Calculate the spoke point's expected position
            if row[spoke_idx] > 0:

                # Use the row and column indices to calculate the angle of the point and normalize it to [0, 360)
                angle = math.degrees(math.atan2(1 - row_idx, spoke_idx - 1)) % 360
                radius = distance

                # If the point is diagonal, its angle modulo 90 degrees will be ~45, as opposed to 0
                # The length of a diagonal spoke should be multiplied by the square root of 2, ~1.414
                if abs(angle % 90) > 1:
                    radius *= 1.414

                expectedPoints.append((radius, angle))

    # Sort the points by angle for convenience to the user
    expectedPoints.sort(key=lambda x: x[1])
    return expectedPoints


def angleDiff(point1, point2):
    """
    Return the difference in angle between two points in polar form.
    :param point1:          The first point
    :param point2:          The second point
    :return:                The angle between the points as measured from the origin
    """
    return abs(point1[1] - point2[1])


def cartesianToPolarList(points, origin_point):
    """
    Convert a list of 2D Cartesian points to polar form.
    :param points:          The list of 2D Cartesian points
    :param origin_point:    The point to use as the origin of the polar coordinate system
    :return:                The list of converted points in polar form
    """

    polar_points = []
    for point in points:

        # Get the displacement vector of the point from the origin and convert it to polar
        relative_point = displacement(origin_point, point)
        polar_point = cartesianToPolar(relative_point)
        polar_points.append(polar_point)

    return polar_points


def displacement(ref_point, point):
    """
    Get the rectangular displacement vector between a point and a reference point.
    The two points must be expressed in the same Cartesian coordinate system with the same origin.
    :param ref_point:       The reference point from which the displacement vector points
    :param point:           The point to which the displacement vector points
    :return:                The displacement vector between the two points
    """

    return point[0] - ref_point[0], point[1] - ref_point[1]


def distance(point1, point2):
    """
    Get the distance between two Cartesian points.
    :param point1:          The first point
    :param point2:          The second point
    :return:                The distance between the two points
    """

    radius, _ = cartesianToPolar(displacement(point1, point2))
    return radius

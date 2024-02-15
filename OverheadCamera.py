import math

# Camera field of view in degrees
FOV_HORIZONTAL = 65
FOV_VERTICAL = 37

# Field size in feet
FIELD_LENGTH = 90
FIELD_WIDTH = 46


class OverheadCamera:

    def __init__(self, image_size, midfield_offset, sideline_offset, height):
        self.image_size = image_size

        self.x_offset = midfield_offset
        self.y_offset = -sideline_offset
        self.z_offset = height

    def pixels_to_spherical(self, x, y):
        # phi indicates a horizontal angle from the x axis
        # theta indicates the angle from the vertical, with 0 degrees pointing straight up
        phi_cam = 90        # 90 degree is a baseline but will be procedurally changed later
        theta_cam = 135     # 90 degree means the camera is pointed horizontally

        phi = phi_cam + FOV_HORIZONTAL * (0.5 - x / self.image_size[0])
        theta = theta_cam + FOV_VERTICAL * (y / self.image_size[1] - 0.5)
        radius = -self.z_offset / math.cos(theta * math.pi / 180)

        spherical_point = (radius, theta, phi)

        return spherical_point

    def spherical_to_cartesian(self, spherical_point):
        z = -self.z_offset
        radius, theta, phi = spherical_point
        x = radius * math.sin(theta * math.pi / 180) * math.cos(phi * math.pi / 180) + FIELD_LENGTH / 2 - self.x_offset
        y = radius * math.sin(theta * math.pi / 180) * math.sin(phi * math.pi / 180) + self.y_offset

        cartesian_point = (x, y, z)

        return cartesian_point

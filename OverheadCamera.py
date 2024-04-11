import math

# Field size in feet
FIELD_LENGTH = 90
FIELD_WIDTH = 46


class OverheadCamera:

    def __init__(self, field_of_view, phi, image_size, midfield_offset, sideline_offset, height):
        self.field_of_view = field_of_view

        self.image_size = image_size

        self.x_offset = midfield_offset
        self.y_offset = -sideline_offset
        self.z_offset = height

        # Calculate the vertical angle (theta) and horizontal angle (phi) of the center of the camera's view
        max_y = sideline_offset + FIELD_WIDTH
        vert_fov_max = math.atan(max_y/height)
        self.cam_theta = 180 - vert_fov_max + (self.field_of_view[1] / 2)
        self.cam_phi = phi

    def pixelsToSpherical(self, x, y):
        # phi indicates a horizontal angle from the x axis
        # theta indicates the angle from the vertical, with 0 degrees pointing straight up

        phi = self.cam_phi + self.field_of_view[0] * (0.5 - x / self.image_size[0])
        theta = self.cam_theta + self.field_of_view[1] * (y / self.image_size[1] - 0.5)
        radius = -self.z_offset / math.cos(theta * math.pi / 180)

        spherical_point = (radius, theta, phi)

        return spherical_point

    def sphericalToCartesian(self, spherical_point):
        z = -self.z_offset
        radius, theta, phi = spherical_point
        x = radius * math.sin(theta * math.pi / 180) * math.cos(phi * math.pi / 180) + FIELD_LENGTH / 2 - self.x_offset
        y = radius * math.sin(theta * math.pi / 180) * math.sin(phi * math.pi / 180) + self.y_offset

        cartesian_point = (x, y, z)

        return cartesian_point

    def pixelsToCartesian(self, x, y):
        return self.sphericalToCartesian(self.pixelsToSpherical(x, y))

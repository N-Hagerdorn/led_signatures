import math




class OverheadCamera:

    # Field size in feet
    FIELD_LENGTH = 90
    FIELD_WIDTH = 46

    def __init__(self, field_of_view, phi, image_size, midfield_offset, sideline_offset, height, bot_height):
        """
        Initialize the overhead camera with geometric parameters.
        All distance parameters must be measured in feet and angle parameters in degrees.

        :param field_of_view:       A tuple representing the horizontal and vertical fields of view of the camera in degrees
        :param phi:                 The angle between the camera's line of sight and the sideline
        :param image_size:          The resolution of the images being captured by the camera
        :param midfield_offset:     The distance between the camera and the midfield line along the sideline axis
        :param sideline_offset:     The distance between the camera and the sideline
        :param height:              The height of the camera above the field
        :param bot_height           The height of the robots being detected by the camera
        """
        self.field_of_view = field_of_view

        self.image_size = image_size

        self.x_offset = midfield_offset
        self.y_offset = -sideline_offset
        self.z_offset = height - bot_height

        # Calculate the vertical angle (theta) and horizontal angle (phi) of the center of the camera's view
        max_y = sideline_offset + OverheadCamera.FIELD_WIDTH
        vert_fov_max = math.degrees(math.atan(max_y/height))
        self.cam_theta = 180 - vert_fov_max + (self.field_of_view[1] / 2)
        self.cam_phi = phi

    def pixelsToSpherical(self, x, y):
        # phi indicates a horizontal angle from the x axis
        # theta indicates the angle from the vertical, with 0 degrees pointing straight up

        # Find the distance in pixels from the point to the vertical centerline
        delta_x = self.image_size[0] / 2 - x

        '''
        Fisheye lens correction
        The fisheye effect of the RPi camera (Arducam B0449) causes the vertical (y) pixel to not correspond linearly
        to the theta angle. Through testing, a factor of -0.0021 times the square of the horizontal distance from center
        was found to correct the y-theta relationship back to linearity.
        '''
        corrected_y = y - 0.00021 * math.pow(delta_x, 2)
        delta_y = corrected_y - self.image_size[1] / 2

        phi = self.cam_phi + self.field_of_view[0] * delta_x / self.image_size[0]
        theta = self.cam_theta + self.field_of_view[1] * delta_y / self.image_size[1]
        radius = -self.z_offset / math.cos(theta * math.pi / 180)

        spherical_point = (radius, theta, phi)

        return spherical_point

    def sphericalToCartesian(self, spherical_point):
        z = -self.z_offset
        radius, theta, phi = spherical_point
        x = radius * math.sin(theta * math.pi / 180) * math.cos(phi * math.pi / 180) + OverheadCamera.FIELD_LENGTH / 2 - self.x_offset
        y = radius * math.sin(theta * math.pi / 180) * math.sin(phi * math.pi / 180) + self.y_offset

        cartesian_point = (x, y, z)

        return cartesian_point

    def pixelsToCartesian(self, x, y):
        return self.sphericalToCartesian(self.pixelsToSpherical(x, y))

    def cartesianToSpherical(self, cartesian_point):
        x, y = cartesian_point
        x = x - OverheadCamera.FIELD_LENGTH / 2 + self.x_offset
        y = y - self.y_offset
        z = -self.z_offset
        r = math.sqrt(x * x + y * y + z * z)
        phi = math.acos(x / math.sqrt(x * x + y * y)) * 180 / math.pi
        theta = 180 + math.atan(math.sqrt(x * x + y * y) / z) * 180 / math.pi

        spherical_point = (r, theta, phi)
        return spherical_point

    def sphericalToPixels(self, spherical_point):
        r, theta, phi = spherical_point

        x = self.image_size[0] * (0.5 - (phi - self.cam_phi) / self.field_of_view[0])
        # phi = self.cam_phi + self.field_of_view[0] * (0.5 - x / self.image_size[0])

        y = self.image_size[1] * (0.5 + (theta - self.cam_theta) / self.field_of_view[1])
        # theta = self.cam_theta + self.field_of_view[1] * (y / self.image_size[1] - 0.5)
        # radius = -self.z_offset / math.cos(theta * math.pi / 180)

        screen_point = (x, y)

        return screen_point

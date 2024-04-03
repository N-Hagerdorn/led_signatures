import cv2
import numpy as np
import socket, select, time

import botDetector, botPatterns
from OverheadCamera import OverheadCamera as oc
from botDetector import *

# Run parameters
RUN_SERVER = False   # Set to True to run the server communication with the GUI client
IS_RPI = False       # Set to True for the Raspberry Pi, False for a Windows computer (for testing only)


#  Define a function to perform the contour detection
def get_all_contours(grayscale_img):
    canny = cv2.Canny(grayscale_img, 50, 240)
    contours, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return contours


CAM_WIDTH = 4656 # Width of the camera frame in pixels
CAM_HEIGHT = 3496 # Height of the camera frame in pixels
CAM_FOV_WIDTH = 120 # Width of the camera frame in degrees, also called horizontal field of view
CAM_FOV_HEIGHT = 95 # Height of the camera frame in degrees, also called vertical field of view

# Define the overhead camera object that performs coordinate transformations
cam = oc(image_size=(CAM_WIDTH, CAM_HEIGHT), midfield_offset=0, sideline_offset=6 + 8/12, height=217/12)

# Configure the camera
if IS_RPI:
    # Pi-only module for operating the camera
    # picamera2 does not need to be installed to run on a non-RPi system
    from picamera2 import Picamera2

    # Set up the Raspberry Pi webcam
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={'format': 'XRGB8888', 'size': (CAM_WIDTH, CAM_HEIGHT)}))
    
    picam2.start()
    print('Configuring exposure...')
    exposure = picam2.capture_metadata()['ExposureTime']
    print(exposure)

    exposure_dimming = 5 # Higher dimming makes for a dimmer picture.
    
    picam2.stop()
    picam2.set_controls({'ExposureTime': int(exposure / exposure_dimming)})
    
    picam2.start()
else:

    # Set up the default Windows webcam
    vid = cv2.VideoCapture(0)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    #vid.set(cv2.CAP_PROP_FPS, 2)
    vid.set(cv2.CAP_PROP_EXPOSURE, -8)#-8)

    if not vid.isOpened():
        print('Cannot open camera...')
        exit()

if RUN_SERVER:
    print('Starting server...')
    host = socket.gethostname()
    print(host)
    port = 5000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

while True:

    # Capture video from the webcam
    if IS_RPI:
        frame = picam2.capture_array()
    else:
        _, frame = vid.read()

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Identify bright spots in the image, such as LEDs and put them in a binary image
    _, binary_m = cv2.threshold(gray_frame, 230, 255, cv2.THRESH_BINARY)

    # Get all contours (boundaries of the white spots) in the binary image
    contours = get_all_contours(binary_m)

    # Get a list of the center points of all LEDs
    LEDs = []

    # Print each contour on the original frame
    for contour in contours:

        M = cv2.moments(contour)
        if M["m00"] != 0 and cv2.contourArea(contour) > 1:

            # Draw the contour
            cv2.drawContours(frame, [contour], -1, (255, 255, 0), 3)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 4, (0, 255, 255), -1)

            radius, theta, phi = cam.pixels_to_spherical(cX, cY)
            x, y, z = cam.spherical_to_cartesian((radius, theta, phi))

            LEDs.append((x, y))
            cv2.putText(frame, 'LED position: {:.2f}, {:.2f}'.format(x, y), (cX, cY), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)

    groups = botDetector.groupNearbyPoints(LEDs, 1)
    X = []
    for group in groups:

        if len(group) < 1:
            continue

        score = botDetector.detectShape(group, botPatterns.getPattern('X'))
        if score < math.inf:

            print('Matching score: ' + str(score))

    LEDs = X

    # If the server is running, transmit the points to the client
    if RUN_SERVER:

        # Split the list of captured LEDs into transmissible chunks
        split_LEDs = [LEDs[i:i+50] for i in range(0, len(LEDs), 50)]
        LEDs = []

        num_packets = len(split_LEDs)
        print("Num packets: " + str(num_packets))
        data = ''

        timeout = 10  # in seconds

        for i in range(num_packets):

            ready_sockets, _, _ = select.select(
                [conn], [], [], timeout
            )
            if ready_sockets:
                response = conn.recv(256).decode()
                if response != 'OK':
                    print('Bad response from client')
                    break

            else:
                print('No response')
                break

            data = '['
            for point in split_LEDs[i]:
                formatted_point = '({X:.2f}, {Y:.2f})'.format(X=point[0], Y=point[1])
                data += formatted_point + ', '

            data = data[0:-2] + ']'

            print('Sending ' + data)
            conn.send(data.encode())

        ready_sockets, _, _ = select.select(
            [conn], [], [], timeout
        )
        if ready_sockets:
            response = conn.recv(256).decode()
            if response != 'OK':
                print('Bad response from client')
                break
            print(response)
        else:
            print('No response')
            break

        data = 'EOT'
        conn.send(data.encode())

    cv2.imshow('frame', frame)


if RUN_SERVER:
    # Close the TCP socket
    conn.close()

    print('TCP socket closed...')

# Destroy all the windows
cv2.destroyAllWindows()

# After the loop release the cap object
vid.release()
# After the loop release the cap object
vid.release()

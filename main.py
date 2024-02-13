import cv2
import numpy as np
from OverheadCamera import OverheadCamera as oc


#  Define a function to perform the contour detection
def get_all_contours(grayscale_img):
    canny = cv2.Canny(grayscale_img, 50, 240)
    contours, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return contours


CAM_WIDTH = 1280
CAM_HEIGHT = 720

# Define the overhead camera object that performs coordinate transformations
cam = oc(image_size=(CAM_WIDTH, CAM_HEIGHT), midfield_offset=0, sideline_offset=2, height=3.5)

# Configure the camera
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
vid.set(cv2.CAP_PROP_FPS, 2)
vid.set(cv2.CAP_PROP_EXPOSURE, -8)

while True:

    # Capture video from the webcam
    ret, frame = vid.read()

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Identify bright spots in the image, such as LEDs and put them in a binary image
    thresh, binary_m = cv2.threshold(gray_frame, 230, 255, cv2.THRESH_BINARY)

    # Get all contours (boundaries of the white spots) in the binary image
    contours = get_all_contours(binary_m)

    # Try to identify circles in the image. This doesn't work very well
    circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1, 20, param1=100, param2=15, minRadius=0, maxRadius=40)

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
            LEDs.append((cX, cY))
            cv2.circle(frame, (cX, cY), 4, (0, 255, 0), -1)

            radius, theta, phi = cam.pixels_to_spherical(cX, cY)
            x, y, z = cam.spherical_to_cartesian((radius, theta, phi))

            cv2.putText(frame, 'LED position: ' + str(x) + ', ' + str(y), (cX, cY), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)


    # Draw all circles
    if circles is not None:

        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            center = (i[0], i[1])
            # circle center
            cv2.circle(frame, center, 1, (0, 100, 100), 3)
            # circle outline
            radius = i[2]
            cv2.circle(frame, center, radius, (255, 0, 255), 3)

    else:
        print('No circles')

    cv2.imshow('frame', frame)

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

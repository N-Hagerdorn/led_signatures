import cv2
import numpy as np


def calculate_contour_distance(contour1, contour2):
    x1, y1, w1, h1 = cv2.boundingRect(contour1)
    c_x1 = x1 + w1/2
    c_y1 = y1 + h1/2

    x2, y2, w2, h2 = cv2.boundingRect(contour2)
    c_x2 = x2 + w2/2
    c_y2 = y2 + h2/2

    return max(abs(c_x1 - c_x2) - (w1 + w2)/2, abs(c_y1 - c_y2) - (h1 + h2)/2)

def merge_contours(contour1, contour2):
    return np.concatenate((contour1, contour2), axis=0)

def agglomerative_cluster(contours, threshold_distance=40.0):
    current_contours = contours
    while len(current_contours) > 1:
        min_distance = None
        min_coordinate = None

        for x in range(len(current_contours)-1):
            for y in range(x+1, len(current_contours)):
                distance = calculate_contour_distance(current_contours[x], current_contours[y])
                if min_distance is None:
                    min_distance = distance
                    min_coordinate = (x, y)
                elif distance < min_distance:
                    min_distance = distance
                    min_coordinate = (x, y)

        if min_distance < threshold_distance:
            index1, index2 = min_coordinate
            current_contours[index1] = merge_contours(current_contours[index1], current_contours[index2])
            del current_contours[index2]
        else:
            break

    return current_contours



#  Define a function to perform the contour detection
def get_all_contours(img):
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(img, 50, 240)
    contours, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return contours


# define a video capture

vid = cv2.VideoCapture(0)
#vid.set(cv2.CAP_PROP_BRIGHTNESS, 0)

vid.set(cv2.CAP_PROP_EXPOSURE, -8)
#vid.set(cv2.CAP_PROP_GAIN, -1)

while (True):

    # Capture the video frame
    # by frame
    ret, frame = vid.read()

    # Display the resulting frame
    #cv2.imshow('frame', frame)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    lower = np.array([0, 0, 250])
    upper = np.array([180, 255, 255])

    # cv2.inRange() returns a binary matrix, the element of which is 1 where the pixels values are between the lower and upper limits and 0 otherwise.
    binary_m = cv2.inRange(hsv_frame, lower, upper)

    thresh, binary_m = cv2.threshold(grey_frame, 240, 255, cv2.THRESH_BINARY)

    # The operation of "and" will be performed only if mask[i] doesn't equal zero
    res = cv2.bitwise_and(frame, frame, mask=binary_m)

    # Erode and dilate remove small spots of noise from the image
    thresh = cv2.erode(binary_m, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    # We actually want to isolate the "noise" as this contains our LEDs, so an XOR removes all but the noise
    bitwiseXor = cv2.bitwise_xor(binary_m, thresh)
    gray = cv2.blur(bitwiseXor, (1, 1))

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 2, 0.01, param1=200, param2=15, maxRadius=4)
    contours = get_all_contours(gray)

    #cv2.drawContours(frame, contours, -1, (255, 255, 0), 3)
    print(len(contours))

    #contours = agglomerative_cluster(contours)

    for contour in contours:

        M = cv2.moments(contour)
        if M["m00"] != 0 and cv2.contourArea(contour) > 1:
            cv2.drawContours(frame, [contour], -1, (255, 255, 0), 3)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 4, (0, 255, 0), -1)

            cv2.putText(frame, 'LED position: ' + str(cX) + ', ' + str(cY), (cX, cY), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2, cv2.LINE_AA)


    # draw all contours that look like green circles
    '''if circles is not None:

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
'''

    #for contour in contours_yellow:
    #    cv2.drawContours(res_yellow, contour, -1, (255, 255, 0), thickness=5)
    cv2.imshow('frame', frame)
    #cv2.imshow('frame', bitwiseXor)

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

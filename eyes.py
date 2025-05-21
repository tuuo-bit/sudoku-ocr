from imutils.perspective import four_point_transform
from skimage.segmentation import clear_border
import numpy as np
import imutils
import cv2
import time

def find_puzzle( img, debug = False):
    gray = cv2.cvtColor( img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur( gray, (7,7), 3)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.bitwise_not(thresh)
    if debug:
        cv2.imshow("Puzzle Thresh", thresh)
        cv2.waitKey(0)
    # find contours in the thresholded image and sort them by size in
	# descending order
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	    cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
	# initialize a contour that corresponds to the puzzle outline
    puzzleCnt = None
	# loop over the contours
    for c in cnts:
		# approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
		# if our approximated contour has four points, then we can
		# assume we have found the outline of the puzzle
        if len(approx) == 4:
            puzzleCnt = approx
            break
    if puzzleCnt is None:
        raise Exception(("Could not find Sudoku puzzle outline. "
			"Try debugging your thresholding and contour steps."))
	# check to see if we are visualizing the outline of the detected
	# Sudoku puzzle
    if debug:
		# draw the contour of the puzzle on the image and then display
		# it to our screen for visualization/debugging purposes
        output = img.copy()
        cv2.drawContours(output, [puzzleCnt], -1, (0, 255, 0), 2)
        cv2.imshow("Puzzle Outline", output)
        cv2.waitKey(0)
    puzzle = four_point_transform( img, puzzleCnt.reshape(4,2))
    warped = four_point_transform( gray, puzzleCnt.reshape(4,2))
    if debug:
		# show the output warped image (again, for debugging purposes)
        cv2.imshow("Puzzle Transform", puzzle)
        cv2.imshow( "Transform", warped)
        cv2.waitKey(0)
	# return a 2-tuple of puzzle in both RGB and grayscale
    return (puzzle, warped)

def extract_digit( cell, debug = False):
    thresh = cv2.threshold( cell, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    thresh = clear_border( thresh)
    if debug:
        cv2.imshow( "Cell Thresh", thresh)
        cv2.waitKey(0)
    cnts = cv2.findContours( thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours( cnts)
    if len( cnts) == 0:
        return None
    c = max( cnts, key = cv2.contourArea)
    mask = np.zeros( thresh.shape, dtype = "uint8")
    cv2.drawContours( mask, [c], -1, 255, -1)
    h,w = thresh.shape
    percentFilled = cv2.countNonZero( mask)/float( w*h)
    if percentFilled < 0.03:
        return None
    digit = cv2.bitwise_and( thresh, thresh, mask = mask)
    if debug:
        cv2.imshow( "Digit", digit)
        cv2.waitKey(0)
    return digit


def capture_puzzle():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print( "Error Opening Camera")
        return
    cv2.namedWindow( "Webcam")
    clicked = False
    def click_event( event, x, y, flags, params):
        nonlocal clicked
        if event == cv2.EVENT_LBUTTONDOWN:
            clicked = True
    cv2.setMouseCallback( "Webcam", click_event)
    frame = None
    while True:
        ret,frame = cap.read()
        if not ret:
            print( "Error Capturing Frame")
            return
        cv2.imshow( "Webcam", frame)
        if clicked:
            timestamp = str( int( round( time.time() * 1000)))
            cv2.imwrite( f"imaje_{timestamp}.jpg", frame)
            print( "Captured!")
            clicked = False
            break
        # q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    return frame

# capture_puzzle()
# find_puzzle( capture_puzzle(), True)
# find_puzzle( cv2.imread( "imaje_1743324224384.jpg"), True)
# find_puzzle( cv2.imread( "test.jpg"), True)
# find_puzzle( cv2.imread( "sample.jpeg"), True)
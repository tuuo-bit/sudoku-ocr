from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from brain import parse, solve_puzzle
from eyes import capture_puzzle, find_puzzle, extract_digit
import numpy as np
import cv2
import os
import time
import imutils

class sudoku:
    
    def __init__( s):
        s.model = load_model( "digit_classifier.h5")
        s.base_url = "firmware\\RPI3"
        s.message_from_proteus = "solveButtonPressed.txt"
        s.message_to_proteus = "imageModified.txt"
        print( "~ Sudoku class initialized")

    def getImage( s):
        # image = cv2.imread( "samples\\sample.jpeg")
        # corrections 1 5 4 1 7 2 2 3 9 3 2 7 4 0 9 4 2 1 5 2 6 6 4 9 6 5 7 6 7 5 6 8 2 7 3 5 7 4 8
        # image = capture_puzzle()
        while s.message_from_proteus not in os.listdir( s.base_url):
            print( "~ Awaiting message file")
            time.sleep(5)
        print( "~ Message recieved, proceeding")
        s.filename = sorted( [ filename[:-4] for filename in os.listdir( s.base_url) if filename[-3:] == "jpg"])[-1]
        print( f"Last Image name: {s.filename}")
        image = cv2.imread( s.base_url + "\\" + s.filename + ".jpg")
        image = imutils.resize( image, width = 600)
        s.puzzleImage, s.warped = find_puzzle( image, False)
        print( "~Getting the image")
    
    def buildBoard( s):
        s.board = np.zeros( (9,9), dtype="int")
        stepX = s.warped.shape[1]//9
        stepY = s.warped.shape[0]//9
        s.cellLocs = []
        for y in range( 0, 9):
            row = []
            for x in range( 0, 9):
                startX = x*stepX
                startY = y*stepY
                endX = (x+1)*stepX
                endY = (y+1)*stepY
                row.append((startX,startY,endX,endY))
                cell = s.warped[ startY:endY, startX:endX]
                digit = extract_digit( cell, debug = False)
                if digit is not None:
                    roi = cv2.resize( digit, (28, 28))
                    roi = roi.astype( "float")/ 255.0
                    roi = img_to_array( roi)
                    roi = np.expand_dims( roi, axis=0)
                    pred = s.model.predict( roi, verbose = 0).argmax( axis=1)[0]
                    s.board[y,x] = pred
                    # cv2.imshow( "digit", roi)
                    # cv2.waitKey(0)
            s.cellLocs.append( row)
        print( "~ Building the board")
        return None
    
    def makeChanges( s):
        print( f"\nBoard:\n{s.board}\n")
        doesUserWantToMakeChanges = True
        temp_board = s.board.copy()
        s.changesMade = []
        while doesUserWantToMakeChanges:
            print( f"Make Changes, list of 'row col newVal', else 'enter'")
            coords = np.array( list( map( int, input().split()))).reshape( -1, 3)
            for coord in coords:
                row,col,val = coord
                s.changesMade.append( [ row,col,val])
                print( f"{row, col}: {temp_board[row,col]} -> {val}")
                temp_board[row,col] = val
            print(f"Any more changes? Enter y/n")
            doesUserWantToMakeChanges = bool( input() == "y")
        s.board = temp_board
        print( f"\nCorrected board:\n{ s.board}\n")
        return None

    def solveBoard( s):
        s.board1D = "".join( "".join(row) for row in s.board.astype("str"))
        s.solvedBoard1D = solve_puzzle( parse( s.board1D), False)
        s.solvedBoard = np.array( list( int(ch) for ch in s.solvedBoard1D)).reshape( 9,9)
        print( "~ Solving the puzzle")
        return None

    def createSolution( s):
        print( "~ Making the final image")
        for (cellRow, boardRow) in zip( s.cellLocs, s.solvedBoard):
            for (box, digit) in zip(cellRow, boardRow):
                startX, startY, endX, endY = box
                textX = int((endX - startX) * 0.33)
                textY = int((endY - startY) * -0.2)
                textX += startX
                textY += endY
                cv2.putText( s.puzzleImage, str(digit), (textX, textY),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 3)
        # show the output image
        # cv2.imshow("Sudoku Result", s.puzzleImage)
        # timestamp = "_".join( [ str(v) if i < 1 or v > 9 else f"0{v}" for i,v in enumerate( time.localtime()[:6])])
        # cv2.imwrite( f"{timestamp}.jpg", s.puzzleImage)
        # cv2.waitKey(0)
        cv2.imwrite( s.base_url + "\\" + s.filename + ".jpg", s.puzzleImage)
        time.sleep(1)
        acknowledge = open( s.base_url + "\\" + s.message_to_proteus, "x")
        acknowledge.close()
        print( "~ Solution is here!")
    
    def summary( s):
        print( s.board)
        print( s.board1D)
        print( s.solvedBoard)
        print( s.solvedBoard1D)
        print( s.changesMade)
        
sdk = sudoku()
sdk.getImage()
sdk.buildBoard()
sdk.makeChanges()
sdk.solveBoard()
sdk.createSolution()
# sdk.summary()
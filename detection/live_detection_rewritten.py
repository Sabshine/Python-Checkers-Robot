import cv2 as cv
import copy
import itertools   
import math

# BEGIN GAME
firstCheck = True

# CHECKER PIECES VARIABLES
oldWhitePieces = []  # [{'cv':[x,y], 'ai':[row,col]}, {...}]
whitePieces = [] # [{'cv':[x,y], 'ai':[row,col]}, {...}]
blockDistance = 0 # calculated with 5x - 7x: Outcome (if positive) is block FORWARD (to the right when looking at stream)


def startVideoCapture():
    cap = cv.VideoCapture(0);
    if cap.isOpened():
        while True:
            ret, frame = cap.read()

            cv.imshow('frame', frame)

            # Start detecting current state of checkers pieces on 's' input
            # Can be changed to player/start button
            if cv.waitKey(1) == ord('s'):
                # Recognises all white pieces. Best for testing new functions
                img = cv.imread("img/movement1/board-pieces-1.png")
                img = cv.resize(img, (640, 480))

                img1 = cv.imread("img/movement1/board-pieces-2.png")
                img1 = cv.resize(img1, (640, 480))

                # When checking new state safe old state
                global oldWhitePieces
                global whitePieces
                global firstCheck
                global blockDistance

                #TODO: Test firstcheck live
                if len(whitePieces) != 12 and firstCheck:
                    whitePieces = []
                    currentWhitePieces, calculatedBlockDistance = detectWhitePiecesOnBoard(img, firstCheck) # Pass 'frame' for live detection
                    whitePieces = copy.deepcopy(currentWhitePieces)
                    blockDistance = copy.deepcopy(calculatedBlockDistance)

                    print("===================OLD===================")
                    print(oldWhitePieces)
                    print("===================NEW===================")
                    print(whitePieces)

                    if len(whitePieces) == 12:
                        firstCheck = False
                    
                elif firstCheck == False:
                    oldWhitePieces = copy.deepcopy(whitePieces)
                    whitePieces = []
                    currentWhitePieces, distanceNone = detectWhitePiecesOnBoard(img1, firstCheck) # detect white pieces and then assign x,y and row,col
                    whitePieces = copy.deepcopy(currentWhitePieces)
                    newRowCol = calculateNewPosition(oldWhitePieces, whitePieces, blockDistance) # detect movement, calculate new position
                    whitePieces[detectMovement(whitePieces, oldWhitePieces, False)]['ai'] = newRowCol

                    print("===================OLD===================")
                    print(oldWhitePieces)
                    print("===================NEW===================")
                    print(whitePieces)

                #TODO: Connection with AI
                #TODO: Send movement to AI

            if cv.waitKey(1) == ord('q'):
                break

    cap.release()
    cv.destroyAllWindows()


def detectWhitePiecesOnBoard(frame, firstCheck):
    currentStateImg = frame.copy()
    # cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
    # Load frame, grayscale, median blur, Otsus threshold
    gray = cv.cvtColor(currentStateImg, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    blur = cv.medianBlur(blur, 5)
    # thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv.THRESH_BINARY, 3, 2)

    # Morph open 
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=3)

    currentWhitePieces = []
    # Find contours and filter using contour area and aspect ratio
    cnts = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.04 * peri, True)
        area = cv.contourArea(c)
        if len(approx) > 5 and area > 1000 and area < 1800:
            ((x, y), r) = cv.minEnclosingCircle(c)

            currentWhitePieces.append({'cv':[int(x),int(y)], 'ai':[]})

            # Debug feedback x y
            # cv.circle(currentStateImg, (int(x), int(y)), int(r), (0, 0, 255), 2)
            # cv.putText(currentStateImg, "x: " + str(round(x)), (int(x), int(y)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
            # cv.putText(currentStateImg, "y: " + str(round(y)), (int(x), (int(y)+10)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
    
    whitePieces, blockDistance = sortWhitePieces(currentWhitePieces, firstCheck)

    # # Debug feedback rows cols
    # rowColImg = frame.copy()
    # if len(whitePieces[0]['ai']) > 0: # If row and cols aren't empty
    #     for x in range(len(whitePieces)):
    #         cv.putText(rowColImg, "row: " + str(whitePieces[x]['ai'][0]), (int(whitePieces[x]['cv'][0]), int(whitePieces[x]['cv'][1])), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
    #         cv.putText(rowColImg, "col: " +  str(whitePieces[x]['ai'][1]), (int(whitePieces[x]['cv'][0]), (int(whitePieces[x]['cv'][1])+10)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)

    # cv.imshow('Current state', currentStateImg)
    # cv.imshow('Row Col', rowColImg)

    return whitePieces, blockDistance


def sortWhitePieces(whitePieces, firstCheck):
    # Sort all X from low to high
    xSorted = sorted(whitePieces, key=lambda k : k['cv'][0]) 

    if firstCheck:
        for x in range(len(xSorted)):
            if x < 4:
                xSorted[x]['ai'].append(7)
            elif x > 3 and x < 8:
                xSorted[x]['ai'].append(6)
            else:
                xSorted[x]['ai'].append(5)

    # Sort all Y from low to high
    ySorted = sorted(xSorted, key=lambda k : k['cv'][1]) 
    
    blockDistance = None
    if firstCheck:
        counter = 0
        yVal = 0
        for x in range(len(ySorted)):
            if (counter == 0) or (counter == 1):
                counter += 1
                ySorted[x]['ai'].append(yVal) # Row 5 7, y = 0, 2, 4, 6
            else:
                yVal += 2
                ySorted[x]['ai'].append(yVal-1) # Row 6, y = 1, 3, 5, 7
                counter = 0
        
        blockDistance = int((ySorted[0]['cv'][0] - ySorted[1]['cv'][0])/2)

    return ySorted, blockDistance
    # See sorted checker pieces dict WITH x,y and row,col
    # print("===================")
    # print("Sorted checker pieces. Only receives AI rows and cols when it's the first check...")
    # print(whitePieces)


def grouper(n, iterable):
    it = iter(iterable)
    while True:
       chunk = tuple(itertools.islice(it, n))
       if not chunk:
           return
       yield chunk


def detectMovement(pieces_list1, pieces_list2, repopulate):
    temp = []
    check = []
    for i in pieces_list1:
        x = i['cv'][0]
        y = i['cv'][1]
        if repopulate:
            xAi = i['ai'][0]
            yAi = i['ai'][1]
        for j in pieces_list2:
            x2 = j['cv'][0]
            y2 = j['cv'][1]
            
            if x in range(x2-5, x2+5) and y in range(y2-5, y2+5):
                temp.append(1)
                if repopulate:
                    j['ai'].append(xAi)
                    j['ai'].append(yAi)
            else:
                temp.append(0)
                
    for group in grouper(len(pieces_list1), temp):
        if 1 in group:
            check.append(1)
        else:
            check.append(0)
            
    return check.index(0)


def normalRound(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def calculateNewPosition(oldWhitePieces, whitePieces, blockDistance):
    oldPosition = oldWhitePieces[detectMovement(oldWhitePieces, whitePieces, True)]['cv'] # Just one time repopulate all old AI rows and cols
    newPosition = whitePieces[detectMovement(whitePieces, oldWhitePieces, False)]['cv']
    
    # Calculate how many steps difference between old and new
    stepX = normalRound((newPosition[0] - oldPosition[0]) / blockDistance)
    stepY =  normalRound((newPosition[1] - oldPosition[1]) / blockDistance)

    oldRowCol = oldWhitePieces[detectMovement(oldWhitePieces, whitePieces, False)]['ai']
    newRowCol = []

    # Calculate new row,col
    if stepX < 0:
        newRowCol.append(oldRowCol[0]-abs(stepX))
    else:
        newRowCol.append(oldRowCol[0]+abs(stepX))

    if stepY < 0:
        newRowCol.append(oldRowCol[1]+abs(stepY))
    else:
        newRowCol.append(oldRowCol[1]-abs(stepY))

    print("A piece has moved from  the position: {} to a new position of: {}".format(oldWhitePieces[detectMovement(oldWhitePieces, whitePieces, False)]["cv"], whitePieces[detectMovement(whitePieces, oldWhitePieces, False)]["cv"]))
    print("Old row,col : " + str(oldRowCol))
    print("New row,col : " + str(newRowCol))

    # Add new row,col to current "whitePieces"
    return newRowCol


startVideoCapture()
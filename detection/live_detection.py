import cv2 as cv
import itertools   
import math

def detect_white_pieces_on_board(frame, first_check):
    current_state_img = frame.copy()
    # cv.normalize(frame, frame, 0, 255, cv.NORM_MINMAX)
    # Load frame, grayscale, median blur, Otsus threshold
    gray = cv.cvtColor(current_state_img, cv.COLOR_BGR2GRAY)
    blur = cv.GaussianBlur(gray, (5,5), 0)
    blur = cv.medianBlur(blur, 5)
    # thresh = cv.threshold(blur, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)[1]
    thresh = cv.adaptiveThreshold(blur,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,\
        cv.THRESH_BINARY, 3, 2.6)

    # Morph open 
    kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9,9))
    opening = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel, iterations=3)

    current_white_pieces = []
    # Find contours and filter using contour area and aspect ratio
    cnts = cv.findContours(opening, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.04 * peri, True)
        area = cv.contourArea(c)
        if len(approx) > 5 and area > 800 and area < 1800:
            ((x, y), r) = cv.minEnclosingCircle(c)

            current_white_pieces.append({'cv':[int(x),int(y)], 'ai':[]})

            # Debug feedback x y
            cv.circle(current_state_img, (int(x), int(y)), int(r), (0, 0, 255), 2)
            cv.putText(current_state_img, "x: " + str(round(x)), (int(x), int(y)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
            cv.putText(current_state_img, "y: " + str(round(y)), (int(x), (int(y)+10)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
    
    white_pieces, block_distance = sort_white_pieces(current_white_pieces, first_check)

    # Debug feedback rows cols
    row_col_img = frame.copy()
    if len(white_pieces[0]['ai']) > 0: # If row and cols aren't empty
        for x in range(len(white_pieces)):
            cv.putText(row_col_img, "row: " + str(white_pieces[x]['ai'][0]), (int(white_pieces[x]['cv'][0]), int(white_pieces[x]['cv'][1])), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)
            cv.putText(row_col_img, "col: " +  str(white_pieces[x]['ai'][1]), (int(white_pieces[x]['cv'][0]), (int(white_pieces[x]['cv'][1])+10)), cv.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), int(1), cv.LINE_AA)

    cv.imshow('Current state', current_state_img)
    cv.imshow('Row Col', row_col_img)

    return white_pieces, block_distance


def sort_white_pieces(white_pieces, first_check):
    # Sort all X from low to high
    x_sorted = sorted(white_pieces, key=lambda k : k['cv'][0]) 

    if first_check:
        for x in range(len(x_sorted)):
            if x < 4:
                x_sorted[x]['ai'].append(7)
            elif x > 3 and x < 8:
                x_sorted[x]['ai'].append(6)
            else:
                x_sorted[x]['ai'].append(5)

    # Sort all Y from low to high
    y_sorted = sorted(x_sorted, key=lambda k : k['cv'][1]) 
    
    block_distance = None
    if first_check:
        counter = 0
        y_val = 0
        for x in range(len(y_sorted)):
            if (counter == 0) or (counter == 1):
                counter += 1
                y_sorted[x]['ai'].append(y_val) # Row 5 7, y = 0, 2, 4, 6
            else:
                y_val += 2
                y_sorted[x]['ai'].append(y_val-1) # Row 6, y = 1, 3, 5, 7
                counter = 0
        
        block_distance = int((y_sorted[0]['cv'][0] - y_sorted[1]['cv'][0])/2)

    return y_sorted, block_distance


def grouper(n, iterable, cast_type):
    it = iter(iterable)
    while True:
        if cast_type == "tuple":
            chunk = tuple(itertools.islice(it, n))
        elif cast_type == "list":
            chunk = list(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def detect_movement(pieces_list1, pieces_list2, repopulate):
    temp = []
    check = []
    for i in pieces_list1:
        x = i['cv'][0]
        y = i['cv'][1]
        if repopulate:
            x_ai = i['ai'][0]
            y_ai = i['ai'][1]
        for j in pieces_list2:
            x2 = j['cv'][0]
            y2 = j['cv'][1]
            
            if x in range(x2-5, x2+5) and y in range(y2-5, y2+5):
                temp.append(1)
                if repopulate:
                    j['ai'].append(x_ai)
                    j['ai'].append(y_ai)
            else:
                temp.append(0)
                
    for group in grouper(len(pieces_list1), temp, "tuple"):
        if 1 in group:
            check.append(1)
        else:
            check.append(0)

    if 0 in check:        
        return check.index(0)
    else:
        return None


def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)


def calculate_new_position(old_white_pieces, white_pieces, block_distance):
    old_move = detect_movement(old_white_pieces, white_pieces, True)
    new_move = detect_movement(white_pieces, old_white_pieces, False)
    print(old_move, new_move)

    if old_move != None and new_move != None:
        print("No none received")
        old_position = old_white_pieces[old_move]['cv'] # Just one time repopulate all old AI rows and cols
        new_position = white_pieces[new_move]['cv']
    
        # Calculate how many steps difference between old and new
        step_x = normal_round((new_position[0] - old_position[0]) / block_distance)
        step_y =  normal_round((new_position[1] - old_position[1]) / block_distance)

        old_row_col = old_white_pieces[detect_movement(old_white_pieces, white_pieces, False)]['ai']
        new_row_col = []

        # Calculate new row,col
        if step_x > 0:
            new_row_col.append(old_row_col[0]-abs(step_x))
        else:
            new_row_col.append(old_row_col[0]+abs(step_x))

        if step_y > 0:
            new_row_col.append(old_row_col[1]+abs(step_y))
        else:
            new_row_col.append(old_row_col[1]-abs(step_y))

        print("A piece has moved from  the position: {} to a new position of: {}".format(old_white_pieces[detect_movement(old_white_pieces, white_pieces, False)]["cv"], white_pieces[detect_movement(white_pieces, old_white_pieces, False)]["cv"]))
        print("Old row,col : " + str(old_row_col))
        print("New row,col : " + str(new_row_col))

        # Add new row,col to current "white_pieces"
        return old_row_col, new_row_col
    
    return None, None
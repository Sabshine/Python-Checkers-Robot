# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import pygame
import cv2 as cv
import copy

import checkers
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game_v2 import Game
from checkers.board import Board
from minimax.algorithm import minimax
from detection.live_detection import detect_white_pieces_on_board, calculate_new_position, detect_movement, grouper
from detection.live_detect_pieces import detect_pieces_live

FPS = 60

# BEGIN GAME
first_check = True
move = False
invalid_move = False

# CHECKER PIECES VARIABLES
backup_old_white_pieces = [] # [{'cv':[x,y], 'ai':[row,col]}, {...}]
old_white_pieces = []  # [{'cv':[x,y], 'ai':[row,col]}, {...}]
white_pieces = [] # [{'cv':[x,y], 'ai':[row,col]}, {...}]
block_distance = 0 # calculated with 5x - 7x: Outcome (if positive) is block FORWARD (to the right when looking at stream)


WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def modify_list(modify):
    modified = []
    modified_grouped = []
    
    for row in range(0, 8):
        for col in range(0, 8):
            if isinstance(modify[row][col], checkers.piece.Piece):
                modified.append(modify[row][col].__dict__['color'])
            else:
                modified.append(modify[row][col])
    
    for group in grouper(8, modified, "list"):
        modified_grouped.append(group)

    return modified_grouped

def get_ai_move(old, new):
    old_loc = []
    new_loc = []
    
    modified_old = modify_list(old)
    modified_new = modify_list(new)

    for row in range(0, 8):
        if modified_old[row] != modified_new[row]:
            for col in range(0,8):
                if modified_old[row][col] != modified_new[row][col]:
                    if isinstance(modified_new[row][col], int):
                        old_loc.append(row)
                        old_loc.append(col)
                        
                    if isinstance(modified_new[row][col], tuple):
                        new_loc.append(row)
                        new_loc.append(col)
    
    old = []
    skipped = []
    length = len(old_loc)
    # if length > 3:
    #     print("Zit erin ;-;")
    #     i = 0
    #     for group in grouper(2, old_loc, "list"):
    #         if i == 0:
    #             old.append(group)
    #         else:
    #             skipped.append(group)
    #         i+=1

    #     old_loc = []
    #     old_loc.append(old[0][0])
    #     old_loc.append(old[0][1])

    if length > 3:
        for group in grouper(2, old_loc, "list"):
            if modified_old[group[0]][group[1]] == (255, 0, 0):
                skipped.append(group)
            elif modified_old[group[0]][group[1]] == (255, 255, 255):
                old_loc = []
                old_loc.append(group[0])
                old_loc.append(group[1])

    # print(skipped)
    return old_loc, new_loc, skipped

def delete_skipped_pieces(skipped):
    global white_pieces

    if len(skipped) != 0:
        for piece in white_pieces:
            if piece['ai'] in skipped:
                index_skipped = skipped.index(piece['ai'])
                skipped.pop(index_skipped)

                index = white_pieces.index(piece)
                white_pieces.pop(index)  

                delete_skipped_pieces(skipped)

def start_capture(cap, game):
    ret, frame = cap.read()

    cv.imshow('frame', frame)

    # Start detecting current state of checkers pieces on 's' input
    # Can be changed to player/start button
    if cv.waitKey(1) == ord('s'):
        # Recognises all white pieces. Best for testing new functions
        img = cv.imread("img/movement2/board-pieces-1.png")
        img = cv.resize(img, (640, 480))

        img_1 = cv.imread("img/movement2/board-pieces-2.png")
        img_1 = cv.resize(img_1, (640, 480))

        # When checking new state safe old state
        global backup_old_white_pieces
        global old_white_pieces
        global white_pieces
        global first_check
        global block_distance
        global invalid_move

        # print("Outcome elif:")
        # print(first_check == False and len(white_pieces) == game.get_player())
        print("Current pieces and pieces of player:")
        print(len(white_pieces))
        print(game.get_player())
        
        if invalid_move:
            print("in if invalid move")
            old_white_pieces = copy.deepcopy(backup_old_white_pieces)
            invalid_move = False
            
        if len(white_pieces) != 12 and first_check:
            white_pieces = []
            current_white_pieces, calculated_block_distance = detect_white_pieces_on_board(frame, first_check) # Pass 'frame' for live detection
            white_pieces = copy.deepcopy(current_white_pieces)
            block_distance = copy.deepcopy(calculated_block_distance)

            print("===================OLD===================")
            print(old_white_pieces)
            print("===================NEW===================")
            print(white_pieces)

            if len(white_pieces) == 12:
                first_check = False

        elif first_check == False and len(white_pieces) == game.get_player():
            global old_row_col
            global new_row_col
            global move
            
            backup_old_white_pieces = copy.deepcopy(old_white_pieces)
            old_white_pieces = copy.deepcopy(white_pieces)
            white_pieces = []
            current_white_pieces, distance_none = detect_white_pieces_on_board(frame, first_check) # detect white pieces and then assign x,y and row,col
            white_pieces = copy.deepcopy(current_white_pieces)

            result_old_row_col, result_new_row_col = calculate_new_position(old_white_pieces, white_pieces, block_distance) # detect movement, calculate new position
            if result_old_row_col != None and result_new_row_col != None:
                old_row_col = result_old_row_col
                new_row_col = result_new_row_col

            movement = detect_movement(white_pieces, old_white_pieces, False)
            if movement is not None:
                white_pieces[detect_movement(white_pieces, old_white_pieces, False)]['ai'] = new_row_col
            
                print("===================OLD===================")
                print(old_white_pieces)
                print("===================NEW===================")
                print(white_pieces)
                            
                move = True
            else:
                old_white_pieces = copy.deepcopy(backup_old_white_pieces)
                print("No move detected")

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    cap = cv.VideoCapture(1);
    global move
    global invalid_move

    while run:
        start_capture(cap, game)
        detect_pieces_live(cap) # Check detection / camera position

        clock.tick(FPS)
        
        if game.turn == WHITE:
            board_old = game.get_board().__dict__['board']
            value, new_board = minimax(game.get_board(), 4, WHITE, game)
            board_new = new_board.__dict__['board']
            
            old, new, skipped = get_ai_move(board_old, board_new)
            print(skipped)
            if len(skipped) != 0:
                game.take_skipped_pieces(skipped)  
                delete_skipped_pieces(skipped)          
            
            game.ai_move(new_board, old, new)

        if game.winner() != None:
            print(game.winner())
            run = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        if move == True:
            result = game.select(old_row_col[0], old_row_col[1], new_row_col[0], new_row_col[1])
            if result:
                game.select(old_row_col[0], old_row_col[1], new_row_col[0], new_row_col[1])
            else:
                print("invalid move")
                invalid_move = True
            move = False
        
        game.update()
    
    pygame.quit()
    cap.release()
    cv.destroyAllWindows()

main()
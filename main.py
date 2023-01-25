# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import os
import time
import pygame
import cv2 as cv
import copy
import gpiozero
import serial

import checkers
from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game_v2 import Game
from checkers.board import Board
from minimax.algorithm import minimax
from detection.live_detection import detect_white_pieces_on_board, calculate_new_position, detect_movement, grouper
from detection.live_detect_pieces import detect_pieces_live


FPS = 60

# BEGIN GAME
difficulty = None
first_check = True
move = False
invalid_move = False

# CHECKER PIECES VARIABLES
backup_old_white_pieces = [] # [{'cv':[x,y], 'ai':[row,col]}, {...}]
old_white_pieces = []  # [{'cv':[x,y], 'ai':[row,col]}, {...}]
white_pieces = [] # [{'cv':[x,y], 'ai':[row,col]}, {...}]
block_distance = 0 # calculated with 5x - 7x: Outcome (if positive) is block FORWARD (to the right when looking at stream)

# HARDWARE
button_reset = gpiozero.Button(17)
button_move = gpiozero.Button(22)
led_player = gpiozero.LED(24)
led_computer = gpiozero.LED(23)

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
    global backup_old_white_pieces
    global old_white_pieces
    global white_pieces
    global first_check
    global invalid_move
    global block_distance
    global difficulty

    ret, frame = cap.read()

    # Invalid move
    if invalid_move:
        print("in if invalid move")
        old_white_pieces = copy.deepcopy(backup_old_white_pieces)
        invalid_move = False

    # First setup board
    if len(white_pieces) != 12 and first_check and difficulty != None:
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

    # Do move
    # if cv.waitKey(1) & 0xFF == ord("s"):
    if cv.waitKey(1) and button_move.is_pressed:
        print("Current pieces and pieces of player:")
        print(len(white_pieces))
        print(game.get_player())
            
        if first_check == False and len(white_pieces) == game.get_player():
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
                os.system('espeak -a 30 "No move detected, please try again"')
                print("No move detected")

def reset_variables():
    global first_check
    global move
    global invalid_move
    global backup_old_white_pieces
    global old_white_pieces
    global white_pieces
    global block_distance
    global difficulty
    first_check = True
    move = False
    invalid_move = False
    backup_old_white_pieces = []
    old_white_pieces = []
    white_pieces = []
    block_distance = 0
    difficulty = None

def main():
    com = serial.Serial("/dev/ttyUSB0", 9600)
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    cap = cv.VideoCapture(0);
    global move
    global invalid_move
    global difficulty
    printed = False

    while run:
        detect_pieces_live(cap) # Check detection / camera position

        if difficulty == None:
            # print(com.readline().decode("utf-8"))
            if com.in_waiting and "dif" in com.readline().decode("utf-8"):
                difficulty = int(com.readline().decode("utf-8").strip("dif: "))
                print(difficulty)
        else:
            if difficulty != None and printed == False:
                print("Sending stop to Arduino")
                msg = "stop".encode('utf-8')
                time.sleep(1)
                com.write(msg)
                com.flush()
                printed = True

            start_capture(cap, game)

            clock.tick(FPS)
            
            # If AI turn
            if game.turn == WHITE:
                led_player.on()
                led_computer.off()
                board_old = game.get_board().__dict__['board']
                value, new_board = minimax(game.get_board(), difficulty, WHITE, game)
                board_new = new_board.__dict__['board']
                
                old, new, skipped = get_ai_move(board_old, board_new)
                if len(skipped) != 0:
                    game.take_skipped_pieces(skipped)  
                    delete_skipped_pieces(skipped)          
                
                game.ai_move(new_board, old, new)
            else:
                led_player.off()
                led_computer.on()

            if game.winner() != None:
                if game.winner() == (255, 255, 255):
                    os.system('espeak -a 30 "Computer wins!"')
                else:
                    os.system('espeak -a 30 "Player wins!"')
                print(game.winner())
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            
            if move == True:
                result = game.select(old_row_col[0], old_row_col[1], new_row_col[0], new_row_col[1])
                print("Result: " + str(result))
                if result:
                    selection_result = game.select(old_row_col[0], old_row_col[1], new_row_col[0], new_row_col[1])
                    print("Selection Result: " + str(selection_result))
                    if selection_result:
                        os.system('espeak -a 30 "Invalid move"')

                        invalid_move = True
                move = False
            
            # Reset everything (also Arduino screen)
            # if button_reset.is_pressed:
            #     led_computer.off()
            #     led_player.off()

            #     print("Sending reset to Arduino")
            #     msg = "reset".encode('utf-8')
            #     time.sleep(1)
            #     com.write(msg)
            #     com.flush()

            #     game.reset()
            #     reset_variables()
                
            game.update()
    
    pygame.quit()
    cap.release()
    cv.destroyAllWindows()

main()
# Assets: https://techwithtim.net/wp-content/uploads/2020/09/assets.zip
import pygame
import cv2 as cv
import copy

from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE
from checkers.game import Game
from minimax.algorithm import minimax
from opencv.liveDetection import detectWhitePiecesOnBoard, calculateNewPosition, firstCheck, oldWhitePieces, whitePieces, blockDistance

FPS = 60

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    cap = cv.VideoCapture(1);
    if cap.isOpened():
        while run:
        # ============================= LIVE FEED ================================
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

                #TODO: Test firstcheck live
                if len(whitePieces) != 12 and firstCheck:
                    whitePieces = []
                    detectWhitePiecesOnBoard(img) # Pass 'frame' for live detection
                    if len(whitePieces) == 12:
                        firstCheck = False
                    
                elif firstCheck == False:
                    oldWhitePieces = copy.deepcopy(whitePieces)
                    whitePieces = []
                    detectWhitePiecesOnBoard(img1) # detect white pieces and then assign x,y and row,col
                    calculateNewPosition() # detect movement, calculate new position

                    print("===================OLD===================")
                    print(oldWhitePieces)
                    print("===================NEW===================")
                    print(whitePieces)

            # ============================= CHECKERS GAME ============================
            clock.tick(FPS)
            
            if game.turn == WHITE:
                value, new_board = minimax(game.get_board(), 4, WHITE, game)
                game.ai_move(new_board)

            if game.winner() != None:
                print(game.winner())
                run = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    # print("Row: " + str(row) + " Col: " + str(col))
                    game.select(row, col)

            game.update()

            if cv.waitKey(1) == ord('q'):
                break
    
        # pygame.quit()
        # cap.release()
        # cv.destroyAllWindows()

main()
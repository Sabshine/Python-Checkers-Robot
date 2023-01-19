import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE
from checkers.board import Board

import time
from uarm.wrapper import SwiftAPI

class Game:
    def __init__(self, win, muted):
        self._init()
        self.win = win
        self.muted = muted

        self.board_piece_height = 23
        self.zero_posistion = [105, -95] # [106.53, -94.2, 23.53]
        self.avg_x_movement = 28.0
        self.avg_y_movement = 27.0
        self.arm_height = 120
        
        self.swift = SwiftAPI(filters={'hwid': 'USB VID:PID=2341:0042'}, cmd_pend_size=2, callback_thread_pool_size=1)
        self.swift.waiting_ready()
        self.speed = 100000
        self.swift_ready = False
        
        if self.swift.connected:
            self.swift_ready = True
            self.swift.set_buzzer(duration=0.05)
    
    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def winner(self):
        return self.board.winner()

    def reset(self):
        self._init()

    def select(self, curRow, curCol, newRow, newCol):
        if self.selected:
            result = self._move(newRow, newCol)
            if not result:
                self.selected = None
                self.select(curRow, curCol, newRow, newCol)
            #     return False
            # else:
            #     return True
        
        piece = self.board.get_piece(curRow, curCol)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
            
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
            self.change_turn()
        else:
            return False

        return True

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED

    def get_player(self):
        return self.board.get_player_pieces()
    
    def get_board(self):
        return self.board

    def ai_move(self, board, old, new):
        self.board = board
        self.change_turn()

        if self.swift_ready == True:
            print("Arm moving piece on " + str(old) + " to " + str(new))
            self.move_arm([old[0], old[1]], [new[0], new[1]])

    def move_arm(self, old_pos, new_pos):
        old_x_pos, old_y_pos = self.calculate_coordinates(old_pos)

        # Pump off at start
        self.swift.set_pump(on=False)

        # Move to old position
        self.swift.set_position(z=self.arm_height, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
        self.swift.set_position(x=old_x_pos, y=old_y_pos, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
        self.swift.set_position(z=self.board_piece_height, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)

        # Pump on (pick piece)
        self.swift.set_pump(on=True)
        time.sleep(1)

        new_x_pos, new_y_pos = self.calculate_coordinates(new_pos)

        # Move to new position
        self.swift.set_position(z=self.arm_height, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
        self.swift.set_position(x=new_x_pos, y=new_y_pos, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
        self.swift.set_position(z=self.board_piece_height, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
    
        # Pump off (set piece)
        self.swift.set_pump(on=False)

        # Move away from board (turn right)
        # [6.24, -169.38, 61.84]
        self.swift.set_position(z=self.arm_height, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)
        self.swift.set_position(x=5, y=-160, speed=self.speed)
        self.swift.flush_cmd(wait_stop=True)

    def take_skipped_pieces(self, skipped):
        for piece in skipped:
            x_pos, y_pos = self.calculate_coordinates(piece)

            # Pump off at start
            self.swift.set_pump(on=False)

            # Move to old position
            self.swift.set_position(z=self.arm_height, speed=self.speed)
            self.swift.flush_cmd(wait_stop=True)
            self.swift.set_position(x=x_pos, y=y_pos, speed=self.speed)
            self.swift.flush_cmd(wait_stop=True)
            self.swift.set_position(z=self.board_piece_height, speed=self.speed)
            self.swift.flush_cmd(wait_stop=True)

            # Pump on (pick piece)
            self.swift.set_pump(on=True)
            time.sleep(1)

            # Move away from board (turn right)
            self.swift.set_position(z=self.arm_height, speed=self.speed)
            self.swift.flush_cmd(wait_stop=True)
            self.swift.set_position(x=5, y=-160, speed=self.speed)
            self.swift.flush_cmd(wait_stop=True)

            # Pump off (set piece)
            self.swift.set_pump(on=False)

    def calculate_coordinates(self, pos):
        row = pos[0]
        col = pos[1]

        x = self.zero_posistion[0] + (row * self.avg_x_movement)
        y = self.zero_posistion[1] + (col * self.avg_y_movement)

        return x, y
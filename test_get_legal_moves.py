from PyQt6.QtWidgets import QApplication
import sys
from UI import ChessUI
from main import Board, Move
from timer import Timer
from settings import TURN_TIME_MS, INCREMENT_MS
from default_player import DefaultPlayer
from player_one import PlayerOne
from player_two import PlayerTwo
import time


board = Board(fen="8/1kr5/8/8/8/8/2K5/8 w - - 0 1")

moves = board.get_all_legal_moves()

for move in moves:
    print(f"Form col {move.start_col}, row {move.start_row} to col {move.end_col}, row {move.end_row}")



import random
from main import Board
from timer import Timer
from time import sleep
from main import Move


class DefaultPlayer:
    def __init__(self):
        self.name = "Default Player"
        
    def think(self, board: Board, timer: Timer) -> Move:
        """
        Generate a move for the current position.
        
        Args:
            board: The current board state
            timer: The game timer
            
        Returns:
            tuple: (start_row, start_col, end_row, end_col) representing the move
        """
        # Get all legal moves for the current position
        legal_moves = board.get_all_legal_moves()
            
        # Select a random move
        chosen_move = random.choice(legal_moves)

        # sleep(0.1)

        return chosen_move

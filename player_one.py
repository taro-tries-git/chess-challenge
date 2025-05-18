from main import Board
from timer import Timer
from main import Move
from train_model import load_model
from default_player import DefaultPlayer


class PlayerOne(DefaultPlayer):
    def __init__(self):
        super().__init__()
        self.name = "Player One"
        # Load the trained model

        self.model = load_model('chess_evaluator_best.pth')
        print("Neural network model loaded successfully!")

    def think(self, board: Board, timer: Timer) -> Move:
        # Get all legal moves
        legal_moves = board.get_all_legal_moves()
        best_eval = float('inf') if board.is_white_turn else float('-inf')
        
        # Evaluate each move
        for move in legal_moves:
            # Create a copy of the board and make the move
            board.make_move(move)
            # Get evaluation from neural network
            eval_cp = self.model.evaluate_position(board)

            board.undo_move()
            
            # Choose the best move based on side to move
            if board.is_white_turn:
                if eval_cp < best_eval:
                    best_eval = eval_cp
                    best_move = move
            else:
                if eval_cp > best_eval:
                    best_eval = eval_cp
                    best_move = move
        
        print(f"Chosen move evaluation: {-best_eval/100:.2f} pawns")
        return best_move


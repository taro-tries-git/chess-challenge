from main import Board, Move


board = Board("8/8/2K5/8/8/8/1R6/5k2 b - - 0 1")
moves = board.get_all_legal_moves()
for move in moves:
    print(move.get_printable())
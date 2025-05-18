from main import Board, Move


board = Board("8/1K6/8/8/8/8/Rb2k3/8 b - - 0 1")
moves = board.get_all_legal_moves()
for move in moves:
    print(move.get_printable())
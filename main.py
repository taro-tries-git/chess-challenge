class piece_helper:
    # Piece constants
    empty = 0
    white_pawn = 1
    white_knight = 2
    white_bishop = 3
    white_rook = 4
    white_queen = 5
    white_king = 6
    black_pawn = -1
    black_knight = -2
    black_bishop = -3
    black_rook = -4
    black_queen = -5
    black_king = -6

class Move:
    def __init__(self, start_row: int, start_col: int, end_row: int, end_col: int, 
                 is_en_passant: bool = False, is_kingside_castle: bool = False, 
                 is_queenside_castle: bool = False):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.is_en_passant = is_en_passant
        self.is_kingside_castle = is_kingside_castle
        self.is_queenside_castle = is_queenside_castle

class Board:
    def __init__(self):
        # Initialize empty 8x8 board
        self.board = [[piece_helper.empty for _ in range(8)] for _ in range(8)]
        
        self.piece_positions = {            # Dictionary to store positions of pieces by type
            piece_helper.empty: [],         # Format: {piece_type: [(row, col), ...]}
            piece_helper.white_pawn: [],
            piece_helper.white_knight: [],
            piece_helper.white_bishop: [],
            piece_helper.white_rook: [],
            piece_helper.white_queen: [],
            piece_helper.white_king: [],
            piece_helper.black_pawn: [],
            piece_helper.black_knight: [],
            piece_helper.black_bishop: [],
            piece_helper.black_rook: [],
            piece_helper.black_queen: [],
            piece_helper.black_king: []
        }
        self.white_turn = True  # True if it's white's turn, False if it's black's turn
        
        # En passant target square (row, col) or None if not available
        self.en_passant_target = None
        
        # History
        self.position_history = []  # List of comprehensive board states
        
        # Halfmove clock
        self.halfmove_clock = 0 # Number of halfmoves since the last capture or pawn advance
        
        # Castling rights
        self.white_kingside_castle = True   # White can castle kingside
        self.white_queenside_castle = True  # White can castle queenside
        self.black_kingside_castle = True   # Black can castle kingside
        self.black_queenside_castle = True  # Black can castle queenside

    def get_piece(self, row, col):
        """Get the piece type at the specified position."""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def get_pseudo_legal_moves(self, row: int, col: int, only_captures: bool = False) -> list[Move]:
        """
        Get all possible moves for a piece at the given position, without checking if the move would leave the king in check.
        Args:
            row: Row of the piece
            col: Column of the piece
            only_captures: If True, only return moves that capture a piece
        Returns:
            List of Move objects representing possible moves
        """
        piece = self.get_piece(row, col)
        if piece == piece_helper.empty:
            return []

        moves = []
        is_white = piece > 0

        # Pawn moves
        if abs(piece) == piece_helper.white_pawn:
            row_direction = -1 if is_white else 1
            # Forward move
            if not only_captures:
                if 0 <= row + row_direction < 8 and self.get_piece(row + row_direction, col) == piece_helper.empty:
                    moves.append(Move(row, col, row + row_direction, col))
                    # Double move from starting position
                    if (is_white and row == 6) or (not is_white and row == 1):
                        if self.get_piece(row + 2 * row_direction, col) == piece_helper.empty:
                            moves.append(Move(row, col, row + 2 * row_direction, col))
            # Regular captures
            for col_direction in [-1, 1]:
                if 0 <= col + col_direction < 8 and 0 <= row + row_direction < 8:
                    target = self.get_piece(row + row_direction, col + col_direction)
                    if target != piece_helper.empty and (target > 0) != is_white:
                        moves.append(Move(row, col, row + row_direction, col + col_direction))
            
            # En passant captures
            if self.en_passant_target is not None:
                en_passant_row, en_passant_col = self.en_passant_target
                if row == (3 if is_white else 4):  # Correct rank for en passant
                    if abs(col - en_passant_col) == 1:  # Adjacent column
                        moves.append(Move(row, col, en_passant_row + row_direction, en_passant_col, is_en_passant=True))

        # Knight moves
        elif abs(piece) == piece_helper.white_knight:
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for row_direction, col_direction in knight_moves:
                new_row, new_col = row + row_direction, col + col_direction
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    target = self.get_piece(new_row, new_col)
                    if (not only_captures and target == piece_helper.empty) or \
                       (target != piece_helper.empty and (target > 0) != is_white):
                        moves.append(Move(row, col, new_row, new_col))

        # Bishop moves
        elif abs(piece) == piece_helper.white_bishop:
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for row_direction, col_direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + i * row_direction, col + i * col_direction
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    target = self.get_piece(new_row, new_col)
                    if not only_captures and target == piece_helper.empty:
                        moves.append(Move(row, col, new_row, new_col))
                    elif target != piece_helper.empty:
                        if (target > 0) != is_white:
                            moves.append(Move(row, col, new_row, new_col))
                        break
                    else:
                        break

        # Rook moves
        elif abs(piece) == piece_helper.white_rook:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for row_direction, col_direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + i * row_direction, col + i * col_direction
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    target = self.get_piece(new_row, new_col)
                    if not only_captures and target == piece_helper.empty:
                        moves.append(Move(row, col, new_row, new_col))
                    elif target != piece_helper.empty:
                        if (target > 0) != is_white:
                            moves.append(Move(row, col, new_row, new_col))
                        break
                    else:
                        break

        # Queen moves (combination of bishop and rook)
        elif abs(piece) == piece_helper.white_queen:
            directions = [
                (-1, -1), (-1, 1), (1, -1), (1, 1),  # Bishop directions
                (-1, 0), (1, 0), (0, -1), (0, 1)     # Rook directions
            ]
            for row_direction, col_direction in directions:
                for i in range(1, 8):
                    new_row, new_col = row + i * row_direction, col + i * col_direction
                    if not (0 <= new_row < 8 and 0 <= new_col < 8):
                        break
                    target = self.get_piece(new_row, new_col)
                    if not only_captures and target == piece_helper.empty:
                        moves.append(Move(row, col, new_row, new_col))
                    elif target != piece_helper.empty:
                        if (target > 0) != is_white:
                            moves.append(Move(row, col, new_row, new_col))
                        break
                    else:
                        break

        # King moves
        elif abs(piece) == piece_helper.white_king:
            for row_direction in [-1, 0, 1]:
                for col_direction in [-1, 0, 1]:
                    if row_direction == 0 and col_direction == 0:
                        continue
                    new_row, new_col = row + row_direction, col + col_direction
                    if 0 <= new_row < 8 and 0 <= new_col < 8:
                        target = self.get_piece(new_row, new_col)
                        if (not only_captures and target == piece_helper.empty) or \
                           (target != piece_helper.empty and (target > 0) != is_white):
                            moves.append(Move(row, col, new_row, new_col))

        return moves

    def king_is_attacked(self, white_king: bool) -> bool:
        """
        Check if the specified king is under attack.
        Args:
            white_king: True to check white king, False to check black king
        Returns:
            bool: True if the king is under attack, False otherwise
        """
        # Get the king's position
        king = piece_helper.white_king if white_king else piece_helper.black_king
        king_positions = self.piece_positions[king]
        
        if not king_positions:  # King not found
            return False
            
        king_row, king_col = king_positions[0]  # There should only be one king
        
        # Check if any opponent piece can attack the king
        opponent_pieces = [
            piece_helper.black_pawn, piece_helper.black_knight, piece_helper.black_bishop,
            piece_helper.black_rook, piece_helper.black_queen, piece_helper.black_king
        ] if white_king else [
            piece_helper.white_pawn, piece_helper.white_knight, piece_helper.white_bishop,
            piece_helper.white_rook, piece_helper.white_queen, piece_helper.white_king
        ]
        
        # Check each opponent piece's possible moves (only captures)
        for piece_type in opponent_pieces:
            for piece_row, piece_col in self.piece_positions[piece_type]:
                moves = self.get_pseudo_legal_moves(piece_row, piece_col, only_captures=True)
                if any(move.end_row == king_row and move.end_col == king_col for move in moves):
                    return True
        
        return False

    def make_move(self, move: Move) -> bool:
        """
        Make a move on the board.
        Args:
            move: The move to make
        Returns:
            bool: True if the move was successful, False otherwise
        """
        # Save current comprehensive state BEFORE making the move
        current_state = {
            'board': [row[:] for row in self.board],
            'white_kingside_castle': self.white_kingside_castle,
            'white_queenside_castle': self.white_queenside_castle,
            'black_kingside_castle': self.black_kingside_castle,
            'black_queenside_castle': self.black_queenside_castle,
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'white_turn': self.white_turn  # Whose turn it is before this move
        }
        self.position_history.append(current_state)
        
        # Get the piece being moved
        piece = self.get_piece(move.start_row, move.start_col)
        if piece == piece_helper.empty:
            return False
            
        # Remove piece from old position
        self.board[move.start_row][move.start_col] = piece_helper.empty
        self.piece_positions[piece].remove((move.start_row, move.start_col))
        
        # Handle captures (including en passant)
        captured_piece = self.get_piece(move.end_row, move.end_col)
        if captured_piece != piece_helper.empty:
            self.piece_positions[captured_piece].remove((move.end_row, move.end_col))
        
        # Handle en passant capture
        if move.is_en_passant:
            captured_pawn_row = move.start_row  # The captured pawn is on the same row as the moving pawn
            captured_pawn_col = move.end_col    # The captured pawn is on the same column as the destination
            captured_piece = self.get_piece(captured_pawn_row, captured_pawn_col)
            self.board[captured_pawn_row][captured_pawn_col] = piece_helper.empty
            self.piece_positions[captured_piece].remove((captured_pawn_row, captured_pawn_col))
        
        # Handle castling
        if move.is_kingside_castle or move.is_queenside_castle:
            is_white = piece > 0
            rook_col = 7 if move.is_kingside_castle else 0
            rook_piece = piece_helper.white_rook if is_white else piece_helper.black_rook
            new_rook_col = move.end_col - 1 if move.is_kingside_castle else move.end_col + 1
            
            # Move the rook
            self.board[move.start_row][rook_col] = piece_helper.empty
            self.board[move.start_row][new_rook_col] = rook_piece
            self.piece_positions[rook_piece].remove((move.start_row, rook_col))
            self.piece_positions[rook_piece].append((move.start_row, new_rook_col))
        
        # Place piece in new position
        self.board[move.end_row][move.end_col] = piece
        self.piece_positions[piece].append((move.end_row, move.end_col))
        
        # Update halfmove clock
        if abs(piece) == piece_helper.white_pawn or captured_piece != piece_helper.empty or move.is_en_passant:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # Update castling rights
        if abs(piece) == piece_helper.white_king:
            if piece > 0:  # White king
                self.white_kingside_castle = False
                self.white_queenside_castle = False
            else:  # Black king
                self.black_kingside_castle = False
                self.black_queenside_castle = False
        elif abs(piece) == piece_helper.white_rook:
            if piece > 0:  # White rook
                if move.start_col == 7:  # Kingside rook
                    self.white_kingside_castle = False
                elif move.start_col == 0:  # Queenside rook
                    self.white_queenside_castle = False
            else:  # Black rook
                if move.start_col == 7:  # Kingside rook
                    self.black_kingside_castle = False
                elif move.start_col == 0:  # Queenside rook
                    self.black_queenside_castle = False
        
        # Update en passant target if it was a double pawn move
        if abs(piece) == piece_helper.white_pawn and abs(move.end_row - move.start_row) == 2:
            self.en_passant_target = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_target = None
        
        # Switch turns
        self.white_turn = not self.white_turn
        
        return True

    def undo_move(self) -> bool:
        """
        Undo the last move made.
        Returns:
            bool: True if a move was undone, False if there are no moves to undo
        """
        if not self.position_history:
            return False
            
        # Restore the comprehensive state from before the undone move
        last_saved_state = self.position_history.pop()
        
        self.board = last_saved_state['board']
        self.white_kingside_castle = last_saved_state['white_kingside_castle']
        self.white_queenside_castle = last_saved_state['white_queenside_castle']
        self.black_kingside_castle = last_saved_state['black_kingside_castle']
        self.black_queenside_castle = last_saved_state['black_queenside_castle']
        self.en_passant_target = last_saved_state['en_passant_target']
        self.halfmove_clock = last_saved_state['halfmove_clock']
        self.white_turn = last_saved_state['white_turn'] # This restores the turn to what it was before the move

        # Rebuild piece positions from the restored board
        self.piece_positions = {piece_type: [] for piece_type in self.piece_positions}
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != piece_helper.empty:
                    self.piece_positions[piece].append((r, c))
        
        return True

    def get_legal_moves(self, row: int, col: int) -> list[Move]:
        """
        Get all legal moves for a piece at the given position, including castling.
        A move is legal if it doesn't leave the king in check.
        Args:
            row: Row of the piece
            col: Column of the piece
        Returns:
            List of Move objects representing legal moves
        """
        piece = self.get_piece(row, col)
        if piece == piece_helper.empty:
            return []
            
        is_white = piece > 0
        moves = []
        
        # Get pseudo-legal moves
        pseudo_moves = self.get_pseudo_legal_moves(row, col)
        
        # Try each move and check if it leaves the king in check
        for move in pseudo_moves:
            # Make the move
            self.make_move(move)
            
            # Check if the king is safe
            king_safe = not self.king_is_attacked(is_white)
            
            # Undo the move
            self.undo_move()
            
            if king_safe:
                moves.append(move)
        
        # Add castling moves if it's a king
        if abs(piece) == piece_helper.white_king:
            # Kingside castling
            if (is_white and self.white_kingside_castle) or (not is_white and self.black_kingside_castle):
                # Check if path is clear
                path_clear = True
                for c in range(col + 1, 7):  # Check squares between king and rook
                    if self.get_piece(row, c) != piece_helper.empty:
                        path_clear = False
                        break
                
                # Check if squares are not under attack
                squares_safe = True
                for c in range(col, col + 3):  # Check king's square and two squares to the right
                    # Make temporary move
                    self.board[row][col] = piece_helper.empty
                    self.board[row][c] = piece
                    # Check if square is under attack
                    if self.king_is_attacked(is_white):
                        squares_safe = False
                    # Undo temporary move
                    self.board[row][col] = piece
                    self.board[row][c] = piece_helper.empty
                    if not squares_safe:
                        break
                
                if path_clear and squares_safe:
                    moves.append(Move(row, col, row, col + 2, is_kingside_castle=True))
            
            # Queenside castling
            if (is_white and self.white_queenside_castle) or (not is_white and self.black_queenside_castle):
                # Check if path is clear
                path_clear = True
                for c in range(col - 1, 0, -1):  # Check squares between king and rook
                    if self.get_piece(row, c) != piece_helper.empty:
                        path_clear = False
                        break
                
                # Check if squares are not under attack
                squares_safe = True
                for c in range(col, col - 3, -1):  # Check king's square and two squares to the left
                    # Make temporary move
                    self.board[row][col] = piece_helper.empty
                    self.board[row][c] = piece
                    # Check if square is under attack
                    if self.king_is_attacked(is_white):
                        squares_safe = False
                    # Undo temporary move
                    self.board[row][col] = piece
                    self.board[row][c] = piece_helper.empty
                    if not squares_safe:
                        break
                
                if path_clear and squares_safe:
                    moves.append(Move(row, col, row, col - 2, is_queenside_castle=True))
        
        return moves

    def get_all_legal_moves(self, white: bool) -> list[Move]:
        """
        Get all legal moves for the given color.
        Args:
            white: True for white's moves, False for black's moves
        Returns:
            List of Move objects representing all legal moves for the given color
        """
        moves = []
        piece_types = [
            piece_helper.white_pawn,
            piece_helper.white_knight,
            piece_helper.white_bishop,
            piece_helper.white_rook,
            piece_helper.white_queen,
            piece_helper.white_king
        ] if white else [
            piece_helper.black_pawn,
            piece_helper.black_knight,
            piece_helper.black_bishop,
            piece_helper.black_rook,
            piece_helper.black_queen,
            piece_helper.black_king
        ]
        
        # Get all legal moves for each piece of the given color
        for piece_type in piece_types:
            for row, col in self.piece_positions[piece_type]:
                moves.extend(self.get_legal_moves(row, col))
        
        return moves

    def get_gamestate(self) -> str:
        """
        Determines the current state of the game.
        Returns:
            str: "ongoing", "checkmate", "stalemate", "draw_50_move", "draw_threefold_repetition"
        """
        # Check for checkmate or stalemate
        legal_moves = self.get_all_legal_moves(self.white_turn)
        if not legal_moves:
            if self.king_is_attacked(self.white_turn):
                return "checkmate"
            else:
                return "stalemate"

        # Check for 50-move rule
        if self.halfmove_clock >= 100:  # 50 full moves (100 halfmoves)
            return "draw_50_move"

        # Check for threefold repetition
        # A position is repeated if the board, current turn, castling rights, and en passant target are identical.
        current_board_tuple = tuple(map(tuple, self.board))
        current_comparable_state = (
            current_board_tuple,
            self.white_turn,
            self.white_kingside_castle,
            self.white_queenside_castle,
            self.black_kingside_castle,
            self.black_queenside_castle,
            self.en_passant_target
        )

        # Count occurrences of the current state in history.
        # The current state itself counts as one occurrence.
        occurrences = 1 
        for past_saved_state_dict in self.position_history:
            past_board_tuple = tuple(map(tuple, past_saved_state_dict['board']))
            past_comparable_state = (
                past_board_tuple,
                past_saved_state_dict['white_turn'],
                past_saved_state_dict['white_kingside_castle'],
                past_saved_state_dict['white_queenside_castle'],
                past_saved_state_dict['black_kingside_castle'],
                past_saved_state_dict['black_queenside_castle'],
                past_saved_state_dict['en_passant_target']
            )
            if past_comparable_state == current_comparable_state:
                occurrences += 1
        
        if occurrences >= 3:
            return "draw_threefold_repetition"

        return "ongoing"

def main():
    print("Hello, World!")

if __name__ == "__main__":
    main() 
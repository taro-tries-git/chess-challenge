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
                 is_queenside_castle: bool = False, promotion_piece: int = None):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        self.is_en_passant = is_en_passant
        self.is_kingside_castle = is_kingside_castle
        self.is_queenside_castle = is_queenside_castle
        self.promotion_piece = promotion_piece  # The piece type to promote to


class Board:
    def __init__(self, fen: str ="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """
       Set the board position from FEN notation.
       Args:
           fen: FEN string representing the position
       Returns:
           bool: True if successful, False if invalid FEN
       """
        # Initialize empty 8x8 board
        self.last_board = None
        self.board = [[piece_helper.empty for _ in range(8)] for _ in range(8)]

        # History
        self.position_history = []  # List of comprehensive board states
        
        # Split FEN into its components
        parts = fen.split()
        if len(parts) < 4:
            print("ERROR: fen has less than 4 parts")

        position, turn, castling, en_passant = parts[:4]
        halfmove = "0" if len(parts) < 5 else parts[4]

        # Parse position
        rows = position.split('/')
        if len(rows) != 8:
            print("ERROR: fen needs 8 rows")

        # FEN piece to piece_helper mapping
        piece_map = {
            'P': piece_helper.white_pawn,
            'N': piece_helper.white_knight,
            'B': piece_helper.white_bishop,
            'R': piece_helper.white_rook,
            'Q': piece_helper.white_queen,
            'K': piece_helper.white_king,
            'p': piece_helper.black_pawn,
            'n': piece_helper.black_knight,
            'b': piece_helper.black_bishop,
            'r': piece_helper.black_rook,
            'q': piece_helper.black_queen,
            'k': piece_helper.black_king
        }

        for row_idx, row in enumerate(rows):
            col_idx = 0
            for char in row:
                if char.isdigit():
                    col_idx += int(char)
                else:
                    if col_idx >= 8:
                        print("ERROR: fen problem")
                    if char in piece_map:
                        piece = piece_map[char]
                        self.board[row_idx][col_idx] = piece
                    col_idx += 1
            if col_idx != 8:
                print("ERROR: fen problem")

        # Parse turn
        self.is_white_turn = turn == 'w'

        # Parse castling rights
        self.white_kingside_castle = 'K' in castling
        self.white_queenside_castle = 'Q' in castling
        self.black_kingside_castle = 'k' in castling
        self.black_queenside_castle = 'q' in castling

        # Parse en passant
        if en_passant != '-':
            col = ord(en_passant[0]) - ord('a')
            row = 8 - int(en_passant[1])
            self.en_passant_target = (row, col)
        else:
            self.en_passant_target = None

        # Parse halfmove clock
        self.halfmove_clock = int(halfmove)

    def get_fen(self) -> str:
        """
        Get the current position in FEN notation.
        Returns:
            str: FEN string representing the current position
        """
        # Piece helper to FEN piece mapping
        piece_map = {
            piece_helper.white_pawn: 'P',
            piece_helper.white_knight: 'N',
            piece_helper.white_bishop: 'B',
            piece_helper.white_rook: 'R',
            piece_helper.white_queen: 'Q',
            piece_helper.white_king: 'K',
            piece_helper.black_pawn: 'p',
            piece_helper.black_knight: 'n',
            piece_helper.black_bishop: 'b',
            piece_helper.black_rook: 'r',
            piece_helper.black_queen: 'q',
            piece_helper.black_king: 'k'
        }
        
        # Build position string
        position = []
        for row in self.board:
            empty_count = 0
            row_str = ""
            for piece in row:
                if piece == piece_helper.empty:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str += str(empty_count)
                        empty_count = 0
                    row_str += piece_map[piece]
            if empty_count > 0:
                row_str += str(empty_count)
            position.append(row_str)
        position = '/'.join(position)
        
        # Add turn
        turn = 'w' if self.is_white_turn else 'b'
        
        # Add castling rights
        castling = ''
        if self.white_kingside_castle:
            castling += 'K'
        if self.white_queenside_castle:
            castling += 'Q'
        if self.black_kingside_castle:
            castling += 'k'
        if self.black_queenside_castle:
            castling += 'q'
        if not castling:
            castling = '-'
        
        # Add en passant target
        if self.en_passant_target:
            row, col = self.en_passant_target
            en_passant = chr(ord('a') + col) + str(8 - row)
        else:
            en_passant = '-'
        
        # Combine all parts
        return f"{position} {turn} {castling} {en_passant} {self.halfmove_clock}"

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
            print("ERROR: get_pseudo_legal_moves called on empty square")
            return []

        # Validate coordinates
        if not (0 <= row < 8 and 0 <= col < 8):
            print(f"ERROR: get_pseudo_legal_moves called with invalid coordinates: {row}, {col}")
            return []

        moves = []
        is_white = piece > 0

        # Pawn moves
        if abs(piece) == piece_helper.white_pawn:
            row_direction = -1 if is_white else 1
            promotion_rank = 0 if is_white else 7
            
            # Forward move
            if not only_captures:
                if 0 <= row + row_direction < 8 and self.get_piece(row + row_direction, col) == piece_helper.empty:
                    # Check for promotion
                    if row + row_direction == promotion_rank:
                        # Add all possible promotion moves
                        promotion_pieces = [
                            piece_helper.white_queen if is_white else piece_helper.black_queen,
                            piece_helper.white_rook if is_white else piece_helper.black_rook,
                            piece_helper.white_bishop if is_white else piece_helper.black_bishop,
                            piece_helper.white_knight if is_white else piece_helper.black_knight
                        ]
                        for promotion_piece in promotion_pieces:
                            moves.append(Move(row, col, row + row_direction, col, promotion_piece=promotion_piece))
                    else:
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
                        # Check for promotion
                        if row + row_direction == promotion_rank:
                            # Add all possible promotion captures
                            promotion_pieces = [
                                piece_helper.white_queen if is_white else piece_helper.black_queen,
                                piece_helper.white_rook if is_white else piece_helper.black_rook,
                                piece_helper.white_bishop if is_white else piece_helper.black_bishop,
                                piece_helper.white_knight if is_white else piece_helper.black_knight
                            ]
                            for promotion_piece in promotion_pieces:
                                moves.append(Move(row, col, row + row_direction, col + col_direction, promotion_piece=promotion_piece))
                        else:
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

    def find_king(self, is_white: bool) -> tuple[int, int]:
        """Find the position of the specified king."""
        king = piece_helper.white_king if is_white else piece_helper.black_king
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king:
                    return row, col
        print(f"ERROR: No {'white' if is_white else 'black'} king found on the board!")
        return -1, -1  # Should never happen in a valid chess position

    def is_square_attacked(self, row: int, col: int, is_white: bool) -> bool:
        """Check if a square is attacked by any opponent piece."""
        if not (0 <= row < 8 and 0 <= col < 8):
            print(f"ERROR: is_square_attacked called with invalid coordinates: {row}, {col}")
            return False

        # Check each square on the board for opponent pieces
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece != piece_helper.empty and (piece > 0) != is_white:
                    # Get all possible moves for this piece
                    moves = self.get_pseudo_legal_moves(r, c)
                    # Check if any move attacks the target square
                    if any(move.end_row == row and move.end_col == col for move in moves):
                        return True
        return False

    def king_is_attacked(self, white_king: bool) -> bool:
        """
        Check if the specified king is under attack.
        Args:
            white_king: True to check white king, False to check black king
        Returns:
            bool: True if the king is under attack, False otherwise
        """
        king_row, king_col = self.find_king(white_king)
        if king_row == -1 or king_col == -1:
            print("ERROR: king_is_attacked called but king not found!")
            return False
        
        return self.is_square_attacked(king_row, king_col, white_king)

    def make_move(self, move: Move) -> bool:
        """
        Make a move on the board.
        Args:
            move: The move to make
        Returns:
            bool: True if the move was successful, False otherwise
        """
        # Validate move coordinates
        if not (0 <= move.start_row < 8 and 0 <= move.start_col < 8 and 
                0 <= move.end_row < 8 and 0 <= move.end_col < 8):
            print(f"ERROR: make_move called with invalid coordinates: from ({move.start_row}, {move.start_col}) to ({move.end_row}, {move.end_col})")
            return False

        # Save current comprehensive state BEFORE making the move
        current_state = {
            'board': [row[:] for row in self.board],
            'white_kingside_castle': self.white_kingside_castle,
            'white_queenside_castle': self.white_queenside_castle,
            'black_kingside_castle': self.black_kingside_castle,
            'black_queenside_castle': self.black_queenside_castle,
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'is_white_turn': self.is_white_turn  # Whose turn it is before this move
        }
        self.position_history.append(current_state)
        
        # Get the piece being moved
        piece = self.get_piece(move.start_row, move.start_col)
        if piece == piece_helper.empty:
            print(f"ERROR: Attempting to move an empty square from ({move.start_row}, {move.start_col})")
            return False

        # Verify piece color matches turn
        if (piece > 0) != self.is_white_turn:
            print(f"ERROR: Wrong color piece moved! Turn: {'white' if self.is_white_turn else 'black'}, Piece: {piece}")
            return False
            
        # Remove piece from old position
        self.board[move.start_row][move.start_col] = piece_helper.empty
        
        # Handle en passant capture
        if move.is_en_passant:
            if self.en_passant_target is None:
                print("ERROR: En passant move attempted but no en passant target exists!")
                return False
            captured_pawn_row = move.start_row  # The captured pawn is on the same row as the moving pawn
            captured_pawn_col = move.end_col    # The captured pawn is on the same column as the destination
            self.board[captured_pawn_row][captured_pawn_col] = piece_helper.empty
        
        # Handle castling
        if move.is_kingside_castle or move.is_queenside_castle:
            if abs(piece) != piece_helper.white_king:
                print("ERROR: Castling attempted with non-king piece!")
                return False
            rook_col = 7 if move.is_kingside_castle else 0
            rook_piece = piece_helper.white_rook if piece > 0 else piece_helper.black_rook
            new_rook_col = move.end_col - 1 if move.is_kingside_castle else move.end_col + 1
            
            # Verify rook is present
            if self.get_piece(move.start_row, rook_col) != rook_piece:
                print(f"ERROR: Castling attempted but no rook found at {move.start_row}, {rook_col}")
                return False
            
            # Move the rook
            self.board[move.start_row][rook_col] = piece_helper.empty
            self.board[move.start_row][new_rook_col] = rook_piece
        
        # Place piece in new position
        target_piece = self.get_piece(move.end_row, move.end_col)
        if abs(target_piece) == piece_helper.white_king:
            print("ERROR: Attempting to capture a king!")
            return False
        
        # Handle pawn promotion
        if move.promotion_piece is not None:
            if abs(piece) != piece_helper.white_pawn:
                print("ERROR: Promotion attempted with non-pawn piece!")
                return False
            if (piece > 0 and move.end_row != 0) or (piece < 0 and move.end_row != 7):
                print("ERROR: Promotion attempted on wrong rank!")
                return False
            piece = move.promotion_piece
        
        self.board[move.end_row][move.end_col] = piece

        # Handle captures (including en passant)
        captured_piece = target_piece
        
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
        self.is_white_turn = not self.is_white_turn
        
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
        self.is_white_turn = last_saved_state['is_white_turn'] # This restores the turn to what it was before the move
        
        return True

    def get_piece_moves(self, row: int, col: int) -> list[Move]:
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
            print(f"ERROR: get_piece_moves called on empty square at {row}, {col}")
            return []
            
        is_white = piece > 0
        moves = []
        
        # Get pseudo-legal moves
        pseudo_moves = self.get_pseudo_legal_moves(row, col)
        
        # Try each move and check if it leaves the king in check
        for move in pseudo_moves:
            # Make the move
            if not self.make_move(move):
                print("ERROR: Failed to make move during move generation!")
                continue
            
            # Check if the king is safe
            if not self.king_is_attacked(is_white):
                moves.append(move)
            
            # Undo the move
            if not self.undo_move():
                print("ERROR: Failed to undo move during move generation!")
                continue
        
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
                    squares_safe &= not self.is_square_attacked(row, c, is_white)
                
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
                    squares_safe &= not self.is_square_attacked(row, c, is_white)
                
                if path_clear and squares_safe:
                    moves.append(Move(row, col, row, col - 2, is_queenside_castle=True))
        
        return moves

    def get_all_legal_moves(self) -> list[Move]:
        """
        Get all legal moves for the given color.
        Returns:
            List of Move objects representing all legal moves for the given color
        """
        moves = []
        # Iterate through all squares
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                # If we find a piece of the right color
                if piece != piece_helper.empty and (piece > 0) == self.is_white_turn:
                    moves.extend(self.get_piece_moves(row, col))
        return moves

    def get_gamestate(self) -> str:
        """
        Determines the current state of the game.
        Returns:
            str: "ongoing", "checkmate", "stalemate", "draw_50_move", "draw_threefold_repetition"
        """
        # Check for checkmate or stalemate
        legal_moves = self.get_all_legal_moves()
        if not legal_moves:
            if self.king_is_attacked(self.is_white_turn):
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
            self.is_white_turn,
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
                past_saved_state_dict['is_white_turn'],
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
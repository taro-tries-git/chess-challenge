import unittest
from main import Board, Move, piece_helper


class TestBoard(unittest.TestCase):
    def test_initial_position_moves(self):
        """Test legal moves from the initial position"""
        board = Board()
        moves = board.get_all_legal_moves()
        self.assertEqual(len(moves), 20)  # 16 pawn moves + 4 knight moves

    def test_en_passant(self):
        """Test en passant capture is correctly generated"""
        # Position after 1. e4 c5 2. e5 d5
        board = Board("rnbqkbnr/pp2pppp/8/2ppP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")
        moves = board.get_all_legal_moves()
        # Find en passant capture
        en_passant_moves = [move for move in moves if move.is_en_passant]
        self.assertEqual(len(en_passant_moves), 1)
        move = en_passant_moves[0]
        self.assertEqual((move.start_row, move.start_col), (3, 4))  # e5
        self.assertEqual((move.end_row, move.end_col), (2, 3))      # d6

    def test_castling(self):
        """Test castling moves are correctly generated"""
        # Position where both sides can castle both ways
        board = Board("r3k2r/pppqpppp/2n2n2/3p4/3P4/2N2N2/PPPQPPPP/R3K2R w KQkq - 0 1")
        moves = board.get_all_legal_moves()
        castle_moves = [move for move in moves if move.is_kingside_castle or move.is_queenside_castle]
        self.assertEqual(len(castle_moves), 2)  # Both kingside and queenside castling should be possible

    def test_pawn_promotion(self):
        """Test pawn promotion moves are correctly generated"""
        # Position with white pawn about to promote
        board = Board("8/3P4/8/8/8/8/8/k6K w - - 0 1")
        moves = board.get_all_legal_moves()
        promotion_moves = [move for move in moves if move.promotion_piece is not None]
        self.assertEqual(len(promotion_moves), 4)  # Should be able to promote to Q, R, B, N

    def test_checkmate_position(self):
        """Test that no moves are available in checkmate position"""
        # Scholar's mate position
        board = Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 4")
        moves = board.get_all_legal_moves()
        self.assertEqual(len(moves), 0)  # No legal moves in checkmate

    def test_stalemate_position(self):
        """Test that no moves are available in stalemate position"""
        # Common stalemate position
        board = Board("k7/8/1Q6/8/8/8/8/7K b - - 0 1")
        moves = board.get_all_legal_moves()
        self.assertEqual(len(moves), 0)  # No legal moves in stalemate

    def test_check_evasion(self):
        """Test that only legal moves that do not enter check are generated"""
        board = Board("8/8/8/8/3r4/8/4K3/8 w - - 0 1")
        moves = board.get_all_legal_moves()
        self.assertTrue(all(board.get_piece(move.start_row, move.start_col) == piece_helper.white_king for move in moves))
        self.assertEqual(len(moves), 5)

    def test_discovered_check(self):
        """Test that discovered checks are correctly handled"""
        # Position where moving a bishop reveals a rook's check
        board = Board("8/1K6/8/8/8/8/Rb2k3/8 b - - 0 1")
        moves = board.get_all_legal_moves()
        # The bishop cannot move in a way that exposes the king to the rook
        bishop_moves = [move for move in moves if board.get_piece(move.start_row, move.start_col) == piece_helper.black_bishop]
        self.assertEqual(len(bishop_moves), 0)  # Can only move along the diagonal to maintain protection

if __name__ == '__main__':
    unittest.main() 
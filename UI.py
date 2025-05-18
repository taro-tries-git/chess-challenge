from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QSize
import sys
from main import Board, piece_helper
from timer import Timer

class ChessUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Game")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Create board widget
        self.board_widget = ChessBoardWidget()
        main_layout.addWidget(self.board_widget)
        
        # Create info panel
        info_panel = QWidget()
        info_layout = QVBoxLayout(info_panel)
        
        # Timer labels
        self.white_timer_label = QLabel("White: 3:00")
        self.black_timer_label = QLabel("Black: 3:00")
        self.white_timer_label.setStyleSheet("QLabel { font-size: 24px; }")
        self.black_timer_label.setStyleSheet("QLabel { font-size: 24px; }")
        
        # FEN label
        self.fen_label = QLabel("FEN: ")
        self.fen_label.setWordWrap(True)
        
        # Add widgets to info panel
        info_layout.addWidget(self.white_timer_label)
        info_layout.addWidget(self.black_timer_label)
        info_layout.addWidget(self.fen_label)
        info_layout.addStretch()
        
        main_layout.addWidget(info_panel)
        
        # Set size ratio between board and info panel
        main_layout.setStretch(0, 7)  # Board takes 70% of width
        main_layout.setStretch(1, 3)  # Info panel takes 30% of width

    def update_display(self, board: Board, timer: Timer):
        """Update the display with current board position and timer values"""
        # Update board
        self.board_widget.update_display(board, timer)
        
        # Update timers
        white_time_ms = timer.milliseconds_remaining if board.is_white_turn else timer.opponent_milliseconds_remaining
        black_time_ms = timer.opponent_milliseconds_remaining if board.is_white_turn else timer.milliseconds_remaining
        
        self.white_timer_label.setText(f"White: {self._format_time(white_time_ms)}")
        self.black_timer_label.setText(f"Black: {self._format_time(black_time_ms)}")
        
        # Update FEN
        self.fen_label.setText(f"FEN: {board.get_fen()}")
        
        # Force a repaint
        self.update()

    def _format_time(self, milliseconds: int) -> str:
        """Format milliseconds into MM:SS format"""
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

class ChessBoardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.board = None
        self.timer = None
        
        # Piece to image filename mapping
        self.piece_to_filename = {
            piece_helper.white_pawn: "wp.svg",
            piece_helper.white_knight: "wn.svg",
            piece_helper.white_bishop: "wb.svg",
            piece_helper.white_rook: "wr.svg",
            piece_helper.white_queen: "wq.svg",
            piece_helper.white_king: "wk.svg",
            piece_helper.black_pawn: "bp.svg",
            piece_helper.black_knight: "bn.svg",
            piece_helper.black_bishop: "bb.svg",
            piece_helper.black_rook: "br.svg",
            piece_helper.black_queen: "bq.svg",
            piece_helper.black_king: "bk.svg",
        }
        
        # Load piece images
        self.piece_images = {}
        for piece, filename in self.piece_to_filename.items():
            self.piece_images[piece] = QPixmap(f"pieces/{filename}")

    def update_display(self, board: Board, timer: Timer):
        """Update the board and timer state"""
        self.board = board
        self.timer = timer
        self.update()  # Force a repaint

    def paintEvent(self, event):
        if not self.board:
            return
            
        painter = QPainter(self)
        square_size = min(self.width(), self.height()) // 8
        
        # Draw board squares
        for row in range(8):
            for col in range(8):
                x = col * square_size
                y = (7 - row) * square_size  # Flip the board so white is at bottom
                
                # Alternate square colors
                if (row + col) % 2 == 0:
                    color = QColor(240, 217, 181)  # Light squares
                else:
                    color = QColor(181, 136, 99)   # Dark squares
                
                painter.fillRect(x, y, square_size, square_size, color)
                
                # Draw piece if present
                piece = self.board.get_piece(row, col)
                if piece != piece_helper.empty and piece in self.piece_images:
                    piece_pixmap = self.piece_images[piece]
                    scaled_pixmap = piece_pixmap.scaled(
                        square_size, 
                        square_size, 
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(x, y, scaled_pixmap)

    def resizeEvent(self, event):
        """Handle widget resize to maintain square board"""
        size = min(event.size().width(), event.size().height())
        self.setFixedSize(size, size)

def main():
    """Test the UI"""
    app = QApplication(sys.argv)
    board = Board()
    timer = Timer(180000, 0)  # 3 minutes per side, no increment
    
    window = ChessUI()
    window.update_display(board, timer)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

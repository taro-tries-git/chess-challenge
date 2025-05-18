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


def play_game(board: Board, timer: Timer, white_player: DefaultPlayer, black_player: DefaultPlayer, window: ChessUI) -> str:
    """Play a single game between two bots"""
    while True:
        # Update the display
        window.update_display(board, timer)
        QApplication.processEvents()  # Process UI events
        time.sleep(0.5)  # Add a small delay to make the game visible
        
        # Get the current player
        current_player = white_player if board.is_white_turn else black_player
        
        # Start the timer for this turn
        timer.start_turn()
        
        # Get the move from the current player
        move = current_player.think(board, timer)

        board.make_move(move)
        # End the turn and update the timer
        timer.end_turn()
        
        # Check game state
        game_state = board.get_gamestate()
        if game_state != "ongoing":
            return game_state

def main():
    # Create the application
    app = QApplication(sys.argv)
    
    # Initialize players
    player_one = PlayerOne()
    player_two = PlayerTwo()
    
    # Initialize score tracking
    scores = {
        player_one.name: 0,
        player_two.name: 0,
        "Draws": 0
    }
    
    # Create the UI window
    window = ChessUI()
    window.show()
    
    # Read positions from file
    with open("start_positions.txt", "r") as f:
        positions = [line.strip() for line in f if line.strip()]
    
    # Play each position twice (switching colors)
    for fen in positions:
        for reverse_players in [False, True]:
            # Initialize game components
            board = Board()
                
            timer = Timer(TURN_TIME_MS, INCREMENT_MS)
            
            # Set up players for this game
            white_player = player_two if reverse_players else player_one
            black_player = player_one if reverse_players else player_two
            
            print(f"\nStarting game: {white_player.name} (White) vs {black_player.name} (Black)")
            print(f"Position: {fen}")
            
            # Play the game
            result = play_game(board, timer, white_player, black_player, window)
            
            # Update scores
            if result == "checkmate":
                winner = black_player.name if board.is_white_turn else white_player.name
                scores[winner] += 1
                print(f"Game Over: {winner} wins by checkmate!")
            else:
                scores["Draws"] += 1
                print(f"Game Over: Draw by {result}!")
            
            # Print current scores
            print("\nCurrent Scores:")
            for player, score in scores.items():
                print(f"{player}: {score}")
            
            # Small delay between games
            time.sleep(2)
    
    print("\nFinal Scores:")
    for player, score in scores.items():
        print(f"{player}: {score}")
    
    # Keep the window open
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 
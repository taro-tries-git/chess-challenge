import time

class Timer:
    def __init__(self, initial_time_ms: int, increment_ms: int):
        """
        Initialize the chess timer.
        
        Args:
            initial_time_ms (int): Initial time in milliseconds for each player
            increment_ms (int): Time increment in milliseconds after each move
        """
        self.game_start_time_milliseconds = initial_time_ms
        self.increment_milliseconds = increment_ms
        
        # Initialize remaining time for both players
        self.milliseconds_remaining = initial_time_ms
        self.opponent_milliseconds_remaining = initial_time_ms
        
        # Track turn timing
        self.milliseconds_elapsed_this_turn = 0
        self._turn_start_time = None
        self._is_running = False

    def start_turn(self):
        """Start the timer for the current player's turn."""
        if not self._is_running:
            self._turn_start_time = time.time()
            self._is_running = True
            self.milliseconds_elapsed_this_turn = 0

    def end_turn(self):
        """
        End the current player's turn, apply time increment, and switch players.
        Returns the elapsed time for the turn in milliseconds.
        """
        if self._is_running:
            current_time = time.time()
            elapsed = int((current_time - self._turn_start_time) * 1000)
            self.milliseconds_elapsed_this_turn = elapsed
            
            # Update remaining time and add increment
            self.milliseconds_remaining -= elapsed
            self.milliseconds_remaining += self.increment_milliseconds
            
            # Switch players
            self.milliseconds_remaining, self.opponent_milliseconds_remaining = (
                self.opponent_milliseconds_remaining,
                self.milliseconds_remaining
            )
            
            self._is_running = False
            self._turn_start_time = None
            
            return elapsed
        return 0

    def update(self):
        """
        Update the elapsed time for the current turn.
        Should be called periodically to update the display.
        """
        if self._is_running and self._turn_start_time is not None:
            current_time = time.time()
            self.milliseconds_elapsed_this_turn = int((current_time - self._turn_start_time) * 1000)
            return self.milliseconds_elapsed_this_turn
        return 0

    def get_current_player_time(self) -> int:
        """Get the current player's remaining time in milliseconds."""
        if self._is_running:
            return max(0, self.milliseconds_remaining - self.milliseconds_elapsed_this_turn)
        return self.milliseconds_remaining

    def is_time_up(self) -> bool:
        """Check if the current player has run out of time."""
        return self.get_current_player_time() <= 0

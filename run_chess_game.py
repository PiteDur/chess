#!/usr/bin/env python3
"""
Example script to run the chess game viewer.

This script demonstrates how to start a new chess game with the GUI.
"""

import sys
from pathlib import Path

# Add pieces_board to path
sys.path.insert(0, str(Path(__file__).parent / "pieces_board"))

from chess import board
from chess_viewer.chess_game_viewer import ChessGameViewer


def main():
    """Start a new chess game with the default starting position.

    Returns:
        None

    This function:
        - creates a board instance
        - initializes a ChessGameViewer
        - starts the pygame main loop
    """
    print("="*50)
    print("Chess Game Viewer")
    print("="*50)
    
    # Create a new board (starting position)
    print("\nInitializing game...")
    game_board = board()
    
    # Create the viewer with default colors
    print("Starting GUI...")
    viewer = ChessGameViewer(
        game_board,
        width=1200,
        height=800,
        square_size=80,
        light_color=(220, 220, 220),  # Light gray
        dark_color=(255, 255, 255)     # White
    )
    
    # Start the game
    print("\nGame is starting. Rules:")
    print("1. Click a piece to select it (gold highlight)")
    print("2. Click a destination square (green dot) to move")
    print("3. Valid moves only - illegal moves will be rejected")
    print("4. Game ends with checkmate, stalemate, or draw")
    print("\nClose the window to exit.\n")
    
    viewer.start_game()


def main_with_custom_position():
    """Start a game from a custom board position.

    Returns:
        None

    This function:
        - defines a custom piece placement dictionary
        - rebuilds the board with create_board(positions=(...,'w'))
        - launches the viewer on that board state
    """
    print("="*50)
    print("Chess Game - Custom Position")
    print("="*50)
    
    game_board = board()
    
    # Create a custom starting position
    # (This would be a board after some moves)
    custom_positions = {
        'P': ['e4', 'f2', 'g2', 'h2'],
        'p': ['e5', 'f7', 'g7', 'h7'],
        'R': ['a1', 'h1'],
        'N': ['b1', 'g1'],
        'B': ['c1', 'f1'],
        'Q': ['d1'],
        'K': ['e1'],
        'r': ['a8', 'h8'],
        'n': ['b8', 'g8'],
        'b': ['c8', 'f8'],
        'q': ['d8'],
        'k': ['e8']
    }
    
    # Create board from custom position with white to move
    board_array = game_board.create_board(positions=(custom_positions, 'w'))
    
    # Create and run viewer
    viewer = ChessGameViewer(game_board)
    print("Starting game from custom position...")
    viewer.current_board = board_array
    viewer.run()


if __name__ == "__main__":
    try:
        # Uncomment the line below to start from a custom position
        # main_with_custom_position()
        
        # Run the standard game
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

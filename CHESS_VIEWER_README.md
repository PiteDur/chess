# Chess Game Viewer - User Guide

A fully-featured chess game with visual GUI, move validation, and game-end detection.

## Features

- **Interactive Board**: Click-to-select, click-to-move interface
- **Move Validation**: Full chess rule enforcement (check, checkmate, castling, en passant, pawn promotion)
- **Game-End Detection**: Automatic detection of checkmate, stalemate, and draw conditions
- **Score Tracking**: Real-time material count and captured pieces display
- **Visual Feedback**: Legal moves highlighted, selected piece highlighted

## Installation

1. Ensure Python 3.10+ is installed
2. Install required packages:
   ```bash
   pip install pygame numpy
   ```

3. Ensure piece images are in the `pieces_png/` folder with subfolders:
   - White pieces in `pieces_png/white/`:
     - `P.png` (white pawn), `R.png` (white rook), `N.png` (white knight)
     - `B.png` (white bishop), `Q.png` (white queen), `K.png` (white king)
   - Black pieces in `pieces_png/black/`:
     - `p.png` (black pawn), `r.png` (black rook), `n.png` (black knight)
     - `b.png` (black bishop), `q.png` (black queen), `k.png` (black king)

## Quick Start

```python
from chess import board
from chess_viewer.chess_game_viewer import ChessGameViewer

# Create a new game
game_board = board()
viewer = ChessGameViewer(game_board)
viewer.start_game()
```

## How to Play

1. **Select a Piece**: Click on one of your pieces (white pieces at start)
   - The piece will be highlighted in gold
   - Legal moves appear as green dots on the board

2. **Move the Piece**: Click on a destination square to move
   - The move is validated automatically
   - Turn switches to opponent after legal move
   - Illegal moves are rejected with a console error message

3. **Special Moves**:
   - **Castling**: Move king toward rook (handled automatically)
   - **En Passant**: Capture opponent pawn diagonally (handled automatically)
   - **Pawn Promotion**: Pawn reaching 1st or 8th rank auto-promotes to queen

4. **Game End**:
   - When checkmate or stalemate occurs, a message appears
   - Click the window close button or press Ctrl+C to exit

## Customization

### Custom Board Colors

```python
viewer = ChessGameViewer(
    game_board,
    light_color=(200, 200, 220),  # Light blue-gray
    dark_color=(255, 255, 255)     # White
)
```

### Different Board Size

```python
viewer = ChessGameViewer(
    game_board,
    square_size=100,  # Default is 80 pixels per square
    width=1400,
    height=900
)
```

## Game Rules Implemented

### Move Validation
- Piece-specific movement rules (pawn forward, rook straight, bishop diagonal, etc.)
- Turn alternation (white then black)
- Destination square legality (empty or opponent piece)
- Check prevention (cannot move into or leave king in check)

### Special Moves
- **Castling**: King and rook move together if unobstructed and not previously moved
- **En Passant**: Pawn captures opponent pawn after its double-step advance
- **Pawn Promotion**: Pawn reaching opposite rank automatically promotes to queen

### Game End Conditions
- **Checkmate**: No legal moves + king in check → Opponent wins
- **Stalemate**: No legal moves + king not in check → Draw
- **50-Move Rule**: 50 consecutive moves without pawn move or capture → Draw
- **Three-Fold Repetition**: Same position repeated 3 times (implemented in detection)

## Architecture

### Piece Classes
- `pawn`: Forward movement, diagonal captures, en passant
- `rook`: Straight movement along ranks and files
- `knight`: L-shaped jumps ignoring obstacles
- `bishop`: Diagonal movement
- `queen`: Combined rook and bishop movement
- `king`: Single square movement, special castling rules

### Board Class
Manages game state:
- Board array (8x8 numpy array with piece characters)
- Turn tracking (white/black)
- Move history (for en passant and castling validation)
- Score calculation (material values)

### Rules Class
Validates movements:
- Legal piece movement checking
- Check/checkmate detection
- Special move validation (castling, en passant)
- Self-check prevention

### ChessGameViewer Class
Handles GUI:
- Pygame event loop
- Board rendering and piece drawing
- Click event processing
- Score/capture display
- Game-end overlay

## Troubleshooting

### "ModuleNotFoundError: No module named 'pygame'"
```bash
pip install pygame
```

### Pieces not displaying
- Ensure PNG files are in the `pieces_png/white/` and `pieces_png/black/` folders
- Check file names are exactly: `P.png`, `p.png`, etc. (uppercase for white, lowercase for black)
- PNG files should be square (e.g., 80x80 pixels)

### Move accepted but board doesn't update
- There may be an exception in the UI. Check the console output
- Ensure all coordinates are valid (a-h, 1-8)

### Cannot move pieces
- Check that it's your turn (turn indicator in sidebar)
- Ensure the destination is highlighted green (legal move)
- Kings cannot move into check

## Development

### Testing Game Logic
```python
from chess import board, rules

b = board()
game_board = b.create_board()

# Test a move
game_board = b.move_piece(game_board, ("Pe2", "e4"))
b.turn = "black"

# Check game status
game_over, message, winner = b.check_game_end(game_board)
print(f"Game over: {game_over}, Message: {message}")
```

### Extending the Viewer
Create custom viewers by subclassing `ChessGameViewer`:
```python
class CustomViewer(ChessGameViewer):
    def _draw_side_panel(self):
        # Custom score display logic
        super()._draw_side_panel()
```

## Performance Notes

- Move validation: ~1-5ms per move (depends on board complexity)
- Legal move calculation: ~5-20ms per piece (depends on piece type)
- Rendering: 60 FPS target (smooth gameplay on modern systems)

## License

See LICENSE.md in project root

## Support

For issues or contributions, refer to the project repository.

---

**Enjoy playing chess!** ♟️♖

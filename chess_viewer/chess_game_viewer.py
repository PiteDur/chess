"""
Chess Game Viewer - Interactive GUI for Chess Game

This module provides a graphical interface for playing chess using the rules
and board logic from chess.py. Uses pygame for rendering and user interaction.

Features:
- Clickable board squares for piece selection and movement
- Color-customizable board (default: light gray and white)
- Piece images displayed on top of squares
- Side panel showing scores and captured pieces
- Coordinate labels (a-h, 1-8) on board edges

https://www.google.com/search?q=chess+pieces+no+background&client=firefox-b-d&hs=F2zU&sca_esv=1a51245140343e35&udm=2&biw=1920&bih=955&sxsrf=ANbL-n5n5G-KatetLpFulZyXl_b5A7yUKA%3A1775590228382&ei=VFvVaenuFtqvkdUPhaOiuAE&ved=0ahUKEwjp6NCGvdyTAxXaV6QEHYWRCBcQ4dUDCBI&uact=5&oq=chess+pieces+no+background&gs_lp=Egtnd3Mtd2l6LWltZyIaY2hlc3MgcGllY2VzIG5vIGJhY2tncm91bmQyCBAAGBMYBxgeMgcQABiABBgTSNQTUN0CWL0ScAF4AJABAJgBSaAB-QKqAQE3uAEDyAEA-AEBmAIIoAKWA8ICCBAAGBMYCBgewgIGEAAYBxgewgIIEAAYBRgHGB7CAggQABgTGAUYHpgDAIgGAZIHATigB-YesgcBN7gHjgPCBwUwLjUuM8gHFIAIAA&sclient=gws-wiz-img#sv=CAMSVhoyKhBlLXhIeDFHaVBsdXBrcEdNMg54SHgxR2lQbHVwa3BHTToOSjRiU0lvU0I3ZVNkd00gBCocCgZtb3NhaWMSEGUteEh4MUdpUGx1cGtwR00YADABGAcgz_ihvQ1KCBABGAEgASgB
"""

import pygame
import sys
from pathlib import Path


class ChessGameViewer:
    """
    Graphical interface for chess game using pygame.
    
    Parameters:
    -----------
    - board_obj: board instance from chess.py
    - width: pixel width of the window (default 1200)
    - height: pixel height of the window (default 800)
    - square_size: pixel size of each board square (default 80)
    - light_color: RGB tuple for light squares (default light gray)
    - dark_color: RGB tuple for dark squares (default white)
    """
    
    def __init__(self, board_obj, width=1200, height=800, square_size=80,
                 light_color=(220, 220, 220), dark_color=(255, 255, 255)):
        """Initialize the chess game viewer.

        Args:
            board_obj (board): Game board controller from chess.py.
            width (int): Window width in pixels.
            height (int): Window height in pixels.
            square_size (int): Size of each board square in pixels.
            light_color (tuple): RGB color for light squares.
            dark_color (tuple): RGB color for dark squares.

        Attributes:
            self.current_board (ndarray): Current board state.
            self.selected_square (str|None): Selected square like 'e2'.
            self.possible_moves (list): Legal destination squares for selected piece.
            self.game_over (bool): Whether the game is finished.
            self.game_message (str): Message displayed when the game ends.
        """
        pygame.init()
        
        self.board_obj = board_obj
        self.width = width
        self.height = height
        self.square_size = square_size
        self.light_color = light_color
        self.dark_color = dark_color
        
        # Board display position
        self.board_x = 50
        self.board_y = 50
        self.board_size = 8 * square_size
        
        # Side panel position
        self.panel_x = self.board_x + self.board_size + 30
        self.panel_y = self.board_y
        self.panel_width = width - self.panel_x - 20
        self.panel_height = height - 100
        
        # Game state
        self.current_board = None
        self.selected_square = None
        self.possible_moves = []
        self.game_over = False
        self.game_message = ""
        
        # Initialize display
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Chess Game Viewer")
        self.clock = pygame.time.Clock()
        
        # Load piece images
        self.piece_images = self._load_piece_images()
        
        # Font for text rendering
        self.font_large = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
    
    def _load_piece_images(self):
        """Load piece images from the pieces folder.

        Returns:
            dict: Mapping piece characters like 'P' or 'k' to pygame Surface objects.
        """
        piece_images = {}
        pieces_dir = Path(__file__).parent.parent / "pieces"
        
        piece_names = ["P", "R", "N", "B", "K", "Q", "p", "r", "n", "b", "k", "q"]
        
        for piece in piece_names:
            path = pieces_dir / f"{piece}.png"
            try:
                img = pygame.image.load(str(path))
                # Scale image to fit square with some padding
                img = pygame.transform.scale(img, (self.square_size - 10, self.square_size - 10))
                piece_images[piece] = img
            except FileNotFoundError:
                print(f"Warning: Image for piece '{piece}' not found at {path}")
                piece_images[piece] = None
        
        return piece_images
    
    def start_game(self):
        """Initialize and start the game loop."""
        self.current_board = self.board_obj.create_board()
        self.game_over = False
        self.game_message = ""
        self.run()
    
    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    self._handle_click(event.pos)
            
            self._draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _handle_click(self, pos):
        """Handle mouse click on the board.

        Args:
            pos (tuple): Mouse position in pixels (x, y).

        This method updates:
            - self.selected_square when the user selects a piece or a new square
            - self.possible_moves for the selected piece
            - executes a move when the second click is valid
        """
        # Check if click is within board bounds
        if not (self.board_x <= pos[0] < self.board_x + self.board_size and
                self.board_y <= pos[1] < self.board_y + self.board_size):
            return
        
        # Convert pixel position to board square
        col = (pos[0] - self.board_x) // self.square_size
        row = (pos[1] - self.board_y) // self.square_size
        square = self._index_to_square(row, col)
        
        if self.selected_square is None:
            # First click: select a piece
            piece = self.current_board[row][col]
            if piece != " " and ((piece.isupper() and self.board_obj.turn == "white") or
                                 (piece.islower() and self.board_obj.turn == "black")):
                self.selected_square = square
                self._update_possible_moves(row, col, piece)
        else:
            # Second click: move piece
            if square == self.selected_square:
                # Deselect if clicking same square
                self.selected_square = None
                self.possible_moves = []
            elif square in self.possible_moves:
                # Execute move
                self._execute_move(self.selected_square, square)
                self.selected_square = None
                self.possible_moves = []
            else:
                # Select different piece
                piece = self.current_board[row][col]
                if piece != " " and ((piece.isupper() and self.board_obj.turn == "white") or
                                     (piece.islower() and self.board_obj.turn == "black")):
                    self.selected_square = square
                    self._update_possible_moves(row, col, piece)
                else:
                    self.selected_square = None
                    self.possible_moves = []
    
    def _index_to_square(self, row, col):
        """Convert board indices to algebraic notation."""
        return chr(ord('a') + col) + str(8 - row)
    
    def _update_possible_moves(self, row, col, piece):
        """Update list of possible moves for selected piece.

        Args:
            row (int): Board row index (0-7).
            col (int): Board column index (0-7).
            piece (str): Piece character at the selected square.

        Side effects:
            - sets self.possible_moves to the list of legal target squares.
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "pieces_board"))
        from chess import pawn, rook, knight, bishop, queen, king
        
        piece_map = {
            'p': pawn, 'P': pawn,
            'r': rook, 'R': rook,
            'n': knight, 'N': knight,
            'b': bishop, 'B': bishop,
            'q': queen, 'Q': queen,
            'k': king, 'K': king,
        }
        
        PieceClass = piece_map.get(piece.lower())
        if PieceClass:
            piece_obj = PieceClass(piece)
            square = self._index_to_square(row, col)
            self.possible_moves = piece_obj.possible_moves(square, self.current_board, 
                                                           self.board_obj.last_move if hasattr(self.board_obj, 'last_move') else [])

    
    def _execute_move(self, from_square, to_square):
        """Execute a move and update the board.

        Args:
            from_square (str): Source square in algebraic notation like 'e2'.
            to_square (str): Destination square in algebraic notation like 'e4'.

        Side effects:
            - updates self.current_board with the new position
            - toggles self.board_obj.turn between 'white' and 'black'
            - updates self.game_over and self.game_message if the game ends
        """
        piece = self.current_board[8 - int(from_square[1])][ord(from_square[0]) - ord('a')]
        move = (piece + from_square, to_square)
        
        try:
            self.current_board = self.board_obj.move_piece(self.current_board, move)
            # Switch turn
            self.board_obj.turn = "black" if self.board_obj.turn == "white" else "white"
            
            # Check game end condition
            game_over, message, winner = self.board_obj.check_game_end(self.current_board)
            if game_over:
                self.game_over = True
                self.game_message = message
        
        except ValueError as e:
            print(f"Illegal move: {e}")
            self.selected_square = None
            self.possible_moves = []
    
    def _draw(self):
        """Render the game state to the screen.

        This method draws the board, the sidebar, and the end-game message if needed.
        """
        self.screen.fill((240, 240, 240))
        
        # Draw board
        self._draw_board()
        
        # Draw side panel
        self._draw_side_panel()
        
        # Draw game over message if game ended
        if self.game_over:
            self._draw_game_over_message()
        
        pygame.display.flip()
    
    def _draw_board(self):
        """Draw the chess board with pieces and coordinates.

        This method renders:
            - the 8x8 board grid
            - algebraic labels on the left and bottom edges
            - piece sprites on occupied squares
            - the selected square highlight and legal move markers
        """
        # Draw squares and coordinates
        for row in range(8):
            for col in range(8):
                x = self.board_x + col * self.square_size
                y = self.board_y + row * self.square_size
                
                # Alternate colors for checkered pattern
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
                
                # Draw border
                pygame.draw.rect(self.screen, (100, 100, 100), (x, y, self.square_size, self.square_size), 1)
        
        # Draw coordinate labels (left side: ranks)
        for rank in range(8):
            y = self.board_y + rank * self.square_size + self.square_size // 2
            text = self.font_small.render(str(8 - rank), True, (0, 0, 0))
            self.screen.blit(text, (self.board_x - 25, y - 10))
        
        # Draw coordinate labels (bottom: files)
        for file in range(8):
            x = self.board_x + file * self.square_size + self.square_size // 2
            text = self.font_small.render(chr(ord('a') + file), True, (0, 0, 0))
            self.screen.blit(text, (x - 8, self.board_y + self.board_size + 5))
        
        # Draw pieces
        for row in range(8):
            for col in range(8):
                piece = self.current_board[row][col]
                if piece != " ":
                    x = self.board_x + col * self.square_size + 5
                    y = self.board_y + row * self.square_size + 5
                    if self.piece_images[piece]:
                        self.screen.blit(self.piece_images[piece], (x, y))
        
        # Draw selected square highlight
        if self.selected_square:
            col = ord(self.selected_square[0]) - ord('a')
            row = 8 - int(self.selected_square[1])
            x = self.board_x + col * self.square_size
            y = self.board_y + row * self.square_size
            pygame.draw.rect(self.screen, (255, 200, 0), (x, y, self.square_size, self.square_size), 3)
        
        # Draw possible moves
        for move_square in self.possible_moves:
            col = ord(move_square[0]) - ord('a')
            row = 8 - int(move_square[1])
            x = self.board_x + col * self.square_size + self.square_size // 2
            y = self.board_y + row * self.square_size + self.square_size // 2
            pygame.draw.circle(self.screen, (0, 255, 0), (x, y), 5)
    
    def _draw_side_panel(self):
        """Draw the side panel with scores, captured pieces, and current turn.

        This method renders:
            - score values for white and black
            - lists of captured pieces for each side
            - current player's turn
        """
        # Background
        pygame.draw.rect(self.screen, (230, 230, 230), 
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (self.panel_x, self.panel_y, self.panel_width, self.panel_height), 2)
        
        # Get scores and lost pieces
        (white_score, black_score), lost_pieces = self.board_obj.calculate_scores(self.current_board)
        
        # Draw scores
        y_offset = self.panel_y + 20
        title = self.font_large.render("Scores", True, (0, 0, 0))
        self.screen.blit(title, (self.panel_x + 10, y_offset))
        
        y_offset += 40
        white_text = self.font_small.render(f"White: {white_score}", True, (0, 0, 0))
        self.screen.blit(white_text, (self.panel_x + 10, y_offset))
        
        y_offset += 30
        black_text = self.font_small.render(f"Black: {black_score}", True, (0, 0, 0))
        self.screen.blit(black_text, (self.panel_x + 10, y_offset))
        
        # Draw captured pieces
        y_offset += 50
        captured_title = self.font_large.render("Captured", True, (0, 0, 0))
        self.screen.blit(captured_title, (self.panel_x + 10, y_offset))
        
        y_offset += 40
        white_lost_text = self.font_small.render(f"White lost: {len(lost_pieces['white'])}", True, (0, 0, 0))
        self.screen.blit(white_lost_text, (self.panel_x + 10, y_offset))
        
        y_offset += 25
        white_pieces_str = " ".join(lost_pieces['white'][:10])  # Show first 10
        white_pieces_text = self.font_tiny.render(white_pieces_str, True, (80, 80, 80))
        self.screen.blit(white_pieces_text, (self.panel_x + 10, y_offset))
        
        y_offset += 35
        black_lost_text = self.font_small.render(f"Black lost: {len(lost_pieces['black'])}", True, (0, 0, 0))
        self.screen.blit(black_lost_text, (self.panel_x + 10, y_offset))
        
        y_offset += 25
        black_pieces_str = " ".join(lost_pieces['black'][:10])  # Show first 10
        black_pieces_text = self.font_tiny.render(black_pieces_str, True, (80, 80, 80))
        self.screen.blit(black_pieces_text, (self.panel_x + 10, y_offset))
        
        # Draw current turn
        y_offset += 50
        turn_text = self.font_small.render(f"Turn: {self.board_obj.turn}", True, (0, 0, 0))
        self.screen.blit(turn_text, (self.panel_x + 10, y_offset))
    
    def _draw_game_over_message(self):
        """Draw game over message overlay.

        This method displays a semi-transparent dark overlay and the final game message.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Message box
        msg_text = self.font_large.render(self.game_message, True, (255, 255, 255))
        msg_rect = msg_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(msg_text, msg_rect)
        
        # Instructions
        instr_text = self.font_small.render("Press Q to quit or close the window", True, (200, 200, 200))
        instr_rect = instr_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(instr_text, instr_rect)


if __name__ == "__main__":
    # Example usage
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "pieces_board"))
    from chess import board
    
    game_board = board()
    viewer = ChessGameViewer(game_board)
    viewer.start_game()

""""
Chess: Rules, Board and Pieces

GOAL : creation of my own chess game with IA assistance and possibility to train an IA to play chess against me.
IN THIS FILE :   
    1- definition of the board and its methods
    2- definition of the rules and how to check if a move is legal or not
    3- definition of the pieces and their methods
"""

import numpy as np


# helper functions for coordinate conversion

def _algebraic_to_index(pos: str) -> tuple:
    """Convert a square like "e4" or "Pe4" into board indices (row, col).

    The board array uses row 0 for the 8th rank and row 7 for the 1st rank.
    Columns go from 0 ('a') to 7 ('h').
    """
    if len(pos) > 2:
        pos = pos[1:3]

    col = ord(pos[0].lower()) - ord("a")
    row = 8 - int(pos[1])
    return (row, col)


def _square_from_notation(pos: str) -> str:
    """Return the square portion of piece-prefixed input like 'Pe4'."""
    return pos[1:3] if len(pos) > 2 else pos



def _index_to_algebraic(row: int, col: int) -> str:
    """Convert board indices back to algebraic notation.

    Reverse of :func:`_algebraic_to_index`.
    """
    return chr(col + ord("a")) + str(8 - row)


# DEFINITION OF THE BOARD
class board :
    """
    This class represents the chess board and its methods.

    Parameters :
    ------------
     - color: str, color displayed at the bottom of the board. Def.: "white".
     
     

    Methods :
    ---------
    - create_board:  initializes the board with the pieces in their starting positions.
    - display_board: returns the current state of the board.
    - display_positions: returns a dictionary that maps the positions 
        of the pieces on the board to their corresponding piece objects.
    - move_piece: returns a new board with the piece moved from its current position to the new position
    - calculate_scores: calculates the scores for each player based on the pieces they have on the board 

    

    Improving ideas :
    -----------------
    - method to translates moves in std notation (and vice versa) 

    """

    def __init__(self, color = "white", last_move = None):
        self.color = color
        self.last_move = [] if last_move is None else list(last_move)
        self.turn = "white"

    def create_board(self, positions=None):
        """
        Returns a 2D array representing the chess board and its pieces.

        Parameters: 
        -----------
        - positions: optional tuple (positions_dict, turn_char).
            positions_dict should match display_positions() output, e.g. {'P': ['e2'], 'k': ['e8']}.
            turn_char should be 'w' or 'b' to indicate which player moves next.

        If no positions tuple is provided, the standard starting position is returned.
        """
        if positions is None:
            return np.array(
                    [["r", "n", "b", "q", "k", "b", "n", "r"],
                    ["p", "p", "p", "p", "p", "p", "p", "p"],
                    [" ", " ", " ", " ", " ", " ", " ", " "],
                    [" ", " ", " ", " ", " ", " ", " ", " "],
                    [" ", " ", " ", " ", " ", " ", " ", " "],
                    [" ", " ", " ", " ", " ", " ", " ", " "],
                    ["P", "P", "P", "P", "P", "P", "P", "P"],
                    ["R", "N", "B", "Q", "K", "B", "N", "R"]])

        if not isinstance(positions, tuple) or len(positions) != 2:
            raise ValueError("positions must be a tuple: (positions_dict, turn_char).")

        positions_dict, turn_char = positions
        if not isinstance(positions_dict, dict):
            raise ValueError("First element of positions must be a dictionary.")
        if not isinstance(turn_char, str) or turn_char.lower() not in ("w", "b"):
            raise ValueError("Second element of positions must be 'w' or 'b'.")

        self.turn = "white" if turn_char.lower() == "w" else "black"

        board = np.full((8, 8), " ", dtype=object)
        for piece, squares in positions_dict.items():
            if not isinstance(squares, (list, tuple)):
                raise ValueError("Piece positions must be a list or tuple of square strings.")
            for square in squares:
                board[_algebraic_to_index(square)] = piece
        return board


    def move_piece(self, actual_board, move, promotion_piece=None):
        """
        Returns a new board with the piece moved from its current position to the new position.

        Parameters:
        -----------
        - actual_board: 2D array representing the chess board and its pieces.
        - move: tuple of str, the first string contains piece and source square and the second string contains piece and destination square.
            Example: ("Pe2", "Pe4"). Both plain squares ("e4") and piece-prefixed squares ("Pe4") are normalized internally.
        - promotion_piece: str, optional. The piece to promote a pawn to ('Q', 'R', 'N', 'B' for white, lowercase for black).
                         If None and a pawn reaches the last rank, defaults to 'Q' or 'q'.
        
        """
        if not isinstance(move, tuple) or len(move) != 2:
            raise ValueError("Move must be a tuple of (piece_and_source, destination).")

        # normalize user input like ('Pe2','Pe4') to internal squares 'e2' and 'e4'
        departure = _square_from_notation(move[0])
        destination = _square_from_notation(move[1])

        # validate the move using the rules engine before changing the board
        rule = rules(move, self.last_move, actual_board)
        if not rule.check_all():
            raise ValueError(f"Illegal move: {rule.message}")

        new_board = np.copy(actual_board)
        origin_idx = _algebraic_to_index(departure)
        dest_idx = _algebraic_to_index(destination)
        piece = move[0][0]

        if rule.is_castle_move():
            new_board[origin_idx] = " "
            new_board[dest_idx] = piece
            if destination in ("g1", "g8"):
                rook_from = _algebraic_to_index("h1" if destination == "g1" else "h8")
                rook_to = _algebraic_to_index("f1" if destination == "g1" else "f8")
            else:
                rook_from = _algebraic_to_index("a1" if destination == "c1" else "a8")
                rook_to = _algebraic_to_index("d1" if destination == "c1" else "d8")
            new_board[rook_to] = new_board[rook_from]
            new_board[rook_from] = " "
        else:
            if rule.is_en_passant_move():
                capture_row = origin_idx[0]
                capture_col = dest_idx[1]
                new_board[capture_row][capture_col] = " "

            final_piece = piece
            if piece.lower() == "p" and dest_idx[0] in (0, 7):
                # Pawn promotion
                if promotion_piece is None:
                    final_piece = "Q" if piece.isupper() else "q"
                else:
                    final_piece = promotion_piece

            new_board[origin_idx] = " "
            new_board[dest_idx] = final_piece

        self.last_move.append(move)
        return new_board



    def display_board(self, board):
        """
        Returns a dictionnary in which keys are the squares and values are the content of the square (empty or piece).

        parameters:
        -----------
        - board: 2D array representing the chess board and its pieces.
        """
        d = {}
        for row, i in zip(board,range(8)):
            for square,j in zip(row, range(97, 105)):
                d[chr(j)+str(8-i)] = square
        return d

    def display_positions(self, board):
        """
        Returns a dictionnary in which keys are the pieces and values are the squares they occupy on the board.

        parameters:
        -----------
        - board: 2D array representing the chess board and its pieces.
        """ 

        d = {}
        for row, i in zip(board,range(8)):
            for square,j in zip(row, range(97, 105)):
                if square != " ":
                    if square in d.keys():
                        d[square].append(chr(j)+str(8-i))
                    else:
                        d[square] = [chr(j)+str(8-i)]
        return d
    




    def calculate_scores(self, board):
        """
        Returns cumulative scores and the lost pieces list for each player.

        The function deduces lost pieces from the current board compared to the
        standard starting material count.

        Returns:
        --------
        - tuple: ((white_score, black_score), {"white": lost_white, "black": lost_black})

        Parameters:
        -----------
        - board: 2D array representing the chess board and its pieces.
        """
        white_score = 0
        black_score = 0
        counts = {"white": {}, "black": {}}

        for row in board:
            for square in row:
                if square == " ":
                    continue
                color = "white" if square.isupper() else "black"
                counts[color][square] = counts[color].get(square, 0) + 1
                if color == "white":
                    white_score += {"P": 1, "R": 5, "N": 3, "B": 3, "Q": 9, "K": 0}[square]
                else:
                    black_score += {"p": 1, "r": 5, "n": 3, "b": 3, "q": 9, "k": 0}[square]

        starting_counts = {
            "white": {"P": 8, "R": 2, "N": 2, "B": 2, "Q": 1, "K": 1},
            "black": {"p": 8, "r": 2, "n": 2, "b": 2, "q": 1, "k": 1},
        }

        lost = {"white": [], "black": []}
        for color in ("white", "black"):
            for piece, start_count in starting_counts[color].items():
                current_count = counts[color].get(piece, 0)
                missing = start_count - current_count
                if missing > 0:
                    lost[color].extend([piece] * missing)

        return (white_score, black_score), lost

    def check_game_end(self, board):
        """
        Check if the game has ended due to checkmate, stalemate, or other draw conditions.

        Returns:
        --------
        - tuple: (game_over: bool, message: str, winner: str)
            - game_over: True if game has ended
            - message: Description of the end condition (e.g., "Checkmate!", "Stalemate!")
            - winner: "white", "black", or "draw" (empty string if game not over)

        Parameters:
        -----------
        - board: 2D array representing the current board state
        """
        current_player = self.turn
        opponent = "black" if current_player == "white" else "white"
        
        # Check if current player has any legal moves
        has_legal_move = False
        
        # Scan all pieces of the current player
        piece_char = "P" if current_player == "white" else "p"
        for row in range(8):
            for col in range(8):
                piece = board[row, col]
                if piece == " " or (piece.isupper() != (current_player == "white")):
                    continue
                
                # Get possible moves for this piece
                origin_square = _index_to_algebraic(row, col)
                try:
                    piece_obj = self._get_piece_object(piece)
                    possible_moves = piece_obj.possible_moves(origin_square, board, self.last_move)
                    
                    # Test each possible move for legality
                    for dest_square in possible_moves:
                        move = (piece + origin_square, dest_square)
                        try:
                            rule = rules(move, self.last_move, board)
                            if rule.check_all():
                                has_legal_move = True
                                break
                        except:
                            pass
                    
                    if has_legal_move:
                        break
                except:
                    pass
            
            if has_legal_move:
                break
        
        # If no legal moves found, determine if it's checkmate or stalemate
        if not has_legal_move:
            # Create a temporary rule object to check for check
            dummy_move = (("P" if current_player == "white" else "p") + "a1", "a2")
            temp_rule = rules(dummy_move, self.last_move, board)
            
            if temp_rule._king_in_check(current_player == "white", board=board):
                # Checkmate
                winner = opponent
                message = f"Checkmate! {opponent.capitalize()} wins!"
                return (True, message, winner)
            else:
                # Stalemate
                message = "Stalemate! Game is a draw."
                return (True, message, "draw")
        
        # Check for draw conditions: threefold repetition or 50-move rule
        if len(self.last_move) >= 50:
            move_count = 0
            for move in reversed(self.last_move):
                piece = move[0][0]
                if piece.lower() in ("p", "P") or move[1][0] != move[1][0]:  # pawn move or capture
                    break
                move_count += 1
            
            if move_count >= 50:
                message = "50-move rule: Game is a draw."
                return (True, message, "draw")
        
        # Game is still ongoing
        return (False, "", "")

    def _get_piece_object(self, piece_char):
        """Helper method to create a piece object from its character."""
        mapping = {
            "p": pawn, "P": pawn,
            "r": rook, "R": rook,
            "n": knight, "N": knight,
            "b": bishop, "B": bishop,
            "q": queen, "Q": queen,
            "k": king, "K": king,
        }
        piece_class = mapping.get(piece_char)
        if piece_class is None:
            raise ValueError(f"Unknown piece type: {piece_char}")
        return piece_class(piece_char)
            



class rules :
    """
    This class represents the rules of chess and how to check if a move is legal or not.
    It also accounts for the order of the moves: alternance between white and black pieces.

    Parameters: 
    -----------
    - move: tuple of str, the move being made. It can be "P" for pawn, "R" for rook, 
        "N" for knight, "B" for bishop, "Q" for queen and "K" for king. Than we have 
        the square of departure and the square of arrival (e.g. "Qe2" for white Queen on the square e2).
    - last_move: list of str, all moves made since the beginning of the game. It is used to check for the taken in passing rule.
    - board: 2D array representing the chess board and its pieces.
    
    Methods:
    --------
    - check_move: is the move in the list of possible moves for the piece? (in which case the move is legal)
    - check_checked: is the king in check ? (in which case the move is not legal)
    - check_checking: is the move putting the king in check ? (in which case the move is not legal)
    - check pat: is the move putting the opponent in pat ? 
        * no piece can move and the king is not in check => pat => game over => draw
        * repetition of the same position 3 times => pat => game over => draw
        * 50 moves without any capture or pawn move => pat => game over => draw
    - check castling: is the move a castling move ? in which case the move is legal if the conditions for castling are met :
        * the king and the rook involved in the castling have not moved yet (see last_move)
        * there are no pieces between the king and the rook
        * the king is not in check, and does not pass through or end up in a square that is under attack by an enemy piece
    - check_mate: is the move putting the opponent in checkmate ? (in which case the game is over and the player wins)
    - check_all: check all the previous rules and return True if the move is legal, False otherwise with a message 
        explaining why the move is not legal.


    """
    def __init__(self, move, last_move, board):
        if not isinstance(move, tuple) or len(move) != 2:
            raise ValueError("Move must be a tuple: (piece_and_source, destination).")

        self.move = move
        # normalize any piece-prefixed squares to plain algebraic form
        self.sq_departure = _square_from_notation(move[0])
        self.sq_arrival = _square_from_notation(move[1])
        self.last_move = [] if last_move is None else list(last_move)
        self.board = board
        self.piece = move[0][0]
        self.color = self.piece.isupper() # True for white pieces, False for black pieces
        self.message = ""


    def _piece_factory(self, piece_char=None):
        # create the right piece object for move validation
        if piece_char is None:
            piece_char = self.piece
        mapping = {
            "p": pawn,
            "r": rook,
            "n": knight,
            "b": bishop,
            "q": queen,
            "k": king,
        }
        piece_type = mapping.get(piece_char.lower())
        if piece_type is None:
            raise ValueError(f"Unknown piece type: {piece_char}")
        return piece_type(piece_char)

    def _board_piece(self, square, board=None):
        board = self.board if board is None else board
        return board[_algebraic_to_index(square)]

    def _same_color(self, square, board=None):
        piece = self._board_piece(square, board=board)
        return piece != " " and piece.isupper() == self.color

    def _square_under_attack(self, square, attacker_color, board=None):
        board = self.board if board is None else board
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == " " or piece.isupper() != attacker_color:
                    continue
                origin = _index_to_algebraic(r, c)
                if piece.lower() == "p":
                    attacker = pawn(piece)
                    attacks = attacker.attack_squares(origin, board)
                else:
                    attacker = self._piece_factory(piece)
                    attacks = attacker.possible_moves(origin, board, self.last_move)
                if square in attacks:
                    return True
        return False

    def _king_position(self, color, board=None):
        board = self.board if board is None else board
        target = "K" if color else "k"
        for r in range(8):
            for c in range(8):
                if board[r][c] == target:
                    return _index_to_algebraic(r, c)
        return None

    def _turn_color(self):
        return "white" if len(self.last_move) % 2 == 0 else "black"

    def is_castle_move(self):
        return self.piece.lower() == "k" and self.sq_departure in ("e1", "e8") and self.sq_arrival in ("g1", "c1", "g8", "c8")

    def is_en_passant_move(self):
        if self.piece.lower() != "p":
            return False
        origin = _algebraic_to_index(self.sq_departure)
        destination = _algebraic_to_index(self.sq_arrival)
        if self._board_piece(self.sq_arrival) != " ":
            return False
        return origin[0] != destination[0] and origin[1] != destination[1]

    def _possible_moves(self):
        if self.is_castle_move():
            return [self.sq_arrival]
        return self._piece_factory().possible_moves(self.sq_departure, self.board, self.last_move)

    def _king_in_check(self, color, board=None):
        square = self._king_position(color, board=board)
        if square is None:
            return False
        return self._square_under_attack(square, attacker_color=not color, board=board)

    def _simulate_move(self):
        new_board = np.copy(self.board)
        origin = _algebraic_to_index(self.sq_departure)
        destination = _algebraic_to_index(self.sq_arrival)
        new_board[origin] = " "
        if self.is_en_passant_move():
            new_board[origin[0]][destination[1]] = " "
        new_board[destination] = self.piece
        return new_board

    def _piece_moved(self, char, start_squares=None):
        for move in self.last_move:
            if move[0][0].lower() != char.lower():
                continue
            prior_square = _square_from_notation(move[0])
            if start_squares is None:
                return True
            if prior_square in start_squares:
                return True
        return False

    def check_castling(self):
        if not self.is_castle_move():
            self.message = "Not a castling move."
            return False
        if self._turn_color() != ("white" if self.color else "black"):
            self.message = "It is not the correct player's turn."
            return False

        if self._piece_moved("k"):
            self.message = "King has already moved."
            return False

        if self.sq_arrival in ("g1", "g8"):
            rook_square = "h1" if self.sq_arrival == "g1" else "h8"
            path = ["f1", "g1"] if self.sq_arrival == "g1" else ["f8", "g8"]
        else:
            rook_square = "a1" if self.sq_arrival == "c1" else "a8"
            path = ["d1", "c1", "b1"] if self.sq_arrival == "c1" else ["d8", "c8", "b8"]

        if self._piece_moved("r", start_squares=[rook_square]):
            self.message = "Rook has already moved."
            return False
        if self._board_piece(rook_square).lower() != "r":
            self.message = "No rook in the correct castling square."
            return False

        for square in path:
            if self._board_piece(square) != " ":
                self.message = "Pieces block the castling path."
                return False

        if self._king_in_check(self.color):
            self.message = "King is currently in check."
            return False

        for square in path:
            if square == self.sq_departure:
                continue
            if self._square_under_attack(square, attacker_color=not self.color):
                self.message = "Castling path is under attack."
                return False

        return True

    def check_move(self):
        if self._turn_color() != ("white" if self.color else "black"):
            self.message = "It is not the correct player's turn."
            return False

        if self._board_piece(self.sq_departure) != self.piece:
            self.message = "Departure square does not contain the requested piece."
            return False

        if self._same_color(self.sq_arrival):
            self.message = "Arrival square is occupied by a same-color piece."
            return False

        if self.is_castle_move():
            return self.check_castling()

        possible = self._possible_moves()
        # compare normalized destination squares against plain algebraic moves
        if self.sq_arrival not in possible:
            self.message = "Piece cannot move to the requested square."
            return False

        if self.is_en_passant_move() and self._board_piece(self.sq_arrival) != " ":
            self.message = "Invalid en passant destination."
            return False

        self.message = "Move shape is legal."
        return True

    def check_checked(self, color=None, board=None):
        if color is None:
            color = self.color
        return self._king_in_check(color, board=board)

    def check_checking(self):
        new_board = self._simulate_move()
        future_rule = rules(self.move, self.last_move, new_board)
        return future_rule.check_checked(not self.color, board=new_board)

    def check_all(self):
        if not self.check_move():
            return False

        new_board = self._simulate_move()
        if self._king_in_check(self.color, board=new_board):
            self.message = "Move would leave king in check."
            return False

        self.message = "Legal move."
        return True

    def check_pat(self):
        return False

    def check_mate(self):
        return False







class pawn : 
    """
    This class represents the pawn piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "P" for white pawn, "p" for black pawn).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (1 for pawn).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the pawn given its current position and the state of the board.
    """
    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 1

    def possible_moves(self, position, board, last_move):
        """Return all legal target squares in algebraic notation."""
        moves = []
        row, col = _algebraic_to_index(position)
        direction = -1 if self.color else 1
        start = 6 if self.color else 1

        # one step forward
        nr = row + direction
        if 0 <= nr < 8 and board[nr][col] == " ":
            moves.append((nr, col))
            # two squares from starting rank
            if row == start:
                nnr = row + 2 * direction
                if board[nnr][col] == " ":
                    moves.append((nnr, col))

        # captures
        for dc in (-1, 1):
            nc = col + dc
            nr = row + direction
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target != " " and target.isupper() != self.color:
                    moves.append((nr, nc))

        # en passant
        if last_move is not None and len(last_move) > 0 and last_move[-1][0][0].lower() == "p":
            last_origin = _algebraic_to_index(last_move[-1][0][1:])
            last_destination = _algebraic_to_index(last_move[-1][1])
            if abs(last_origin[0] - last_destination[0]) == 2:
                if last_destination[0] == row and abs(last_destination[1] - col) == 1:
                    capture_dest = (row + direction, last_destination[1])
                    if 0 <= capture_dest[0] < 8 and board[capture_dest] == " ":
                        moves.append(capture_dest)

        return [_index_to_algebraic(r, c) for r, c in moves]

    def attack_squares(self, position, board):
        row, col = _algebraic_to_index(position)
        direction = -1 if self.color else 1
        moves = []
        for dc in (-1, 1):
            nr, nc = row + direction, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                moves.append(_index_to_algebraic(nr, nc))
        return moves


class rook :
    """
    This class represents the rook piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "R" for white rook, "r" for black rook).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (5 for rook).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the rook given its current position and the state of the board.
    """


    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 5

    def possible_moves(self, position, board, last_move):
        """Rook moves along ranks and files.

        ``position`` is a square string and the returned list contains legal
        destination squares as strings. Captures are allowed but the rook will
        not jump over pieces.
        """
        moves = []
        row, col = _algebraic_to_index(position)

        # four directions
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == " ":
                    moves.append((nr, nc))
                else:
                    if target.isupper() != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc

        return [_index_to_algebraic(r, c) for r, c in moves]




class knight :
    """
    This class represents the rook piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "N" for white knight, "n" for black knight).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (3 for knight).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the rook given its current position and the state of the board.
    """

    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 3
    
    def possible_moves(self, position, board, last_move):
        """Knight jumps in an L-shape; ignores intermediate squares."""
        moves = []
        row, col = _algebraic_to_index(position)
        deltas = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for dr, dc in deltas:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == " " or target.isupper() != self.color:
                    moves.append((nr, nc))
        return [_index_to_algebraic(r, c) for r, c in moves]
    

class bishop :
    """
    This class represents the bishop piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "B" for white bishop, "b" for black bishop).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (3 for bishop).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the bishop given its current position and the state of the board.
    """

    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 3


    def possible_moves(self, position, board, last_move):
        """Bishop moves diagonally."""
        moves = []
        row, col = _algebraic_to_index(position)
        for dr, dc in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == " ":
                    moves.append((nr, nc))
                else:
                    if target.isupper() != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc
        return [_index_to_algebraic(r, c) for r, c in moves]




class queen :
    """
    This class represents the queen piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "Q" for white queen, "q" for black queen).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (9 for queen).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the queen given its current position and the state of the board.
    """

    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 9


    def possible_moves(self, position, board, last_move):
        """Queen moves along ranks, files, and diagonals."""
        moves = []
        row, col = _algebraic_to_index(position)

        # eight directions
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nr, nc = row + dr, col + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == " ":
                    moves.append((nr, nc))
                else:
                    if target.isupper() != self.color:
                        moves.append((nr, nc))
                    break
                nr += dr
                nc += dc

        return [_index_to_algebraic(r, c) for r, c in moves]
    



class king :
    """
    This class represents the king piece and its methods.

    Parameters:
    -----------
    - piece: str, the piece being represented (e.g. "K" for white king, "k" for black king).
    - color: bool, the color of the piece (True for white pieces, False for black pieces).
    - value: int, the value of the piece (0 for king).

    Methods:
    ---------
    - possible_moves: returns a list of possible moves for the king given its current position and the state of the board.
    """

    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 0

    def possible_moves(self, position, board, last_move):
        """King moves one square in any direction. Also includes castling moves."""
        moves = []
        row, col = _algebraic_to_index(position)
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target == " " or target.isupper() != self.color:
                        moves.append((nr, nc))

        # Castling moves
        if position == "e1" and self.color:  # White king at e1
            # Check kingside castling (h1)
            if board[7][7] == "R" and all(board[7][i] == " " for i in range(5, 7)):
                # Check if king and rook haven't moved (only possible if last_move is empty or they weren't the pieces moved)
                king_moved = any(move[0][0].lower() == 'k' and _square_from_notation(move[0]) == "e1" for move in last_move)
                rook_moved = any(move[0][0].lower() == 'r' and _square_from_notation(move[0]) == "h1" for move in last_move)
                if not king_moved and not rook_moved:
                    moves.append((7, 6))  # g1
            # Check queenside castling (a1)
            if board[7][0] == "R" and all(board[7][i] == " " for i in range(1, 4)):
                king_moved = any(move[0][0].lower() == 'k' and _square_from_notation(move[0]) == "e1" for move in last_move)
                rook_moved = any(move[0][0].lower() == 'r' and _square_from_notation(move[0]) == "a1" for move in last_move)
                if not king_moved and not rook_moved:
                    moves.append((7, 2))  # c1
                    
        elif position == "e8" and not self.color:  # Black king at e8
            # Check kingside castling (h8)
            if board[0][7] == "r" and all(board[0][i] == " " for i in range(5, 7)):
                king_moved = any(move[0][0].lower() == 'k' and _square_from_notation(move[0]) == "e8" for move in last_move)
                rook_moved = any(move[0][0].lower() == 'r' and _square_from_notation(move[0]) == "h8" for move in last_move)
                if not king_moved and not rook_moved:
                    moves.append((0, 6))  # g8
            # Check queenside castling (a8)
            if board[0][0] == "r" and all(board[0][i] == " " for i in range(1, 4)):
                king_moved = any(move[0][0].lower() == 'k' and _square_from_notation(move[0]) == "e8" for move in last_move)
                rook_moved = any(move[0][0].lower() == 'r' and _square_from_notation(move[0]) == "a8" for move in last_move)
                if not king_moved and not rook_moved:
                    moves.append((0, 2))  # c8

        return [_index_to_algebraic(r, c) for r, c in moves]




 

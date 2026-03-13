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
    """Convert a square like "e4" into board indices (row, col).

    The board array uses row 0 for the 8th rank and row 7 for the 1st rank.
    Columns go from 0 ('a') to 7 ('h').
    """
    col = ord(pos[0].lower()) - ord("a")
    row = 8 - int(pos[1])
    return (row, col)



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

    def __init__(self, color = "white",last_move = None,w_castling=True, b_castling=True):
        self.color = color
        self.last_move = []
        self.w_castling = w_castling
        self.b_castling = b_castling


    def create_board(self):
        """
        Returns a 2D array representing the chess board and its pieces in their starting positions.
        The pieces are represented by their initials (P for pawn, R for rook, N for knight, B for bishop, 
        Q for queen and K for king) and the color of the pieces is represented by uppercase for white and 
        lowercase for black.

        Parameters: 
        -----------
        - color: str, the color of the pieces that will be at the bottom of the board (white or black). Default: white.

        Improving idea
        --------------
        - generate an empty board
        - function to generate an intial board
        - function put pieces on an ampty board  
        """
        return np.array(
                [["r", "n", "b", "q", "k", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "Q", "K", "B", "N", "R"]])
    

    def move_piece(self, actual_board, move):
        """
        Returns a new board with the piece moved from its current position to the new position.

        Parameters:
        -----------
        - actual_board: 2D array representing the chess board and its pieces.
        - move: tuple of str, the first string is the current position of the piece moved and the second 
            string is the new position of the piece. The positions are in algebraic notation 
            (e.g. "Qe2" for white Queen on the square e2).
        
        """
        # intégrer la vérification de la légalité du coup avant de faire le move => utiliser la classe rules

            # intégrer la prise en passant
            # intégrer un choix sur la piece de promotion d'un pion si arrivé en bout de colonne
            # intégrer la vérification du mate => if mate, game over, return the winner and the final board
            # intégrer la vérification du pat => if pat, game over, return draw and the final board 

        # vérifier si on est sur un roque

        # vérifier si on est sur une prise en passant



        # updating castling status for both players
        if move[0][0] == "K":
            self.w_castling = False
        elif move[0][0] == "k":
            self.b_castling = False


        # adapting the board to the last move
        new_board = np.copy(actual_board)
        piece = move[0]
        new_board[8-int(move[0][2]), ord(move[0][1])-97] = " "
        new_board[8-int(move[1][2]), ord(move[1][1])-97] = piece

        # update the last move: used in the taken in passing rule
        self.last_move.append(move)    



        return new_board
        



    def last_move(self):
        return self.last_move

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
        Returns a tuple with the scores of each player (white, black). Each score corresponds to the sum of the values of the pieces that the player has on the board. 
        Values are given in each piece class

        Parameters:
        -----------
        - board: 2D array representing the chess board and its pieces.
        """
        scores = (0, 0)
        
        return scores
            



class rules :
    """
    This class represents the rules of chess and how to check if a move is legal or not.
    It also accounts for the order of the moves: alternance between white and black pieces.

    Parameters: 
    -----------
    - move: tuple of str, the move being made. It can be "P" for pawn, "R" for rook, 
        "N" for knight, "B" for bishop, "Q" for queen and "K" for king. Than we have 
        the square of departure and the square of arrival (e.g. "Qe2" for white Queen on the square e2).
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
    - check_mate: is the move putting the opponent in checkmate ? (in which case the game is over and the player wins)
    - check_all: check all the previous rules and return True if the move is legal, False otherwise with a message 
        explaining why the move is not legal.


    """
    def __init__(self, move, last_move, board):
        self.move = move
        self.sq_departure = move[0][1:3]
        self.sq_arrival = move[1][1:3]
        self.last_move = last_move
        self.board = board
        self.piece = move[0]
        self.color = move[0].isupper() # True for white pieces, False for black pieces


    def check_move(self):
        checked = 0
        index_sq_departure = _algebraic_to_index(self.sq_departure)
        index_sq_arrival = _algebraic_to_index(self.sq_arrival)
        
        # is the departure square occupied by the piece that is being moved ?
        if self.board[index_sq_departure] == piece :
            checked += 1

     
                    

        # is the arrival square in the list of possible moves ?
        

        


        if checked == 3 : 
            return True






# pour chaque piece il faut vérifier la couleur et la position pour vérifier la direction du move. Il faut attribuer une valeur
# pour calculer le score de chaque joueur. Il faut attribuer l'ensemble des cases possibles à partir d'une position. 

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
        """Return all legal target squares in algebraic notation (e.g. "e4").

        The argument ``position`` must be an algebraic coordinate of the pawn's
        current square. The board is the 8x8 numpy array used throughout the
        module. The returned list contains only destination squares; move legality
        (checks, en passant, promotion choice, etc.) is handled elsewhere.
        """
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


        if last_move is not None and last_move[-1][0][0].lower() == "p" : # if the last move was a pawn move
            if abs(_algebraic_to_index(last_move[-1][0][1::])[0] - _algebraic_to_index(last_move[-1][1][1::])[0]) == 2 : # if the last move was a double squares move
                    # if the arrival square of the last move is next to the departure square of the current move
                if _algebraic_to_index(last_move[-1][1][1::])[0] == row and abs(_algebraic_to_index(last_move[-1][1][1::])[1] - col) == 1 :
                    moves.append((row, col + dc)) # en passant capture  

        # convert back to algebraic coordinates
        return [_index_to_algebraic(r, c) for r, c in moves]


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
        """King moves one square in any direction (castling not implemented)."""
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

        # castling move :
            # check for castling status according to the board object (self attributes)
            # if True => check for pieces btw the k and the rook => if not, True
            # check if the king or squares of the castling are in check => if not, True
            # if True : add the corresponding squares on in the possibles moves (carreful with the 
            # symetry btw black and white)

        return [_index_to_algebraic(r, c) for r, c in moves]




 

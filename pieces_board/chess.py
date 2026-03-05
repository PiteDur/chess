""""
Chess: Rules, Board and Pieces

GOAL : creation of my own chess game with IA assistance and possibility to train an IA to play chess against me.
IN THIS FILE :   
    1- definition of the board and its methods
    2- definition of the rules and how to check if a move is legal or not
    3- definition of the pieces and their methods
"""

import numpy as np

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

    """

    def __init__(self, color = "white",last_move = None):
        self.color = color
        self.last_move = last_move

    def create_board(self):
        """
        Returns a 2D array representing the chess board and its pieces in their starting positions.
        The pieces are represented by their initials (P for pawn, R for rook, N for knight, B for bishop, 
        Q for queen and K for king) and the color of the pieces is represented by uppercase for white and 
        lowercase for black.

        Parameters: 
        -----------
        - color: str, the color of the pieces that will be at the bottom of the board (white or black). Default: white.  
        """
        if self.color == "black": 
            return np.array(
                [["R", "N", "B", "Q", "K", "B", "N", "R"],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                ["r", "n", "b", "q", "k", "b", "n", "r"]])
        else :
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
        # intégrer la vérification de la légalité du coup avant de faire le move
        if self.color == "black":
            actual_board = np.flipud(actual_board) # flip the board to display it with black pieces at the bottom


        new_board = np.copy(actual_board)
        piece = move[0]
        new_board[8-int(move[0][2]), ord(move[0][1])-97] = " "
        new_board[8-int(move[1][2]), ord(move[1][1])-97] = piece
        if self.color == "black":
            new_board = np.flipud(new_board)

        # intégrer la prise en passant
        # intégrer un choix sur la piece de promotion d'un pion si arrivé en bout de colonne
        # intégrer la vérification du mate => if mate, game over, return the winner and the final board


        # update the last move: used in the taken in passing rule
        self.last_move = move    
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
        if self.color == "black":
            board = np.flipud(board) # flip the board to display it with black pieces at the bottom
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
    - check_move: is the move in the list of possible moves for the piece ? (in which case the move is legal)
    - check_checked: is the king in check ? (in which case the move is not legal)
    - check_checking: is the move putting the king in check ? (in which case the move is not legal)
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







# pour chaque piece il faut vérifier la couleur et la position pour vérifier la direction du move. Il faut attribuer une valeur
# pour calculer le score de chaque joueur. Il faut attribuer l'ensemble des cases possibles à partir d'une position. 

class pawn : 
    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 1

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

    def possible_moves(self, position, board):
        possible_moves = []
        # check the squares in the same row and column as the rook
        for i in range(8):
            if board[position[0]][i] == " ": # empty square
                possible_moves.append((position[0], i)) 
            elif board[position[0]][i].isupper() != self.color: # if there is an opponent piece, we can capture it but we can't go further
                possible_moves.append((position[0], i))
                break
            else: # if there is a piece of the same color, we can't go further
                break
        for i in range(8):
            if board[i][position[1]] == " ": # empty square
                possible_moves.append((i, position[1]))
            elif board[i][position[1]].isupper() != self.color: # if there is an opponent piece, we can capture it but we can't go further
                possible_moves.append((i, position[1]))
                break
            else: # if there is a piece of the same color, we can't go further
                break
        return possible_moves




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

    

class bishop :
    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 3

class queen :
    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 9

class king :
    def __init__(self, piece):
        self.piece = piece
        self.color = piece.isupper()
        self.value = 0




 

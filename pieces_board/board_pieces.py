""""
Chess: Board and Pieces

GOAL : creation of my own chess game with IA assistance and possibility to train an IA to play chess against me.
IN THIS FILE :   
    1- definition of the board and its methods
    2- definition of the pieces and their methods
"""

import numpy as np

# DEFINITION OF THE BOARD
class board :
    """
    This class represents the chess board and its methods.

    Attributes :
    ------------
     - it has an attribute "board" which is a 2D array representing the chess board and its pieces.
     - it has an attribute "pieces" which is a list of all the pieces on the board.
     - it has an attibute "positions" which is a dictionary that maps the positions 
        of the pieces on the board to their corresponding piece objects.

    Methods :
    ---------
    - it has a method "create_board" which initializes the board with the pieces in their starting positions.
    - it has a method "display_board" which prints the current state of the board.

    """

    def __init__(self):
        pass

    def create_board(self):
        return np.array(
                [["r", "n", "b", "q", "k", "b", "n", "r"],
                ["p", "p", "p", "p", "p", "p", "p", "p"],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                [" ", " ", " ", " ", " ", " ", " ", " "],
                ["P", "P", "P", "P", "P", "P", "P", "P"],
                ["R", "N", "B", "Q", "K", "B", "N", "R"]])


b = board()
b.create_board()


 

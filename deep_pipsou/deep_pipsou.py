"""
Deep Pipsou - Playing Chess Algorithm
Author: Pierre Durand

GOAL: propose a naïve approach to set up an algorithm to play chess, and then improve it step by step. We will use
the pieces_board library to represent the chess board, pieces and rules. 

We have a approach in four steps:
1- Make it possible to play a move
2- Make it possible to evaluate a position => which cost function to use? 
3- Optimize the move selection => which move is the best?
4- Learning and stock experience to build a playing algo 
"""


from pieces_board.chess import *



def get_all_legal_moves(board_obj, board):
    """
    Get all legal moves for the current player at the current board state.
    Args:
        board_obj: an instance of the board class, which contains methods to get piece objects and track last move
        board: the current board state, represented as a dictionary of piece placements
    Returns:       
        A list of legal moves, where each move is a tuple (piece+square: str, destination: str)

    """
    moves = []
    positions = board_obj.display_positions(board)

    for piece, squares in positions.items():
        for square in squares:
            piece_obj = board_obj._get_piece_object(piece)
            possible = piece_obj.possible_moves(square, board, board_obj.last_move)

            for dest in possible:
                move = (piece + square, dest)
                rule = rules(move, board_obj.last_move, board)
                if rule.check_all():
                    moves.append(move)

    return moves







"""
COST FUNCTION

The cost function must evaluate the position of the board and give a score. The higher the score, the better the position for the player.
The score is based on the material balance

"""








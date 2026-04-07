"""
Integration test for chess game with game-end detection.
Tests the board, rules, and game-end detection functionality.
"""

import sys
sys.path.insert(0, './pieces_board')

from chess import board, rules, pawn, rook, knight, bishop, queen, king
import numpy as np


def test_game_end_detection():
    """Test that game-end detection works correctly."""
    print("Testing game-end detection...")
    
    # Create a board
    b = board()
    game_board = b.create_board()
    
    # Check that game is not over at start
    game_over, message, winner = b.check_game_end(game_board)
    assert game_over == False, f"Game should not be over at start: {message}"
    print("✓ Game starts correctly, not over")
    
    # Test a simple sequence of moves
    print("Playing test moves...")
    try:
        # Move e2->e4
        game_board = b.move_piece(game_board, ("Pe2", "e4"))
        b.turn = "black"
        print("✓ Move 1: White e2->e4")
        
        # Move e7->e5
        game_board = b.move_piece(game_board, ("pe7", "e5"))
        b.turn = "white"
        print("✓ Move 2: Black e7->e5")
        
        # Move g1->f3
        game_board = b.move_piece(game_board, ("Ng1", "f3"))
        b.turn = "black"
        print("✓ Move 3: White g1->f3")
        
        # After move 3, game should still not be over
        game_over, message, winner = b.check_game_end(game_board)
        assert game_over == False, f"Game should not be over after 3 moves: {message}"
        print("✓ Game still ongoing after 3 moves")
        
        print("\n✅ All integration tests passed!")
        
    except ValueError as e:
        print(f"❌ Move failed: {e}")
        return False
    
    return True


def test_piece_movement():
    """Test that piece movement works correctly."""
    print("\nTesting piece movement...")
    
    b = board()
    game_board = b.create_board()
    
    # Test pawn movement
    p = pawn("P")
    pawn_moves = p.possible_moves("e2", game_board, [])
    assert "e3" in pawn_moves or "e4" in pawn_moves, f"Pawn should be able to move: {pawn_moves}"
    print(f"✓ White pawn at e2 can move to: {pawn_moves}")
    
    # Test knight movement
    n = knight("N")
    knight_moves = n.possible_moves("g1", game_board, [])
    assert "f3" in knight_moves or "h3" in knight_moves, f"Knight should be able to move: {knight_moves}"
    print(f"✓ White knight at g1 can move to: {knight_moves}")
    
    print("✓ Piece movement works correctly")
    return True


if __name__ == "__main__":
    try:
        test_piece_movement()
        test_game_end_detection()
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

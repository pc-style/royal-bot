#!/usr/bin/env python3
"""
Example usage of Royal Match Bot
Demonstrates how to use the bot programmatically.
"""

import sys
import os
import logging
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game_rules import Piece, PieceColor, PowerUpType, Move, Objective
from core.board_parser import BoardParser
from core.move_generator import MoveGenerator, MoveSimulator
from core.strategy_engine import StrategyEngine
from utils.debugging import TestDataGenerator, print_debug_info
from utils.visualization import MoveVisualizer

def create_sample_board():
    """Create a sample board with some strategic opportunities"""
    # Create an 8x8 board
    board = np.empty((8, 8), dtype=object)
    
    # Fill with a pattern that has some obvious moves
    colors = [PieceColor.RED, PieceColor.BLUE, PieceColor.GREEN, 
              PieceColor.YELLOW, PieceColor.PURPLE, PieceColor.ORANGE]
    
    # Create a board with some potential matches
    for row in range(8):
        for col in range(8):
            if row == 3 and col in [3, 4, 5]:
                # Create a potential 3-in-a-row
                board[row, col] = Piece(color=PieceColor.RED)
            elif row == 4 and col in [3, 4, 5]:
                # Create another potential match
                board[row, col] = Piece(color=PieceColor.BLUE)
            elif row == 5 and col in [3, 4, 5]:
                # Create a third potential match
                board[row, col] = Piece(color=PieceColor.GREEN)
            else:
                # Random colors for the rest
                color = np.random.choice(colors)
                board[row, col] = Piece(color=color)
    
    return board

def create_sample_objectives():
    """Create sample level objectives"""
    return [
        Objective(type="collect", target="red", amount=15, current=0),
        Objective(type="clear", target="boxes", amount=3, current=0),
        Objective(type="spread", target="jelly", amount=8, current=0)
    ]

def demonstrate_board_analysis():
    """Demonstrate board analysis capabilities"""
    print("Demonstrating Board Analysis")
    print("=" * 40)
    
    # Create sample board
    board = create_sample_board()
    objectives = create_sample_objectives()
    
    # Initialize components
    board_parser = BoardParser()
    move_generator = MoveGenerator()
    strategy_engine = StrategyEngine()
    
    # Analyze board
    print(f"Board dimensions: {board.shape}")
    
    # Get board statistics
    stats = board_parser.get_board_statistics(board)
    print(f"Total pieces: {stats.get('total_pieces', 0)}")
    print(f"Empty cells: {stats.get('empty_cells', 0)}")
    print(f"Colors: {list(stats.get('color_counts', {}).keys())}")
    
    # Find possible moves
    possible_moves = move_generator.find_all_possible_moves(board)
    print(f"Possible moves: {len(possible_moves)}")
    
    if possible_moves:
        # Score and select best move
        best_move = strategy_engine.select_best_move(possible_moves, board, objectives)
        
        if best_move:
            print(f"\nBest move: {best_move.from_pos} -> {best_move.to_pos}")
            print(f"Score: {best_move.score}")
            print(f"Reasoning: {best_move.reasoning}")
            
            # Simulate the move
            move_simulator = MoveSimulator()
            new_board, matches = move_simulator.simulate_move_effects(board, best_move)
            
            print(f"Matches created: {len(matches)}")
            print(f"Pieces cleared: {move_simulator.count_pieces_cleared(matches)}")
    
    print()

def demonstrate_move_scoring():
    """Demonstrate how moves are scored"""
    print("Demonstrating Move Scoring")
    print("=" * 40)
    
    # Create a simple test scenario
    board = create_sample_board()
    objectives = create_sample_objectives()
    
    # Create some test moves
    test_moves = [
        Move(from_pos=(3, 3), to_pos=(3, 4)),
        Move(from_pos=(4, 3), to_pos=(4, 4)),
        Move(from_pos=(5, 3), to_pos=(5, 4))
    ]
    
    strategy_engine = StrategyEngine()
    
    print("Scoring individual moves:")
    for i, move in enumerate(test_moves):
        score, breakdown = strategy_engine.score_move(move, board, objectives)
        print(f"Move {i+1}: {move.from_pos} -> {move.to_pos}")
        print(f"  Total Score: {score}")
        print(f"  Breakdown: {breakdown}")
        print()
    
    # Select best move
    best_move = strategy_engine.select_best_move(test_moves, board, objectives)
    if best_move:
        print(f"Best move selected: {best_move.from_pos} -> {best_move.to_pos}")
        print(f"Score: {best_move.score}")
    
    print()

def demonstrate_visualization():
    """Demonstrate visualization capabilities"""
    print("Demonstrating Visualization")
    print("=" * 40)
    
    # Create sample data
    board = create_sample_board()
    move = Move(from_pos=(3, 3), to_pos=(3, 4))
    move.score = 150
    move.reasoning = "Creates rocket and advances objectives"
    
    # Create visualizer
    visualizer = MoveVisualizer()
    
    # Create debug board visualization
    debug_board = visualizer.create_debug_board(board)
    
    # Save it
    if visualizer.save_visualization(debug_board, "example_debug_board.png"):
        print("✅ Debug board visualization saved to 'example_debug_board.png'")
    else:
        print("❌ Failed to save debug board visualization")
    
    print()

def demonstrate_test_data_generation():
    """Demonstrate test data generation"""
    print("Demonstrating Test Data Generation")
    print("=" * 40)
    
    # Generate test data
    test_board = TestDataGenerator.create_test_board((6, 6))
    test_objectives = TestDataGenerator.create_test_objectives()
    test_move = TestDataGenerator.create_test_move()
    
    print(f"Generated {test_board.shape[0]}x{test_board.shape[1]} test board")
    print(f"Generated {len(test_objectives)} test objectives")
    print(f"Generated test move: {test_move.from_pos} -> {test_move.to_pos}")
    
    # Show some board statistics
    board_parser = BoardParser()
    stats = board_parser.get_board_statistics(test_board)
    
    print(f"Board stats: {stats.get('total_pieces', 0)} pieces, "
          f"{stats.get('empty_cells', 0)} empty cells")
    
    print()

def main():
    """Main demonstration function"""
    print("Royal Match Bot - Example Usage")
    print("=" * 60)
    print()
    
    # Configure logging to reduce noise
    logging.basicConfig(level=logging.WARNING)
    
    try:
        # Run demonstrations
        demonstrate_board_analysis()
        demonstrate_move_scoring()
        demonstrate_visualization()
        demonstrate_test_data_generation()
        
        print("🎉 All demonstrations completed successfully!")
        print("\nThe bot is working correctly and ready for use.")
        print("\nTo use with actual screenshots:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run: python main.py path/to/screenshot.png")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
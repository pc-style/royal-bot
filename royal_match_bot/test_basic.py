#!/usr/bin/env python3
"""
Basic test script for Royal Match Bot
Tests core functionality without requiring actual screenshots.
"""

import sys
import os
import logging

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game_rules import Piece, PieceColor, PowerUpType, Move, Objective
from core.move_generator import MoveGenerator, MoveSimulator
from core.strategy_engine import StrategyEngine
from utils.debugging import TestDataGenerator, print_debug_info

def test_basic_functionality():
    """Test basic bot functionality with generated data"""
    print("Testing Royal Match Bot Basic Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Create test data
        print("\n1. Creating test data...")
        test_board = TestDataGenerator.create_test_board((8, 8))
        test_objectives = TestDataGenerator.create_test_objectives()
        
        if test_board.size == 0:
            print("❌ Failed to create test board")
            return False
        print("✅ Test board created successfully")
        
        # Test 2: Initialize components
        print("\n2. Initializing components...")
        move_generator = MoveGenerator()
        move_simulator = MoveSimulator()
        strategy_engine = StrategyEngine()
        print("✅ Components initialized successfully")
        
        # Test 3: Find possible moves
        print("\n3. Finding possible moves...")
        possible_moves = move_generator.find_all_possible_moves(test_board)
        print(f"✅ Found {len(possible_moves)} possible moves")
        
        if len(possible_moves) == 0:
            print("⚠️  No moves found - this might indicate an issue")
        
        # Test 4: Simulate a move
        if possible_moves:
            print("\n4. Simulating a move...")
            test_move = possible_moves[0]
            new_board, matches = move_simulator.simulate_move_effects(test_board, test_move)
            
            if new_board.size > 0:
                print("✅ Move simulation successful")
                print(f"   Matches created: {len(matches)}")
            else:
                print("❌ Move simulation failed")
                return False
        
        # Test 5: Score moves
        print("\n5. Scoring moves...")
        if possible_moves:
            scored_moves = []
            for move in possible_moves[:3]:  # Test first 3 moves
                score, breakdown = strategy_engine.score_move(move, test_board, test_objectives)
                scored_moves.append((move, score, breakdown))
                print(f"   Move {move.from_pos} -> {move.to_pos}: {score} points")
            
            print("✅ Move scoring completed")
        
        # Test 6: Select best move
        print("\n6. Selecting best move...")
        if possible_moves:
            best_move = strategy_engine.select_best_move(possible_moves, test_board, test_objectives)
            if best_move:
                print(f"✅ Best move selected: {best_move.from_pos} -> {best_move.to_pos}")
                print(f"   Score: {best_move.score}")
                print(f"   Reasoning: {best_move.reasoning}")
            else:
                print("❌ Failed to select best move")
                return False
        
        print("\n" + "=" * 50)
        print("✅ All basic tests passed!")
        print("The Royal Match Bot is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_game_rules():
    """Test game rules and constants"""
    print("\nTesting Game Rules...")
    print("-" * 30)
    
    try:
        # Test piece creation
        piece = Piece(color=PieceColor.RED)
        print(f"✅ Created piece: {piece.color.value}")
        
        # Test move creation
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        print(f"✅ Created move: {move.from_pos} -> {move.to_pos}")
        
        # Test objective creation
        objective = Objective(type="collect", target="red", amount=20)
        print(f"✅ Created objective: {objective.type} {objective.amount} {objective.target}")
        
        print("✅ Game rules tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Game rules test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Royal Match Bot - Basic Functionality Test")
    print("=" * 60)
    
    # Configure logging
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_game_rules():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    # Summary
    print(f"\nTest Summary: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! The bot is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Test with a screenshot: python main.py path/to/screenshot.png")
        print("3. Run in test mode: python main.py --test")
        return 0
    else:
        print(f"\n❌ {total_tests - tests_passed} tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
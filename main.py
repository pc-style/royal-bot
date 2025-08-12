#!/usr/bin/env python3
"""
Royal Match Move Suggestion Bot
Main entry point for the application.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from royal_match_bot.core.image_processing import preprocess_screenshot, extract_game_board
from royal_match_bot.core.board_parser import build_board_matrix, parse_level_objectives, detect_board_boundaries
from royal_match_bot.core.move_generator import find_all_possible_moves
from royal_match_bot.core.strategy_engine import StrategyEngine, generate_move_explanation
from royal_match_bot.utils.visualization import visualize_suggested_move, save_annotated_image
from royal_match_bot.utils.debugging import DebugLogger, print_board_analysis, print_move_analysis, create_test_board_state


class RoyalMatchBot:
    """Main bot class that orchestrates all components."""
    
    def __init__(self, debug: bool = False):
        self.strategy_engine = StrategyEngine()
        self.debug_logger = DebugLogger(verbose=debug)
        self.debug_mode = debug
    
    def analyze_screenshot(self, image_path: str) -> dict:
        """
        Analyze a Royal Match screenshot and suggest the best move.
        
        Args:
            image_path: Path to the screenshot file
            
        Returns:
            Dictionary with analysis results
        """
        self.debug_logger.log("Starting screenshot analysis")
        
        try:
            # 1. Load and preprocess screenshot
            self.debug_logger.log("Loading screenshot")
            screenshot = preprocess_screenshot(image_path)
            if screenshot is None:
                return {'error': 'Could not load screenshot'}
            
            # 2. Extract game board
            self.debug_logger.log("Extracting game board")
            board_image = extract_game_board(screenshot)
            
            # 3. Parse board state
            self.debug_logger.log("Parsing board state")
            board_state = build_board_matrix(board_image)
            
            if self.debug_mode:
                self.debug_logger.log_board_state(board_state, "after parsing")
            
            # 4. Parse objectives (placeholder for now)
            self.debug_logger.log("Parsing objectives")
            objectives = parse_level_objectives(screenshot)
            
            # 5. Find possible moves
            self.debug_logger.log("Finding possible moves")
            possible_moves = find_all_possible_moves(board_state)
            
            if self.debug_mode:
                self.debug_logger.log_moves(possible_moves, "found")
            
            if not possible_moves:
                return {
                    'success': True,
                    'message': 'No valid moves found',
                    'best_move': None,
                    'board_state': board_state
                }
            
            # 6. Select best move
            self.debug_logger.log("Selecting best move")
            best_move = self.strategy_engine.select_best_move(possible_moves, board_state, objectives)
            
            # 7. Generate explanation
            explanation = generate_move_explanation(best_move)
            
            self.debug_logger.log(f"Best move selected: {best_move}")
            
            return {
                'success': True,
                'best_move': best_move,
                'explanation': explanation,
                'total_moves': len(possible_moves),
                'board_state': board_state,
                'objectives': objectives
            }
            
        except Exception as e:
            self.debug_logger.log(f"Error during analysis: {e}", "ERROR")
            return {'error': str(e)}
    
    def create_visualization(self, image_path: str, analysis_result: dict, output_path: str = None) -> str:
        """
        Create a visualization of the suggested move.
        
        Args:
            image_path: Path to original screenshot
            analysis_result: Result from analyze_screenshot
            output_path: Optional output path for visualization
            
        Returns:
            Path to the generated visualization
        """
        if not analysis_result.get('success') or not analysis_result.get('best_move'):
            self.debug_logger.log("No valid move to visualize", "WARNING")
            return None
        
        try:
            # Load original image
            screenshot = preprocess_screenshot(image_path)
            if screenshot is None:
                return None
            
            # Create visualization
            best_move = analysis_result['best_move']
            reasoning = analysis_result.get('explanation', '')
            
            annotated_image = visualize_suggested_move(screenshot, best_move, reasoning)
            
            # Save visualization
            if output_path is None:
                base_name = Path(image_path).stem
                output_path = f"{base_name}_suggestion.png"
            
            if save_annotated_image(annotated_image, output_path):
                self.debug_logger.log(f"Visualization saved to {output_path}")
                return output_path
            else:
                self.debug_logger.log("Failed to save visualization", "ERROR")
                return None
                
        except Exception as e:
            self.debug_logger.log(f"Error creating visualization: {e}", "ERROR")
            return None


def run_demo():
    """Run a demo with a test board state."""
    print("=" * 60)
    print("ROYAL MATCH BOT - DEMO MODE")
    print("=" * 60)
    
    # Create a test board for demonstration
    bot = RoyalMatchBot(debug=True)
    board_state = create_test_board_state()
    
    print("\nDemo board state:")
    print_board_analysis(board_state)
    
    # Find moves
    print("\nFinding possible moves...")
    possible_moves = find_all_possible_moves(board_state)
    
    if possible_moves:
        print_move_analysis(possible_moves)
        
        # Select best move
        objectives = {'collect_red': 20, 'remaining_moves': 25}
        best_move = bot.strategy_engine.select_best_move(possible_moves, board_state, objectives)
        
        print("\nBEST MOVE SELECTED:")
        explanation = generate_move_explanation(best_move)
        print(explanation)
    else:
        print("No valid moves found in demo board!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Royal Match Move Suggestion Bot')
    parser.add_argument('--image', '-i', type=str, help='Path to Royal Match screenshot')
    parser.add_argument('--output', '-o', type=str, help='Output path for visualization')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    parser.add_argument('--demo', action='store_true', help='Run demo with test board')
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
        return
    
    if not args.image:
        print("Error: Please provide an image path with --image or run --demo")
        parser.print_help()
        return
    
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        return
    
    # Create bot and analyze
    bot = RoyalMatchBot(debug=args.debug)
    
    print("Analyzing Royal Match screenshot...")
    result = bot.analyze_screenshot(args.image)
    
    if result.get('error'):
        print(f"Error: {result['error']}")
        return
    
    if not result.get('success'):
        print("Analysis failed")
        return
    
    # Display results
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    
    if result.get('best_move'):
        print(result['explanation'])
        print(f"\nTotal possible moves: {result.get('total_moves', 0)}")
        
        # Create visualization
        viz_path = bot.create_visualization(args.image, result, args.output)
        if viz_path:
            print(f"\nVisualization saved to: {viz_path}")
    else:
        print(result.get('message', 'No moves available'))


if __name__ == '__main__':
    main()
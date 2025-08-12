"""
Royal Match Move Suggestion Bot - Main Entry Point
Orchestrates the entire workflow from screenshot to move suggestion.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from core.image_processing import preprocess_screenshot, BoardDetector
from core.board_parser import BoardParser
from core.move_generator import MoveGenerator
from core.strategy_engine import StrategyEngine
from utils.visualization import MoveVisualizer
from utils.debugging import DebugHelper, BoardAnalyzer, MoveAnalyzer, print_debug_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('royal_match_bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class RoyalMatchBot:
    """Main bot class that orchestrates the entire workflow"""
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        
        # Initialize components
        self.board_detector = BoardDetector()
        self.board_parser = BoardParser()
        self.move_generator = MoveGenerator()
        self.strategy_engine = StrategyEngine()
        self.visualizer = MoveVisualizer()
        
        # Debug helpers
        if debug_mode:
            self.debug_helper = DebugHelper()
            self.board_analyzer = BoardAnalyzer()
            self.move_analyzer = MoveAnalyzer()
        
        logger.info("Royal Match Bot initialized")
    
    def analyze_screenshot(self, screenshot_path: str) -> Optional[Tuple[np.ndarray, str]]:
        """
        Analyze a screenshot and suggest the best move
        
        Args:
            screenshot_path: Path to the screenshot file
            
        Returns:
            Tuple of (annotated_image, move_description) or None if failed
        """
        try:
            logger.info(f"Analyzing screenshot: {screenshot_path}")
            
            if self.debug_mode:
                self.debug_helper.start_performance_tracking("screenshot_analysis")
            
            # Step 1: Preprocess screenshot
            screenshot = preprocess_screenshot(screenshot_path)
            if screenshot is None:
                logger.error("Failed to preprocess screenshot")
                return None
            
            # Step 2: Extract game board
            board_image = self.board_detector.extract_game_board(screenshot)
            if board_image is None:
                logger.error("Failed to extract game board")
                return None
            
            # Step 3: Parse level objectives
            objectives = self.board_parser.parse_level_objectives(screenshot)
            logger.info(f"Parsed {len(objectives)} objectives")
            
            # Step 4: Build board matrix
            board_matrix = self.board_parser.build_board_matrix(board_image)
            if board_matrix.size == 0:
                logger.error("Failed to build board matrix")
                return None
            
            # Validate board matrix
            if not self.board_parser.validate_board_matrix(board_matrix):
                logger.error("Board matrix validation failed")
                return None
            
            # Debug: Print board matrix
            if self.debug_mode:
                self.board_parser.print_board_matrix(board_matrix)
                
                # Analyze board state
                board_analysis = self.board_analyzer.analyze_board_state(board_matrix)
                print_debug_info("Board Analysis", board_analysis)
            
            # Step 5: Find all possible moves
            possible_moves = self.move_generator.find_all_possible_moves(board_matrix)
            if not possible_moves:
                logger.warning("No valid moves found")
                return None
            
            logger.info(f"Found {len(possible_moves)} possible moves")
            
            # Step 6: Select best move
            best_move = self.strategy_engine.select_best_move(possible_moves, board_matrix, objectives)
            if best_move is None:
                logger.error("Failed to select best move")
                return None
            
            # Debug: Analyze the best move
            if self.debug_mode:
                move_analysis = self.move_analyzer.analyze_move(best_move, board_matrix, objectives)
                print_debug_info("Best Move Analysis", move_analysis)
            
            # Step 7: Visualize the suggestion
            annotated_image = self.visualizer.visualize_suggested_move(
                screenshot, best_move, best_move.reasoning, board_matrix
            )
            
            # Generate move description
            move_description = self._generate_move_description(best_move, objectives)
            
            if self.debug_mode:
                self.debug_helper.end_performance_tracking("screenshot_analysis")
                self.debug_helper.print_performance_summary()
            
            logger.info("Screenshot analysis completed successfully")
            return annotated_image, move_description
            
        except Exception as e:
            logger.error(f"Error analyzing screenshot: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return None
    
    def _generate_move_description(self, move: 'Move', objectives: list) -> str:
        """Generate a human-readable description of the suggested move"""
        try:
            description = f"Suggested Move: Swap piece at ({move.from_pos[0]}, {move.from_pos[1]}) "
            description += f"with piece at ({move.to_pos[0]}, {move.to_pos[1]})\n\n"
            
            description += f"Score: {move.score} points\n"
            description += f"Reasoning: {move.reasoning}\n\n"
            
            # Add objective information
            if objectives:
                description += "Level Objectives:\n"
                for obj in objectives:
                    progress = obj.progress * 100
                    description += f"- {obj.type.title()} {obj.amount} {obj.target} ({progress:.1f}% complete)\n"
            
            return description
            
        except Exception as e:
            logger.error(f"Error generating move description: {e}")
            return "Move description generation failed"
    
    def save_results(self, annotated_image: np.ndarray, output_path: str) -> bool:
        """Save the annotated image to file"""
        try:
            return self.visualizer.save_visualization(annotated_image, output_path)
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def run_test_mode(self) -> None:
        """Run the bot in test mode with generated data"""
        try:
            logger.info("Running in test mode")
            
            # Generate test data
            from utils.debugging import TestDataGenerator
            
            test_board = TestDataGenerator.create_test_board()
            test_objectives = TestDataGenerator.create_test_objectives()
            test_move = TestDataGenerator.create_test_move()
            
            print_debug_info("Test Board", test_board)
            print_debug_info("Test Objectives", test_objectives)
            print_debug_info("Test Move", test_move)
            
            # Test move generation
            possible_moves = self.move_generator.find_all_possible_moves(test_board)
            print_debug_info("Possible Moves", f"Found {len(possible_moves)} moves")
            
            # Test move selection
            best_move = self.strategy_engine.select_best_move(possible_moves, test_board, test_objectives)
            if best_move:
                print_debug_info("Best Move", f"Selected: {best_move.from_pos} -> {best_move.to_pos}")
            
            # Test visualization
            debug_board = self.visualizer.create_debug_board(test_board)
            self.visualizer.save_visualization(debug_board, "test_debug_board.png")
            
            logger.info("Test mode completed")
            
        except Exception as e:
            logger.error(f"Error in test mode: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Royal Match Move Suggestion Bot")
    parser.add_argument("screenshot", nargs="?", help="Path to screenshot file")
    parser.add_argument("--output", "-o", default="suggested_move.png", 
                       help="Output file for annotated image")
    parser.add_argument("--debug", "-d", action="store_true", 
                       help="Enable debug mode")
    parser.add_argument("--test", "-t", action="store_true", 
                       help="Run in test mode")
    
    args = parser.parse_args()
    
    # Initialize bot
    bot = RoyalMatchBot(debug_mode=args.debug)
    
    if args.test:
        # Run test mode
        bot.run_test_mode()
        return
    
    if not args.screenshot:
        print("Error: Screenshot path is required (unless using --test)")
        parser.print_help()
        return
    
    # Check if screenshot exists
    if not os.path.exists(args.screenshot):
        print(f"Error: Screenshot file not found: {args.screenshot}")
        return
    
    # Analyze screenshot
    result = bot.analyze_screenshot(args.screenshot)
    
    if result is None:
        print("Failed to analyze screenshot. Check logs for details.")
        return
    
    annotated_image, move_description = result
    
    # Save results
    if bot.save_results(annotated_image, args.output):
        print(f"Annotated image saved to: {args.output}")
    else:
        print("Failed to save annotated image")
    
    # Print move description
    print("\n" + "="*60)
    print("MOVE SUGGESTION")
    print("="*60)
    print(move_description)
    print("="*60)

if __name__ == "__main__":
    main()
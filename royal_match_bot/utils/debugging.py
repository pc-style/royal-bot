"""
Debugging Utility Module for Royal Match Bot
Provides development helpers and testing utilities.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict
import logging
import json
import os

from ..core.game_rules import Piece, PieceColor, PowerUpType, Move, Objective
from ..core.board_parser import BoardParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DebugHelper:
    """Helper class for debugging and development"""
    
    def __init__(self):
        self.board_parser = BoardParser()
        
    def create_test_board(self, grid_size: int = 8) -> List[List[Piece]]:
        """
        Create a test board for development and testing
        
        Args:
            grid_size: Size of the grid
            
        Returns:
            Test board matrix
        """
        try:
            # Create a simple test board with some matches
            board = []
            
            # Define some test patterns
            test_patterns = [
                [PieceColor.RED, PieceColor.BLUE, PieceColor.RED, PieceColor.GREEN],
                [PieceColor.BLUE, PieceColor.RED, PieceColor.BLUE, PieceColor.YELLOW],
                [PieceColor.RED, PieceColor.BLUE, PieceColor.RED, PieceColor.PURPLE],
                [PieceColor.GREEN, PieceColor.RED, PieceColor.BLUE, PieceColor.ORANGE]
            ]
            
            for row in range(grid_size):
                row_pieces = []
                for col in range(grid_size):
                    # Use pattern cycling for variety
                    pattern_idx = (row + col) % len(test_patterns)
                    color_idx = col % len(test_patterns[pattern_idx])
                    color = test_patterns[pattern_idx][color_idx]
                    
                    # Add some power-ups for testing
                    power_up = None
                    if row == 2 and col == 2:
                        power_up = PowerUpType.ROCKET
                    elif row == 5 and col == 5:
                        power_up = PowerUpType.TNT
                    
                    piece = Piece(color=color, power_up=power_up)
                    row_pieces.append(piece)
                
                board.append(row_pieces)
            
            logger.info(f"Created test board: {grid_size}x{grid_size}")
            return board
            
        except Exception as e:
            logger.error(f"Error creating test board: {e}")
            return []
    
    def print_board_matrix(self, board_matrix: List[List[Piece]], show_coordinates: bool = True) -> None:
        """
        Print the board matrix in a readable format
        
        Args:
            board_matrix: Board to print
            show_coordinates: Whether to show row/column coordinates
        """
        try:
            if not board_matrix:
                print("Empty board")
                return
            
            grid_size = len(board_matrix)
            
            if show_coordinates:
                # Print column headers
                print("   ", end="")
                for col in range(grid_size):
                    print(f" {col:2}", end="")
                print()
                
                # Print separator
                print("   " + "-" * (grid_size * 3))
            
            # Print board rows
            for row_idx, row in enumerate(board_matrix):
                if show_coordinates:
                    print(f"{row_idx:2} |", end="")
                
                for piece in row:
                    if piece.is_empty():
                        print(" . ", end="")
                    else:
                        # Get color abbreviation
                        color_abbr = piece.color.value[:3].upper()
                        
                        # Add power-up indicator
                        if piece.power_up:
                            power_abbr = piece.power_up.value[:3].upper()
                            print(f"{color_abbr}{power_abbr}", end="")
                        else:
                            print(f"{color_abbr} ", end="")
                
                print()
            
            print()
            
        except Exception as e:
            logger.error(f"Error printing board matrix: {e}")
    
    def visualize_board_state(self, board_matrix: List[List[Piece]], 
                             save_path: Optional[str] = None) -> np.ndarray:
        """
        Create a visual representation of the board state
        
        Args:
            board_matrix: Board to visualize
            save_path: Optional path to save the visualization
            
        Returns:
            Visualization image
        """
        try:
            if not board_matrix:
                return np.array([])
            
            grid_size = len(board_matrix)
            cell_size = 60
            image_size = grid_size * cell_size
            
            # Create image
            image = np.ones((image_size, image_size, 3), dtype=np.uint8) * 255
            
            # Color mapping
            color_map = {
                PieceColor.RED: (255, 0, 0),
                PieceColor.BLUE: (0, 0, 255),
                PieceColor.GREEN: (0, 255, 0),
                PieceColor.YELLOW: (255, 255, 0),
                PieceColor.PURPLE: (128, 0, 128),
                PieceColor.ORANGE: (255, 165, 0),
                PieceColor.EMPTY: (128, 128, 128)
            }
            
            # Draw grid and pieces
            for row in range(grid_size):
                for col in range(grid_size):
                    piece = board_matrix[row][col]
                    
                    # Calculate cell position
                    x1 = col * cell_size
                    y1 = row * cell_size
                    x2 = x1 + cell_size
                    y2 = y1 + cell_size
                    
                    # Draw cell background
                    color = color_map.get(piece.color, (128, 128, 128))
                    cv2.rectangle(image, (x1, y1), (x2, y2), color, -1)
                    
                    # Draw cell border
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), 2)
                    
                    # Add power-up indicator
                    if piece.power_up:
                        power_text = piece.power_up.value[:3].upper()
                        text_size = cv2.getTextSize(power_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                        text_x = x1 + (cell_size - text_size[0]) // 2
                        text_y = y1 + (cell_size + text_size[1]) // 2
                        cv2.putText(image, power_text, (text_x, text_y), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    # Add coordinates
                    coord_text = f"{row},{col}"
                    cv2.putText(image, coord_text, (x1 + 2, y1 + 15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
            
            # Save if requested
            if save_path:
                cv2.imwrite(save_path, image)
                logger.info(f"Board visualization saved to: {save_path}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error visualizing board state: {e}")
            return np.array([])
    
    def analyze_board_patterns(self, board_matrix: List[List[Piece]]) -> Dict:
        """
        Analyze the board for patterns and statistics
        
        Args:
            board_matrix: Board to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            if not board_matrix:
                return {}
            
            analysis = {
                'grid_size': len(board_matrix),
                'total_cells': len(board_matrix) * len(board_matrix[0]),
                'color_distribution': {},
                'power_up_count': 0,
                'potential_matches': [],
                'empty_cells': 0
            }
            
            # Count pieces by color
            for row in board_matrix:
                for piece in row:
                    if piece.is_empty():
                        analysis['empty_cells'] += 1
                    else:
                        color = piece.color.value
                        analysis['color_distribution'][color] = analysis['color_distribution'].get(color, 0) + 1
                        
                        if piece.power_up:
                            analysis['power_up_count'] += 1
            
            # Find potential matches
            analysis['potential_matches'] = self._find_potential_matches(board_matrix)
            
            # Calculate match percentages
            total_pieces = analysis['total_cells'] - analysis['empty_cells']
            for color, count in analysis['color_distribution'].items():
                percentage = (count / total_pieces * 100) if total_pieces > 0 else 0
                analysis['color_distribution'][color] = {
                    'count': count,
                    'percentage': round(percentage, 1)
                }
            
            logger.info(f"Board analysis completed: {analysis['total_cells']} cells, {analysis['power_up_count']} power-ups")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing board patterns: {e}")
            return {}
    
    def _find_potential_matches(self, board_matrix: List[List[Piece]]) -> List[Dict]:
        """Find potential matches on the board"""
        try:
            potential_matches = []
            grid_size = len(board_matrix)
            
            # Check horizontal potential
            for row in range(grid_size):
                for col in range(grid_size - 2):
                    piece1 = board_matrix[row][col]
                    piece2 = board_matrix[row][col + 1]
                    piece3 = board_matrix[row][col + 2]
                    
                    if (not piece1.is_empty() and not piece2.is_empty() and not piece3.is_empty() and
                        piece1.color == piece2.color == piece3.color):
                        potential_matches.append({
                            'type': 'horizontal',
                            'position': (row, col),
                            'length': 3,
                            'color': piece1.color.value
                        })
            
            # Check vertical potential
            for row in range(grid_size - 2):
                for col in range(grid_size):
                    piece1 = board_matrix[row][col]
                    piece2 = board_matrix[row + 1][col]
                    piece3 = board_matrix[row + 2][col]
                    
                    if (not piece1.is_empty() and not piece2.is_empty() and not piece3.is_empty() and
                        piece1.color == piece2.color == piece3.color):
                        potential_matches.append({
                            'type': 'vertical',
                            'position': (row, col),
                            'length': 3,
                            'color': piece1.color.value
                        })
            
            return potential_matches
            
        except Exception as e:
            logger.error(f"Error finding potential matches: {e}")
            return []
    
    def save_board_state(self, board_matrix: List[List[Piece]], file_path: str) -> bool:
        """
        Save board state to a JSON file
        
        Args:
            board_matrix: Board to save
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert board to serializable format
            serializable_board = []
            for row in board_matrix:
                serializable_row = []
                for piece in row:
                    piece_data = {
                        'color': piece.color.value,
                        'power_up': piece.power_up.value if piece.power_up else None,
                        'obstacle': piece.obstacle.value if piece.obstacle else None,
                        'obstacle_layers': piece.obstacle_layers
                    }
                    serializable_row.append(piece_data)
                serializable_board.append(serializable_row)
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(serializable_board, f, indent=2)
            
            logger.info(f"Board state saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving board state: {e}")
            return False
    
    def load_board_state(self, file_path: str) -> List[List[Piece]]:
        """
        Load board state from a JSON file
        
        Args:
            file_path: Path to load the file from
            
        Returns:
            Loaded board matrix
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to Piece objects
            board_matrix = []
            for row_data in data:
                row = []
                for piece_data in row_data:
                    piece = Piece(
                        color=PieceColor(piece_data['color']),
                        power_up=PowerUpType(piece_data['power_up']) if piece_data['power_up'] else None,
                        obstacle=None,  # TODO: Add obstacle loading
                        obstacle_layers=piece_data['obstacle_layers']
                    )
                    row.append(piece)
                board_matrix.append(row)
            
            logger.info(f"Board state loaded from: {file_path}")
            return board_matrix
            
        except Exception as e:
            logger.error(f"Error loading board state: {e}")
            return []
    
    def create_test_scenario(self, scenario_name: str) -> Tuple[List[List[Piece]], List[Objective]]:
        """
        Create a predefined test scenario
        
        Args:
            scenario_name: Name of the scenario to create
            
        Returns:
            Tuple of (board_matrix, objectives)
        """
        try:
            if scenario_name == "simple_match":
                # Simple scenario with obvious matches
                board = self.create_test_board(8)
                objectives = [Objective("collect", "red", 10)]
                
            elif scenario_name == "power_up_creation":
                # Scenario designed to create power-ups
                board = self._create_power_up_scenario()
                objectives = [Objective("collect", "any", 20)]
                
            elif scenario_name == "obstacle_clearing":
                # Scenario with obstacles to clear
                board = self._create_obstacle_scenario()
                objectives = [Objective("clear", "box", 5)]
                
            else:
                # Default scenario
                board = self.create_test_board(8)
                objectives = [Objective("collect", "any", 15)]
            
            logger.info(f"Created test scenario: {scenario_name}")
            return board, objectives
            
        except Exception as e:
            logger.error(f"Error creating test scenario: {e}")
            return [], []
    
    def _create_power_up_scenario(self) -> List[List[Piece]]:
        """Create a scenario designed to create power-ups"""
        try:
            # Create a board with many pieces of the same color in rows
            board = []
            grid_size = 8
            
            for row in range(grid_size):
                row_pieces = []
                for col in range(grid_size):
                    if row == 2:  # Row with many red pieces
                        color = PieceColor.RED
                    elif row == 5:  # Row with many blue pieces
                        color = PieceColor.BLUE
                    else:
                        # Random colors
                        colors = [PieceColor.GREEN, PieceColor.YELLOW, PieceColor.PURPLE, PieceColor.ORANGE]
                        color = colors[(row + col) % len(colors)]
                    
                    piece = Piece(color=color)
                    row_pieces.append(piece)
                
                board.append(row_pieces)
            
            return board
            
        except Exception as e:
            logger.error(f"Error creating power-up scenario: {e}")
            return []
    
    def _create_obstacle_scenario(self) -> List[List[Piece]]:
        """Create a scenario with obstacles"""
        try:
            # Create a board with some obstacles
            board = []
            grid_size = 8
            
            for row in range(grid_size):
                row_pieces = []
                for col in range(grid_size):
                    # Simple color pattern
                    colors = [PieceColor.RED, PieceColor.BLUE, PieceColor.GREEN, PieceColor.YELLOW]
                    color = colors[(row + col) % len(colors)]
                    
                    piece = Piece(color=color)
                    row_pieces.append(piece)
                
                board.append(row_pieces)
            
            return board
            
        except Exception as e:
            logger.error(f"Error creating obstacle scenario: {e}")
            return []
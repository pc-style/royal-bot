"""
Debugging Utilities Module for Royal Match Bot
Provides development and testing support tools.
"""

import logging
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ..core.game_rules import Piece, PieceColor, PowerUpType, ObstacleType, Move, Objective
from ..core.board_parser import BoardParser
from ..core.move_generator import MoveGenerator, MoveSimulator
from ..core.strategy_engine import StrategyEngine

logger = logging.getLogger(__name__)

class DebugHelper:
    """Helper class for debugging and development"""
    
    def __init__(self):
        self.board_parser = BoardParser()
        self.move_generator = MoveGenerator()
        self.move_simulator = MoveSimulator()
        self.strategy_engine = StrategyEngine()
        
        # Performance tracking
        self.performance_metrics = {}
        self.start_time = None
    
    def start_performance_tracking(self, operation_name: str) -> None:
        """Start timing an operation"""
        self.start_time = time.time()
        logger.info(f"Starting performance tracking for: {operation_name}")
    
    def end_performance_tracking(self, operation_name: str) -> float:
        """End timing an operation and return duration"""
        if self.start_time is None:
            return 0.0
        
        duration = time.time() - self.start_time
        self.performance_metrics[operation_name] = duration
        logger.info(f"{operation_name} completed in {duration:.3f} seconds")
        self.start_time = None
        return duration
    
    def get_performance_summary(self) -> Dict[str, float]:
        """Get summary of all performance metrics"""
        return self.performance_metrics.copy()
    
    def print_performance_summary(self) -> None:
        """Print performance summary to console"""
        if not self.performance_metrics:
            print("No performance metrics recorded")
            return
        
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)
        
        total_time = sum(self.performance_metrics.values())
        for operation, duration in self.performance_metrics.items():
            percentage = (duration / total_time) * 100
            print(f"{operation:30} {duration:8.3f}s ({percentage:5.1f}%)")
        
        print(f"{'TOTAL':30} {total_time:8.3f}s (100.0%)")
        print("="*50)

class BoardAnalyzer:
    """Analyzes board states for debugging purposes"""
    
    def __init__(self):
        self.board_parser = BoardParser()
    
    def analyze_board_state(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """
        Comprehensive analysis of board state
        
        Args:
            board_matrix: Board matrix to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            analysis = {
                'board_dimensions': board_matrix.shape if board_matrix.size > 0 else (0, 0),
                'total_cells': board_matrix.size if board_matrix.size > 0 else 0,
                'piece_distribution': {},
                'power_up_analysis': {},
                'obstacle_analysis': {},
                'match_analysis': {},
                'potential_moves': 0,
                'board_health': 'unknown'
            }
            
            if board_matrix.size == 0:
                return analysis
            
            # Analyze piece distribution
            analysis['piece_distribution'] = self._analyze_piece_distribution(board_matrix)
            
            # Analyze power-ups
            analysis['power_up_analysis'] = self._analyze_power_ups(board_matrix)
            
            # Analyze obstacles
            analysis['obstacle_analysis'] = self._analyze_obstacles(board_matrix)
            
            # Analyze matches
            analysis['match_analysis'] = self._analyze_matches(board_matrix)
            
            # Count potential moves
            analysis['potential_moves'] = len(self.move_generator.find_all_possible_moves(board_matrix))
            
            # Assess board health
            analysis['board_health'] = self._assess_board_health(board_matrix)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing board state: {e}")
            return {'error': str(e)}
    
    def _analyze_piece_distribution(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze distribution of pieces by color"""
        try:
            distribution = {
                'colors': {},
                'empty_cells': 0,
                'total_pieces': 0
            }
            
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece is None:
                        continue
                    
                    if piece.is_empty():
                        distribution['empty_cells'] += 1
                    else:
                        distribution['total_pieces'] += 1
                        color = piece.color.value
                        distribution['colors'][color] = distribution['colors'].get(color, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error analyzing piece distribution: {e}")
            return {}
    
    def _analyze_power_ups(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze power-ups on the board"""
        try:
            power_up_analysis = {
                'total_power_ups': 0,
                'by_type': {},
                'positions': []
            }
            
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece and piece.is_power_up():
                        power_up_analysis['total_power_ups'] += 1
                        
                        power_up_type = piece.power_up.value
                        power_up_analysis['by_type'][power_up_type] = \
                            power_up_analysis['by_type'].get(power_up_type, 0) + 1
                        
                        power_up_analysis['positions'].append((row, col))
            
            return power_up_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing power-ups: {e}")
            return {}
    
    def _analyze_obstacles(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze obstacles on the board"""
        try:
            obstacle_analysis = {
                'total_obstacles': 0,
                'by_type': {},
                'positions': []
            }
            
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece and piece.has_obstacle():
                        obstacle_analysis['total_obstacles'] += 1
                        
                        obstacle_type = piece.obstacle.value
                        obstacle_analysis['by_type'][obstacle_type] = \
                            obstacle_analysis['by_type'].get(obstacle_type, 0) + 1
                        
                        obstacle_analysis['positions'].append((row, col))
            
            return obstacle_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing obstacles: {e}")
            return {}
    
    def _analyze_matches(self, board_matrix: np.ndarray) -> Dict[str, Any]:
        """Analyze current matches on the board"""
        try:
            matches = self.move_generator.find_matches(board_matrix)
            
            match_analysis = {
                'total_matches': len(matches),
                'match_lengths': [],
                'total_pieces_in_matches': 0
            }
            
            for match in matches:
                match_length = len(match)
                match_analysis['match_lengths'].append(match_length)
                match_analysis['total_pieces_in_matches'] += match_length
            
            return match_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing matches: {e}")
            return {}
    
    def _assess_board_health(self, board_matrix: np.ndarray) -> str:
        """Assess overall health of the board"""
        try:
            # Count empty cells
            empty_cells = 0
            total_cells = board_matrix.size
            
            for row in range(board_matrix.shape[0]):
                for col in range(board_matrix.shape[1]):
                    piece = board_matrix[row, col]
                    if piece and piece.is_empty():
                        empty_cells += 1
            
            empty_percentage = (empty_cells / total_cells) * 100
            
            if empty_percentage > 30:
                return "poor"
            elif empty_percentage > 15:
                return "fair"
            elif empty_percentage > 5:
                return "good"
            else:
                return "excellent"
                
        except Exception as e:
            logger.error(f"Error assessing board health: {e}")
            return "unknown"

class MoveAnalyzer:
    """Analyzes moves for debugging purposes"""
    
    def __init__(self):
        self.move_simulator = MoveSimulator()
        self.strategy_engine = StrategyEngine()
    
    def analyze_move(self, move: Move, board_matrix: np.ndarray, 
                     objectives: List[Objective]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a move
        
        Args:
            move: Move to analyze
            board_matrix: Current board state
            objectives: Level objectives
            
        Returns:
            Dictionary with move analysis
        """
        try:
            analysis = {
                'move_details': {
                    'from_pos': move.from_pos,
                    'to_pos': move.to_pos,
                    'is_horizontal': move.is_horizontal(),
                    'is_vertical': move.is_vertical()
                },
                'simulation_results': {},
                'scoring': {},
                'strategic_analysis': {}
            }
            
            # Simulate the move
            new_board, matches = self.move_simulator.simulate_move_effects(board_matrix, move)
            analysis['simulation_results'] = {
                'matches_created': len(matches),
                'total_pieces_cleared': self.move_simulator.count_pieces_cleared(matches),
                'cascade_length': len(matches)
            }
            
            # Score the move
            score, breakdown = self.strategy_engine.score_move(move, board_matrix, objectives)
            analysis['scoring'] = {
                'total_score': score,
                'score_breakdown': breakdown
            }
            
            # Strategic analysis
            analysis['strategic_analysis'] = self._analyze_strategic_aspects(move, board_matrix, objectives)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing move: {e}")
            return {'error': str(e)}
    
    def _analyze_strategic_aspects(self, move: Move, board_matrix: np.ndarray, 
                                  objectives: List[Objective]) -> Dict[str, Any]:
        """Analyze strategic aspects of a move"""
        try:
            strategic_analysis = {
                'objective_progress': 0,
                'power_up_creation': False,
                'obstacle_clearing': False,
                'setup_for_future': False
            }
            
            # Check objective progress
            for objective in objectives:
                if objective.type == "collect":
                    # This would require more sophisticated analysis
                    pass
            
            # Check power-up creation
            new_board, matches = self.move_simulator.simulate_move_effects(board_matrix, move)
            for match in matches:
                if len(match) >= 4:
                    strategic_analysis['power_up_creation'] = True
                    break
            
            return strategic_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing strategic aspects: {e}")
            return {}

class TestDataGenerator:
    """Generates test data for development and testing"""
    
    @staticmethod
    def create_test_board(size: Tuple[int, int] = (8, 8)) -> np.ndarray:
        """Create a test board with random pieces"""
        try:
            rows, cols = size
            board = np.empty((rows, cols), dtype=object)
            
            # Available colors
            colors = [PieceColor.RED, PieceColor.BLUE, PieceColor.GREEN, 
                     PieceColor.YELLOW, PieceColor.PURPLE, PieceColor.ORANGE]
            
            # Fill board with random pieces
            for row in range(rows):
                for col in range(cols):
                    color = np.random.choice(colors)
                    board[row, col] = Piece(color=color)
            
            return board
            
        except Exception as e:
            logger.error(f"Error creating test board: {e}")
            return np.array([])
    
    @staticmethod
    def create_test_objectives() -> List[Objective]:
        """Create test objectives"""
        return [
            Objective(type="collect", target="red", amount=20, current=0),
            Objective(type="clear", target="boxes", amount=5, current=0)
        ]
    
    @staticmethod
    def create_test_move() -> Move:
        """Create a test move"""
        return Move(
            from_pos=(3, 4),
            to_pos=(3, 5)
        )

def print_debug_info(title: str, data: Any, indent: int = 0) -> None:
    """Print debug information in a formatted way"""
    indent_str = "  " * indent
    
    print(f"\n{indent_str}{'='*20} {title} {'='*20}")
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_debug_info(f"  {key}", value, indent + 1)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{indent_str}[{i}]: {item}")
    else:
        print(f"{indent_str}{data}")
    
    print(f"{indent_str}{'='*(40 + len(title))}")

def log_function_call(func_name: str, args: Dict[str, Any] = None, 
                     kwargs: Dict[str, Any] = None) -> None:
    """Log function call for debugging"""
    try:
        args_str = f"args={args}" if args else ""
        kwargs_str = f"kwargs={kwargs}" if kwargs else ""
        params = " ".join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func_name}({params})")
        
    except Exception as e:
        logger.error(f"Error logging function call: {e}")

def log_function_result(func_name: str, result: Any, duration: float = None) -> None:
    """Log function result for debugging"""
    try:
        duration_str = f" in {duration:.3f}s" if duration else ""
        logger.debug(f"{func_name} returned {result}{duration_str}")
        
    except Exception as e:
        logger.error(f"Error logging function result: {e}")
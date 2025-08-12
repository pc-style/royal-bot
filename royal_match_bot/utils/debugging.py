"""
Debugging utilities for Royal Match bot development.
"""

import time
import json
from typing import Any, Dict, List
from ..core.board_parser import BoardState
from ..core.move_generator import Move


class DebugLogger:
    """Simple debug logger for tracking bot operations."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logs = []
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = time.time() - self.start_time
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        
        if self.verbose:
            print(f"[{timestamp:.2f}s] {level}: {message}")
    
    def log_board_state(self, board_state: BoardState, description: str = ""):
        """Log current board state for debugging."""
        self.log(f"Board State {description}:")
        if self.verbose:
            board_state.print_board()
    
    def log_moves(self, moves: List[Move], description: str = ""):
        """Log list of moves for debugging."""
        self.log(f"Moves {description}: {len(moves)} found")
        if self.verbose and moves:
            for i, move in enumerate(moves[:5]):  # Show top 5 moves
                print(f"  {i+1}. {move}")
    
    def save_logs(self, filepath: str):
        """Save logs to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.logs, f, indent=2)
            self.log(f"Logs saved to {filepath}")
        except Exception as e:
            self.log(f"Error saving logs: {e}", "ERROR")


def print_board_analysis(board_state: BoardState):
    """Print detailed analysis of board state."""
    print("=" * 50)
    print("BOARD ANALYSIS")
    print("=" * 50)
    
    # Count pieces by color
    color_counts = {}
    power_up_counts = {}
    obstacle_counts = {}
    
    for row in range(board_state.rows):
        for col in range(board_state.cols):
            piece = board_state.get_piece(row, col)
            if piece:
                color = piece.get('color', 'unknown')
                power_up = piece.get('power_up_type')
                obstacle = piece.get('obstacle_type')
                
                color_counts[color] = color_counts.get(color, 0) + 1
                
                if power_up:
                    power_up_counts[power_up] = power_up_counts.get(power_up, 0) + 1
                
                if obstacle:
                    obstacle_counts[obstacle] = obstacle_counts.get(obstacle, 0) + 1
    
    print("Piece Colors:")
    for color, count in sorted(color_counts.items()):
        print(f"  {color}: {count}")
    
    if power_up_counts:
        print("\nPower-ups:")
        for power_up, count in sorted(power_up_counts.items()):
            print(f"  {power_up}: {count}")
    
    if obstacle_counts:
        print("\nObstacles:")
        for obstacle, count in sorted(obstacle_counts.items()):
            print(f"  {obstacle}: {count}")
    
    print("\nBoard Layout:")
    board_state.print_board()
    print("=" * 50)


def print_move_analysis(moves: List[Move], top_n: int = 5):
    """Print detailed analysis of possible moves."""
    print("=" * 50)
    print("MOVE ANALYSIS")
    print("=" * 50)
    
    if not moves:
        print("No valid moves found!")
        return
    
    print(f"Total valid moves: {len(moves)}")
    print(f"\nTop {min(top_n, len(moves))} moves:")
    
    for i, move in enumerate(moves[:top_n]):
        print(f"\n{i+1}. {move}")
        print(f"   Matches {len(move.matches)} pieces at: {move.matches}")
        if move.reasoning:
            print(f"   Reasoning: {move.reasoning}")
    
    print("=" * 50)


def validate_board_state(board_state: BoardState) -> List[str]:
    """
    Validate board state and return list of issues found.
    
    Args:
        board_state: Board state to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check board dimensions
    if board_state.rows <= 0 or board_state.cols <= 0:
        issues.append("Invalid board dimensions")
    
    # Check each cell
    for row in range(board_state.rows):
        for col in range(board_state.cols):
            piece = board_state.get_piece(row, col)
            if piece is None:
                issues.append(f"Null piece at ({row}, {col})")
            elif not isinstance(piece, dict):
                issues.append(f"Invalid piece type at ({row}, {col})")
            else:
                # Check required fields
                required_fields = ['piece_type', 'color', 'power_up_type', 'obstacle_type']
                for field in required_fields:
                    if field not in piece:
                        issues.append(f"Missing field '{field}' at ({row}, {col})")
    
    return issues


def measure_performance(func):
    """Decorator to measure function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    return wrapper


def create_test_board_state() -> BoardState:
    """Create a test board state for debugging purposes."""
    board = BoardState(8, 8)
    
    # Fill with some test pieces
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % len(colors)]
            piece = {
                'piece_type': 'normal',
                'color': color,
                'power_up_type': None,
                'obstacle_type': None
            }
            board.set_piece(row, col, piece)
    
    # Add some strategic pieces for testing
    # Create a potential 4-match
    for col in range(4):
        piece = {
            'piece_type': 'normal',
            'color': 'red',
            'power_up_type': None,
            'obstacle_type': None
        }
        board.set_piece(0, col, piece)
    
    return board


def export_board_state(board_state: BoardState, filepath: str):
    """Export board state to JSON file for testing."""
    data = {
        'rows': board_state.rows,
        'cols': board_state.cols,
        'board_matrix': board_state.board_matrix,
        'objectives': board_state.objectives,
        'remaining_moves': board_state.remaining_moves
    }
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Board state exported to {filepath}")
    except Exception as e:
        print(f"Error exporting board state: {e}")


def import_board_state(filepath: str) -> BoardState:
    """Import board state from JSON file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        board = BoardState(data['rows'], data['cols'])
        board.board_matrix = data['board_matrix']
        board.objectives = data.get('objectives', {})
        board.remaining_moves = data.get('remaining_moves', 0)
        
        print(f"Board state imported from {filepath}")
        return board
    except Exception as e:
        print(f"Error importing board state: {e}")
        return None
"""
Strategy Engine Module for Royal Match Bot
Handles move scoring and selection based on objectives and game strategy.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import logging

from .game_rules import (
    Move, Piece, PieceColor, PowerUpType, ObstacleType, Objective, 
    SCORE_WEIGHTS, get_power_up_type, calculate_cascade_score
)
from .move_generator import MoveSimulator

logger = logging.getLogger(__name__)

class StrategyEngine:
    """Main strategy engine for evaluating and selecting moves"""
    
    def __init__(self):
        self.move_simulator = MoveSimulator()
        self.score_weights = SCORE_WEIGHTS.copy()
    
    def score_move(self, move: Move, board_state: np.ndarray, 
                   objectives: List[Objective]) -> Tuple[int, Dict[str, int]]:
        """
        Score a move based on multiple criteria
        
        Args:
            move: Move to score
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Tuple of (total_score, score_breakdown)
        """
        try:
            score_breakdown = {}
            
            # Simulate the move
            new_board, matches = self.move_simulator.simulate_move_effects(board_state, move)
            
            # 1. OBJECTIVE PROGRESS (100+ points)
            objective_score = self._calculate_objective_score(move, new_board, objectives)
            score_breakdown['objective_progress'] = objective_score
            
            # 2. POWER-UP CREATION (50+ points)
            power_up_score = self._calculate_power_up_creation_score(matches)
            score_breakdown['power_up_creation'] = power_up_score
            
            # 3. POWER-UP COMBINATIONS (75+ points)
            combination_score = self._calculate_power_up_combination_score(matches)
            score_breakdown['power_up_combinations'] = combination_score
            
            # 4. CASCADE POTENTIAL (25+ points)
            cascade_score = self._calculate_cascade_potential_score(matches)
            score_breakdown['cascade_potential'] = cascade_score
            
            # 5. BOARD CLEARING (10+ points)
            clearing_score = self._calculate_board_clearing_score(matches)
            score_breakdown['board_clearing'] = clearing_score
            
            # 6. OBSTACLE CLEARING (30+ points)
            obstacle_score = self._calculate_obstacle_clearing_score(move, board_state, new_board)
            score_breakdown['obstacle_clearing'] = obstacle_score
            
            # Calculate total score
            total_score = sum(score_breakdown.values())
            
            # Update move with score and reasoning
            move.score = total_score
            move.reasoning = self._generate_move_reasoning(score_breakdown)
            
            logger.info(f"Move scored: {total_score} points")
            return total_score, score_breakdown
            
        except Exception as e:
            logger.error(f"Error scoring move: {e}")
            return 0, {}
    
    def _calculate_objective_score(self, move: Move, new_board: np.ndarray, 
                                  objectives: List[Objective]) -> int:
        """Calculate score based on objective progress"""
        try:
            score = 0
            
            for objective in objectives:
                if objective.type == "collect":
                    # Count pieces of target color that would be cleared
                    target_color = objective.target
                    pieces_cleared = self._count_color_pieces_cleared(new_board, target_color)
                    if pieces_cleared > 0:
                        score += pieces_cleared * self.score_weights['objective_progress']
                
                elif objective.type == "clear":
                    # Count obstacles that would be cleared
                    target_obstacle = objective.target
                    obstacles_cleared = self._count_obstacles_cleared(new_board, target_obstacle)
                    if obstacles_cleared > 0:
                        score += obstacles_cleared * self.score_weights['objective_progress']
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating objective score: {e}")
            return 0
    
    def _calculate_power_up_creation_score(self, matches: List[List[Tuple[int, int]]]) -> int:
        """Calculate score for power-up creation"""
        try:
            score = 0
            
            for match in matches:
                match_length = len(match)
                power_up_type = get_power_up_type(match_length)
                
                if power_up_type:
                    power_up_score = self.score_weights['power_up_creation'].get(power_up_type, 0)
                    score += power_up_score
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating power-up creation score: {e}")
            return 0
    
    def _calculate_power_up_combination_score(self, matches: List[List[Tuple[int, int]]]) -> int:
        """Calculate score for power-up combinations"""
        try:
            score = 0
            
            # Count power-ups in matches
            power_up_count = 0
            for match in matches:
                if len(match) >= 4:  # Likely to create power-ups
                    power_up_count += 1
            
            # Bonus for multiple power-ups
            if power_up_count >= 2:
                score += self.score_weights['power_up_combination']
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating power-up combination score: {e}")
            return 0
    
    def _calculate_cascade_potential_score(self, matches: List[List[Tuple[int, int]]]) -> int:
        """Calculate score for cascade potential"""
        try:
            if len(matches) <= 1:
                return 0
            
            # Bonus for each additional match in cascade
            return (len(matches) - 1) * self.score_weights['cascade_potential']
            
        except Exception as e:
            logger.error(f"Error calculating cascade potential score: {e}")
            return 0
    
    def _calculate_board_clearing_score(self, matches: List[List[Tuple[int, int]]]) -> int:
        """Calculate score for board clearing"""
        try:
            total_pieces_cleared = self.move_simulator.count_pieces_cleared(matches)
            return total_pieces_cleared * self.score_weights['board_clearing']
            
        except Exception as e:
            logger.error(f"Error calculating board clearing score: {e}")
            return 0
    
    def _calculate_obstacle_clearing_score(self, move: Move, old_board: np.ndarray, 
                                         new_board: np.ndarray) -> int:
        """Calculate score for obstacle clearing"""
        try:
            score = 0
            
            # Check if move clears obstacles
            for row, col in [move.from_pos, move.to_pos]:
                old_piece = old_board[row, col]
                new_piece = new_board[row, col]
                
                if (old_piece and old_piece.has_obstacle() and 
                    (new_piece is None or not new_piece.has_obstacle())):
                    score += self.score_weights['obstacle_clearing']
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating obstacle clearing score: {e}")
            return 0
    
    def _count_color_pieces_cleared(self, board: np.ndarray, color: str) -> int:
        """Count pieces of a specific color that would be cleared"""
        try:
            count = 0
            for row in range(board.shape[0]):
                for col in range(board.shape[1]):
                    piece = board[row, col]
                    if piece and piece.color.value == color:
                        count += 1
            return count
            
        except Exception as e:
            logger.error(f"Error counting color pieces: {e}")
            return 0
    
    def _count_obstacles_cleared(self, board: np.ndarray, obstacle_type: str) -> int:
        """Count obstacles of a specific type that would be cleared"""
        try:
            count = 0
            for row in range(board.shape[0]):
                for col in range(board.shape[1]):
                    piece = board[row, col]
                    if piece and piece.has_obstacle() and piece.obstacle.value == obstacle_type:
                        count += 1
            return count
            
        except Exception as e:
            logger.error(f"Error counting obstacles: {e}")
            return 0
    
    def _generate_move_reasoning(self, score_breakdown: Dict[str, int]) -> str:
        """Generate human-readable reasoning for a move"""
        try:
            reasons = []
            
            for category, score in score_breakdown.items():
                if score > 0:
                    if category == 'objective_progress':
                        reasons.append(f"Advances objectives (+{score})")
                    elif category == 'power_up_creation':
                        reasons.append(f"Creates power-ups (+{score})")
                    elif category == 'power_up_combinations':
                        reasons.append(f"Power-up combinations (+{score})")
                    elif category == 'cascade_potential':
                        reasons.append(f"Cascade potential (+{score})")
                    elif category == 'board_clearing':
                        reasons.append(f"Clears board (+{score})")
                    elif category == 'obstacle_clearing':
                        reasons.append(f"Clears obstacles (+{score})")
            
            if reasons:
                return "; ".join(reasons)
            else:
                return "Basic match"
                
        except Exception as e:
            logger.error(f"Error generating move reasoning: {e}")
            return "Move analysis error"
    
    def select_best_move(self, possible_moves: List[Move], board_state: np.ndarray, 
                         objectives: List[Objective]) -> Optional[Move]:
        """
        Select the best move from all possible moves
        
        Args:
            possible_moves: List of all valid moves
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Best move or None if no moves available
        """
        try:
            if not possible_moves:
                logger.warning("No possible moves to evaluate")
                return None
            
            # Score all moves
            scored_moves = []
            for move in possible_moves:
                score, breakdown = self.score_move(move, board_state, objectives)
                scored_moves.append((move, score, breakdown))
            
            # Sort by score (highest first)
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            
            # Apply strategic preferences
            best_move = self._apply_strategic_preferences(scored_moves, board_state, objectives)
            
            if best_move:
                logger.info(f"Selected best move: {best_move.from_pos} -> {best_move.to_pos} "
                          f"(Score: {best_move.score})")
            
            return best_move
            
        except Exception as e:
            logger.error(f"Error selecting best move: {e}")
            return None
    
    def _apply_strategic_preferences(self, scored_moves: List[Tuple[Move, int, Dict]], 
                                   board_state: np.ndarray, objectives: List[Objective]) -> Optional[Move]:
        """Apply strategic preferences to move selection"""
        try:
            if not scored_moves:
                return None
            
            # Get the highest scoring move
            best_move, best_score, best_breakdown = scored_moves[0]
            
            # If there's a clear winner (significantly higher score), choose it
            if len(scored_moves) > 1:
                second_score = scored_moves[1][1]
                if best_score > second_score * 1.5:  # 50% higher than second best
                    return best_move
            
            # Apply strategic preferences for close scores
            preferred_moves = []
            
            for move, score, breakdown in scored_moves[:3]:  # Top 3 moves
                preference_score = self._calculate_preference_score(move, board_state, objectives)
                preferred_moves.append((move, score, preference_score))
            
            # Sort by preference score
            preferred_moves.sort(key=lambda x: x[1] + x[2], reverse=True)
            
            return preferred_moves[0][0]
            
        except Exception as e:
            logger.error(f"Error applying strategic preferences: {e}")
            return scored_moves[0][0] if scored_moves else None
    
    def _calculate_preference_score(self, move: Move, board_state: np.ndarray, 
                                  objectives: List[Objective]) -> int:
        """Calculate strategic preference score for a move"""
        try:
            preference_score = 0
            
            # Prefer moves that create power-ups in lower board positions
            if self._creates_power_up_in_lower_board(move, board_state):
                preference_score += 20
            
            # Prefer moves that don't waste existing power-ups
            if not self._wastes_power_up(move, board_state):
                preference_score += 15
            
            # Prefer moves that set up future combinations
            if self._sets_up_future_combination(move, board_state):
                preference_score += 10
            
            # Prefer moves that clear obstacles blocking objectives
            if self._clears_objective_blocking_obstacles(move, board_state, objectives):
                preference_score += 25
            
            return preference_score
            
        except Exception as e:
            logger.error(f"Error calculating preference score: {e}")
            return 0
    
    def _creates_power_up_in_lower_board(self, move: Move, board_state: np.ndarray) -> bool:
        """Check if move creates power-up in lower board positions"""
        try:
            # Simulate move to see if it creates power-ups
            new_board, matches = self.move_simulator.simulate_move_effects(board_state, move)
            
            for match in matches:
                if len(match) >= 4:  # Power-up creation
                    # Check if any match position is in lower half of board
                    for row, col in match:
                        if row >= board_state.shape[0] // 2:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking power-up position: {e}")
            return False
    
    def _wastes_power_up(self, move: Move, board_state: np.ndarray) -> bool:
        """Check if move wastes existing power-ups"""
        try:
            # Check if either piece being moved is a power-up
            for row, col in [move.from_pos, move.to_pos]:
                piece = board_state[row, col]
                if piece and piece.is_power_up():
                    # Moving a power-up might waste it
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking power-up waste: {e}")
            return False
    
    def _sets_up_future_combination(self, move: Move, board_state: np.ndarray) -> bool:
        """Check if move sets up future power-up combinations"""
        try:
            # This is a simplified check - in practice, you'd look for patterns
            # that suggest future combination opportunities
            
            # For now, prefer moves that create L or T shapes
            new_board, _ = self.move_simulator.simulate_move_effects(board_state, move)
            
            # Check for L or T shapes that could become TNT
            return self._has_l_or_t_shape(new_board)
            
        except Exception as e:
            logger.error(f"Error checking future combination setup: {e}")
            return False
    
    def _has_l_or_t_shape(self, board: np.ndarray) -> bool:
        """Check if board has L or T shapes that could become TNT"""
        try:
            # Simplified L/T shape detection
            # In practice, you'd implement more sophisticated pattern recognition
            return False
            
        except Exception as e:
            logger.error(f"Error checking L/T shapes: {e}")
            return False
    
    def _clears_objective_blocking_obstacles(self, move: Move, board_state: np.ndarray, 
                                           objectives: List[Objective]) -> bool:
        """Check if move clears obstacles that block objectives"""
        try:
            # Check if any objective requires clearing obstacles
            for objective in objectives:
                if objective.type == "clear":
                    # Simulate move to see if it clears target obstacles
                    new_board, _ = self.move_simulator.simulate_move_effects(board_state, move)
                    
                    # Count obstacles before and after
                    old_count = self._count_obstacles(board_state, objective.target)
                    new_count = self._count_obstacles(new_board, objective.target)
                    
                    if new_count < old_count:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking obstacle clearing: {e}")
            return False
    
    def _count_obstacles(self, board: np.ndarray, obstacle_type: str) -> int:
        """Count obstacles of a specific type on the board"""
        try:
            count = 0
            for row in range(board.shape[0]):
                for col in range(board.shape[1]):
                    piece = board[row, col]
                    if piece and piece.has_obstacle() and piece.obstacle.value == obstacle_type:
                        count += 1
            return count
            
        except Exception as e:
            logger.error(f"Error counting obstacles: {e}")
            return 0
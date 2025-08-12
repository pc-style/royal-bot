"""
Strategy engine module for Royal Match bot.
Handles move scoring and selection based on game objectives.
"""

from typing import List, Dict, Tuple
from .board_parser import BoardState
from .move_generator import Move
from .game_rules import PowerUpType, PieceColor


class StrategyEngine:
    """Main strategy engine for selecting optimal moves."""
    
    def __init__(self):
        self.scoring_weights = {
            'objective_progress': 100,
            'power_up_creation': 50,
            'power_up_combination': 75,
            'cascade_potential': 25,
            'board_clearing': 10,
            'obstacle_clearing': 30
        }
    
    def score_move(self, move: Move, board_state: BoardState, objectives: Dict) -> float:
        """
        Score a move based on multiple criteria.
        
        Args:
            move: Move to score
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Total score for the move
        """
        total_score = 0.0
        reasoning_parts = []
        
        # 1. Objective progress scoring
        obj_score = self._score_objective_progress(move, objectives)
        total_score += obj_score
        if obj_score > 0:
            reasoning_parts.append(f"Objective progress: +{obj_score:.1f}")
        
        # 2. Power-up creation scoring
        power_score = self._score_power_up_creation(move, board_state)
        total_score += power_score
        if power_score > 0:
            reasoning_parts.append(f"Power-up creation: +{power_score:.1f}")
        
        # 3. Power-up combination scoring
        combo_score = self._score_power_up_combinations(move, board_state)
        total_score += combo_score
        if combo_score > 0:
            reasoning_parts.append(f"Power-up combo: +{combo_score:.1f}")
        
        # 4. Cascade potential scoring
        cascade_score = self._score_cascade_potential(move, board_state)
        total_score += cascade_score
        if cascade_score > 0:
            reasoning_parts.append(f"Cascade potential: +{cascade_score:.1f}")
        
        # 5. Board clearing scoring
        clear_score = self._score_board_clearing(move)
        total_score += clear_score
        if clear_score > 0:
            reasoning_parts.append(f"Board clearing: +{clear_score:.1f}")
        
        # 6. Obstacle clearing scoring
        obstacle_score = self._score_obstacle_clearing(move, board_state)
        total_score += obstacle_score
        if obstacle_score > 0:
            reasoning_parts.append(f"Obstacle clearing: +{obstacle_score:.1f}")
        
        move.score = total_score
        move.reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Basic match"
        
        return total_score
    
    def _score_objective_progress(self, move: Move, objectives: Dict) -> float:
        """Score move based on how much it helps with level objectives."""
        score = 0.0
        
        # Count pieces of each color in the matches
        color_counts = {}
        for pos in move.matches:
            # This would need board state to get actual colors
            # For now, estimate based on match size
            pass
        
        # TODO: Implement proper objective scoring
        # For now, give points based on match size
        match_size = len(move.matches)
        if match_size >= 5:
            score += self.scoring_weights['objective_progress']
        elif match_size >= 4:
            score += self.scoring_weights['objective_progress'] * 0.7
        elif match_size >= 3:
            score += self.scoring_weights['objective_progress'] * 0.3
        
        return score
    
    def _score_power_up_creation(self, move: Move, board_state: BoardState) -> float:
        """Score move based on power-ups it creates."""
        score = 0.0
        match_size = len(move.matches)
        
        if match_size >= 5:
            score += 100  # Light Ball creation
        elif match_size == 4:
            score += 50   # Rocket creation (assuming line)
        
        return score * (self.scoring_weights['power_up_creation'] / 50)
    
    def _score_power_up_combinations(self, move: Move, board_state: BoardState) -> float:
        """Score move based on power-up combinations it creates."""
        # TODO: Detect if move involves combining power-ups
        # For now, return 0
        return 0.0
    
    def _score_cascade_potential(self, move: Move, board_state: BoardState) -> float:
        """Score move based on potential for cascade reactions."""
        # Basic heuristic: larger matches have more cascade potential
        match_size = len(move.matches)
        base_score = min(match_size * 5, 50)  # Cap at 50 points
        
        return base_score * (self.scoring_weights['cascade_potential'] / 25)
    
    def _score_board_clearing(self, move: Move) -> float:
        """Score move based on how many pieces it clears."""
        pieces_cleared = len(move.matches)
        base_score = pieces_cleared * 2
        
        return base_score * (self.scoring_weights['board_clearing'] / 10)
    
    def _score_obstacle_clearing(self, move: Move, board_state: BoardState) -> float:
        """Score move based on obstacles it clears."""
        # TODO: Check if any matched positions contain obstacles
        # For now, return 0
        return 0.0
    
    def select_best_move(self, possible_moves: List[Move], board_state: BoardState, objectives: Dict) -> Move:
        """
        Select the best move from a list of possible moves.
        
        Args:
            possible_moves: List of valid moves
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Best move with highest score
        """
        if not possible_moves:
            return None
        
        # Score all moves
        for move in possible_moves:
            self.score_move(move, board_state, objectives)
        
        # Sort by score (highest first)
        possible_moves.sort(key=lambda m: m.score, reverse=True)
        
        best_move = possible_moves[0]
        
        # Add strategic preferences
        best_move = self._apply_strategic_preferences(possible_moves, board_state)
        
        return best_move
    
    def _apply_strategic_preferences(self, sorted_moves: List[Move], board_state: BoardState) -> Move:
        """
        Apply strategic preferences to move selection.
        
        Args:
            sorted_moves: Moves sorted by score
            board_state: Current board state
            
        Returns:
            Best move considering strategic preferences
        """
        # For now, just return the highest scored move
        # TODO: Add preferences like:
        # - Prefer power-up creation in lower board
        # - Avoid moves that waste power-ups
        # - Consider setup moves for future combinations
        
        return sorted_moves[0]


def generate_move_explanation(move: Move, score_breakdown: Dict = None) -> str:
    """
    Generate human-readable explanation for a move.
    
    Args:
        move: Move to explain
        score_breakdown: Optional detailed score breakdown
        
    Returns:
        Human-readable move explanation
    """
    if not move:
        return "No valid moves available"
    
    pos1_str = f"({move.pos1[0]}, {move.pos1[1]})"
    pos2_str = f"({move.pos2[0]}, {move.pos2[1]})"
    
    explanation = f"Swap pieces at {pos1_str} with {pos2_str}\n"
    explanation += f"- Creates match of {len(move.matches)} pieces\n"
    explanation += f"- Score: {move.score:.1f} points\n"
    
    if move.reasoning:
        explanation += f"- Reasoning: {move.reasoning}"
    
    return explanation
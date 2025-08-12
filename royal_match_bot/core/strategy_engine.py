"""
Strategy Engine Module for Royal Match Bot
Handles move scoring and strategic move selection.
"""

from typing import List, Dict, Tuple, Optional
import logging

from .game_rules import Move, Piece, PieceColor, PowerUpType, Objective, SCORING_WEIGHTS
from .move_generator import MoveGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StrategyEngine:
    """Strategic move selection and scoring engine"""
    
    def __init__(self):
        self.move_generator = MoveGenerator()
        
    def score_move(self, move: Move, board_state: List[List[Piece]], objectives: List[Objective]) -> float:
        """
        Score a move based on multiple criteria
        
        Args:
            move: Move to score
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Total score for the move
        """
        try:
            total_score = 0.0
            score_breakdown = {}
            
            # Get move analysis
            move_analysis = self.move_generator.get_move_potential(board_state, move)
            
            # 1. OBJECTIVE PROGRESS (highest priority)
            objective_score = self._score_objective_progress(move, board_state, objectives, move_analysis)
            total_score += objective_score
            score_breakdown['objective_progress'] = objective_score
            
            # 2. POWER-UP CREATION
            power_up_score = self._score_power_up_creation(move, board_state, move_analysis)
            total_score += power_up_score
            score_breakdown['power_up_creation'] = power_up_score
            
            # 3. POWER-UP COMBINATIONS
            combo_score = self._score_power_up_combinations(move, board_state, move_analysis)
            total_score += combo_score
            score_breakdown['power_up_combinations'] = combo_score
            
            # 4. CASCADE POTENTIAL
            cascade_score = self._score_cascade_potential(move, board_state, move_analysis)
            total_score += cascade_score
            score_breakdown['cascade_potential'] = cascade_score
            
            # 5. BOARD CLEARING
            clearing_score = self._score_board_clearing(move, board_state, move_analysis)
            total_score += clearing_score
            score_breakdown['board_clearing'] = clearing_score
            
            # 6. OBSTACLE CLEARING
            obstacle_score = self._score_obstacle_clearing(move, board_state, move_analysis)
            total_score += obstacle_score
            score_breakdown['obstacle_clearing'] = obstacle_score
            
            # 7. MATCH BONUSES
            match_score = self._score_match_bonuses(move, board_state, move_analysis)
            total_score += match_score
            score_breakdown['match_bonuses'] = match_score
            
            # Store score breakdown in the move object
            move.score = total_score
            move.reasoning = self._generate_move_reasoning(score_breakdown)
            
            logger.debug(f"Move {move.pos1} <-> {move.pos2} scored: {total_score}")
            return total_score
            
        except Exception as e:
            logger.error(f"Error scoring move: {e}")
            return 0.0
    
    def _score_objective_progress(self, move: Move, board_state: List[List[Piece]], 
                                 objectives: List[Objective], move_analysis: Dict) -> float:
        """Score based on progress toward level objectives"""
        try:
            score = 0.0
            
            for objective in objectives:
                if objective.type == "collect":
                    # Check if this move collects pieces of the target color
                    colors_cleared = move_analysis.get('colors_cleared', {})
                    target_color = objective.target
                    
                    if target_color in colors_cleared:
                        pieces_collected = colors_cleared[target_color]
                        # Higher score for more pieces collected
                        score += pieces_collected * SCORING_WEIGHTS["OBJECTIVE_PROGRESS"]
                        
                        # Bonus for completing objective
                        if objective.current + pieces_collected >= objective.count:
                            score += SCORING_WEIGHTS["OBJECTIVE_PROGRESS"] * 2
                
                elif objective.type == "clear":
                    # Check if this move clears obstacles
                    # TODO: Implement obstacle clearing detection
                    pass
                
                elif objective.type == "spread":
                    # Check if this move spreads jelly
                    # TODO: Implement jelly spreading detection
                    pass
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring objective progress: {e}")
            return 0.0
    
    def _score_power_up_creation(self, move: Move, board_state: List[List[Piece]], 
                                 move_analysis: Dict) -> float:
        """Score based on power-up creation"""
        try:
            score = 0.0
            
            # Check if the move creates power-ups
            pieces_cleared = move_analysis.get('pieces_cleared', 0)
            
            # Simple heuristic: more pieces cleared = higher chance of power-up
            if pieces_cleared >= 5:
                score += SCORING_WEIGHTS["LIGHT_BALL_CREATION"]
            elif pieces_cleared >= 4:
                score += SCORING_WEIGHTS["ROCKET_CREATION"]
            
            # TODO: Implement actual power-up detection in move simulation
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring power-up creation: {e}")
            return 0.0
    
    def _score_power_up_combinations(self, move: Move, board_state: List[List[Piece]], 
                                    move_analysis: Dict) -> float:
        """Score based on power-up combinations"""
        try:
            score = 0.0
            
            # Check if this move would combine existing power-ups
            # TODO: Implement power-up combination detection
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring power-up combinations: {e}")
            return 0.0
    
    def _score_cascade_potential(self, move: Move, board_state: List[List[Piece]], 
                                move_analysis: Dict) -> float:
        """Score based on cascade potential"""
        try:
            score = 0.0
            
            # Use the cascade potential from move analysis
            cascade_potential = move_analysis.get('cascade_potential', 0)
            score += cascade_potential * SCORING_WEIGHTS["CASCADE_POTENTIAL"]
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring cascade potential: {e}")
            return 0.0
    
    def _score_board_clearing(self, move: Move, board_state: List[List[Piece]], 
                              move_analysis: Dict) -> float:
        """Score based on board clearing"""
        try:
            score = 0.0
            
            # Use the board clearing percentage from move analysis
            board_clearing = move_analysis.get('board_clearing', 0)
            score += board_clearing * SCORING_WEIGHTS["BOARD_CLEARING"] * 100  # Scale up
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring board clearing: {e}")
            return 0.0
    
    def _score_obstacle_clearing(self, move: Move, board_state: List[List[Piece]], 
                                 move_analysis: Dict) -> float:
        """Score based on obstacle clearing"""
        try:
            score = 0.0
            
            # TODO: Implement obstacle clearing detection
            # For now, return 0
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring obstacle clearing: {e}")
            return 0.0
    
    def _score_match_bonuses(self, move: Move, board_state: List[List[Piece]], 
                             move_analysis: Dict) -> float:
        """Score based on match bonuses"""
        try:
            score = 0.0
            
            # Check for different match lengths
            colors_cleared = move_analysis.get('colors_cleared', {})
            
            for color, count in colors_cleared.items():
                if count >= 6:
                    score += SCORING_WEIGHTS["MATCH_6"]
                elif count >= 5:
                    score += SCORING_WEIGHTS["MATCH_5"]
                elif count >= 4:
                    score += SCORING_WEIGHTS["MATCH_4"]
                elif count >= 3:
                    score += SCORING_WEIGHTS["MATCH_3"]
            
            return score
            
        except Exception as e:
            logger.error(f"Error scoring match bonuses: {e}")
            return 0.0
    
    def _generate_move_reasoning(self, score_breakdown: Dict) -> str:
        """Generate human-readable reasoning for a move"""
        try:
            reasons = []
            
            if score_breakdown.get('objective_progress', 0) > 0:
                reasons.append("Advances objectives")
            
            if score_breakdown.get('power_up_creation', 0) > 0:
                reasons.append("Creates power-ups")
            
            if score_breakdown.get('power_up_combinations', 0) > 0:
                reasons.append("Combines power-ups")
            
            if score_breakdown.get('cascade_potential', 0) > 0:
                reasons.append("High cascade potential")
            
            if score_breakdown.get('board_clearing', 0) > 0:
                reasons.append("Clears many pieces")
            
            if score_breakdown.get('obstacle_clearing', 0) > 0:
                reasons.append("Clears obstacles")
            
            if score_breakdown.get('match_bonuses', 0) > 0:
                reasons.append("Creates large matches")
            
            if not reasons:
                reasons.append("Basic match creation")
            
            return "; ".join(reasons)
            
        except Exception as e:
            logger.error(f"Error generating move reasoning: {e}")
            return "Move analysis"
    
    def select_best_move(self, possible_moves: List[Move], board_state: List[List[Piece]], 
                         objectives: List[Objective]) -> Tuple[Optional[Move], str]:
        """
        Select the best move based on scoring and strategic preferences
        
        Args:
            possible_moves: List of possible moves
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Tuple of (best_move, reasoning)
        """
        try:
            if not possible_moves:
                return None, "No valid moves available"
            
            # Score all moves
            scored_moves = []
            for move in possible_moves:
                score = self.score_move(move, board_state, objectives)
                scored_moves.append((move, score))
            
            # Sort by score (highest first)
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            
            # Apply strategic preferences
            best_move = self._apply_strategic_preferences(scored_moves, board_state, objectives)
            
            if best_move:
                reasoning = f"Selected move {best_move.pos1} <-> {best_move.pos2} with score {best_move.score:.1f}. {best_move.reasoning}"
                return best_move, reasoning
            else:
                return None, "No suitable move found after strategic filtering"
                
        except Exception as e:
            logger.error(f"Error selecting best move: {e}")
            return None, f"Error in move selection: {e}"
    
    def _apply_strategic_preferences(self, scored_moves: List[Tuple[Move, float]], 
                                    board_state: List[List[Piece]], 
                                    objectives: List[Objective]) -> Optional[Move]:
        """
        Apply strategic preferences to select the best move
        
        Args:
            scored_moves: List of (move, score) tuples, sorted by score
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            Best move after strategic filtering
        """
        try:
            if not scored_moves:
                return None
            
            # Get the top moves (within 10% of the best score)
            best_score = scored_moves[0][1]
            threshold = best_score * 0.9
            
            top_moves = [move for move, score in scored_moves if score >= threshold]
            
            # Strategic preferences (in order of priority)
            
            # 1. Prioritize objective completion
            for move, score in scored_moves:
                if self._would_complete_objective(move, board_state, objectives):
                    return move
            
            # 2. Prefer power-up creation in lower board positions
            for move, score in scored_moves:
                if self._creates_power_up_in_lower_board(move, board_state):
                    return move
            
            # 3. Avoid moves that waste existing power-ups
            for move, score in scored_moves:
                if not self._wastes_power_ups(move, board_state):
                    return move
            
            # 4. Consider setup moves for future combinations
            for move, score in scored_moves:
                if self._is_good_setup_move(move, board_state):
                    return move
            
            # If no strategic preferences apply, return the highest-scoring move
            return scored_moves[0][0]
            
        except Exception as e:
            logger.error(f"Error applying strategic preferences: {e}")
            return scored_moves[0][0] if scored_moves else None
    
    def _would_complete_objective(self, move: Move, board_state: List[List[Piece]], 
                                  objectives: List[Objective]) -> bool:
        """Check if a move would complete an objective"""
        try:
            # TODO: Implement objective completion checking
            return False
        except Exception as e:
            logger.error(f"Error checking objective completion: {e}")
            return False
    
    def _creates_power_up_in_lower_board(self, move: Move, board_state: List[List[Piece]]) -> bool:
        """Check if a move creates a power-up in the lower part of the board"""
        try:
            # TODO: Implement power-up creation detection
            return False
        except Exception as e:
            logger.error(f"Error checking power-up creation: {e}")
            return False
    
    def _wastes_power_ups(self, move: Move, board_state: List[List[Piece]]) -> bool:
        """Check if a move wastes existing power-ups"""
        try:
            # TODO: Implement power-up waste detection
            return False
        except Exception as e:
            logger.error(f"Error checking power-up waste: {e}")
            return False
    
    def _is_good_setup_move(self, move: Move, board_state: List[List[Piece]]) -> bool:
        """Check if a move is a good setup for future combinations"""
        try:
            # TODO: Implement setup move detection
            return False
        except Exception as e:
            logger.error(f"Error checking setup move: {e}")
            return False
    
    def get_move_ranking(self, possible_moves: List[Move], board_state: List[List[Piece]], 
                         objectives: List[Objective]) -> List[Tuple[Move, float, str]]:
        """
        Get a ranked list of all moves with scores and reasoning
        
        Args:
            possible_moves: List of possible moves
            board_state: Current board state
            objectives: Level objectives
            
        Returns:
            List of (move, score, reasoning) tuples, sorted by score
        """
        try:
            # Score all moves
            scored_moves = []
            for move in possible_moves:
                score = self.score_move(move, board_state, objectives)
                scored_moves.append((move, score, move.reasoning))
            
            # Sort by score (highest first)
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            
            return scored_moves
            
        except Exception as e:
            logger.error(f"Error getting move ranking: {e}")
            return []
# model/interaction.py
from typing import Tuple
from .agent import Individual


class InteractionManager:
    """Handles agent interactions and opinion updates"""
    
    def __init__(self, config):
        self.config = config
        self.strength_variation = 0.0
        self.reinforcement = config.reinforcement
    
    def choose_dimension(self, ind: Individual, neigh: Individual, 
                         abs_A: float, abs_B: float) -> int:
        """选择讨论维度 (0=A, 1=B)"""
        order = self.config.interaction_order
        if order == "0-importance-based":
            sum_A = ind.importance_A + neigh.importance_A
            sum_B = ind.importance_B + neigh.importance_B
            return 0 if sum_A >= sum_B else 1
        elif order == "1-high agreement":
            return 0 if abs_A < abs_B else 1
        elif order == "2-low agreement":
            return 0 if abs_A > abs_B else 1
        return 0
    
    def apply_confirmation_bias(self, pos_abs: float, advocated: float, 
                                 self_pos: float, ind: Individual, dim: int) -> float:
        """Apply confirmation bias, modifies non-commitment and rejectance threshold"""
        if self.config.confirmation_bias:
            ind.non_commitment = 0
            if dim == 0:  # A dimension
                ind.latitude_reject_A = ind.latitude_accept_A + ind.non_commitment
            else:  # B dimension
                ind.latitude_reject_B = ind.latitude_accept_B + ind.non_commitment
            
            if advocated * self_pos > 0:
                return 0.0
            else:
                return 2.0
        return pos_abs
    
    def apply_social_judgment(self, current: float, diff: float, abs_diff: float,
                               ind: Individual, dim: str) -> Tuple[float, float]:
        """Apply social judgment theory (assimilation-contrast effect)"""
        if dim == 'A':
            acc = ind.latitude_accept_A
            rej = ind.latitude_reject_A
        else:
            acc = ind.latitude_accept_B
            rej = ind.latitude_reject_B
        
        if abs_diff < acc:
            variation = 1.0
            new_value = current + diff * self.reinforcement
        elif abs_diff >= rej:
            variation = -1.0
            new_value = current - diff * self.reinforcement
        else:
            variation = 0.0
            new_value = current
        
        self.strength_variation = variation
        return new_value, variation
    
    def interact_pair(self, ind: Individual, neighbor: Individual, 
                      current_A: float, current_B: float) -> Tuple[float, float, float]:
        """Complete interaction between a pair of individuals"""
        # Calculate differences
        diff_A = neighbor.opinion_A - ind.opinion_A
        diff_B = neighbor.opinion_B - ind.opinion_B
        abs_A, abs_B = abs(diff_A), abs(diff_B)
        
        # Choose dimension
        option = self.choose_dimension(ind, neighbor, abs_A, abs_B)
        
        # Get current positions
        if option == 0:
            self_pos = current_A
            self_pos_2 = current_B
            neigh_pos = neighbor.opinion_A
            neigh_pos_2 = neighbor.opinion_B
            pos_diff = diff_A
            pos_diff_2 = diff_B
            pos_abs = abs_A
            pos_abs_2 = abs_B
        else:
            self_pos = current_B
            self_pos_2 = current_A
            neigh_pos = neighbor.opinion_B
            neigh_pos_2 = neighbor.opinion_A
            pos_diff = diff_B
            pos_diff_2 = diff_A
            pos_abs = abs_B
            pos_abs_2 = abs_A
        
        # Apply confirmation bias
        used_abs = self.apply_confirmation_bias(pos_abs, neigh_pos, self_pos, ind, option)
        used_abs_2 = self.apply_confirmation_bias(pos_abs_2, neigh_pos_2, self_pos_2, ind, 1 - option)
        
        # Apply influence
        if self.config.interaction_rule == "0-central only":
            new_self, var = self.apply_social_judgment(self_pos, pos_diff, used_abs, ind, 'A' if option == 0 else 'B')
            new_self_2, var_2 = self.apply_social_judgment(self_pos_2, pos_diff_2, used_abs_2, ind, 'B' if option == 0 else 'A')
        else:  # "1-with peripheral"
            new_self, var = self.apply_social_judgment(self_pos, pos_diff, used_abs, ind, 'A' if option == 0 else 'B')
            new_self_2, var_2 = self.apply_social_judgment(self_pos_2, pos_diff_2, used_abs, ind, 'B' if option == 0 else 'A')
        
        # Return updated values and variation
        if option == 0:
            return new_self, new_self_2, var
        else:
            return new_self_2, new_self, var_2

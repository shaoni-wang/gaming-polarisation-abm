# model/agent.py
import random
from typing import List, Optional
from .utils import trunc_normal, bound, get_behaviour

class Individual:
    """Individual agent - contains two-dimensional opinions and importance weights"""
    
    def __init__(self, uid: int, x: float, y: float, importance_A: float):
        self.uid = uid
        self.x = x
        self.y = y
        
        # Two-dimensional opinions [-1, 1], using truncated normal distribution
        self.opinion_A = trunc_normal(0, 1, -1, 1)
        self.opinion_B = trunc_normal(0, 1, -1, 1)
        
        # Importance weights (A and B sum to 1)
        self.importance_A = importance_A
        self.importance_B = 1 - importance_A
        
        # Initial opinions (for comparison with current)
        self.init_opinion_A = self.opinion_A
        self.init_opinion_B = self.opinion_B
        
        # Tolerance values for A and B dimensions (can be set separately)
        self.tolerance_A = 0.3
        self.tolerance_B = 0.3
        
        # Social judgment theory parameters
        self.latitude_accept_A = 0.3
        self.latitude_accept_B = 0.3
        self.latitude_reject_A = 0.5
        self.latitude_reject_B = 0.5
        self.non_commitment = 0.5
        
        # Network connections
        self.neighbors: List[int] = []
        self.neighbor_distances: List[float] = []
        
        # Behavior label
        self._behaviour = "neu"
        
        # Influencer influence (for follow_influencers)
        self.influencer_influence = 0.0
        
        # Overall opinion
        self._opinion = self.opinion_A * self.importance_A + self.opinion_B * self.importance_B
    
    @property
    def opinion(self) -> float:
        """Overall opinion = A*importance_A + B*importance_B"""
        return self.opinion_A * self.importance_A + self.opinion_B * self.importance_B
    
    @opinion.setter
    def opinion(self, value: float):
        """Set overall opinion (used for influencer updates)"""
        self._opinion = value
    
    @property
    def opinion_list(self) -> List[float]:
        return [self.opinion_A, self.opinion_B]
    
    @property
    def importance_list(self) -> List[float]:
        return [self.importance_A, self.importance_B]
    
    @property
    def behaviour(self) -> str:
        if self.opinion < -0.1:
            return "oppo"
        elif self.opinion <= 0.1:
            return "neu"
        return "suppo"
    
    def update_behaviour(self):
        """Update behaviour based on current opinion"""
        self._behaviour = self.behaviour
    
    def set_involvement(self, level: float):
        """
        Set involvement level, affects assimilation/contrast thresholds.
        Matches NetLogo: non-commitment = 1 - level-of-involvement
        latitude-of-rejectance = latitude-of-acceptance + non-commitment
        """
        self.non_commitment = 1 - level
        self.latitude_accept_A = self.tolerance_A
        self.latitude_accept_B = self.tolerance_B
        self.latitude_reject_A = self.tolerance_A + self.non_commitment
        self.latitude_reject_B = self.tolerance_B + self.non_commitment
    
    def update_from_list(self, opinion_list: List[float]):
        self.opinion_A = bound(opinion_list[0])
        self.opinion_B = bound(opinion_list[1])
    
    def to_dict(self) -> dict:
        # Get color based on overall opinion
        if self.opinion < -0.1:
            main_color = "#4169e1"  # Blue for opponents
        elif self.opinion > 0.1:
            main_color = "#ff69b4"  # Pink for supporters
        else:
            main_color = "#a0a0a0"  # Grey for neutral
        
        return {
            'id': self.uid,
            'x': self.x,
            'y': self.y,
            'opinion_A': self.opinion_A,
            'opinion_B': self.opinion_B,
            'opinion': self.opinion,
            'behaviour': self.behaviour,
            'importance_A': self.importance_A,
            'importance_B': self.importance_B,
            'color': main_color
        }


class Influencer:
    """Influencer/Authority agent"""
    
    def __init__(self, uid: int, x: float, y: float):
        self.uid = uid
        self.x = x
        self.y = y
        self.endorsement = random.choice(["oppo", "neut", "suppo"])
        
        if self.endorsement == "oppo":
            self.influence = -1.0
            self.color = "#4169e1"  # Blue
        elif self.endorsement == "neut":
            self.influence = 0.0
            self.color = "#a0a0a0"  # Grey
        else:
            self.influence = 1.0
            self.color = "#ff69b4"  # Pink
        
        self.followers: List[int] = []
    
    def to_dict(self) -> dict:
        return {
            'id': self.uid,
            'x': self.x,
            'y': self.y,
            'endorsement': self.endorsement,
            'influence': self.influence,
            'color': self.color,
            'followers_count': len(self.followers)
        }
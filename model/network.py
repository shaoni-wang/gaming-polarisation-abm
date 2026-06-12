import math
from typing import Dict, List, Tuple
from .agent import Individual
from .utils import distance


class NetworkManager:
    """Manages network creation and updates"""
    
    def __init__(self, config):
        self.config = config
        self.connections: List[Tuple[int, int, float]] = []  # (a, b, strength)
        self.relations: List[Tuple[int, int]] = []  # (influencer, follower)
        self.strength_variation = 0.0
    
    def build_network(self, individuals: Dict[int, Individual]) -> None:
        """Establish social links based on average social connections"""
        target_edges = (self.config.avg_connections * self.config.num_agents) // 2
        max_attempts = 50000
        attempts = 0
        
        print(f"Building network: target edges = {target_edges}")
        
        while len(self.connections) < target_edges and attempts < max_attempts:
            agent_ids = list(individuals.keys())
            if not agent_ids:
                break
                
            agent_id = random.choice(agent_ids)
            agent = individuals[agent_id]
            
            best_target = None
            min_distance = float('inf')
            
            for other_id in agent_ids:
                if other_id == agent_id:
                    continue
                if self._are_connected(agent_id, other_id):
                    continue
                other = individuals[other_id]
                dist = distance(agent.x, agent.y, other.x, other.y)
                if dist < min_distance:
                    min_distance = dist
                    best_target = other_id
            
            if best_target is not None:
                self._create_connection(agent_id, best_target, individuals)
            attempts += 1
        
        print(f"Network built: {len(self.connections)} connections created")
    
    def _are_connected(self, agent1_id: int, agent2_id: int) -> bool:
        """Check if two agents are already connected"""
        for a, b, _ in self.connections:
            if (a == agent1_id and b == agent2_id) or (a == agent2_id and b == agent1_id):
                return True
        return False
    
    def _create_connection(self, agent1_id: int, agent2_id: int, individuals: Dict[int, Individual]) -> None:
        """Create a connection between two agents"""
        self.connections.append((agent1_id, agent2_id, 0.0))
        individuals[agent1_id].neighbors.append(agent2_id)
        individuals[agent2_id].neighbors.append(agent1_id)
    
    def update_connection_strength(self, agent_id: int, neighbor_id: int, variation: float) -> None:
        """Update link strength between two individuals"""
        for i, (a, b, strength) in enumerate(self.connections):
            if (a == agent_id and b == neighbor_id) or (a == neighbor_id and b == agent_id):
                new_strength = strength + variation
                self.connections[i] = (a, b, new_strength)
                break
    
    def get_connection_color(self, strength: float) -> str:
        """Get connection color based on link strength"""
        if strength > 0:
            normalized = min(1.0, strength / 100.0)
            alpha = 0.2 + normalized * 0.7
            return f"rgba(0, 0, 0, {alpha})"
        elif strength < 0:
            normalized = min(1.0, abs(strength) / 100.0)
            alpha = 0.2 + normalized * 0.7
            return f"rgba(0, 0, 0, {alpha})"
        else:
            return "rgba(0, 0, 0, 0.1)"
    
    def to_dict(self) -> List[dict]:
        """Return connection data for frontend"""
        return [
            {
                'source': a,
                'target': b,
                'strength': float(strength),
                'color': self.get_connection_color(strength)
            }
            for a, b, strength in self.connections
        ]


# Add missing random import
import random
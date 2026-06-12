import random
import math
import numpy as np
from typing import Dict, List, Tuple

from .config import Config
from .agent import Individual, Influencer
from .utils import bound, bound_coord, distance, get_behaviour
from .network import NetworkManager
from .interaction import InteractionManager
from .statistics import StatisticsManager


class Simulation:
    """Main simulation engine - coordinates all modules"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        
        # Initialize managers
        self.network = NetworkManager(self.config)
        self.interaction = InteractionManager(self.config)
        self.stats = StatisticsManager(self.config)
        
        # State
        self.individuals: Dict[int, Individual] = {}
        self.influencers: Dict[int, Influencer] = {}
        self.tick = 0
        
        # Setup
        self._setup()
    
    def _setup(self):
        """Initialize model"""
        random.seed(self.config.random_seed)
        np.random.seed(self.config.random_seed)
        
        self._create_individuals()
        self.network.build_network(self.individuals)
        self._setup_individual_properties()
        
        # Record initial distributions
        self.stats.record_initial_distributions(self.individuals)
        
        if self.config.influencer_present:
            self._setup_influencers()
        
        self.stats.update_stats(self.individuals)
    
    def _create_individuals(self):
        """Create all individuals"""
        for uid in range(self.config.num_agents):
            x = random.uniform(0, self.config.world_size)
            y = random.uniform(0, self.config.world_size)
            ind = Individual(uid, x, y, self.config.importance_attitude_A)
            ind.tolerance_A = self.config.tolerance_attitude_A
            ind.tolerance_B = self.config.tolerance_attitude_B
            ind.set_involvement(self.config.level_of_involvement)
            self.individuals[uid] = ind
    
    def _setup_individual_properties(self):
        """Initialize individual properties"""
        for ind in self.individuals.values():
            ind.update_behaviour()
    
    def _setup_influencers(self):
        """Create influencers"""
        inf_uid = 9999
        x = random.uniform(0, self.config.world_size)
        y = random.uniform(0, self.config.world_size)
        inf = Influencer(inf_uid, x, y)
        self.influencers[inf_uid] = inf
        
        all_ids = list(self.individuals.keys())
        num_followers = int(0.6 * self.config.num_agents)
        followers = random.sample(all_ids, min(num_followers, len(all_ids)))
        
        for fid in followers:
            self.network.relations.append((inf_uid, fid))
            inf.followers.append(fid)
    
    def _calculate_distances(self):
        """Calculate distances to neighbors for each agent"""
        for ind in self.individuals.values():
            dist_list = []
            for nid in ind.neighbors:
                neighbor = self.individuals[nid]
                dist_list.append(distance(ind.x, ind.y, neighbor.x, neighbor.y))
            ind.neighbor_distances = dist_list
    
    def _move_towards(self, ind: Individual, neighbor: Individual, variation: float):
        """Move agents based on interaction strength"""
        if not (ind.x > 3 and ind.x < 198 and ind.y > 3 and ind.y < 198):
            return
        
        if ind.neighbor_distances:
            max_dis = max(ind.neighbor_distances)
        else:
            return
        
        dist = distance(ind.x, ind.y, neighbor.x, neighbor.y)
        
        if max_dis < 50 and 10 < dist < 50 and variation != 0:
            dx = neighbor.x - ind.x
            dy = neighbor.y - ind.y
            if math.hypot(dx, dy) > 0:
                step = 0.05 * variation
                ind.x += (dx / dist) * step
                ind.y += (dy / dist) * step
    
    def _follow_influencers(self):
        """Individuals follow influencer opinions"""
        if not self.influencers:
            return
        
        for inf_id, follower_id in self.network.relations:
            inf = self.influencers.get(inf_id)
            ind = self.individuals.get(follower_id)
            if inf and ind and inf.influence != 0:
                delta = 0.01 * (inf.influence - ind.opinion)
                new_opinion = ind.opinion + delta
                ind.opinion_A = bound(new_opinion * ind.importance_A)
                ind.opinion_B = bound(new_opinion * ind.importance_B)
    
    def _update_individuals(self):
        """Update individuals after interactions"""
        for ind in self.individuals.values():
            ind.update_behaviour()
    
    def step(self):
        """Execute one time step"""
        if self.tick >= self.config.max_ticks:
            return
        
        self._calculate_distances()
        self._interact_all_pairs()
        self._follow_influencers()
        self._update_individuals()
        self.stats.update_stats(self.individuals)
        self.tick += 1
    
    def _interact_all_pairs(self):
        """All individuals interact with neighbors"""
        updates_A = {}
        updates_B = {}
        
        for ind in self.individuals.values():
            if not ind.neighbors:
                continue
            
            new_A = ind.opinion_A
            new_B = ind.opinion_B
            
            for nid in ind.neighbors:
                neighbor = self.individuals[nid]
                
                # Use InteractionManager to handle interaction
                updated_A, updated_B, variation = self.interaction.interact_pair(
                    ind, neighbor, new_A, new_B
                )
                
                new_A = updated_A
                new_B = updated_B
                
                # Update connection strength
                self.network.update_connection_strength(ind.uid, nid, variation)
                
                # Move agents
                self._move_towards(ind, neighbor, variation)
            
            updates_A[ind.uid] = bound(new_A)
            updates_B[ind.uid] = bound(new_B)
        
        # Apply all updates
        for uid in updates_A:
            self.individuals[uid].opinion_A = updates_A[uid]
            self.individuals[uid].opinion_B = updates_B[uid]
    
    def get_state(self) -> dict:
        """Get current state for frontend"""
        return {
            'tick': self.tick,
            'stats': self.stats.to_dict(),
            'individuals': [ind.to_dict() for ind in self.individuals.values()],
            'influencers': [inf.to_dict() for inf in self.influencers.values()],
            'connections': self.network.to_dict(),
            'initial_distributions': self.stats.initial_distributions,
            'current_distributions': self.stats.get_current_distributions(self.individuals),
            'config': {
                'num_agents': self.config.num_agents,
                'world_size': self.config.world_size,
                'show_links': self.config.show_links,
                'max_ticks': self.config.max_ticks
            }
        }
    
    def reset(self):
        """Reset simulation"""
        self.__init__(self.config)
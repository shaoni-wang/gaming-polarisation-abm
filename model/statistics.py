# model/statistics.py
from typing import Dict, List, Any
import numpy as np
from .agent import Individual
from .config import Config


class StatisticsManager:
    """Handles statistics calculation and distribution recording"""
    
    def __init__(self, config: Config):
        self.config = config
        self.stats = {
            'oppo': 0, 'neut': 0, 'suppo': 0,
            'correlation': 0.0, 'heterogeneity': 0.0, 'consonance': 0.0
        }
        self.initial_distributions = {
            'attitude_a': [],
            'attitude_b': [],
            'opinion': [],
            'bin_centers': []
        }
    
    def update_stats(self, individuals: Dict[int, Individual]) -> None:
        """Update statistics (matches NetLogo evaluation)"""
        oppo = neut = suppo = 0
        opinions = []
        consonances = []
        
        for ind in individuals.values():
            opinions.append([ind.opinion_A, ind.opinion_B])
            consonances.append(ind.opinion_A * ind.opinion_B)
            if ind.opinion < -0.1:
                oppo += 1
            elif ind.opinion <= 0.1:
                neut += 1
            else:
                suppo += 1
        
        self.stats['oppo'] = oppo
        self.stats['neut'] = neut
        self.stats['suppo'] = suppo
        self.stats['consonance'] = float(np.mean(consonances)) if consonances else 0.0
        
        # Calculate correlation between A and B
        if len(opinions) > 1:
            arr = np.array(opinions)
            corr = np.corrcoef(arr.T)[0, 1]
            self.stats['correlation'] = float(corr) if not np.isnan(corr) else 0.0
        else:
            self.stats['correlation'] = 0.0
        
        # Calculate heterogeneity (average difference from neighbors)
        diff_list = []
        for ind in individuals.values():
            if ind.neighbors:
                neigh_As = [individuals[nid].opinion_A for nid in ind.neighbors]
                neigh_Bs = [individuals[nid].opinion_B for nid in ind.neighbors]
                avg_A = np.mean(neigh_As) if neigh_As else 0.0
                avg_B = np.mean(neigh_Bs) if neigh_Bs else 0.0
                diff_list.append(abs(ind.opinion_A - avg_A))
                diff_list.append(abs(ind.opinion_B - avg_B))
        
        self.stats['heterogeneity'] = float(np.mean(diff_list)) if diff_list else 0.0
    
    def record_initial_distributions(self, individuals: Dict[int, Individual]) -> None:
        """Record initial distributions for all three charts"""
        bins = 20
        bin_width = 0.1
        bin_centers = [-1 + (i + 0.5) * bin_width for i in range(bins)]
        
        # Initialize counters
        counts_a = [0] * bins
        counts_b = [0] * bins
        counts_opinion = [0] * bins
        
        # Count distributions
        for ind in individuals.values():
            # Attitude A
            idx_a = min(bins - 1, max(0, int((ind.init_opinion_A + 1) / bin_width)))
            counts_a[idx_a] += 1
            
            # Attitude B
            idx_b = min(bins - 1, max(0, int((ind.init_opinion_B + 1) / bin_width)))
            counts_b[idx_b] += 1
            
            # Overall opinion
            overall = ind.init_opinion_A * ind.importance_A + ind.init_opinion_B * ind.importance_B
            idx_o = min(bins - 1, max(0, int((overall + 1) / bin_width)))
            counts_opinion[idx_o] += 1
        
        # Convert to percentages
        num_agents = len(individuals)
        percentages_a = [c / num_agents * 100 for c in counts_a]
        percentages_b = [c / num_agents * 100 for c in counts_b]
        percentages_opinion = [c / num_agents * 100 for c in counts_opinion]
        
        self.initial_distributions = {
            'attitude_a': percentages_a,
            'attitude_b': percentages_b,
            'opinion': percentages_opinion,
            'bin_centers': bin_centers
        }
    
    def get_current_distributions(self, individuals: Dict[int, Individual]) -> dict:
        """Get current distributions for all three charts"""
        bins = 20
        bin_width = 0.1
        bin_centers = [-1 + (i + 0.5) * bin_width for i in range(bins)]
        
        # Initialize counters
        counts_a = [0] * bins
        counts_b = [0] * bins
        counts_opinion = [0] * bins
        
        # Count distributions
        for ind in individuals.values():
            # Attitude A
            idx_a = min(bins - 1, max(0, int((ind.opinion_A + 1) / bin_width)))
            counts_a[idx_a] += 1
            
            # Attitude B
            idx_b = min(bins - 1, max(0, int((ind.opinion_B + 1) / bin_width)))
            counts_b[idx_b] += 1
            
            # Overall opinion
            overall = ind.opinion_A * ind.importance_A + ind.opinion_B * ind.importance_B
            idx_o = min(bins - 1, max(0, int((overall + 1) / bin_width)))
            counts_opinion[idx_o] += 1
        
        # Convert to percentages
        num_agents = len(individuals)
        percentages_a = [c / num_agents * 100 for c in counts_a]
        percentages_b = [c / num_agents * 100 for c in counts_b]
        percentages_opinion = [c / num_agents * 100 for c in counts_opinion]
        
        return {
            'attitude_a': percentages_a,
            'attitude_b': percentages_b,
            'opinion': percentages_opinion,
            'bin_centers': bin_centers
        }
    
    def to_dict(self) -> dict:
        """Return statistics for frontend"""
        return self.stats.copy()

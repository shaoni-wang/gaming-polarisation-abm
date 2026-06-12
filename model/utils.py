# model/utils.py
import random
import math
from typing import List, Tuple

def trunc_normal(mid: float, dev: float, min_val: float, max_val: float) -> float:
    """Generate truncated normal distribution value"""
    while True:
        val = random.gauss(mid, dev)
        if min_val <= val <= max_val:
            return val

def bound(value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    """Clamp value within range"""
    return max(min_val, min(value, max_val))

def bound_coord(value: float, world_size: int, margin: float = 3.0) -> float:
    """Clamp coordinate within world boundaries"""
    return max(margin, min(value, world_size - margin))

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points"""
    return math.hypot(x1 - x2, y1 - y2)

def normalize_min_max(value: float, old_min: float, old_max: float, 
                       new_min: float, new_max: float) -> float:
    """Normalize value from old range to new range"""
    return new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min)

def get_behaviour(opinion: float) -> str:
    """Get behavior label based on opinion value"""
    if opinion < -0.1:
        return "oppo"   # Opponent
    elif opinion <= 0.1:
        return "neu"    # Neutral
    else:
        return "suppo"  # Supporter
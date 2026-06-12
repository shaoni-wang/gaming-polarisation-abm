# model/__init__.py
from .config import Config
from .agent import Individual, Influencer
from .simulation import Simulation
from .network import NetworkManager
from .interaction import InteractionManager
from .statistics import StatisticsManager
from .utils import trunc_normal, bound, distance, get_behaviour

__all__ = [
    'Config',
    'Individual', 
    'Influencer',
    'Simulation',
    'NetworkManager',
    'InteractionManager',
    'StatisticsManager',
    'trunc_normal',
    'bound',
    'distance',
    'get_behaviour'
]
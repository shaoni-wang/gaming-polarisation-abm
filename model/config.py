class Config:
    """Model configuration parameters - fully aligned with NetLogo interface"""
    
    # ========== Model Parameters ==========
    num_agents = 100
    avg_connections = 5
    importance_attitude_A = 0.5
    level_of_involvement = 0.5
    reinforcement = 0.01
    confirmation_bias = False
    influencer_present = False
    interaction_order = "0-importance-based"
    interaction_rule = "0-central only"
    
    # ========== Tolerance for each attitude dimension ==========
    tolerance_attitude_A = 0.3
    tolerance_attitude_B = 0.3
    
    # ========== Simulation Control ==========
    random_seed = 100
    max_ticks = 1000
    
    # ========== Spatial Parameters ==========
    world_size = 200
    move_speed = 0.05
    min_distance = 10
    max_distance = 80
    
    # ========== Visualization Parameters ==========
    show_links = True
    show_labels = False
    
    @classmethod
    def validate(cls):
        """Validate parameter values"""
        assert 0 <= cls.importance_attitude_A <= 1, "Importance must be between 0 and 1"
        assert 0 <= cls.level_of_involvement <= 1, "Involvement level must be between 0 and 1"
        assert cls.reinforcement > 0, "Reinforcement coefficient must be positive"
        assert 0.1 <= cls.tolerance_attitude_A <= 0.8, "Tolerance A must be between 0.1 and 0.8"
        assert 0.1 <= cls.tolerance_attitude_B <= 0.8, "Tolerance B must be between 0.1 and 0.8"
        assert cls.interaction_order in ["0-importance-based", "1-high agreement", "2-low agreement"]
        assert cls.interaction_rule in ["0-central only", "1-with peripheral"]

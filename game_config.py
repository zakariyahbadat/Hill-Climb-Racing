"""
Advanced game config with shop system and progression
"""

SHOP_ITEMS = {
    "acceleration_boost": {
        "name": "Engine Upgrade",
        "cost": 500,
        "effect": "acceleration",
        "boost": 0.15,
        "description": "Increases acceleration by 15%"
    },
    "speed_boost": {
        "name": "Turbo Kit",
        "cost": 800,
        "effect": "speed",
        "boost": 0.20,
        "description": "Increases top speed by 20%"
    },
    "traction_boost": {
        "name": "Racing Tires",
        "cost": 400,
        "effect": "traction",
        "boost": 0.18,
        "description": "Improves traction by 18%"
    },
    "fuel_boost": {
        "name": "Fuel Tank",
        "cost": 600,
        "effect": "fuel_efficiency",
        "boost": 0.22,
        "description": "Better fuel efficiency by 22%"
    },
    "suspension": {
        "name": "Suspension System",
        "cost": 700,
        "effect": "suspension",
        "boost": 0.25,
        "description": "Smoother ride and better stability"
    }
}

LEVELS = [
    {
        "name": "Mountain Valley",
        "difficulty": "Easy",
        "seed": 42,
        "target_distance": 5000
    },
    {
        "name": "Rocky Hills",
        "difficulty": "Medium",
        "seed": 123,
        "target_distance": 8000
    },
    {
        "name": "Desert Dunes",
        "difficulty": "Hard",
        "seed": 456,
        "target_distance": 12000
    },
    {
        "name": "Alpine Peak",
        "difficulty": "Very Hard",
        "seed": 789,
        "target_distance": 15000
    },
    {
        "name": "Volcanic Crater",
        "difficulty": "Extreme",
        "seed": 999,
        "target_distance": 20000
    }
]

ACHIEVEMENTS = {
    "first_blood": {"title": "First Run", "reward": 100},
    "speed_demon": {"title": "Speed Demon", "reward": 500},
    "distance_5k": {"title": "5K Explorer", "reward": 250},
    "distance_10k": {"title": "10K Warrior", "reward": 500},
    "distance_20k": {"title": "20K Legend", "reward": 1000},
    "flipped_master": {"title": "Flip Master", "reward": 300},
    "fuel_efficient": {"title": "Eco Driver", "reward": 200},
}

CAR_COLORS = [
    (220, 53, 69),      # Red
    (0, 102, 204),      # Blue
    (40, 167, 69),      # Green
    (255, 193, 7),      # Yellow
    (255, 140, 0),      # Orange
    (155, 89, 182),     # Purple
]

PARTICLE_EFFECTS = {
    "dust": {"color": (200, 200, 200), "count": 15, "lifetime": 40},
    "spark": {"color": (255, 215, 0), "count": 20, "lifetime": 50},
    "smoke": {"color": (100, 100, 100), "count": 10, "lifetime": 60},
}

SOUND_SETTINGS = {
    "master_volume": 0.8,
    "music_volume": 0.6,
    "sfx_volume": 0.8,
    "enable_sound": True
}

GRAPHICS_SETTINGS = {
    "resolution": (1400, 800),
    "fps": 60,
    "vsync": True,
    "particle_quality": "high"  # low, medium, high
}

"""
Enhanced Hill Climb Racing Game - Advanced Edition
Features: Shop System, Achievements, Multiple Levels, Advanced Physics
"""

import pygame
import math
import random
import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict
from game_config import SHOP_ITEMS, LEVELS, ACHIEVEMENTS, CAR_COLORS, SOUND_SETTINGS, GRAPHICS_SETTINGS

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game Constants
SCREEN_WIDTH = GRAPHICS_SETTINGS["resolution"][0]
SCREEN_HEIGHT = GRAPHICS_SETTINGS["resolution"][1]
FPS = GRAPHICS_SETTINGS["fps"]
GRAVITY = 0.75  # Increased for realistic physics
FRICTION = 0.96  # More realistic ground friction
AIR_RESISTANCE = 0.985  # Better air drag
TERRAIN_LENGTH = SCREEN_WIDTH * 12  # Much longer terrain for extended gameplay
ROLLOVER_THRESHOLD = math.pi * 0.5  # Damage threshold
FLIP_DAMAGE_THRESHOLD = math.pi * 0.75  # Critical flip threshold

# Colors
class Color(Enum):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_BLUE = (20, 33, 61)
    BLUE = (0, 102, 204)
    LIGHT_BLUE = (100, 149, 237)
    RED = (220, 53, 69)
    GREEN = (40, 167, 69)
    YELLOW = (255, 193, 7)
    ORANGE = (255, 140, 0)
    GRAY = (108, 117, 125)
    LIGHT_GRAY = (200, 200, 200)
    GOLD = (255, 215, 0)
    PURPLE = (155, 89, 182)
    CYAN = (0, 206, 209)

class GameState(Enum):
    """Game states"""
    MENU = 1
    LEVEL_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    GARAGE = 6
    SHOP = 7
    ACHIEVEMENTS = 8
    SETTINGS = 9

@dataclass
class CarStats:
    """Car upgrade statistics"""
    acceleration: float = 1.0
    speed: float = 1.0
    traction: float = 1.0
    fuel_efficiency: float = 1.0
    suspension: float = 1.0

class Terrain:
    """Advanced terrain generation with realistic hills"""
    def __init__(self, seed=42, difficulty=1.0):
        self.seed = seed
        self.difficulty = difficulty
        self.points = []
        self.hazards = []
        self.coins = []
        self.fuel_cans = []
        self.hills = []
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate realistic procedural terrain with smooth hills and hazards"""
        random.seed(self.seed)
        self.points = []
        self.hazards = []
        self.coins = []
        self.fuel_cans = []
        self.hills = []
        
        # Start with smooth base height
        y = 550
        smoothing_factor = 15
        
        for x in range(0, int(TERRAIN_LENGTH), 5):
            # Smooth terrain using multiple sine waves
            base_height = 550
            hill1 = math.sin(x / 300 + self.seed) * 80
            hill2 = math.sin(x / 600 + self.seed * 2) * 60
            hill3 = math.sin(x / 1200 + self.seed * 3) * 40
            
            target_y = base_height + hill1 + hill2 + hill3
            y = y + (target_y - y) * 0.2  # Smooth interpolation
            y = max(200, min(700, y))
            
            # Add small random bumps
            if random.random() < 0.15:
                y += random.uniform(-8, 8)
            
            self.points.append((x, y))
            
            # Add hazards (deep holes) on harder difficulties
            if random.random() < 0.03 * self.difficulty and x % 150 == 0:
                hole_depth = int(60 * (0.5 + self.difficulty))
                hole_width = int(80 * (0.5 + self.difficulty * 0.5))
                self.points.append((x + 20, y + hole_depth))
                self.hazards.append({'x': x + 20, 'depth': hole_depth, 'width': hole_width})
                self.points.append((x + 40, y))
            
            # Spawn coins on safer terrain
            if random.random() < 0.03 and len(self.points) > 5:
                # Check if on relatively flat ground
                if len(self.points) >= 2:
                    prev_y = self.points[-2][1]
                    if abs(y - prev_y) < 5:  # Flat terrain
                        self.coins.append({'x': x, 'y': y - 60, 'collected': False, 'value': 1})
            
            # Spawn fuel cans on terrain
            if random.random() < 0.015 and len(self.points) > 5:
                if len(self.points) >= 2:
                    prev_y = self.points[-2][1]
                    if abs(y - prev_y) < 8:
                        self.fuel_cans.append({'x': x, 'y': y - 65, 'collected': False, 'fuel': 35})
        
        return self.points
    
    def get_ground_height(self, x: float) -> float:
        """Get ground height at given x position"""
        if not self.points:
            return 600
        
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1) if x2 != x1 else 0
                return y1 + (y2 - y1) * t
        
        return self.points[-1][1] if self.points else 600
    
    def get_ground_angle(self, x: float) -> float:
        """Get terrain angle at given x position"""
        if not self.points:
            return 0
        
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x <= x2:
                dx = x2 - x1
                dy = y2 - y1
                return -math.atan2(dy, dx)
        
        return 0

class Wheel:
    """Car wheel with physics"""
    def __init__(self, x_offset: float, radius: float = 8):
        self.x_offset = x_offset
        self.radius = radius
        self.rotation = 0
        self.grip = 1.0
    
    def update(self, velocity: float):
        """Update wheel rotation"""
        if velocity != 0:
            self.rotation += (velocity / self.radius) * 0.1
            self.rotation %= (2 * math.pi)

class Car:
    """Advanced car with physics and upgrades"""
    def __init__(self, x: float, y: float, stats: CarStats):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.stats = stats
        
        # Dimensions
        self.width = 30
        self.height = 50
        
        # Wheels
        self.front_wheel = Wheel(self.width * 0.3, 8)
        self.rear_wheel = Wheel(-self.width * 0.3, 8)
        
        # Fuel system
        self.fuel = 100
        self.max_fuel = 100
        
        # Status
        self.engine_power = 0
        self.brake_power = 0
        self.is_grounded = False
        self.distance_traveled = 0
        self.last_x = x
        self.health = 100
        self.max_health = 100
        self.coins_collected = 0
        self.flip_damage_cooldown = 0
        self.drift_power = 0
        
        # Visual properties
        self.color = random.choice(CAR_COLORS)
    
    def handle_input(self, keys):
        """Handle player input"""
        self.engine_power = 0
        self.brake_power = 0
        
        # Acceleration
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.engine_power = 1.0 * self.stats.acceleration
        
        # Braking
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.brake_power = 0.8
        
        # Steering
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle = min(self.angle + 0.08, math.pi / 3)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle = max(self.angle - 0.08, -math.pi / 3)
        
        # Auto-stabilize
        if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.angle *= 0.92
    
    def update(self, terrain: Terrain):
        """Update car physics"""
        if self.flip_damage_cooldown > 0:
            self.flip_damage_cooldown -= 1
        
        # Apply engine force
        if self.engine_power > 0 and self.fuel > 0:
            self.vx += math.cos(self.angle) * self.engine_power * 0.8
            self.vy += math.sin(self.angle) * self.engine_power * 0.8
            self.fuel -= self.engine_power * 0.3 / self.stats.fuel_efficiency
            self.fuel = max(0, self.fuel)
        
        # Apply braking
        if self.brake_power > 0:
            self.vx *= (1 - self.brake_power * 0.1)
            self.vy *= (1 - self.brake_power * 0.1)
        
        # Physics
        self.vy += GRAVITY * (1 - self.stats.suspension * 0.1)
        self.vx *= AIR_RESISTANCE
        self.vy *= AIR_RESISTANCE
        
        # Ground collision
        ground_y = terrain.get_ground_height(self.x)
        terrain_angle = terrain.get_ground_angle(self.x)
        
        self.is_grounded = False
        
        if self.y + self.height / 2 >= ground_y:
            self.y = ground_y - self.height / 2
            self.is_grounded = True
            self.vy = 0
            
            # Friction and traction
            friction = FRICTION * self.stats.traction
            self.vx *= friction
            
            # Align with terrain
            target_angle = terrain_angle
            self.angle += (target_angle - self.angle) * 0.15
            
            # Flip damage
            flip_angle = abs(self.angle)
            if flip_angle > ROLLOVER_THRESHOLD and flip_angle < FLIP_DAMAGE_THRESHOLD:
                if self.flip_damage_cooldown <= 0:
                    damage = min(20, flip_angle * 5)
                    self.health -= damage
                    self.flip_damage_cooldown = 30
            elif flip_angle > FLIP_DAMAGE_THRESHOLD:
                if self.flip_damage_cooldown <= 0:
                    damage = min(60, flip_angle * 20)
                    self.health -= damage
                    self.flip_damage_cooldown = 60
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Update distance
        self.distance_traveled += abs(self.x - self.last_x)
        self.last_x = self.x
        
        # Update wheels
        self.front_wheel.update(self.vx)
        self.rear_wheel.update(self.vx)
        
        # Boundary checks
        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.y > SCREEN_HEIGHT + 300:
            self.health = 0
        
        # Fuel system
        if self.fuel <= 0:
            self.health = max(0, self.health - 0.5)
    
    def collect_coin(self, coin: Dict):
        """Collect a coin"""
        if not coin['collected']:
            self.coins_collected += 1
            coin['collected'] = True
            return True
        return False
    
    def collect_fuel(self, fuel_can: Dict):
        """Collect fuel can"""
        if not fuel_can['collected']:
            fuel_value = fuel_can['fuel']
            self.fuel = min(self.max_fuel, self.fuel + fuel_value)
            fuel_can['collected'] = True
            return True
        return False
    
    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw car with realistic Hill Climb Racing style graphics"""
        screen_x = self.x - camera_x
        
        if -100 < screen_x < SCREEN_WIDTH + 100:
            # Create larger car surface
            car_width = 45
            car_height = 65
            car_surface = pygame.Surface((car_width, car_height), pygame.SRCALPHA)
            
            # Draw car body (main chassis) - more realistic
            body_color = self.color
            pygame.draw.rect(car_surface, body_color, (5, 20, car_width - 10, 30))
            
            # Draw car roof/cabin
            roof_color = tuple(min(c + 40, 255) for c in body_color)
            pygame.draw.polygon(car_surface, roof_color, [
                (10, 18),
                (car_width - 10, 18),
                (car_width - 8, 10),
                (12, 10)
            ])
            
            # Draw windows/glass
            window_color = (150, 200, 255, 100)
            pygame.draw.rect(car_surface, window_color, (12, 12, car_width - 24, 8))
            
            # Draw headlights
            pygame.draw.circle(car_surface, (255, 255, 200), (8, 22), 3)
            pygame.draw.circle(car_surface, (255, 255, 150), (8, 22), 1)
            
            # Draw front bumper
            pygame.draw.rect(car_surface, (50, 50, 50), (5, 48, car_width - 10, 3))
            
            # Draw wheels with detailed graphics
            wheel_color = (30, 30, 30)
            rim_color = (100, 100, 100)
            
            # Front wheel (left)
            pygame.draw.circle(car_surface, wheel_color, (10, 52), 9)
            pygame.draw.circle(car_surface, rim_color, (10, 52), 5)
            for i in range(4):
                angle = (self.front_wheel.rotation + i * math.pi / 2)
                x_offset = math.cos(angle) * 3
                y_offset = math.sin(angle) * 3
                pygame.draw.line(car_surface, rim_color, 
                               (10 + x_offset, 52 + y_offset), 
                               (10 - x_offset, 52 - y_offset), 1)
            
            # Rear wheel (right)
            pygame.draw.circle(car_surface, wheel_color, (car_width - 10, 52), 9)
            pygame.draw.circle(car_surface, rim_color, (car_width - 10, 52), 5)
            for i in range(4):
                angle = (self.rear_wheel.rotation + i * math.pi / 2)
                x_offset = math.cos(angle) * 3
                y_offset = math.sin(angle) * 3
                pygame.draw.line(car_surface, rim_color, 
                               (car_width - 10 + x_offset, 52 + y_offset), 
                               (car_width - 10 - x_offset, 52 - y_offset), 1)
            
            # Draw suspension (springs between body and wheels)
            suspension_color = (200, 100, 100)
            pygame.draw.line(car_surface, suspension_color, (10, 48), (10, 43), 2)
            pygame.draw.line(car_surface, suspension_color, (car_width - 10, 48), (car_width - 10, 43), 2)
            
            # Draw shadow/undercarriage
            pygame.draw.line(car_surface, (20, 20, 20), (8, 50), (car_width - 8, 50), 3)
            
            # Rotate and blit
            rotated = pygame.transform.rotate(car_surface, math.degrees(self.angle))
            rect = rotated.get_rect(center=(screen_x, self.y))
            
            # Draw shadow under car
            shadow_surface = pygame.Surface((car_width, 10), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (0, 0, car_width, 10))
            shadow_rotated = pygame.transform.rotate(shadow_surface, math.degrees(self.angle))
            shadow_rect = shadow_rotated.get_rect(center=(screen_x, self.y + 30))
            surface.blit(shadow_rotated, shadow_rect)
            
            # Draw the car
            surface.blit(rotated, rect)

class ParticleEffect:
    """Advanced particle system with realistic effects"""
    def __init__(self, x: float, y: float, particle_type: str = "dust"):
        self.particles = []
        self.particle_type = particle_type
        
        if particle_type == "dust":
            count = 20
            colors = [(139, 90, 43), (160, 110, 60), (180, 130, 80)]
        elif particle_type == "spark":
            count = 15
            colors = [(255, 215, 0), (255, 165, 0), (255, 200, 100)]
        else:  # smoke
            count = 10
            colors = [(150, 150, 150), (180, 180, 180), (200, 200, 200)]
        
        for _ in range(random.randint(count - 5, count)):
            vx = random.uniform(-5, 5)
            vy = random.uniform(-6, -1)
            lifetime = random.randint(40, 70)
            
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy,
                'lifetime': lifetime, 'max_lifetime': lifetime,
                'size': random.randint(3, 8),
                'color': random.choice(colors)
            })
    
    def update(self):
        """Update particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.25
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0
    
    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw particles with realistic effects"""
        for particle in self.particles:
            alpha = int(255 * particle['lifetime'] / particle['max_lifetime'])
            size = int(particle['size'] * (particle['lifetime'] / particle['max_lifetime']))
            
            if size > 0:
                screen_x = particle['x'] - camera_x
                if -50 < screen_x < SCREEN_WIDTH + 50:
                    color = particle.get('color', Color.LIGHT_GRAY.value)
                    p_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                    pygame.draw.circle(p_surface, (*color, alpha), (size + 1, size + 1), size)
                    surface.blit(p_surface, (int(screen_x - size - 1), int(particle['y'] - size - 1)))

class Button:
    """UI Button"""
    def __init__(self, x: float, y: float, width: float, height: float, text: str, color=Color.BLUE.value):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        """Draw button"""
        button_color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, button_color, self.rect)
        pygame.draw.rect(surface, Color.WHITE.value, self.rect, 2)
        
        text_surface = font.render(self.text, True, Color.WHITE.value)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)
    
    def update(self, pos: Tuple[int, int]):
        """Update button hover state"""
        self.hover = self.rect.collidepoint(pos)

class GUI:
    """Advanced GUI system"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 64)
        self.font_xl = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
    
    def draw_hud(self, surface: pygame.Surface, car: Car, level: int, current_level_name: str = ""):
        """Draw enhanced in-game HUD"""
        # Draw HUD background panel
        panel_color = (0, 0, 0, 180)
        panel_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, panel_color, (0, 0, 400, 200))
        pygame.draw.rect(panel_surface, Color.GOLD.value, (0, 0, 400, 200), 2)
        surface.blit(panel_surface, (10, 10))
        
        # Speed
        speed = math.sqrt(car.vx ** 2 + car.vy ** 2)
        speed_text = self.font_medium.render(f"Speed: {speed:.1f}", True, Color.CYAN.value)
        surface.blit(speed_text, (30, 25))
        
        # Fuel bar with label
        fuel_ratio = car.fuel / car.max_fuel
        fuel_color = Color.RED.value if fuel_ratio < 0.2 else (Color.YELLOW.value if fuel_ratio < 0.5 else Color.GREEN.value)
        pygame.draw.rect(surface, Color.GRAY.value, (30, 70, 350, 25), 2)
        pygame.draw.rect(surface, fuel_color, (32, 72, 346 * fuel_ratio, 21))
        fuel_text = self.font_tiny.render(f"FUEL: {car.fuel:.0f}/{car.max_fuel:.0f}", True, Color.WHITE.value)
        surface.blit(fuel_text, (40, 75))
        
        # Health bar with label
        health_ratio = car.health / car.max_health
        health_color = Color.GREEN.value if health_ratio > 0.5 else (Color.RED.value if health_ratio < 0.2 else Color.YELLOW.value)
        pygame.draw.rect(surface, Color.GRAY.value, (30, 105, 350, 25), 2)
        pygame.draw.rect(surface, health_color, (32, 107, 346 * health_ratio, 21))
        health_text = self.font_tiny.render(f"HEALTH: {car.health:.0f}", True, Color.WHITE.value)
        surface.blit(health_text, (40, 110))
        
        # Distance and level on right side
        distance_text = self.font_small.render(f"Distance: {car.distance_traveled:.0f}m", True, Color.WHITE.value)
        surface.blit(distance_text, (SCREEN_WIDTH - 380, 25))
        
        level_text = self.font_small.render(f"Level: {level}", True, Color.GOLD.value)
        surface.blit(level_text, (SCREEN_WIDTH - 380, 60))
        
        # Coins collected with icon
        coins_text = self.font_small.render(f"Coins: {car.coins_collected}", True, Color.YELLOW.value)
        surface.blit(coins_text, (SCREEN_WIDTH - 380, 95))
    
    def draw_main_menu(self, surface: pygame.Surface, selected: int = 0):
        """Draw main menu with advanced graphics"""
        # Gradient-like background
        for i in range(SCREEN_HEIGHT):
            color_val = int(20 + (61 - 20) * i / SCREEN_HEIGHT)
            pygame.draw.line(surface, (color_val, color_val + 13, color_val + 41), (0, i), (SCREEN_WIDTH, i))
        
        # Title with gradient effect
        title = self.font_large.render("HILL CLIMB", True, Color.GOLD.value)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title, title_rect)
        
        subtitle = self.font_xl.render("RACING", True, Color.CYAN.value)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = ["Play Game", "Level Select", "Garage", "Shop", "Achievements", "Settings", "Quit"]
        for i, option in enumerate(options):
            color = Color.GOLD.value if i == selected else Color.WHITE.value
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 280 + i * 70))
            surface.blit(text, rect)
            
            if i == selected:
                pygame.draw.rect(surface, Color.GOLD.value, rect.inflate(30, 20), 3)
    
    def draw_level_select(self, surface: pygame.Surface, selected: int = 0):
        """Draw level selection screen"""
        surface.fill(Color.DARK_BLUE.value)
        
        title = self.font_large.render("SELECT LEVEL", True, Color.GOLD.value)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        for i, level in enumerate(LEVELS):
            y = 200 + i * 100
            
            # Level name
            name_text = self.font_medium.render(level["name"], True, Color.WHITE.value)
            surface.blit(name_text, (100, y))
            
            # Difficulty
            difficulty_colors = {
                "Easy": Color.GREEN.value,
                "Medium": Color.YELLOW.value,
                "Hard": Color.ORANGE.value,
                "Very Hard": Color.RED.value,
                "Extreme": Color.PURPLE.value
            }
            diff_text = self.font_small.render(f"Difficulty: {level['difficulty']}", True, difficulty_colors.get(level['difficulty'], Color.WHITE.value))
            surface.blit(diff_text, (100, y + 40))
            
            if i == selected:
                pygame.draw.rect(surface, Color.GOLD.value, (80, y - 10, SCREEN_WIDTH - 160, 90), 3)
    
    def draw_shop(self, surface: pygame.Surface, coins: int, selected: int = 0):
        """Draw shop menu"""
        surface.fill(Color.DARK_BLUE.value)
        
        title = self.font_large.render("SHOP", True, Color.GOLD.value)
        surface.blit(title, (50, 30))
        
        coins_text = self.font_medium.render(f"Coins: {coins}", True, Color.GOLD.value)
        surface.blit(coins_text, (SCREEN_WIDTH - 300, 30))
        
        items = list(SHOP_ITEMS.items())
        for i, (key, item) in enumerate(items):
            y = 150 + i * 110
            
            # Item name
            name_text = self.font_medium.render(item["name"], True, Color.WHITE.value)
            surface.blit(name_text, (100, y))
            
            # Description
            desc_text = self.font_tiny.render(item["description"], True, Color.LIGHT_GRAY.value)
            surface.blit(desc_text, (100, y + 35))
            
            # Cost
            cost_text = self.font_small.render(f"Cost: {item['cost']} Coins", True, Color.GOLD.value)
            surface.blit(cost_text, (100, y + 60))
            
            if i == selected:
                pygame.draw.rect(surface, Color.GOLD.value, (80, y - 10, SCREEN_WIDTH - 160, 100), 3)
    
    def draw_garage(self, surface: pygame.Surface, stats: CarStats, coins: int):
        """Draw garage/upgrade screen"""
        surface.fill(Color.DARK_BLUE.value)
        
        title = self.font_large.render("GARAGE", True, Color.GOLD.value)
        surface.blit(title, (50, 30))
        
        coins_text = self.font_medium.render(f"Coins: {coins}", True, Color.GOLD.value)
        surface.blit(coins_text, (SCREEN_WIDTH - 300, 30))
        
        upgrades = [
            ("Acceleration", stats.acceleration),
            ("Top Speed", stats.speed),
            ("Traction", stats.traction),
            ("Fuel Efficiency", stats.fuel_efficiency),
            ("Suspension", stats.suspension),
        ]
        
        for i, (name, value) in enumerate(upgrades):
            y = 150 + i * 120
            text = self.font_small.render(f"{name}: {value:.2f}x", True, Color.WHITE.value)
            surface.blit(text, (100, y))
            
            # Progress bar
            pygame.draw.rect(surface, Color.GRAY.value, (100, y + 35, 300, 20), 2)
            pygame.draw.rect(surface, Color.LIGHT_BLUE.value, (100, y + 35, 300 * min(value / 3, 1), 20))
        
        back_text = self.font_small.render("Press ESC to return", True, Color.GOLD.value)
        surface.blit(back_text, (50, SCREEN_HEIGHT - 50))
    
    def draw_achievements(self, surface: pygame.Surface, achievements: Dict[str, bool]):
        """Draw achievements screen"""
        surface.fill(Color.DARK_BLUE.value)
        
        title = self.font_large.render("ACHIEVEMENTS", True, Color.GOLD.value)
        surface.blit(title, (50, 30))
        
        y = 150
        for ach_key, ach_data in ACHIEVEMENTS.items():
            unlocked = achievements.get(ach_key, False)
            color = Color.GOLD.value if unlocked else Color.GRAY.value
            
            text = self.font_small.render(f"{'[✓]' if unlocked else '[ ]'} {ach_data['title']} - +{ach_data['reward']}", True, color)
            surface.blit(text, (100, y))
            y += 60
        
        back_text = self.font_small.render("Press ESC to return", True, Color.GOLD.value)
        surface.blit(back_text, (50, SCREEN_HEIGHT - 50))
    
    def draw_pause_menu(self, surface: pygame.Surface, selected: int = 0):
        """Draw pause menu"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(Color.BLACK.value)
        surface.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, Color.GOLD.value)
        surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 150))
        
        options = ["Resume", "Restart", "Main Menu", "Quit"]
        for i, option in enumerate(options):
            color = Color.GOLD.value if i == selected else Color.WHITE.value
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 80))
            surface.blit(text, rect)
    
    def draw_game_over(self, surface: pygame.Surface, car: Car, level: int):
        """Draw game over screen"""
        surface.fill(Color.DARK_BLUE.value)
        
        game_over_text = self.font_large.render("GAME OVER", True, Color.RED.value)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))
        
        distance_text = self.font_medium.render(f"Distance: {car.distance_traveled:.0f}m", True, Color.WHITE.value)
        surface.blit(distance_text, (SCREEN_WIDTH // 2 - distance_text.get_width() // 2, 250))
        
        coins_text = self.font_medium.render(f"Coins Earned: {car.coins_collected}", True, Color.GOLD.value)
        surface.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 310))
        
        level_text = self.font_medium.render(f"Level Reached: {level}", True, Color.WHITE.value)
        surface.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 370))
        
        restart_text = self.font_small.render("Press SPACE to continue", True, Color.GOLD.value)
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 480))

class SaveManager:
    """Manages game saves"""
    def __init__(self, save_file="game_save.json"):
        self.save_file = save_file
        self.data = self.load()
    
    def load(self):
        """Load game data"""
        if os.path.exists(self.save_file):
            with open(self.save_file, 'r') as f:
                return json.load(f)
        return {
            "total_coins": 0,
            "total_distance": 0,
            "car_stats": asdict(CarStats()),
            "achievements": {},
            "high_scores": {}
        }
    
    def save(self):
        """Save game data"""
        with open(self.save_file, 'w') as f:
            json.dump(self.data, f, indent=2)

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hill Climb Racing - Advanced Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState.MENU
        
        # Game objects
        self.gui = GUI()
        self.save_manager = SaveManager()
        
        # Initialize from save
        stats_data = self.save_manager.data.get("car_stats", {})
        self.car_stats = CarStats(**{k: stats_data.get(k, getattr(CarStats(), k)) for k in CarStats.__dataclass_fields__})
        self.total_coins = self.save_manager.data.get("total_coins", 0)
        self.achievements = self.save_manager.data.get("achievements", {})
        
        # Game state
        self.current_level = 0
        self.level_name = ""
        self.terrain = None
        self.car = None
        self.particles: List[ParticleEffect] = []
        self.camera_x = 0
        
        # Menu state
        self.menu_selected = 0
        self.level_selected = 0
        self.pause_selected = 0
        self.shop_selected = 0
        self.achievements_view = False
        
        # Game stats
        self.distance_checkpoint = 0
        self.level = 1
    
    def handle_events(self):
        """Handle all events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                self._handle_key_press(event.key)
    
    def _handle_key_press(self, key):
        """Handle key presses based on game state"""
        if self.game_state == GameState.MENU:
            if key == pygame.K_UP or key == pygame.K_w:
                self.menu_selected = (self.menu_selected - 1) % 7
            elif key == pygame.K_DOWN or key == pygame.K_s:
                self.menu_selected = (self.menu_selected + 1) % 7
            elif key == pygame.K_RETURN:
                self._handle_menu_selection()
        
        elif self.game_state == GameState.LEVEL_SELECT:
            if key == pygame.K_UP or key == pygame.K_w:
                self.level_selected = (self.level_selected - 1) % len(LEVELS)
            elif key == pygame.K_DOWN or key == pygame.K_s:
                self.level_selected = (self.level_selected + 1) % len(LEVELS)
            elif key == pygame.K_RETURN:
                self.start_game(self.level_selected)
            elif key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
        
        elif self.game_state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self.game_state = GameState.PAUSED
        
        elif self.game_state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self.game_state = GameState.PLAYING
            elif key == pygame.K_UP or key == pygame.K_w:
                self.pause_selected = (self.pause_selected - 1) % 4
            elif key == pygame.K_DOWN or key == pygame.K_s:
                self.pause_selected = (self.pause_selected + 1) % 4
            elif key == pygame.K_RETURN:
                self._handle_pause_selection()
        
        elif self.game_state == GameState.GAME_OVER:
            if key == pygame.K_SPACE:
                self.game_state = GameState.MENU
        
        elif self.game_state == GameState.GARAGE:
            if key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
        
        elif self.game_state == GameState.SHOP:
            if key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
        
        elif self.game_state == GameState.ACHIEVEMENTS:
            if key == pygame.K_ESCAPE:
                self.game_state = GameState.MENU
    
    def _handle_menu_selection(self):
        """Handle main menu selection"""
        if self.menu_selected == 0:  # Play
            self.game_state = GameState.LEVEL_SELECT
        elif self.menu_selected == 1:  # Level Select
            self.game_state = GameState.LEVEL_SELECT
        elif self.menu_selected == 2:  # Garage
            self.game_state = GameState.GARAGE
        elif self.menu_selected == 3:  # Shop
            self.game_state = GameState.SHOP
        elif self.menu_selected == 4:  # Achievements
            self.game_state = GameState.ACHIEVEMENTS
        elif self.menu_selected == 6:  # Quit
            self.running = False
    
    def _handle_pause_selection(self):
        """Handle pause menu selection"""
        if self.pause_selected == 0:  # Resume
            self.game_state = GameState.PLAYING
        elif self.pause_selected == 1:  # Restart
            self.start_game(self.current_level)
        elif self.pause_selected == 2:  # Menu
            self.game_state = GameState.MENU
        elif self.pause_selected == 3:  # Quit
            self.running = False
    
    def start_game(self, level_idx: int):
        """Start a new game"""
        self.game_state = GameState.PLAYING
        self.current_level = level_idx
        
        level_data = LEVELS[level_idx]
        self.level_name = level_data["name"]
        
        self.terrain = Terrain(seed=level_data["seed"], difficulty=level_idx + 1)
        self.car = Car(100, 300, self.car_stats)
        self.particles = []
        self.camera_x = 0
        self.distance_checkpoint = 0
        self.level = level_idx + 1
        self.pause_selected = 0
    
    def update(self):
        """Update game logic"""
        if self.game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            self.car.handle_input(keys)
            self.car.update(self.terrain)
            
            # Particle effects
            if self.car.is_grounded and (self.car.engine_power > 0 or self.car.brake_power > 0):
                self.particles.append(ParticleEffect(self.car.x, self.car.y + 25, "dust"))
            
            # Update particles
            self.particles = [p for p in self.particles if p.update()]
            
            # Camera follow
            target_camera_x = self.car.x - 200
            self.camera_x += (target_camera_x - self.camera_x) * 0.1
            
            # Coin collection
            for coin in self.terrain.coins:
                if not coin['collected']:
                    dist = math.sqrt((self.car.x - coin['x']) ** 2 + (self.car.y - coin['y']) ** 2)
                    if dist < 50:
                        self.car.collect_coin(coin)
                        self.total_coins += coin.get('value', 1)
            
            # Fuel can collection
            for fuel_can in self.terrain.fuel_cans:
                if not fuel_can['collected']:
                    dist = math.sqrt((self.car.x - fuel_can['x']) ** 2 + (self.car.y - fuel_can['y']) ** 2)
                    if dist < 50:
                        self.car.collect_fuel(fuel_can)
            
            # Game over condition
            if self.car.health <= 0 or self.car.fuel <= 0:
                self.game_state = GameState.GAME_OVER
                self.save_manager.data["total_coins"] = self.total_coins
                self.save_manager.save()
    
    def draw(self):
        """Draw everything"""
        if self.game_state == GameState.MENU:
            self.gui.draw_main_menu(self.screen, self.menu_selected)
        
        elif self.game_state == GameState.LEVEL_SELECT:
            self.gui.draw_level_select(self.screen, self.level_selected)
        
        elif self.game_state == GameState.PLAYING:
            self._draw_game()
        
        elif self.game_state == GameState.PAUSED:
            self._draw_game()
            self.gui.draw_pause_menu(self.screen, self.pause_selected)
        
        elif self.game_state == GameState.GAME_OVER:
            self.screen.fill(Color.DARK_BLUE.value)
            self.gui.draw_game_over(self.screen, self.car, self.level)
        
        elif self.game_state == GameState.GARAGE:
            self.gui.draw_garage(self.screen, self.car_stats, self.total_coins)
        
        elif self.game_state == GameState.SHOP:
            self.gui.draw_shop(self.screen, self.total_coins, self.shop_selected)
        
        elif self.game_state == GameState.ACHIEVEMENTS:
            self.gui.draw_achievements(self.screen, self.achievements)
        
        pygame.display.flip()
    
    def _draw_game(self):
        """Draw game scene with realistic graphics"""
        # Sky gradient (more realistic)
        for i in range(SCREEN_HEIGHT):
            # Sky color gradient
            ratio = i / SCREEN_HEIGHT
            r = int(135 + (100 - 135) * ratio)
            g = int(206 + (150 - 206) * ratio)
            b = int(235 + (100 - 235) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))
        
        # Draw distant hills/mountains (parallax effect)
        if self.terrain and self.terrain.points:
            # Draw far background hills
            far_points = [(p[0] - self.camera_x * 0.3, p[1] * 0.3 + 100) for p in self.terrain.points[::4]]
            for i in range(len(far_points) - 1):
                x1, y1 = int(far_points[i][0]), int(far_points[i][1])
                x2, y2 = int(far_points[i+1][0]), int(far_points[i+1][1])
                pygame.draw.line(self.screen, (150, 180, 200), (x1, y1), (x2, y2), 3)
            
            # Draw mid-ground terrain
            mid_points = [(p[0] - self.camera_x * 0.6, p[1] * 0.5 + 50) for p in self.terrain.points[::2]]
            for i in range(len(mid_points) - 1):
                x1, y1 = int(mid_points[i][0]), int(mid_points[i][1])
                x2, y2 = int(mid_points[i+1][0]), int(mid_points[i+1][1])
                pygame.draw.line(self.screen, (100, 150, 100), (x1, y1), (x2, y2), 4)
        
        # Draw main terrain with thick grass-like appearance
        if self.terrain and self.terrain.points and len(self.terrain.points) > 1:
            try:
                points = self.terrain.points
                # Draw terrain ground (thick line for solid appearance)
                for i in range(len(points) - 1):
                    x1, y1 = int(points[i][0] - self.camera_x), int(points[i][1])
                    x2, y2 = int(points[i+1][0] - self.camera_x), int(points[i+1][1])
                    
                    if -100 < x1 < SCREEN_WIDTH + 100 or -100 < x2 < SCREEN_WIDTH + 100:
                        # Main terrain line
                        pygame.draw.line(self.screen, (34, 139, 34), (x1, y1), (x2, y2), 12)
                        # Grass highlight
                        pygame.draw.line(self.screen, (50, 180, 50), (x1, y1 - 2), (x2, y2 - 2), 6)
                        # Dirt shadow
                        pygame.draw.line(self.screen, (20, 100, 20), (x1, y1 + 3), (x2, y2 + 3), 4)
                
                # Draw ground beneath terrain
                ground_color = (101, 67, 33)  # Brown dirt
                for i in range(len(points) - 1):
                    x1, y1 = int(points[i][0] - self.camera_x), int(points[i][1])
                    x2, y2 = int(points[i+1][0] - self.camera_x), int(points[i+1][1])
                    
                    if -100 < x1 < SCREEN_WIDTH + 100 or -100 < x2 < SCREEN_WIDTH + 100:
                        # Draw filled polygon from terrain to bottom
                        pygame.draw.polygon(self.screen, ground_color, [
                            (x1, y1), (x2, y2), 
                            (x2, SCREEN_HEIGHT), (x1, SCREEN_HEIGHT)
                        ])
            except Exception as e:
                print(f"Error drawing terrain: {e}")
        
        # Draw coins with shine effect
        for coin in self.terrain.coins:
            if not coin['collected']:
                screen_x = coin['x'] - self.camera_x
                if -50 < screen_x < SCREEN_WIDTH + 50:
                    coin_y = int(coin['y'])
                    coin_x = int(screen_x)
                    
                    # Coin outer circle (gold)
                    pygame.draw.circle(self.screen, (255, 215, 0), (coin_x, coin_y), 10)
                    # Coin inner circle (darker gold)
                    pygame.draw.circle(self.screen, (218, 165, 32), (coin_x, coin_y), 8)
                    # Coin shine/highlight
                    pygame.draw.circle(self.screen, (255, 255, 200), (coin_x - 2, coin_y - 2), 3)
                    # Coin text indicator
                    pygame.draw.circle(self.screen, (200, 150, 0), (coin_x, coin_y), 6, 1)
        
        # Draw fuel cans
        for fuel_can in self.terrain.fuel_cans:
            if not fuel_can['collected']:
                screen_x = fuel_can['x'] - self.camera_x
                if -50 < screen_x < SCREEN_WIDTH + 50:
                    fuel_y = int(fuel_can['y'])
                    fuel_x = int(screen_x)
                    
                    # Fuel can body (red/orange)
                    pygame.draw.rect(self.screen, (220, 50, 50), (fuel_x - 7, fuel_y - 12, 14, 24))
                    # Fuel cap
                    pygame.draw.rect(self.screen, (50, 50, 50), (fuel_x - 5, fuel_y - 14, 10, 3))
                    # Fuel level indicator
                    pygame.draw.line(self.screen, (255, 200, 0), (fuel_x - 3, fuel_y - 8), (fuel_x + 3, fuel_y - 8), 2)
        
        # Car
        self.car.draw(self.screen, self.camera_x)
        
        # Particles
        for particle in self.particles:
            particle.draw(self.screen, self.camera_x)
        
        # HUD
        self.gui.draw_hud(self.screen, self.car, self.level, self.level_name)
    
    def run(self):
        """Main loop"""
        while self.running:
            try:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
            except Exception as e:
                print(f"Error in game loop: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

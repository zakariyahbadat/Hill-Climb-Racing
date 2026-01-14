"""
Advanced Hill Climb Racing Game
A feature-rich car racing game with physics, terrain generation, and progression system
"""

import pygame
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
import os

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.6
FRICTION = 0.98
AIR_RESISTANCE = 0.99

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

@dataclass
class CarStats:
    """Car upgrade statistics"""
    acceleration: float = 1.0
    speed: float = 1.0
    traction: float = 1.0
    fuel_efficiency: float = 1.0
    wheel_grip: float = 1.0

class GameState(Enum):
    """Game states"""
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    LEVEL_SELECT = 5
    GARAGE = 6
    SHOP = 7

class Terrain:
    """Generates and manages terrain"""
    def __init__(self, seed=42):
        self.seed = seed
        self.points = []
        self.generate_terrain()
    
    def generate_terrain(self):
        """Generate smooth terrain using Perlin-like noise"""
        self.points = []
        y = 600
        smoothing = 1
        
        for x in range(0, SCREEN_WIDTH * 5, 20):
            # Simple procedural generation with variation
            variation = math.sin(x / 100) * 30 + math.sin(x / 200) * 40
            y = max(300, min(650, y + random.uniform(-3, 2) + variation * 0.01))
            
            # Add hazards occasionally
            if random.random() < 0.05:
                hazard_depth = random.randint(30, 60)
                self.points.append((x, y))
                self.points.append((x + 30, y + hazard_depth))
                self.points.append((x + 60, y))
            else:
                self.points.append((x, y))
        
        return self.points
    
    def get_ground_height(self, x: float) -> float:
        """Get ground height at given x position"""
        if not self.points:
            return 600
        
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            
            if x1 <= x <= x2:
                # Linear interpolation
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
    """Represents a car wheel"""
    def __init__(self, x_offset: float, radius: float = 8):
        self.x_offset = x_offset
        self.radius = radius
        self.rotation = 0
        self.grip = 1.0
    
    def update(self, velocity: float):
        """Update wheel rotation based on velocity"""
        if velocity != 0:
            self.rotation += (velocity / self.radius) * 0.1
            self.rotation %= (2 * math.pi)

class Car:
    """Main car object with physics"""
    def __init__(self, x: float, y: float, stats: CarStats):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.stats = stats
        
        # Car dimensions
        self.width = 30
        self.height = 50
        
        # Wheels
        self.front_wheel = Wheel(self.width * 0.3)
        self.rear_wheel = Wheel(-self.width * 0.3)
        
        # Fuel system
        self.fuel = 100
        self.max_fuel = 100
        self.fuel_efficiency = stats.fuel_efficiency
        
        # State
        self.engine_power = 0
        self.brake_power = 0
        self.is_grounded = False
        self.distance_traveled = 0
        self.last_x = x
        self.health = 100
        self.max_health = 100
        self.flip_damage_cooldown = 0
    
    def handle_input(self, keys):
        """Handle player input"""
        self.engine_power = 0
        self.brake_power = 0
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.engine_power = 1.0 * self.stats.acceleration
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.brake_power = 0.8
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle = min(self.angle + 0.08, math.pi / 3)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle = max(self.angle - 0.08, -math.pi / 3)
        
        # Auto-stabilize when no turning input
        if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.angle *= 0.9
    
    def update(self, terrain: Terrain):
        """Update car physics"""
        if self.flip_damage_cooldown > 0:
            self.flip_damage_cooldown -= 1
        
        # Apply engine force
        if self.engine_power > 0 and self.fuel > 0:
            self.vx += math.cos(self.angle) * self.engine_power * 0.8
            self.vy += math.sin(self.angle) * self.engine_power * 0.8
            self.fuel -= self.engine_power * 0.3 / self.fuel_efficiency
        
        # Apply braking
        if self.brake_power > 0:
            self.vx *= (1 - self.brake_power * 0.1)
            self.vy *= (1 - self.brake_power * 0.1)
        
        # Apply gravity and air resistance
        self.vy += GRAVITY
        self.vx *= AIR_RESISTANCE
        self.vy *= AIR_RESISTANCE
        
        # Ground collision
        ground_y = terrain.get_ground_height(self.x)
        terrain_angle = terrain.get_ground_angle(self.x)
        
        self.is_grounded = False
        
        if self.y + self.height / 2 >= ground_y:
            self.y = ground_y - self.height / 2
            self.is_grounded = True
            
            # Friction and traction
            friction = FRICTION * self.stats.traction
            self.vy = 0
            self.vx *= friction
            
            # Auto-align with terrain
            target_angle = terrain_angle
            self.angle += (target_angle - self.angle) * 0.15
            
            # Flip damage
            flip_angle = abs(self.angle)
            if flip_angle > math.pi / 2:
                if self.flip_damage_cooldown <= 0:
                    damage = min(50, flip_angle * 10)
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
        
        # Constrain to screen boundaries
        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.y > SCREEN_HEIGHT + 200:
            self.health = 0
    
    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw the car"""
        # Calculate screen position
        screen_x = self.x - camera_x
        
        if -50 < screen_x < SCREEN_WIDTH + 50:
            # Create car surface
            car_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw car body
            pygame.draw.rect(car_surface, Color.RED.value, (0, 10, self.width, 30))
            pygame.draw.rect(car_surface, Color.ORANGE.value, (5, 5, self.width - 10, 10))
            pygame.draw.circle(car_surface, Color.LIGHT_BLUE.value, (self.width // 2, 15), 3)
            
            # Draw wheels
            pygame.draw.circle(car_surface, Color.BLACK.value, (8, 35), self.front_wheel.radius)
            pygame.draw.circle(car_surface, Color.BLACK.value, (self.width - 8, 35), self.rear_wheel.radius)
            
            # Rotate and blit
            rotated = pygame.transform.rotate(car_surface, math.degrees(self.angle))
            rect = rotated.get_rect(center=(screen_x, self.y))
            surface.blit(rotated, rect)

class ParticleEffect:
    """Particle effect system"""
    def __init__(self, x: float, y: float, particle_type: str = "dust"):
        self.particles = []
        self.particle_type = particle_type
        
        for _ in range(random.randint(5, 15)):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-3, 0)
            lifetime = random.randint(20, 40)
            self.particles.append({
                'x': x, 'y': y, 'vx': vx, 'vy': vy, 'lifetime': lifetime, 'max_lifetime': lifetime
            })
    
    def update(self):
        """Update particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.3
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0
    
    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw particles"""
        for particle in self.particles:
            alpha = int(255 * particle['lifetime'] / particle['max_lifetime'])
            color = Color.LIGHT_GRAY.value if self.particle_type == "dust" else Color.ORANGE.value
            
            # Create particle surface
            p_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(p_surface, (*color, alpha), (2, 2), 2)
            
            surface.blit(p_surface, (particle['x'] - camera_x, particle['y']))

class GUI:
    """Game GUI system"""
    def __init__(self):
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
    
    def draw_hud(self, surface: pygame.Surface, car: Car, level: int):
        """Draw heads-up display"""
        # Speed
        speed = math.sqrt(car.vx ** 2 + car.vy ** 2)
        speed_text = self.font_medium.render(f"Speed: {speed:.1f}", True, Color.GOLD.value)
        surface.blit(speed_text, (20, 20))
        
        # Fuel bar
        fuel_ratio = car.fuel / car.max_fuel
        pygame.draw.rect(surface, Color.GRAY.value, (20, 60, 200, 20), 2)
        pygame.draw.rect(surface, Color.GREEN.value, (20, 60, 200 * fuel_ratio, 20))
        fuel_text = self.font_tiny.render(f"Fuel: {car.fuel:.0f}", True, Color.WHITE.value)
        surface.blit(fuel_text, (25, 62))
        
        # Health bar
        health_ratio = car.health / car.max_health
        health_color = Color.GREEN.value if health_ratio > 0.5 else (Color.RED.value if health_ratio < 0.2 else Color.YELLOW.value)
        pygame.draw.rect(surface, Color.GRAY.value, (20, 90, 200, 20), 2)
        pygame.draw.rect(surface, health_color, (20, 90, 200 * health_ratio, 20))
        health_text = self.font_tiny.render(f"Health: {car.health:.0f}", True, Color.WHITE.value)
        surface.blit(health_text, (25, 92))
        
        # Distance and level
        distance_text = self.font_small.render(f"Distance: {car.distance_traveled:.0f}m", True, Color.WHITE.value)
        surface.blit(distance_text, (SCREEN_WIDTH - 400, 20))
        
        level_text = self.font_small.render(f"Level: {level}", True, Color.GOLD.value)
        surface.blit(level_text, (SCREEN_WIDTH - 400, 60))
    
    def draw_menu(self, surface: pygame.Surface, selected: int = 0):
        """Draw main menu"""
        surface.fill(Color.DARK_BLUE.value)
        
        # Title
        title = self.font_large.render("HILL CLIMB RACER", True, Color.GOLD.value)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        surface.blit(title, title_rect)
        
        # Menu options
        options = ["Play Game", "Garage", "Shop", "Settings", "Quit"]
        for i, option in enumerate(options):
            color = Color.GOLD.value if i == selected else Color.WHITE.value
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 80))
            surface.blit(text, rect)
            
            if i == selected:
                pygame.draw.rect(surface, Color.GOLD.value, rect.inflate(20, 20), 3)
    
    def draw_pause_menu(self, surface: pygame.Surface, selected: int = 0):
        """Draw pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Color.BLACK.value)
        surface.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_large.render("PAUSED", True, Color.GOLD.value)
        surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 150))
        
        # Options
        options = ["Resume", "Restart", "Main Menu"]
        for i, option in enumerate(options):
            color = Color.GOLD.value if i == selected else Color.WHITE.value
            text = self.font_medium.render(option, True, color)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 80))
            surface.blit(text, rect)
    
    def draw_game_over(self, surface: pygame.Surface, distance: float, level: int):
        """Draw game over screen"""
        surface.fill(Color.DARK_BLUE.value)
        
        game_over_text = self.font_large.render("GAME OVER", True, Color.RED.value)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        distance_text = self.font_medium.render(f"Distance: {distance:.0f}m", True, Color.WHITE.value)
        surface.blit(distance_text, (SCREEN_WIDTH // 2 - distance_text.get_width() // 2, 280))
        
        level_text = self.font_medium.render(f"Level Reached: {level}", True, Color.WHITE.value)
        surface.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 340))
        
        restart_text = self.font_small.render("Press SPACE to continue", True, Color.GOLD.value)
        surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 450))
    
    def draw_garage(self, surface: pygame.Surface, stats: CarStats, coins: int):
        """Draw garage/upgrade menu"""
        surface.fill(Color.DARK_BLUE.value)
        
        title = self.font_large.render("GARAGE", True, Color.GOLD.value)
        surface.blit(title, (50, 30))
        
        coins_text = self.font_medium.render(f"Coins: {coins}", True, Color.GOLD.value)
        surface.blit(coins_text, (SCREEN_WIDTH - 300, 30))
        
        # Display stats
        upgrades = [
            ("Acceleration", stats.acceleration),
            ("Top Speed", stats.speed),
            ("Traction", stats.traction),
            ("Fuel Efficiency", stats.fuel_efficiency),
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

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hill Climb Racing - Advanced")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = GameState.MENU
        
        # Game objects
        self.gui = GUI()
        self.terrain = Terrain()
        self.car_stats = CarStats()
        self.car = Car(100, 300, self.car_stats)
        self.particles: List[ParticleEffect] = []
        
        # Game state
        self.level = 1
        self.coins = 0
        self.menu_selected = 0
        self.pause_selected = 0
        self.camera_x = 0
        self.distance_checkpoint = 0
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == GameState.MENU:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_selected = (self.menu_selected - 1) % 5
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_selected = (self.menu_selected + 1) % 5
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selected == 0:  # Play
                            self.start_game()
                        elif self.menu_selected == 1:  # Garage
                            self.game_state = GameState.GARAGE
                        elif self.menu_selected == 4:  # Quit
                            self.running = False
                
                elif self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PAUSED
                
                elif self.game_state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PLAYING
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.pause_selected = (self.pause_selected - 1) % 3
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.pause_selected = (self.pause_selected + 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if self.pause_selected == 0:  # Resume
                            self.game_state = GameState.PLAYING
                        elif self.pause_selected == 1:  # Restart
                            self.start_game()
                        elif self.pause_selected == 2:  # Menu
                            self.game_state = GameState.MENU
                
                elif self.game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.game_state = GameState.MENU
                
                elif self.game_state == GameState.GARAGE:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.MENU
    
    def start_game(self):
        """Start a new game"""
        self.game_state = GameState.PLAYING
        self.terrain = Terrain(seed=self.level)
        self.car = Car(100, 300, self.car_stats)
        self.particles = []
        self.camera_x = 0
        self.distance_checkpoint = 0
        self.menu_selected = 0
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
            
            # Level progression
            if self.car.distance_traveled > self.distance_checkpoint + 2000:
                self.level += 1
                self.distance_checkpoint = self.car.distance_traveled
                self.coins += 100 * self.level
            
            # Game over condition
            if self.car.health <= 0 or self.car.fuel <= 0:
                self.game_state = GameState.GAME_OVER
    
    def draw(self):
        """Draw game"""
        self.screen.fill(Color.LIGHT_BLUE.value)
        
        if self.game_state == GameState.MENU:
            self.gui.draw_menu(self.screen, self.menu_selected)
        
        elif self.game_state == GameState.PLAYING:
            # Draw terrain
            points = self.terrain.points
            screen_points = [(p[0] - self.camera_x, p[1]) for p in points]
            
            if len(screen_points) > 1:
                pygame.draw.lines(self.screen, Color.GREEN.value, screen_points, 5)
            
            # Draw car
            self.car.draw(self.screen, self.camera_x)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen, self.camera_x)
            
            # Draw HUD
            self.gui.draw_hud(self.screen, self.car, self.level)
        
        elif self.game_state == GameState.PAUSED:
            # Draw game behind
            points = self.terrain.points
            screen_points = [(p[0] - self.camera_x, p[1]) for p in points]
            if len(screen_points) > 1:
                pygame.draw.lines(self.screen, Color.GREEN.value, screen_points, 5)
            self.car.draw(self.screen, self.camera_x)
            
            # Draw pause menu
            self.gui.draw_pause_menu(self.screen, self.pause_selected)
        
        elif self.game_state == GameState.GAME_OVER:
            self.gui.draw_game_over(self.screen, self.car.distance_traveled, self.level)
        
        elif self.game_state == GameState.GARAGE:
            self.gui.draw_garage(self.screen, self.car_stats, self.coins)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

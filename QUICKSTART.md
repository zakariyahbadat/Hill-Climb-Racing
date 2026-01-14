# 🚀 Quick Start Guide

## 30-Second Setup

### 1. Install Python
Download from [python.org](https://www.python.org/) (version 3.8+)

### 2. Install Dependencies
Open Command Prompt/Terminal and run:
```bash
pip install -r requirements.txt
```

### 3. Launch the Game
Option A (Recommended):
```bash
python launcher.py
```

Option B (Direct):
```bash
python advanced_game.py
```

## 🎮 First Time Playing

1. **Start the game** - Select "Play Game" from the menu
2. **Choose a level** - Start with "Mountain Valley" (Easy)
3. **Learn the controls**:
   - Press **UP** to accelerate
   - Press **LEFT/RIGHT** to steer
   - Press **DOWN** to brake
   - Press **ESC** to pause

4. **Complete the level** - Reach the end without your health dropping to 0

5. **Earn coins** - Use coins to upgrade your car in the Garage

6. **Progress** - Unlock harder levels and challenge yourself!

## 💡 Pro Tips

### Early Game (Level 1-2)
- Focus on learning the terrain
- Don't drive too fast
- Collect coins for upgrades
- Upgrade acceleration first

### Mid Game (Level 3-4)
- Balance speed with control
- Learn to manage fuel
- Upgrade traction for better handling
- Save coins for expensive upgrades

### Late Game (Level 5)
- Master the physics
- Optimize upgrade distribution
- Achieve high speeds safely
- Unlock all achievements

## 🎯 Upgrade Strategy

**Best Progression Order:**
1. **Acceleration** (+15%) - 500 coins
2. **Traction** (+18%) - 400 coins  
3. **Fuel Efficiency** (+22%) - 600 coins
4. **Suspension** (+25%) - 700 coins
5. **Top Speed** (+20%) - 800 coins

## 🏆 Achievement Tips

- **Speed Demon**: Reach 50+ speed in a level
- **Distance Explorer**: Reach specific distance milestones
- **Coin Master**: Collect all coins in a level
- **Flipped Master**: Land a flip successfully
- **Eco Driver**: Complete level with fuel efficiency upgrade

## ⚙️ Graphics Settings

Edit `game_config.py` to customize:

```python
# Change screen resolution
"resolution": (1920, 1080)  # Change to your preference

# Adjust FPS
"fps": 60  # Higher = smoother but needs more power

# Particle quality
"particle_quality": "high"  # high, medium, low
```

## 🔧 Controls Customization

Edit the keyboard checks in `advanced_game.py`:

Current controls:
- Arrows or WASD for movement
- ENTER to select menus
- ESC to pause/back

## 📱 Game States

The game has multiple screens:

1. **Main Menu** - Start game, access features
2. **Level Select** - Choose difficulty level
3. **Game Playing** - Actual gameplay
4. **Pause Menu** - Pause options
5. **Game Over** - Results screen
6. **Garage** - View upgrades
7. **Shop** - Purchase upgrades with coins
8. **Achievements** - View unlocked achievements

## 🎨 Customizing the Game

### Change Car Colors
In `game_config.py`, modify:
```python
CAR_COLORS = [
    (220, 53, 69),    # Red
    (0, 102, 204),    # Blue
    # Add your RGB colors here
]
```

### Adjust Physics
In `advanced_game.py`, change constants:
```python
GRAVITY = 0.6          # How fast cars fall
FRICTION = 0.98        # Ground friction
AIR_RESISTANCE = 0.99  # Air drag
```

### Modify Level Difficulty
In `game_config.py`:
```python
LEVELS = [
    {
        "name": "Your Level",
        "difficulty": "Hard",
        "seed": 42,
        "target_distance": 10000
    }
]
```

## 🐛 Common Issues

**Game crashes on startup**
- Reinstall pygame: `pip install pygame --upgrade`
- Check Python version: `python --version`

**Game runs slowly**
- Close other programs
- Reduce window resolution in `game_config.py`
- Change particle quality to "low"

**Can't collect coins**
- Move closer to coins (within 50 pixels)
- Make sure you're not going too fast
- Complete the level for coins to count

**Game won't save progress**
- Check folder permissions
- Delete `game_save.json` to reset
- Ensure write access to directory

## 📚 Learning Resources

This game demonstrates:
- **Physics Simulation** - Realistic car movement
- **Terrain Generation** - Procedural level creation
- **Game State Management** - Menu/gameplay transitions
- **Save Systems** - Data persistence
- **Particle Effects** - Visual enhancements
- **UI Design** - Professional menus and HUD

## 🎓 Code Structure

```
advanced_game.py
├── Color (Enum) - Color definitions
├── GameState (Enum) - Game modes
├── CarStats (Dataclass) - Car upgrades
├── Terrain - Level generation
├── Car - Player vehicle
├── Wheel - Car wheel physics
├── ParticleEffect - Visual effects
├── Button - UI buttons
├── GUI - All menus and HUD
├── SaveManager - Game saves
└── Game - Main game class
```

## 🎮 Have Fun!

The game is designed to be challenging but fair. Practice makes perfect! Unlock all achievements and reach the highest levels.

Good luck and happy racing! 🏁

---

**Questions?** Check the comments in the code or review `game_config.py` for available settings.

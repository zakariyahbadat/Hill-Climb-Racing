# 🏎️ Hill Climb Racing - Advanced Edition

An extremely advanced, feature-rich car racing game similar to Hill Climb Racing with stunning graphics, physics engine, and a comprehensive progression system.

## 🌟 Features

### Gameplay
- **Realistic Physics Engine**: Advanced gravity, friction, air resistance, and terrain interaction
- **Dynamic Car Control**: Smooth steering, acceleration, and braking mechanics
- **Terrain Generation**: Procedurally generated levels with obstacles and hazards
- **Progressive Difficulty**: Multiple levels with increasing difficulty (Easy to Extreme)
- **Fuel System**: Manage fuel consumption based on driving style
- **Health System**: Take damage from crashes and flips
- **Coin Collection**: Collect coins during gameplay to earn rewards

### Progression System
- **Level Select**: 5 unique levels with different difficulty levels
- **Garage/Upgrades**: Upgrade your car's stats:
  - Acceleration
  - Top Speed
  - Traction/Grip
  - Fuel Efficiency
  - Suspension
- **Shop System**: Purchase upgrades with earned coins
- **Achievement System**: Unlock achievements and earn bonus coins
- **Save System**: Your progress is automatically saved

### User Interface
- **Advanced GUI**: Professional menu system with smooth navigation
- **In-Game HUD**: Real-time display of:
  - Speed
  - Fuel level
  - Health bar
  - Distance traveled
  - Coins collected
- **Pause Menu**: Pause, restart, or return to main menu
- **Game Over Screen**: See statistics and earned coins

### Visual Effects
- **Particle System**: Dust and effect particles
- **Animated Graphics**: Smooth car rotation and terrain rendering
- **Dynamic Camera**: Follows the car smoothly
- **Color Customization**: Random car colors for variety
- **Sky Gradient**: Smooth background transitions

## 🎮 Controls

### Gameplay
- **UP Arrow / W**: Accelerate
- **DOWN Arrow / S**: Brake
- **LEFT Arrow / A**: Turn Left
- **RIGHT Arrow / D**: Turn Right
- **ESC**: Pause Game

### Menu Navigation
- **UP Arrow / W**: Navigate Up
- **DOWN Arrow / S**: Navigate Down
- **ENTER**: Select Option
- **ESC**: Back to Menu
- **SPACE**: Continue (on Game Over screen)

## 📋 System Requirements

- Python 3.8+
- Pygame 2.5.2+
- 1.4GB resolution monitor (recommended 1920x1080)
- Minimum 50MB disk space

## 🚀 Installation & Setup

### Step 1: Install Python
Make sure you have Python 3.8 or newer installed from [python.org](https://www.python.org/)

### Step 2: Clone/Extract the Game
Navigate to the game directory in your terminal/command prompt

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Game

**Option 1: Use the Launcher (Recommended)**
```bash
python launcher.py
```

**Option 2: Run Directly**
```bash
python advanced_game.py
```

Or use the basic version:
```bash
python hill_climb_game.py
```

## 📂 File Structure

```
Dice-Game-/
├── advanced_game.py          # Main game (recommended)
├── hill_climb_game.py        # Basic version
├── game_config.py            # Configuration & constants
├── launcher.py               # Game launcher
├── requirements.txt          # Python dependencies
├── game_save.json           # Auto-saved progress (generated)
└── README.md                # This file
```

## 🎯 Game Modes

### Level Select
Choose from 5 unique levels:
1. **Mountain Valley** (Easy) - Learn the basics
2. **Rocky Hills** (Medium) - More obstacles
3. **Desert Dunes** (Hard) - Extreme terrain
4. **Alpine Peak** (Very Hard) - Dangerous slopes
5. **Volcanic Crater** (Extreme) - Ultimate challenge

### Garage
Upgrade your car's performance:
- Each upgrade increases effectiveness up to 3.0x
- Upgrades are permanent and carry over between levels
- Invest coins strategically

### Shop
Purchase performance upgrades:
- **Engine Upgrade**: 500 coins
- **Turbo Kit**: 800 coins
- **Racing Tires**: 400 coins
- **Fuel Tank**: 600 coins
- **Suspension**: 700 coins

### Achievements
Unlock special achievements by:
- Completing first run
- Achieving high speeds
- Traveling long distances
- Collecting coins efficiently
- Perfect flips

## 💡 Tips & Tricks

1. **Fuel Management**: Don't drive with the engine at full power all the time. Balance acceleration and efficiency.

2. **Terrain Navigation**: Learn the terrain patterns. Anticipate hills and prepare for sudden drops.

3. **Coin Collection**: Coins are worth more than distance in terms of progression. Prioritize collecting them.

4. **Upgrades Strategy**:
   - Early game: Focus on acceleration and traction
   - Mid game: Balance all stats
   - Late game: Maximize speed and suspension

5. **Flipping**: If you flip, try to land upright quickly. Flips cause damage!

6. **Speed Control**: Too much speed can cause you to flip. Use braking on steep downhills.

## 🛠️ Troubleshooting

### Game Won't Start
- Ensure pygame is installed: `pip install pygame`
- Check Python version: `python --version` (should be 3.8+)

### Low FPS
- Disable other background applications
- Reduce graphics settings if available
- Check CPU usage

### Controls Not Working
- Make sure the game window is focused (clicked)
- Try different control schemes in settings

### Save File Issues
- Delete `game_save.json` to reset progress
- Ensure the directory has write permissions

## 📝 Version History

### v2.0 - Advanced Edition
- Added shop system
- Multiple difficulty levels
- Save system
- Achievements
- Enhanced graphics
- Particle effects

### v1.0 - Basic Edition
- Core physics engine
- Basic terrain generation
- Simple UI
- Single level gameplay

## 🎓 Learning Resources

This game is built with educational value:
- **Physics Programming**: Real-world physics simulation
- **Game Development**: Game loops, state management
- **UI Design**: Menu systems and HUD design
- **Object-Oriented Programming**: Class-based game architecture

## 📧 Support

For issues or suggestions, check the code comments or review `game_config.py` for customization options.

## 🎨 Customization

Edit `game_config.py` to customize:
- Car colors
- Game difficulty
- Level parameters
- Physics constants
- Sound settings
- Graphics quality

## ⚖️ License

This project is created for educational purposes.

---

**Happy Racing! 🏁**

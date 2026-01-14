"""
Game Launcher - Starts Hill Climb Racing Advanced Edition
"""

import subprocess
import sys
import os
import platform

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import pygame
        print("✓ Pygame is installed")
        return True
    except ImportError:
        print("✗ Pygame is not installed")
        print("\nInstalling Pygame...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame==2.5.2"])
            print("✓ Pygame installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install Pygame")
            print("Please run: pip install pygame")
            return False

def start_game(version="advanced"):
    """Start the game"""
    if version == "advanced":
        game_file = "advanced_game.py"
        game_name = "Hill Climb Racing - Advanced Edition"
    else:
        game_file = "hill_climb_game.py"
        game_name = "Hill Climb Racing - Basic Edition"
    
    print(f"\n🎮 Starting {game_name}...")
    print("=" * 50)
    
    try:
        if platform.system() == "Windows":
            subprocess.Popen([sys.executable, game_file])
        else:
            subprocess.Popen([sys.executable, game_file])
        
        print(f"✓ {game_name} is running!")
        print("Close the game window to exit.")
        
    except FileNotFoundError:
        print(f"✗ Error: {game_file} not found!")
        print("Make sure you're in the game directory.")
    except Exception as e:
        print(f"✗ Error starting game: {e}")

def show_menu():
    """Show main menu"""
    print("\n" + "=" * 50)
    print("🏎️  HILL CLIMB RACING - LAUNCHER")
    print("=" * 50)
    print("\n1. Play Advanced Edition (Recommended)")
    print("2. Play Basic Edition")
    print("3. Install Dependencies")
    print("4. Exit")
    print("\n" + "=" * 50)

def main():
    """Main launcher function"""
    print("\n🏎️  Hill Climb Racing Game Launcher")
    print("=" * 50)
    
    # Check dependencies on startup
    print("\nChecking dependencies...")
    if not check_dependencies():
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting launcher.")
            return
    
    while True:
        show_menu()
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            print("\nLaunching Advanced Edition...")
            start_game("advanced")
            break
        elif choice == "2":
            print("\nLaunching Basic Edition...")
            start_game("basic")
            break
        elif choice == "3":
            print("\nInstalling dependencies...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                print("✓ Dependencies installed successfully!")
            except subprocess.CalledProcessError:
                print("✗ Failed to install dependencies")
        elif choice == "4":
            print("\n👋 Thanks for playing!")
            break
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Launcher closed.")
    except Exception as e:
        print(f"\n✗ Error: {e}")

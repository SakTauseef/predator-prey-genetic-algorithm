"""
main.py — Entry point for the Predator-Prey Simulation.
Run this file to start the simulation.
"""

import pygame
import sys
from simulation import Simulation
from config import Config

def main():
    print("\n" + "="*60)
    print("     PREDATOR-PREY SIMULATION SETUP")
    print("="*60)
    
    # Show current defaults
    print(f"\n📐 Current defaults:")
    print(f"   Arena: {Config.SIM_WIDTH} x {Config.SIM_HEIGHT}")
    print(f"   Predators: {Config.INITIAL_PREDATORS}")
    print(f"   Prey: {Config.INITIAL_PREY}")
    print(f"   Max Generations: {Config.MAX_GENERATIONS}")
    
    print("\n" + "-"*60)
    print("Press Enter to use defaults, or type new values:")
    print("-"*60)
    
    # 1. Arena Width
    while True:
        try:
            width_input = input(f"   Arena width [{Config.SIM_WIDTH}]: ")
            if width_input.strip():
                Config.SIM_WIDTH = int(width_input)
            break
        except ValueError:
            print("   Invalid! Please enter a number.")
    
    # 2. Arena Height
    while True:
        try:
            height_input = input(f"   Arena height [{Config.SIM_HEIGHT}]: ")
            if height_input.strip():
                Config.SIM_HEIGHT = int(height_input)
            break
        except ValueError:
            print("   Invalid! Please enter a number.")
    
    # Update window dimensions
    Config.WINDOW_WIDTH = Config.SIM_WIDTH + Config.GRAPH_WIDTH
    Config.WINDOW_HEIGHT = Config.SIM_HEIGHT
    
    # 3. Predators
    while True:
        try:
            pred_input = input(f"   Number of PREDATORS [{Config.INITIAL_PREDATORS}]: ")
            if pred_input.strip():
                Config.INITIAL_PREDATORS = int(pred_input)
            break
        except ValueError:
            print("   Invalid! Please enter a number.")
    
    # 4. Prey
    while True:
        try:
            prey_input = input(f"   Number of PREY [{Config.INITIAL_PREY}]: ")
            if prey_input.strip():
                Config.INITIAL_PREY = int(prey_input)
            break
        except ValueError:
            print("   Invalid! Please enter a number.")
    
    # 5. Max Generations
    while True:
        try:
            gen_input = input(f"   Max Generations [{Config.MAX_GENERATIONS}]: ")
            if gen_input.strip():
                Config.MAX_GENERATIONS = int(gen_input)
            break
        except ValueError:
            print("   Invalid! Please enter a number.")
    
    # Summary
    print("\n" + "="*60)
    print("✅ SIMULATION CONFIGURED")
    print("="*60)
    print(f"   Arena:        {Config.SIM_WIDTH} x {Config.SIM_HEIGHT}")
    print(f"   Predators:    {Config.INITIAL_PREDATORS}")
    print(f"   Prey:         {Config.INITIAL_PREY}")
    print(f"   Max Gens:     {Config.MAX_GENERATIONS}")
    print(f"   Window:       {Config.WINDOW_WIDTH} x {Config.WINDOW_HEIGHT}")
    print("="*60)
    print("\n🎮 Controls: [SPACE] Pause  [R] Reset  [ESC] Quit")
    print("⚠️  Click on the Pygame window to activate keyboard controls!\n")
    
    input("Press Enter to start simulation...")

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
    pygame.display.set_caption("Predator-Prey Evolutionary Simulation")

    clock = pygame.time.Clock()
    sim = Simulation(screen)

    print("\n✅ Simulation Running!")
    print("👉 CLICK on the game window to activate keyboard controls! 👈\n")

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sim.show_final_screen()
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC pressed - Quitting...")
                    sim.show_final_screen()
                    running = False
                
                if event.key == pygame.K_SPACE:
                    sim.toggle_pause()
                    status = "PAUSED" if sim.paused else "RUNNING"
                    print(f"⏸️  Simulation {status}")
                
                if event.key == pygame.K_r:
                    sim.reset()
                    print("🔄 Simulation Reset")
                
                # Debug: print any key press
                print(f"Key pressed: {pygame.key.name(event.key)}")

        # Update
        if not sim.paused:
            sim.update()

        # Draw
        sim.draw()
        pygame.display.flip()
        clock.tick(Config.FPS)

        # Stop condition
        if sim.generation >= Config.MAX_GENERATIONS:
            sim.show_final_screen()
            pygame.time.wait(5000)
            running = False

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
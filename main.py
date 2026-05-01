import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from World import World
from Agent import Agent

class SimulationGUI:
    def __init__(self, width=50, height=50):
        self.world = World(width, height)
        self.fig = None
        self.ax1 = None
        self.ax2 = None
        self.ani = None
        
    def initialize_population(self, num_predators=5, num_prey=20):
        """Initialize starting population"""
        for _ in range(num_predators):
            x = np.random.randint(0, self.world.width)
            y = np.random.randint(0, self.world.height)
            agent = Agent(x, y, 'predator')
            self.world.agents.append(agent)
        
        for _ in range(num_prey):
            x = np.random.randint(0, self.world.width)
            y = np.random.randint(0, self.world.height)
            agent = Agent(x, y, 'prey')
            self.world.agents.append(agent)
    
    def animate(self, frame):
        """Animation function for real-time visualization"""
        self.world.tick()
        
        self.ax1.clear()
        self.ax2.clear()
        
        # ===== MAIN GRID VISUALIZATION =====
        self.ax1.set_xlim(-1, self.world.width)
        self.ax1.set_ylim(-1, self.world.height)
        self.ax1.set_title(f'Predator-Prey Simulation\n'
                          f'Tick: {self.world.tick_count} | '
                          f'Generation: {self.world.generation}',
                          fontsize=12, fontweight='bold')
        self.ax1.set_xlabel('X Position', fontsize=10)
        self.ax1.set_ylabel('Y Position', fontsize=10)
        
        # Draw grid lines (lighter for cleaner look)
        self.ax1.set_xticks(range(0, self.world.width, 10))
        self.ax1.set_yticks(range(0, self.world.height, 10))
        self.ax1.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        
        # Draw sanctuary zones (lighter green)
        for sx, sy, sw, sh in self.world.sanctuaries:
            rect = plt.Rectangle((sx, sy), sw, sh, 
                                facecolor='#90EE90', alpha=0.15, 
                                edgecolor='#228B22', linewidth=1.5, linestyle='--')
            self.ax1.add_patch(rect)
        
        # Collect agent positions
        predators_x, predators_y = [], []
        prey_x, prey_y = [], []
        
        for agent in self.world.agents:
            if agent.species == 'predator':
                predators_x.append(agent.x)
                predators_y.append(agent.y)
            else:
                prey_x.append(agent.x)
                prey_y.append(agent.y)
        
        # Draw predators - Red triangles with gradient effect
        if predators_x:
            self.ax1.scatter(predators_x, predators_y, 
                            c='#E74C3C', marker='^', s=80,
                            edgecolors='#C0392B', linewidth=1.5,
                            label=f'Predators ({len(predators_x)})', 
                            alpha=0.9, zorder=3)
        
        # Draw prey - Green circles
        if prey_x:
            self.ax1.scatter(prey_x, prey_y, 
                            c='#2ECC71', marker='o', s=60,
                            edgecolors='#27AE60', linewidth=1.5,
                            label=f'Prey ({len(prey_x)})', 
                            alpha=0.9, zorder=3)
        
        # Draw food - Orange squares
        if self.world.food_patches:
            food_x = [f[0] for f in self.world.food_patches]
            food_y = [f[1] for f in self.world.food_patches]
            self.ax1.scatter(food_x, food_y, 
                            c='#F39C12', marker='s', s=40,
                            edgecolors='#E67E22', linewidth=1,
                            label=f'Food ({len(food_x)})', 
                            alpha=0.8, zorder=2)
        
        # Draw water - Blue diamonds
        if self.world.water_sources:
            water_x = [w[0] for w in self.world.water_sources]
            water_y = [w[1] for w in self.world.water_sources]
            self.ax1.scatter(water_x, water_y, 
                            c='#3498DB', marker='D', s=50,
                            edgecolors='#2980B9', linewidth=1,
                            label=f'Water ({len(water_x)})', 
                            alpha=0.8, zorder=2)
        

        self.ax1.legend(loc='upper right', bbox_to_anchor=(1, 1))
        
        # Stats box - cleaner design
        stats = self.world.get_stats()
        text_str = (f"📊 STATISTICS\n"
                   f"━━━━━━━━━━━━━━━\n"
                   f"🦁 Predators: {stats['predators']}\n"
                   f"🐐 Prey: {stats['prey']}\n"
                   f"📈 Total: {stats['total']}\n"
                   f"🍎 Food: {stats['food']}\n"
                   f"💧 Water: {stats['water']}\n"
                   f"📦 Capacity: {self.world.carrying_capacity}")
        
        self.ax1.text(0.02, 0.98, text_str, transform=self.ax1.transAxes,
                     fontsize=9, verticalalignment='top',
                     fontfamily='monospace',
                     bbox=dict(boxstyle='round,pad=0.5', 
                              facecolor='white', 
                              edgecolor='#CCCCCC',
                              alpha=0.95))
        
        # ===== STATISTICS GRAPH =====
        # Plot population history
        pred_history = self.world.population_history['predator']
        prey_history = self.world.population_history['prey']
        
        if len(pred_history) > 0:
            x_range = range(len(pred_history))
            self.ax2.plot(x_range, pred_history, 'r-', 
                         label='Predators', linewidth=2, alpha=0.8)
            self.ax2.plot(x_range, prey_history, 'g-', 
                         label='Prey', linewidth=2, alpha=0.8)
            
            # Add fitness trend if available
            if len(self.world.fitness_history) > 0:
                # Normalize fitness for display
                fitness_norm = np.array(self.world.fitness_history)
                if len(fitness_norm) > 1 and fitness_norm.max() > fitness_norm.min():
                    max_pop = max(pred_history[-1] if pred_history else 10, 10)
                    fitness_norm = (fitness_norm - fitness_norm.min()) / (fitness_norm.max() - fitness_norm.min()) * max_pop
                    fitness_x = np.linspace(0, len(pred_history)-1, len(fitness_norm))
                    self.ax2.plot(fitness_x, fitness_norm, 
                                'b--', label='Avg Fitness (norm)', 
                                linewidth=2, alpha=0.7)
        
        self.ax2.set_xlabel('Ticks', fontsize=10)
        self.ax2.set_ylabel('Population', fontsize=10)
        self.ax2.set_title('Population Dynamics', fontsize=12, fontweight='bold')
        self.ax2.legend(loc='upper left', fontsize=9, framealpha=0.9)
        self.ax2.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
        self.ax2.set_facecolor('#F8F9FA')
    
    def run(self, frames=2000, interval=100):
        """Run the simulation with GUI"""
 
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(14, 7)) 
        # Create animation
        self.ani = animation.FuncAnimation(
            self.fig, self.animate, frames=frames, 
            interval=interval, repeat=True, cache_frame_data=False
        )
        
        # Display GUI
        plt.tight_layout()
        plt.show()
        
        # Print final statistics
        self.print_final_stats()
    
    def print_final_stats(self):
        """Print final simulation statistics"""
        print("\n" + "="*50)
        print("SIMULATION COMPLETE - FINAL STATISTICS")
        print("="*50)
        print(f"Total Generations: {self.world.generation}")
        print(f"Final Population: {len(self.world.agents)}")
        print(f"  - Predators: {sum(1 for a in self.world.agents if a.species == 'predator')}")
        print(f"  - Prey: {sum(1 for a in self.world.agents if a.species == 'prey')}")
        
        if self.world.fitness_history:
            print(f"\nAverage Fitness (last 10 generations):")
            last_10 = self.world.fitness_history[-10:]
            print(f"  - Mean: {np.mean(last_10):.2f}")
            print(f"  - Max: {np.max(last_10):.2f}")
            print(f"  - Min: {np.min(last_10):.2f}")
        
        print("\n" + "="*50)

# ============ MAIN EXECUTION ============
if __name__ == "__main__":
    # Create simulation with different grid sizes
    print("Choose grid size:")
    print("1. Small (30x30)")
    print("2. Medium (50x50) - Default")
    print("3. Large (80x80)")
    print("4. Custom")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        width, height = 30, 30
    elif choice == '2':
        width, height = 50, 50
    elif choice == '3':
        width, height = 80, 80
    elif choice == '4':
        width = int(input("Enter width: "))
        height = int(input("Enter height: "))
    else:
        width, height = 50, 50
    
    # Create and run simulation
    sim = SimulationGUI(width, height)
    
    # Ask for initial population
    print(f"\nInitializing {width}x{height} grid...")
    
    # ===== REPLACE FROM HERE =====
    # Keep asking until valid number entered
    while True:
        try:
            num_pred = int(input("Number of predators: "))
            if num_pred >= 0:
                break
            else:
                print("Please enter a positive number!")
        except ValueError:
            print("Please enter a valid number!")
    
    while True:
        try:
            num_prey = int(input("Number of prey: "))
            if num_prey >= 0:
                break
            else:
                print("Please enter a positive number!")
        except ValueError:
            print("Please enter a valid number!")
    # ===== REPLACE TO HERE =====
    
    sim.initialize_population(num_pred, num_prey)
    
    print("\nStarting simulation...")
    print("Close the window to stop simulation")
    
    # Run for 2000 frames (can be changed)
    sim.run(frames=2000, interval=100)

import random
import numpy as np
from Agent import Agent

class World:
    def __init__(self, width=50, height=50):
        # Grid parameters
        self.width = width
        self.height = height
        
        # Agents and resources
        self.agents = []
        self.food_patches = []
        self.water_sources = []
        
        # Sanctuary zones (predators can't enter)
        self.sanctuaries = self._create_sanctuaries()
        
        # CSP parameters
        self.carrying_capacity = int(width * height * 0.3)  # 30% of grid
        
        # Evolution tracking
        self.generation = 0
        self.tick_count = 0
        self.generation_ticks = 100  
        
        # Data collection
        self.population_history = {'predator': [], 'prey': []}
        self.fitness_history = []
        self.survival_stats = []
        
        # Regeneration rates
        self.food_regeneration_rate = 0.02  # 2% per tick
        self.water_regeneration_rate = 0.01
        
        # Initialize resources
        self._init_resources()
    
    def _create_sanctuaries(self):
        """Create predator sanctuary zones (prey-only areas)"""
        sanctuaries = []
        num_sanctuaries = max(1, (self.width * self.height) // 1000)
        
        for _ in range(num_sanctuaries):
            sx = random.randint(0, self.width - 10)
            sy = random.randint(0, self.height - 10)
            sanctuaries.append((sx, sy, 5, 5))  # x, y, width, height
        
        return sanctuaries
    
    def _init_resources(self):
        """Initialize food and water patches"""
        total_cells = self.width * self.height
        num_food = int(total_cells * 0.05)  # 5% food coverage
        num_water = int(total_cells * 0.02)  # 2% water coverage
        
        for _ in range(num_food):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.food_patches.append([x, y, 100])  # [x, y, energy_value]
        
        for _ in range(num_water):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.water_sources.append([x, y, 50])  # [x, y, energy_value]
    
    def regenerate_resources(self):
        """Regenerate food and water each tick"""
        # Regenerate existing food
        for patch in self.food_patches:
            patch[2] = min(100, patch[2] + 1)  # Regrow slowly
        
        # Add new food patches randomly
        if random.random() < self.food_regeneration_rate:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.food_patches.append([x, y, 50])
        
        # Add new water sources
        if random.random() < self.water_regeneration_rate:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.water_sources.append([x, y, 30])
    
    def is_sanctuary(self, x, y):
        """Check if position is in a sanctuary zone"""
        for sx, sy, sw, sh in self.sanctuaries:
            if sx <= x < sx + sw and sy <= y < sy + sh:
                return True
        return False
    
    def is_valid_move(self, agent, new_x, new_y):
        """CSP: Check if move is valid"""
        # Energy check
        if agent.energy <= 0:
            return False
        
        # Predator can't enter sanctuary
        if agent.species == 'predator' and self.is_sanctuary(new_x, new_y):
            return False
        
        return True
    
    def can_breed_csp(self, agent):
        """CSP: Check breeding conditions"""
        # Energy threshold
        if not agent.can_breed():
            return False
        
        # Population density check
        total_population = len(self.agents)
        if total_population >= self.carrying_capacity:
            return False
        
        return True
    
    def breed_agents(self):
        """Handle breeding with CSP constraints"""
        new_agents = []
        
        for agent in self.agents:
            if self.can_breed_csp(agent):
                # Find mate (nearby same species)
                mate = self._find_mate(agent)
                if mate:
                    offspring = self._create_offspring(agent, mate)
                    new_agents.append(offspring)
                    agent.energy -= 30
                    mate.energy -= 30
                    agent.offspring_count += 1
                    mate.offspring_count += 1
        
        self.agents.extend(new_agents)
    
    def _find_mate(self, agent):
        """Find nearby mate of same species"""
        for other in self.agents:
            if other != agent and other.species == agent.species:
                # Check distance
                dist = abs(other.x - agent.x) + abs(other.y - agent.y)
                if dist <= 5:  # Within 5 cells
                    return other
        return None
    
    def _create_offspring(self, parent1, parent2):
        """Single-point crossover + mutation (5%)"""
        # Single-point crossover
        crossover_point = random.randint(1, 7)
        genome = parent1.genome[:crossover_point] + parent2.genome[crossover_point:]
        
        # 5% bit-flip mutation
        genome_list = list(genome)
        for i in range(len(genome_list)):
            if random.random() < 0.05:
                genome_list[i] = '1' if genome_list[i] == '0' else '0'
        
        genome = ''.join(genome_list)
        
        # Find position near parents
        x = (parent1.x + parent2.x) // 2
        y = (parent1.y + parent2.y) // 2
        x = (x + random.randint(-2, 2)) % self.width
        y = (y + random.randint(-2, 2)) % self.height
        
        offspring = Agent(x, y, parent1.species, genome, 
                         generation=max(parent1.generation, parent2.generation) + 1)
        offspring.energy = 50  # Start with half energy
        
        return offspring
    
    def tournament_selection(self, fitnesses):
        """Tournament selection (top 20%) for survival"""
        # Sort agents by fitness
        sorted_agents = sorted(zip(self.agents, fitnesses), 
                              key=lambda x: x[1], reverse=True)
        
        # Keep top 20%
        keep_count = max(1, int(len(self.agents) * 0.2))
        survivors = [agent for agent, _ in sorted_agents[:keep_count]]
        
        # Add random chance for middle 30% (diversity)
        middle_start = keep_count
        middle_end = int(len(self.agents) * 0.5)
        for agent, _ in sorted_agents[middle_start:middle_end]:
            if random.random() < 0.3:
                survivors.append(agent)
        
        return survivors
    
    def apply_evolution(self):
        """Evolutionary computation loop"""
        # Calculate fitness for all agents
        fitnesses = [agent.calculate_fitness() for agent in self.agents]
        
        # Record fitness history
        avg_fitness = np.mean(fitnesses) if fitnesses else 0
        self.fitness_history.append(avg_fitness)
        
        # Tournament selection
        survivors = self.tournament_selection(fitnesses)
        
        # Record survival stats
        self.survival_stats.append({
            'generation': self.generation,
            'survival_rate': len(survivors) / len(self.agents) if self.agents else 0,
            'avg_fitness': avg_fitness
        })
        
        # Replace population with survivors
        self.agents = survivors
        self.generation += 1
        
        # Reset ages and survival times for new generation
        for agent in self.agents:
            agent.survival_time = 0
    
    def tick(self):
        """Main simulation tick manager"""
        # Update each agent
        for agent in self.agents[:]:  # Use slice copy for safe removal
            # Update agent state
            agent.update()
            
            # Starvation check
            if not agent.is_alive():
                self.agents.remove(agent)
                continue
            
            
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            new_x = (agent.x + dx) % self.width
            new_y = (agent.y + dy) % self.height
            
            # CSP: Validate move
            if self.is_valid_move(agent, new_x, new_y):
                agent.x = new_x
                agent.y = new_y

	            # ===== PREY EATS FOOD =====
        if agent.species == 'prey':
            for food in self.food_patches[:]:
                if abs(agent.x - food[0]) <= 1 and abs(agent.y - food[1]) <= 1:
                    agent.energy = min(200, agent.energy + food[2])
                    self.food_patches.remove(food)
                    break
        
        # ===== PREY DRINKS WATER =====
        if agent.species == 'prey':
            for water in self.water_sources[:]:
                if abs(agent.x - water[0]) <= 1 and abs(agent.y - water[1]) <= 1:
                    agent.energy = min(200, agent.energy + water[2])
                    self.water_sources.remove(water)
                    break
        
        # ===== PREDATOR EATS PREY =====
        if agent.species == 'predator':
            for other in self.agents[:]:
                if other.species == 'prey':
                    if abs(agent.x - other.x) <= 1 and abs(agent.y - other.y) <= 1:
                        agent.energy = min(200, agent.energy + 60)
                        self.agents.remove(other)
                        break
            
        
        # Regenerate resources
        self.regenerate_resources()
        
        # Handle breeding
        self.breed_agents()
        
        # Update tick counter
        self.tick_count += 1
        
        # Check if generation ended
        if self.tick_count >= self.generation_ticks:
            self.tick_count = 0
            self.apply_evolution()
        
        # Record population data
        self.population_history['predator'].append(
            sum(1 for a in self.agents if a.species == 'predator'))
        self.population_history['prey'].append(
            sum(1 for a in self.agents if a.species == 'prey'))
    
    def get_stats(self):
        """Get current simulation statistics"""
        return {
            'tick': self.tick_count,
            'generation': self.generation,
            'predators': sum(1 for a in self.agents if a.species == 'predator'),
            'prey': sum(1 for a in self.agents if a.species == 'prey'),
            'total': len(self.agents),
            'food': len(self.food_patches),
            'water': len(self.water_sources)
        }
import random

class Agent:
    def __init__(self, x, y, species, genome=None, generation=0):
        self.x = x
        self.y = y
        self.species = species  # 'predator' or 'prey'
        self.age = 0
        self.energy = 200
        self.generation = generation
        self.offspring_count = 0
        self.survival_time = 0
        
        # Genome (8-bit string → behavioral traits)
        if genome is None:
            self.genome = self._random_genome()
        else:
            self.genome = genome
        
        # Decode genome into traits
        self._decode_genome()
    
    def _random_genome(self):
        """Generate random 8-bit genome"""
        return ''.join(str(random.randint(0, 1)) for _ in range(8))
    
    def _decode_genome(self):
        """Decode 8-bit genome to behavioral traits"""
        bits = self.genome
        self.speed = int(bits[0:2], 2) + 1  # 1-4 (movement speed/cost)
        self.aggression = int(bits[2:4], 2)  # 0-3 (hunting tendency)
        self.efficiency = int(bits[4:6], 2) + 1  # 1-4 (energy efficiency)
        self.breeding_threshold = 50 + (int(bits[6:8], 2) * 10)  # 50-80
    
    def calculate_fitness(self):
        """Fitness = survival time + offspring + energy efficiency"""
        fitness = self.survival_time + (self.offspring_count * 50) + self.energy
        return fitness
    
    def update(self):
        """Update agent state each tick"""
        self.age += 1
        self.survival_time += 1
        
        # Energy cost based on speed (faster = more energy cost)
        energy_cost = max(1,self.speed//2)
        self.energy -= energy_cost
    
    def can_breed(self):
        """Check if agent can breed (CSP condition)"""
        return self.energy >= self.breeding_threshold and self.age >= 10
    
    def is_alive(self):
        return self.energy > 0 and self.age < 700  # Max age 700 ticks
    
    def __repr__(self):
        return f"{self.species}({self.x},{self.y}) E:{self.energy:.0f}"
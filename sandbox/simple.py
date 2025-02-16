import numpy as np
from scipy.constants import mu_0
import matplotlib.pyplot as plt

class MagneticGridSimulator:
    def __init__(self, grid_size=(3,3), grid_spacing=0.1):
        """
        Initialize magnetic grid simulator
        grid_size: tuple of (rows, cols) for electromagnet grid
        grid_spacing: distance between electromagnets in meters
        """
        self.grid_size = grid_size
        self.spacing = grid_spacing
        
        # Create grid of electromagnet positions
        self.electromagnet_positions = np.zeros((grid_size[0], grid_size[1], 3))
        for i in range(grid_size[0]):
            for j in range(grid_size[1]):
                self.electromagnet_positions[i,j] = [i*grid_spacing, j*grid_spacing, 0]
        
        # Initialize electromagnet states (on/off)
        self.electromagnet_states = np.zeros(grid_size)
        
        # Permanent magnet state
        self.pm_position = np.array([grid_size[0]*grid_spacing/2, 
                                   grid_size[1]*grid_spacing/2, 
                                   0.05])  # 5cm above grid
        self.pm_velocity = np.array([0., 0., 0.])
        
    def magnetic_force(self, position, strength=1.0):
        """Calculate magnetic force at a point from all active electromagnets"""
        total_force = np.zeros(3)
        
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if self.electromagnet_states[i,j] == 0:
                    continue
                    
                r = position - self.electromagnet_positions[i,j]
                r_mag = np.linalg.norm(r)
                if r_mag < 1e-10:  # Avoid division by zero
                    continue
                
                # Simplified magnetic force calculation (inverse cube law)
                # In reality, this would be more complex
                force_mag = strength * mu_0 / (4 * np.pi * r_mag**3)
                force = force_mag * r / r_mag
                total_force += force
                
        return total_force
    
    def step(self, dt=0.01):
        """Step the simulation forward by dt seconds"""
        # Calculate force on permanent magnet
        force = self.magnetic_force(self.pm_position)
        
        # Simple Euler integration
        self.pm_velocity += force * dt
        self.pm_position += self.pm_velocity * dt
        
        # Add damping
        self.pm_velocity *= 0.95
        
    def set_electromagnet(self, row, col, state):
        """Turn electromagnet on (1) or off (0)"""
        self.electromagnet_states[row,col] = state
        
    def get_pm_position(self):
        """Get current position of permanent magnet"""
        return self.pm_position.copy()

# Example usage
if __name__ == "__main__":
    sim = MagneticGridSimulator()
    
    # Turn on some electromagnets to create a pattern
    sim.set_electromagnet(0, 0, 1)
    sim.set_electromagnet(2, 2, 1)
    
    # Run simulation for a few steps
    positions = []
    for _ in range(100):
        sim.step()
        positions.append(sim.get_pm_position())
    
    # Plot trajectory
    positions = np.array(positions)
    plt.plot(positions[:,0], positions[:,1])
    plt.grid(True)
    plt.title("Permanent Magnet Trajectory")
    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.show()
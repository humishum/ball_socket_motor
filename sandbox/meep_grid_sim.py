# update: this doesn't really work and is obsolete, maybe revisit for fun but magpylib is too good 
# 
import meep as mp
import numpy as np

class MagneticGridSimulation:
    def __init__(self, grid_size=(10, 10), cell_size=1.0, resolution=20):
        """
        Initialize magnetic grid simulation
        
        Parameters:
        grid_size: tuple (nx, ny) - Number of magnets in x and y directions
        cell_size: float - Physical size of each grid cell in simulation units
        resolution: int - Number of pixels per unit length
        """
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.resolution = resolution
        
        # Calculate full simulation size
        self.sx = grid_size[0] * cell_size
        self.sy = grid_size[1] * cell_size
        self.sz = cell_size * 4  # Height of simulation region
        
        # Initialize magnet states (1 = on, 0 = off)
        self.magnet_states = np.ones(grid_size)
        
        # Create the simulation cell
        self.cell = mp.Vector3(self.sx, self.sy, self.sz)
        
        # Initialize simulation
        self.sim = mp.Simulation(
            cell_size=self.cell,
            resolution=resolution,
            geometry=[],
            k_point=None,
            default_material=mp.Medium(epsilon=1)
        )
        
        # Create initial magnet sources
        self.update_sources()
    
    def set_magnet_state(self, x, y, state):
        """Set the state of a specific magnet (on/off)"""
        if 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]:
            self.magnet_states[x, y] = state
            self.update_sources()
        else:
            raise ValueError("Magnet coordinates out of range")
    
    def update_sources(self):
        """Update magnetic sources based on current magnet states"""
        # Clear existing sources
        self.sim.reset_meep()
        
        # Create new sources for active magnets
        sources = []
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                if self.magnet_states[x, y]:
                    pos = mp.Vector3(
                        (x + 0.5) * self.cell_size - self.sx/2,
                        (y + 0.5) * self.cell_size - self.sy/2,
                        0
                    )
                    # Create a magnetic dipole source
                    sources.append(mp.Source(
                        mp.ContinuousSource(frequency=1.0),
                        component=mp.Hx,  # Changed to Hx as an example
                        center=pos,
                        size=mp.Vector3(0.1, 0.1, 0.1),
                        amplitude=1.0
                    ))
        
        self.sim.change_sources(sources)
    
    def run_simulation(self, until=200):
        """Run the simulation for specified time steps"""
        self.sim.run(until=until)
    
    def get_field(self, component='h'):
        """
        Get the field distribution for specified component
        
        Parameters:
        component: str - Field component to return ('h', 'e', or 'b')
                       For magnetic field (h), returns magnitude of H-field
                       For electric field (e), returns magnitude of E-field
                       For magnetic flux density (b), returns magnitude of B-field
        """
        if component.lower() == 'h':
            # Get all magnetic field components
            hx = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Hx)
            hy = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Hy)
            hz = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Hz)
            # Calculate magnitude
            return np.sqrt(np.abs(hx)**2 + np.abs(hy)**2 + np.abs(hz)**2)
        elif component.lower() == 'e':
            # Get all electric field components
            ex = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Ex)
            ey = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Ey)
            ez = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Ez)
            # Calculate magnitude
            return np.sqrt(np.abs(ex)**2 + np.abs(ey)**2 + np.abs(ez)**2)
        elif component.lower() == 'b':
            # Get all magnetic flux density components
            bx = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Bx)
            by = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.By)
            bz = self.sim.get_array(center=mp.Vector3(), size=self.cell, component=mp.Bz)
            # Calculate magnitude
            return np.sqrt(np.abs(bx)**2 + np.abs(by)**2 + np.abs(bz)**2)
        else:
            raise ValueError("Invalid component. Use 'h', 'e', or 'b'")
    
    def visualize_field(self, component='h'):
        """
        Visualize the field distribution
        
        Parameters:
        component: str - Field component to visualize ('h', 'e', or 'b')
        """
        import matplotlib.pyplot as plt
        
        field = self.get_field(component)
        plt.figure(figsize=(10, 10))
        plt.imshow(field.transpose(), interpolation='spline16', cmap='RdBu')
        plt.colorbar(label=f'{component.upper()}-Field Magnitude')
        plt.title(f'{component.upper()}-Field Distribution')
        plt.xlabel('X position')
        plt.ylabel('Y position')
        return plt

# Example usage
if __name__ == "__main__":
    # Create a 5x5 grid of magnets
    sim = MagneticGridSimulation(grid_size=(5, 5))
    
    # Turn off some magnets
    sim.set_magnet_state(1, 1, 0)
    sim.set_magnet_state(3, 3, 0)
    
    # Run simulation
    sim.run_simulation()
    
    # Visualize results
    plt = sim.visualize_field('h')  # Visualize H-field magnitude
    plt.show()

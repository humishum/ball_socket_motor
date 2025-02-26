import numpy as np
import magpylib as mag
from scipy.optimize import differential_evolution

# Constants
mu0 = 4 * np.pi * 1e-7* (1/500) # permeability of free space in H/m

def compute_pull_strength(current, number_turns, coil_diameter):
    """
    Compute the pull strength of a coil electromagnet using Magpylib.
    
    We approximate the coil as a flat coil (all turns co-located) by creating
    a single loop with an effective current = number_turns * current.
    
    The pull force is estimated by first computing the magnetic flux density B
    at a target point (a small gap away from the coil face) and then applying:
    
        F = B^2 * A / (2 * mu0)
    
    where A is the area of the coil face.
    
    Parameters:
        current (float): Current per turn in amperes.
        number_turns (int): Number of turns in the coil.
        coil_diameter (float): Diameter of the coil in meters.
    
    Returns:
        pull_force (float): Estimated pull force in newtons.
    """
    # Effective current for a flat coil (all turns adding constructively)
    effective_current = current * number_turns

    # Create the coil as a current loop
    # Note: coil_diameter is in meters.
    coil = mag.current.Loop(current=effective_current, diameter=coil_diameter)
    
    # Define a target point along the z-axis at a small gap (e.g., 1 mm away)
    gap = 0.001  # gap in meters
    target_point = (0, 0, gap)
    
    # Compute the magnetic field at the target point
    B_vector = coil.getB(target_point)
    B_magnitude = np.linalg.norm(B_vector)
    
    # Assume the contact area is the face of the coil (circle of radius = coil_diameter/2)
    area = np.pi * (coil_diameter / 2) ** 2
    
    # Compute the pull force using F = (B^2 * A) / (2 * mu0)
    pull_force = (B_magnitude ** 2 * area) / (2 * mu0)
    return pull_force

def objective(params):
    """
    Objective function that we want to minimize. It combines:
      - Maximizing pull strength (we subtract it, since optimizers minimize by default)
      - Minimizing current (to reduce power consumption)
      - Minimizing number of turns (to reduce material/complexity)
    
    Parameters:
        params (list or array): [current, number_turns, coil_diameter]
          - current is in amperes (A)
          - number_turns is treated as continuous but will be rounded to the nearest integer
          - coil_diameter is in meters
          
    Returns:
        cost (float): The scalar objective value.
    """
    current = params[0]
    # Ensure number_turns is an integer
    number_turns = int(round(params[1]))
    coil_diameter = params[2]
    
    # Compute pull strength using the Magpylib-based simulation
    pull_strength = compute_pull_strength(current, number_turns, coil_diameter)
    
    # Weight factors for current and number_turns. (Adjust these as needed.)
    weight_current = 1
    weight_turns = 0.1
    
    # We want to maximize pull_strength, so subtract it.
    # Also add penalties for higher current and more turns.
    cost = -pull_strength + weight_current * current + weight_turns * number_turns
    return cost

# Define the bounds for the design variables:
#   current: [0, 0.5 A]
#   number_turns: [50, 1000] (treated as continuous and later rounded)
#   coil_diameter: [1, 2.5] cm, converted to meters -> [0.01, 0.025] m
bounds = [
    (0.1, 0.5),      # current in A
    (200, 1000),      # number_turns
    (0.01, 0.025)    # coil_diameter in m
]

# Run the differential evolution optimizer
result = differential_evolution(objective, bounds, strategy='best1bin', maxiter=10000, popsize=15, tol=1e-6)

# Report the optimal design parameters
optimal_current = result.x[0]
optimal_turns = int(round(result.x[1]))
optimal_diameter = result.x[2]

print("Optimization Result:")
print(f"Optimal Current: {optimal_current:.4f} A")
print(f"Optimal Number of Turns (rounded): {optimal_turns}")
print(f"Optimal Coil Diameter: {optimal_diameter:.4f} m")
print(f"Objective Value: {result.fun:.4f}")

# (Optional) Compute and print the pull strength for the optimal design
optimal_pull_strength = compute_pull_strength(optimal_current, optimal_turns, optimal_diameter)
print(f"Estimated Pull Strength: {optimal_pull_strength} N")

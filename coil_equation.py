import numpy as np
import numpy.typing as npt

def calculate_magnetic_field(radii:npt.ArrayLike, current, z, mu_0=4 * np.pi * 1e-7):
    """
    Calculate the magnetic field strength at a point z along the axis of a flat coil
    with multiple turns at different radii.
    
    Parameters:
    radii (array-like): List or array of radii for each turn in meters
    current (float): Current flowing through the coil in Amperes
    z (float): Distance from the coil center along the axis in meters
    mu_0 (float): Permeability of free space in T⋅m/A (default: 4π × 10⁻⁷)
    
    Returns:
    float: Magnetic field strength in Tesla
    """
    # Convert radii to numpy array if it isn't already
    radii = np.array(radii)
    
    # Calculate field contribution from each turn
    B_contributions = (mu_0 * current * radii**2) / (2 * (radii**2 + z**2)**(3/2))
    
    # Sum all contributions
    B_total = np.sum(B_contributions)
    
    return B_total

def calculate_field_vs_distance(radii, current, z_points):
    """
    Calculate magnetic field strength at multiple points along the axis.
    
    Parameters:
    radii (array-like): List or array of radii for each turn in meters
    current (float): Current flowing through the coil in Amperes
    z_points (array-like): Points along z-axis where to calculate field
    
    Returns:
    array: Magnetic field strength at each z point
    """
    return np.array([calculate_magnetic_field(radii, current, z) for z in z_points])

# Example usage:
if __name__ == "__main__":
    # Example: 3-turn coil with increasing radii
    # radii = [0.05, 0.052, 0.054]  # radii in meters
    n_turns = 50 
    inner_radii_m = 0.003
    outer_radii_m = 0.0058
    radii = np.linspace(inner_radii_m, outer_radii_m,n_turns)
    current = 5.0  
    z_m = 0.01  # 3cm from center
    
    # Calculate field at a single point
    B = calculate_magnetic_field(radii, current, z_m)
    print(f"Magnetic field at z={z_m*100:.1f}cm: {B*1000:.2f} mT")
    
    # Calculate field at multiple points along z-axis
    z_points = np.linspace(0.01, 0.1, 50)  # 1cm to 10cm
    B_points = calculate_field_vs_distance(radii, current, z_points)
    
    print("\nField strength at different distances:")
    for i in range(0, len(z_points), 10):
        print(f"z={z_points[i]*100:.1f}cm: {B_points[i]*1000:.2f} mT")


    # T = N/A*m 
    # Need to move 0.5 KG force 
    

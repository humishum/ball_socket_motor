import numpy as np
import magpylib as magpy
from time import time
import matplotlib.pyplot as plt

start = time()

#Placement Parameters
r_m = 0.1      # hemisphere radius
n_phi_rad = 4   # steps in elevation
n_theta_rad = 8 # steps in azimuth

##  Electromagnet Parameters
coil_diameter_m = 0.02          # [m] (or any length unit)
base_input_current_A = 0.5
n_turns = 250
effective_current_A = base_input_current_A * n_turns # Approximated
# FerroMagnetic Center(need characterization)
include_ferro_center = True
ferro_polarization=(.1,.2,.3) 
ferro_dimension=(.01,.01)


# Generate coils on hemisphere
coils = []
sensor_positions = []
phi_values = np.linspace(0, np.pi/2, n_phi_rad)   # 0 to π/2 for a hemisphere
theta_values = np.linspace(0, 2*np.pi, n_theta_rad, endpoint=False)

# Sensor Offsets
range_offsets = [0, 0.005]  
angle_offsets =[0] # [0, (theta_values[1]- theta_values[0])/2,]#  (theta_values[1]- theta_values[0])/4, (theta_values[1]- theta_values[0])/8]  
angle_offsets.extend([a*-1 for a in angle_offsets])
phi_offsets= [0] # [ 0, (phi_values[1]- phi_values[0])/2]

for phi in phi_values: # elevation
    for theta in theta_values: # azimuth
        for r_offset in range_offsets: # range for sensor
            for theta_offset in angle_offsets: # az for sensor
                for phi_offset in phi_offsets: # el for sensor

                    # Calculate sensor position in cartesian
                    x = (r_m + r_offset) * np.sin(phi+phi_offset) * np.cos(theta + theta_offset)
                    y = (r_m + r_offset) * np.sin(phi+phi_offset) * np.sin(theta + theta_offset)
                    z = (r_m + r_offset) * np.cos(phi+phi_offset)
                    pos = np.array([x, y, z])
                    sensor_positions.append(pos)

                    # Add coil only for the 0 offset case
                    if r_offset == 0 and theta_offset == 0 and phi_offset==0:   
                        coil = magpy.current.Circle(current=effective_current_A, diameter=coil_diameter_m)
                        
                        # Rotate coil from +z-axis to the local radial direction
                        radial_dir = pos / np.linalg.norm(pos)  # Unit Vector for radial direction
                        z_axis = np.array([0, 0, 1])
                        z_cross_radial = np.cross(z_axis, radial_dir)  # Orthogonal vector to z_axis and radial_dir
                        norm_cross = np.linalg.norm(z_cross_radial)  # Magnitude 

                        if norm_cross > 1e-9:
                            z_cross_radial /= norm_cross
                            angle = np.arccos(np.dot(z_axis, radial_dir))
                            coil.rotate_from_angax(angle=angle, axis=z_cross_radial, degrees=False)

                        if include_ferro_center: 
                            ferro = magpy.magnet.Cylinder(position=pos,polarization=ferro_polarization, dimension=ferro_dimension )
                            if norm_cross > 1e-9:
                                ferro.rotate_from_angax(angle=angle, axis=z_cross_radial, degrees=False)
                            coils.append(ferro)
                        # Move coil out to the hemisphere surface
                        coil.move(pos)
                        coils.append(coil)

# Combine all coils into a single Collection
collection = magpy.Collection(coils)
sensors = [magpy.Sensor(i) for i in sensor_positions]
collection.add(sensors)


print(f"{time()-start}s")


## PLOTTING 


grid_length_m = r_m *1.25

# Define grid for the top‐down (x-y) view
nx_top, ny_top = 60, 60
xs_top = np.linspace(-grid_length_m, grid_length_m, nx_top)
ys_top = np.linspace(-grid_length_m, grid_length_m, ny_top)
X_top, Y_top = np.meshgrid(xs_top, ys_top)
# Create a grid of points in the z=0 plane
grid_top = np.stack((X_top, Y_top, np.zeros_like(X_top)), axis=2)

# Compute the B-field on the top view grid and scale it
B_top = magpy.getB(collection, grid_top) * 1E-3

# Calculate the magnetic energy density: Energy = 0.5 * |B|^2
Energy_top = 0.5 * np.sum(np.square(B_top), axis=2)

# Compute the force field (i.e. the gradient of the energy)
# Note: np.gradient returns [dEnergy/dy, dEnergy/dx] for a 2D array with shape (ny, nx)
force_top = np.gradient(Energy_top, ys_top, xs_top)


# Define grid for the side view: here we take an x-z slice at y=0
nx_side, nz_side = 60, 60
xs_side = np.linspace(-grid_length_m, grid_length_m, nx_side)
zs_side = np.linspace(-grid_length_m, grid_length_m, nz_side)
X_side, Z_side = np.meshgrid(xs_side, zs_side)
# Create a grid of points in the y=0 plane (side view)
grid_side = np.stack((X_side, np.zeros_like(X_side), Z_side), axis=2)

B_side = magpy.getB(collection, grid_side) * 1E-3
Energy_side = 0.5 * np.sum(np.square(B_side), axis=2)
# For the side view, the first axis corresponds to z and the second to x
force_side = np.gradient(Energy_side, zs_side, xs_side)


# Create contour plots and overlay the force (gradient) vectors
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Top-down contour plot (x-y view)
contour1 = axes[0].contourf(X_top, Y_top, Energy_top, levels=25, cmap='viridis')
# Overlay quiver: note that force_top[1] is dE/dx and force_top[0] is dE/dy
axes[0].quiver(X_top, Y_top, force_top[1], force_top[0], color='white', scale=50)
axes[0].set_title("Magnetic Energy Top Down (x-y)")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
fig.colorbar(contour1, ax=axes[0], label="Energy")

# Side view contour plot (x-z view)
contour2 = axes[1].contourf(X_side, Z_side, Energy_side, levels=25, cmap='viridis')
# Here force_side[1] is dE/dx and force_side[0] is dE/dz
axes[1].quiver(X_side, Z_side, force_side[1], force_side[0], color='white', scale=50)
axes[1].set_title("Magnetic Energy Side View (x-z)")
axes[1].set_xlabel("x")
axes[1].set_ylabel("z")
fig.colorbar(contour2, ax=axes[1], label="Energy")

plt.tight_layout()
plt.show()


magpy.show(
    collection,
    sensors,
    output="model3d", 
    arrow = True
    # output=("Bxy", "Bxz", "Byz"),
    # style={
    #     # "color": "value",               # Color each sensor marker by the B-field magnitude.
    #     "marker": {"size": 2},          # Define marker size.
    #     # "arrow": {"scale": 0.4, "color": "black"},  # Configure arrow properties.
    #     "arrows": True                  # Toggle drawing of arrows.
    # },
)

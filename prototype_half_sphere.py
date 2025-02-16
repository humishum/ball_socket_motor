import numpy as np
import magpylib as magpy
from time import time
start = time()
#Placement Parameters
r_m = 0.1      # hemisphere radius
n_phi_rad = 4                   # steps in elevation
n_theta_rad = 8                 # steps in azimuth

# ElectroMagnet Parameters
coil_diameter_m = 0.02          # [m] (or any length unit)
coil_current_A = 0.01         # [A]
base_input_current_A = 0.1
n_turns = 200
effective_current_A = base_input_current_A * n_turns # Approximated

# Generate coils on hemisphere
coils = []
sensor_positions = []
phi_values = np.linspace(0, np.pi/2, n_phi_rad)   # 0 to π/2 for a hemisphere
theta_values = np.linspace(0, 2*np.pi, n_theta_rad, endpoint=False)

# Senor Offsets
range_offsets = [0, 0.005]  
angle_offsets = [0, (theta_values[1]- theta_values[0])/2,]#  (theta_values[1]- theta_values[0])/4, (theta_values[1]- theta_values[0])/8]  
angle_offsets.extend([a*-1 for a in angle_offsets])
phi_offsets= [ 0, (phi_values[1]- phi_values[0])/2]

for phi in phi_values:
    for theta in theta_values:
        for r_offset in range_offsets:
            for theta_offset in angle_offsets:
                for phi_offset in phi_offsets: 
                    # Calculate sensor position
                    x = (r_m + r_offset) * np.sin(phi+phi_offset) * np.cos(theta + theta_offset)
                    y = (r_m + r_offset) * np.sin(phi+phi_offset) * np.sin(theta + theta_offset)
                    z = (r_m + r_offset) * np.cos(phi+phi_offset)
                    pos = np.array([x, y, z])
                    sensor_positions.append(pos)

                    # Add coil only for the 0 offset case
                    if r_offset == 0 and theta_offset == 0 and phi_offset==0:   
                        coil = magpy.current.Circle(current=coil_current_A, diameter=coil_diameter_m)

                        # Rotate coil from +z-axis to the local radial direction
                        radial_dir = pos / np.linalg.norm(pos)  # Unit Vector for radial direction
                        z_axis = np.array([0, 0, 1])
                        z_cross_radial = np.cross(z_axis, radial_dir)  # Orthogonal vector to z_axis and radial_dir
                        norm_cross = np.linalg.norm(z_cross_radial)  # Magnitude 

                        if norm_cross > 1e-9:
                            z_cross_radial /= norm_cross
                            angle = np.arccos(np.dot(z_axis, radial_dir))
                            coil.rotate_from_angax(angle=angle, axis=z_cross_radial, degrees=False)

                        # Move coil out to the hemisphere surface
                        coil.move(pos)
                        coils.append(coil)

# Combine all coils into a single Collection
collection = magpy.Collection(coils)

# -----------------------------
# 3) Define sensor grid points
# -----------------------------
# For demonstration, we'll look at the B-field in the z=0 plane
# nx, ny = 11, 11
# xs = np.linspace(-15, 15, nx)  # choose plane extents
# ys = np.linspace(-15, 15, ny)
# pts = [[x, y, 0] for x in xs for y in ys]  # z=0 plane

# pts = np.array([[0,0,0], [1,0,0], [0,1,0], [0,0,1], [1,1,1], [1,0,1], [0,1,1], [1,1,0]])*0.1


# sensor = magpy.Sensor(sensor_positions)
sensors = [magpy.Sensor(i) for i in sensor_positions]
[sensor.getB(collection) for sensor in sensors]
collection.add(sensors)
# Compute the magnetic field at each sensor point
# B_values = sensor.getB(collection)



# print("Magnetic field vectors at sensor points:")
# for pt, B in zip(pts, B_values):
#     print(f"At {pt}: B = {B}")
# import matplotlib.pyplot as plt

# # Extract x and y coordinates (and optionally the B vector components)
# xs = [pt[0] for pt in pts]
# ys = [pt[1] for pt in pts]
# # Assuming B_values is a list of 3-element arrays and we are in the z=0 plane:
# Bx = [B[0] for B in B_values]
# By = [B[1] for B in B_values]

# plt.figure(figsize=(8, 6))
# plt.quiver(xs, ys, Bx, By, color='blue', angles='xy', scale_units='xy', scale=1)
# plt.xlabel("x")
# plt.ylabel("y")
# plt.title("Magnetic Field Vectors (Projection on z=0 plane)")
# plt.axis('equal')
# plt.show()


# ------------------------------------
# 4) Visualize with magpy.show(...)
# ------------------------------------
# * style.color='value': color code each sensor marker by local B magnitude
# * style.show_arrows=True: draw a small arrow at each sensor for direction
# * style.arrow_scale=0.4: scale arrow size
# * style.marker_size=2: scale point markers
# * style.arrow_color='black': arrow color (optional)

# magpy.show(collection, sensor)
print(f"{time()-start}s")
fig = magpy.show(
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
# fig.show()

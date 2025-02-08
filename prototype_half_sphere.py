import numpy as np
import magpylib as magpy

# -------------------
# 1) Parameter setup
# -------------------
r_m = 0.1                      # hemisphere radius
n_phi = 4                   # steps in polar angle
n_theta = 8                 # steps in azimuth
coil_current = 1e7           # [A]
coil_diameter_m = 0.02          # [m] (or any length unit)

# --------------------------------
# 2) Generate coils on hemisphere
# --------------------------------
coils = []

phi_values = np.linspace(0, np.pi/2, n_phi)   # 0 to π/2 for a hemisphere
theta_values = np.linspace(0, 2*np.pi, n_theta, endpoint=False)
sensor_positions = []
for phi in phi_values:
    for theta in theta_values:
        # Hemisphere surface coordinates
        x = r_m * np.sin(phi) * np.cos(theta)
        y = r_m * np.sin(phi) * np.sin(theta)
        z = r_m * np.cos(phi)

        # Create a Loop (flat coil)
        coil = magpy.current.Circle(current=coil_current, diameter=coil_diameter_m)

        # Rotate coil from +z-axis to the local radial direction
        pos = np.array([x, y, z])
        sensor_positions.append(pos)
        print(f"pos: {pos}")
        radial_dir = pos / np.linalg.norm(pos)  # unit vector
        z_axis = np.array([0,0,1])
        cross_vec = np.cross(z_axis, radial_dir)
        norm_cross = np.linalg.norm(cross_vec)
        if norm_cross > 1e-9:
            cross_vec /= norm_cross
            angle = np.arccos(np.dot(z_axis, radial_dir))
            # print(f"angle: {angle}")
            # print(f"cross_vec: {cross_vec}")
            coil.rotate_from_angax(angle=angle, axis=cross_vec, degrees=False)

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
sensor = magpy.Sensor(sensor_positions)

# Compute the magnetic field at each sensor point
B_values = sensor.getB(collection)
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
fig = magpy.show(
    collection,
    sensor,
    # output="model3d"
    output=("Bxy", "Bxz", "Byz"),
    # style={
    #     # "color": "value",               # Color each sensor marker by the B-field magnitude.
    #     "marker": {"size": 2},          # Define marker size.
    #     # "arrow": {"scale": 0.4, "color": "black"},  # Configure arrow properties.
    #     "arrows": True                  # Toggle drawing of arrows.
    # },
)
# fig.show()
import numpy as np
import magpylib as magpy

# -------------------
# 1) Parameter setup
# -------------------
R = 10                      # hemisphere radius
n_phi = 4                   # steps in polar angle
n_theta = 8                 # steps in azimuth
coil_current = 1            # [A]
coil_diameter = 2           # [m] (or any length unit)

# --------------------------------
# 2) Generate coils on hemisphere
# --------------------------------
coils = []

phi_values = np.linspace(0, np.pi/2, n_phi)   # 0 to π/2 for a hemisphere
theta_values = np.linspace(0, 2*np.pi, n_theta, endpoint=False)

for phi in phi_values:
    for theta in theta_values:
        # Hemisphere surface coordinates
        x = R * np.sin(phi) * np.cos(theta)
        y = R * np.sin(phi) * np.sin(theta)
        z = R * np.cos(phi)

        # Create a Loop (flat coil)
        coil = magpy.current.Circle(current=coil_current, diameter=coil_diameter)

        # Rotate coil from +z-axis to the local radial direction
        pos = np.array([x, y, z])
        radial_dir = pos / np.linalg.norm(pos)  # unit vector
        z_axis = np.array([0,0,1])
        cross_vec = np.cross(z_axis, radial_dir)
        norm_cross = np.linalg.norm(cross_vec)
        if norm_cross > 1e-9:
            cross_vec /= norm_cross
            angle = np.arccos(np.dot(z_axis, radial_dir))
            coil.rotate_from_angax(angle=angle, axis=cross_vec)

        # Move coil out to the hemisphere surface
        coil.move(pos)
        coils.append(coil)

# Combine all coils into a single Collection
collection = magpy.Collection(coils)

# -----------------------------
# 3) Define sensor grid points
# -----------------------------
# For demonstration, we'll look at the B-field in the z=0 plane
nx, ny = 11, 11
xs = np.linspace(-15, 15, nx)  # choose plane extents
ys = np.linspace(-15, 15, ny)
pts = [[x, y, 0] for x in xs for y in ys]  # z=0 plane

sensor = magpy.Sensor(pts)

# ------------------------------------
# 4) Visualize with magpy.show(...)
# ------------------------------------
# * style.color='value': color code each sensor marker by local B magnitude
# * style.show_arrows=True: draw a small arrow at each sensor for direction
# * style.arrow_scale=0.4: scale arrow size
# * style.marker_size=2: scale point markers
# * style.arrow_color='black': arrow color (optional)

fig = magpy.show(
    collection,
    sensor,
    # style={
    #     "color": "value",
    #     "cmap": "jet",
    #     "show_arrows": True,
    #     "arrow_scale": 0.4,
    #     "marker_size": 2,
    #     "arrow_color": "black"
    # },
)

fig.show()
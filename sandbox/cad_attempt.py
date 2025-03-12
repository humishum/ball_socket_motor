import math
import cadquery as cq
print("loaded cadquery")
# --- Parameters (adjust as needed) ---
R = 50                # Dome (sphere) radius
hole_d = 10           # Diameter of the holes
hole_depth = 20       # Depth (length) of the cylindrical holes
n_holes_ring = 12     # Number of holes in the ring
theta_ring_deg = 60   # Polar angle (in degrees) for the ring holes

# Convert polar angle to radians for calculations.
theta_ring = math.radians(theta_ring_deg)

# --- Create the dome ---
# Create a full sphere and then intersect it with a box (or half-space) to obtain a hemisphere (dome).
dome = cq.Workplane("XY").sphere(R).intersect(
    cq.Workplane("XY").box(2 * R, 2 * R, R, centered=(True, True, False))
)

# --- Subtract the Top Hole ---
# Create a vertical cylinder for the top hole.
top_hole = cq.Workplane("XY").circle(hole_d / 2).extrude(hole_depth)
# Translate the cylinder so its center (along the hole’s axis) roughly aligns with the top surface.
top_hole = top_hole.translate((0, 0, R - hole_depth / 2))

# Subtract the top hole from the dome.
result = dome.cut(top_hole)

# --- Subtract the Ring of Holes ---
for i in range(n_holes_ring):
    # Compute the azimuth angle for each hole (in radians)
    phi = math.radians(i * 360 / n_holes_ring)
    
    # Compute the (x, y, z) position on the sphere for the ring hole.
    x = R * math.sin(theta_ring) * math.cos(phi)
    y = R * math.sin(theta_ring) * math.sin(phi)
    z = R * math.cos(theta_ring)
    
    # The radial direction (normal to the dome) at this point:
    length = math.sqrt(x * x + y * y + z * z)
    nx, ny, nz = x / length, y / length, z / length
    
    # Create a cylinder oriented along the Z-axis.
    hole_cyl = cq.Workplane("XY").circle(hole_d / 2).extrude(hole_depth)
    
    # To align the cylinder with the radial direction:
    #   - Compute the angle between the Z-axis (0, 0, 1) and the desired direction.
    angle = math.degrees(math.acos(nz))
    #   - The rotation axis is the cross product of (0,0,1) and (nx, ny, nz), which is (-ny, nx, 0).
    rx, ry, rz = -ny, nx, 0
    if abs(angle) > 1e-6:
        hole_cyl = hole_cyl.rotate((0, 0, 0), (rx, ry, rz), angle)
    
    # Translate the hole so that its center (along its axis) is offset by half the hole depth.
    # This positions the cylinder so that it cuts approximately symmetrically through the dome’s wall.
    hole_cyl = hole_cyl.translate((x - (hole_depth / 2) * nx,
                                   y - (hole_depth / 2) * ny,
                                   z - (hole_depth / 2) * nz))
    
    # Subtract this hole from the dome.
    result = result.cut(hole_cyl)

# --- Export the Result as STL ---
cq.exporters.export(result, 'dome_with_holes.stl')
print("STL file 'dome_with_holes.stl' has been created.")

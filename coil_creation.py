import magpylib as mgpy
import numpy as np 


# Create collection 
collection = mgpy.Collection()

n_turns = 1 
n_turns_approx = 300 # assumption that all coils are at same point, magnetic fields can sum up, so dirty solution here
current_A = 0.15
for i in range(n_turns):
    turn = mgpy.current.Circle(current=current_A*n_turns_approx, diameter=0.02, position=[0,0,i*0.001])
    collection.add(turn)

cyl = mgpy.magnet.Cylinder(position=(0,0,0), dimension=(0.02, 0.001), magnetization=(0,0,1))
# Define sensor grid points
z_pos = np.linspace(-.005, 10*0.005, 10)
sensor_postions = [[0,0,z] for z in z_pos]
sensor = mgpy.Sensor(sensor_postions)

print(mgpy.getB(collection, sensor))
# mgpy.show(collection, sensor)
mgpy.show(
    collection, 
    sensor,
    output=("model3d"),
    backend="plotly",
)


import magpylib as mgpy
import numpy as np 


# Create collection 
collection = mgpy.Collection()

n_turns = 1 
n_turns_approx = 300 # assumption that all coils are at same point, magnetic fields can sum up, so dirty solution here

for i in range(n_turns):
    turn = mgpy.current.Circle(current=0.15*n_turns_approx, diameter=0.05, position=[0,0,i*0.001])
    collection.add(turn)

# Define sensor grid points
z_pos = np.linspace(0, n_turns*0.001 +0.005, n_turns+1)
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


import numpy as np
import magpylib as magpy
coil_current = 0          # [A]
coil_diameter = 0.01          # [m] (or any length unit)
coil = magpy.current.Circle(current=coil_current, diameter=coil_diameter)
coil.rotate_from_angax(45, 'x')
collection = magpy.Collection([coil])

sensor = magpy.Sensor([0,0,0])
B_field = sensor.getB(collection)
print("Magnetic field at the sensor position:", B_field)

magpy.show(collection, sensor)
import magpylib
import numpy as np
import magpylib as magpy
from time import time
import numpy.typing as npt


# Simple Coil Design (coil summation approximation)
class SimpleCoil(object): 
    def __init__(self, n_turns:int, current_a_base: float,diameter_m:float): 
        self.n_turns = n_turns
        self.current_a_base = current_a_base
        self.diameter_m = diameter_m

    def get_magnet(self): 
        return magpy.current.Circle(current=self.current_a_base*self.n_turns, diameter=self.diameter_m)

# Coil Design with Cylinder 
class CoilCylinder(object):
    n_turns = 0
    current_a = 0
    coil_diameter  = 0 
    coil_height = 0 

    def __init__(self, n_turns:int, current_a:float, coil_diameter:float, coil_height:float, magnetization:npt.ArrayLike): 
        self.n_turns = n_turns
        self.current_a = current_a
        self.coil_diameter = coil_diameter
        self.coil_height = coil_height
        self.magnetization: npt.ArrayLike = magnetization

    def _get_coils(self): 
        return magpy.current.Circle(current=self.current_a*self.n_turns, diameter=self.coil_diameter*1.1)

    def _get_cylinder(self): 
        return magpy.magnet.Cylinder(position=(0,0,0), dimension=(self.coil_diameter, self.coil_height), magnetization=(0,0,1))

    def get_magnet(self): 
        return magpy.Collection([self._get_coils(), self._get_cylinder()])



# class CoilUShape(object): 
# Can maybe this with a cylinder segment on top of a flat cylinder, but I don't know if this would actually work 
# given that its now two separet objects, with a non-homogenous
#     pass
# Coil Design with hollow cylinder or wtf its called 
# class CoilHollowCylinder(object):
#     n_turns = 0
#     current_a = 0
#     coil_diameter  = 0 
#     coil_height  = 0 
#     coil_innner_diam = 0

#     def __init__(self, n_turns:int, current_a:float, coil_diameter:float, coil_height:float, coil_innner_diam:float): 
#         self.n_turns = n_turns
#         self.current_a = current_a
#         self.coil_diameter = coil_diameter
#         self.coil_height = coil_height
#         self.coil_innner_diam = coil_innner_diam    
    
#     def get_magnet(self): 

    
    


# 




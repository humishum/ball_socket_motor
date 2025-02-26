- Finalize a prototype design: 
    - Using simulation, find the effective MAX field strength at X sensor positions around the sphere. 
        - This should basically determine our maximum stiffness. 
        -  Lets assume <180 deg of electromagnet placement, probably closer to 120.
        - Use this to get the sizing of PMs and EMs  
    - Design makeshift fixture in CAD

- Basically need an optimizer for 
max(pull strength)
min(current) within [0,0.5A]
min(number_turns)
max(pull_strength)
keep diameter [1, 2.5] cm 

Define a base class for the type of magnet. 
Set up simulation for each magnet, compute maximum field strength at X sensor positions around the sphere. 




need to install pymeep using conda, move this to blade instead of mac bc f conda" 

USe magnet designs and see what hyperparameters we need to generate enough torque to hold the sphere at constant position. 
Use this to generate the CAD and circuitry. 
This is the fastest way to prototype. 












For buildout: 

Order rev 1 and Rev 2 materials, 
Design enclosure in CAD, (could use text-to-stl tool here)

Calculate maxmimum B field for each coil. Cant summate this because of 3d positioning 

Calculate Weight of encloser 

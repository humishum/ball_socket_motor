
Decide on dimensions/count of EMs, update dynamic simulator to intake a config file with dimensions and positions 

Run simulator with this config, and get GUI controls working

While that's working, get started on EE prototyping 
Need to spec out Mosfets and Driver circuit. Start with one coil, take measurements on current draw and output. Model this for more and design on a design, hopefully fit in a perf board for prototyping 

Use this for initial FW development, at least to a point where we can have a rev1 PCB. 


- Magnet designer is basically done 
2/25
Next steps: 
    - Run simulation for all magnet types, and sweep with acceptable current and size paraeters 
    - Estimate needed Torque at radius to hold sphere at constant postion 
    - See which of the confugurations can support this 
    - Go with that for CAD and EE design 




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





For buildout: 

Order rev 1 and Rev 2 materials, 
Design enclosure in CAD, (could use text-to-stl tool here)

Calculate maxmimum B field for each coil. Cant summate this because of 3d positioning 

Calculate Weight of encloser 

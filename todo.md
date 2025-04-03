
4-2-25 
- took a longer than expected break from this project, some review to get back up to speed and fast track next steps 
Sensors choices are in, some of which we've already soldered connections onto. 
I think for now, we need to skip the simulator GUI and go straight to HW/FW development. Simulator can be used for optimization once a rev1 design is completed. 

We need two simulatenous protyping efforts: 
1. Breadboard containing EM driver circuit, and a way to measure the output B-Field. 
Primary goal here is to test and verify the driver circuit, and verify field strength. 
    a. situate the EM, connect to driver circuit, and create slider for magnetometer with ruler to measure distance vs B-Field 
    - we can use this to model the real world strength, and compare to theory and simulation 
2. prototype HW for movement
Primary goal here to test movement of sphere, and test the feedback loop. 
Start with a 2d design, where we have a number of EM's in a line or square, a permanent magnet on top, and control of the magnets either via potentiometer or digital interface 

Next steps should be as follows: 
- Spec EE requirements, and design driver circuit schematic 
- Build driver circuit on protoboard 
- Build circuit to measure B-Field 
- Iterate on prototype to get to #2 




========================================

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

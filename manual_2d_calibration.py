
from itertools import product
from pprint import pprint as print
import pandas as pd 
import numpy as np 


if __name__ == "__main__":
    
    # Configuration Parameters 
    linear_positions = [-2, 0, 2]
    mag_power = [0, 0.5, 1]
    cal_configs = [(f"pos: {pos}  Magnet Power: {power}", [pos, power]) 
                   for pos, power in product(linear_positions, mag_power)]

    data = pd.DataFrame(columns=["Position", "Strength", "mx", "my", "mz"])
    
   	# Start cal routine
    while True:
        user_input = input("Hit 'r' when ready to start: ").strip().lower()
        if user_input == "r":
            break
    
    # Loop over each configuration
    for log_statement, config in cal_configs:
        print(f"\nSetting position to {log_statement}")
        
        while True:
            user_input = input("Hit 'r' when ready to take measurement: ").strip().lower()
            if user_input == "r":
                break
        
        # Replace with real data collection
        mx, my, mz = np.random.random(3)
        
        # Create a new row for the DataFrame
        cal_row = {"Position": config[0], "Strength": config[1],
                   "mx": mx, "my": my, "mz": mz}
        
        # Append the row to the DataFrame
        new_row_data = pd.DataFrame([cal_row])
        data = pd.concat([data, new_row_data], ignore_index=True)
    
    # Print the final DataFrame
    print("\nCalibration Data:")
    print(data)
    data.to_csv("generated/cal_data.yaml")
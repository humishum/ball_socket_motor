#!/usr/bin/env python3
"""
TLV493D Magnetometer Visualization

This script reads magnetic field data from the Arduino running the magnetometer_reader sketch
and visualizes the magnetic field vectors and strength in real-time.

Requirements:
- Python 3.x
- pyserial
- matplotlib
- numpy
"""

# Make sure to install pyserial with: pip install pyserial
import serial  as serials# This imports the pyserial package
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# Default serial port settings
DEFAULT_PORT = '/dev/cu.usbmodem1201'  # Linux default, use 'COM3' or similar for Windows
DEFAULT_BAUD = 115200

# Data buffer for plotting history
MAX_HISTORY = 100
x_history = np.zeros(MAX_HISTORY)
y_history = np.zeros(MAX_HISTORY)
z_history = np.zeros(MAX_HISTORY)
strength_history = np.zeros(MAX_HISTORY)
temp_history = np.zeros(MAX_HISTORY)
time_history = np.zeros(MAX_HISTORY)

def parse_data(line):
    """Parse a line of CSV data from the Arduino."""
    try:
        parts = line.strip().split(',')
        if len(parts) == 5:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            strength = float(parts[3])
            temp = float(parts[4])
            return x, y, z, strength, temp
    except (ValueError, IndexError) as e:
        print(f"Error parsing data: {e}")
    return None

def setup_plot():
    """Set up the matplotlib figure with subplots."""
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle('TLV493D Magnetometer Visualization', fontsize=16)
    
    # 3D vector plot
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.set_title('Magnetic Field Vector')
    ax1.set_xlabel('X (mT)')
    ax1.set_ylabel('Y (mT)')
    ax1.set_zlabel('Z (mT)')
    
    # Set equal aspect ratio for 3D plot
    ax1.set_box_aspect([1, 1, 1])
    
    # Field strength over time
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_title('Field Strength Over Time')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Field Strength (mT)')
    
    # XYZ components over time
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_title('Field Components Over Time')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Field (mT)')
    
    # Temperature over time
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_title('Temperature Over Time')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Temperature (°C)')
    
    return fig, (ax1, ax2, ax3, ax4)

def update_plot(frame, ser, fig, axes):
    """Update function for animation."""
    global x_history, y_history, z_history, strength_history, temp_history, time_history
    
    # Try to read a line from serial
    if ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
            
            # Skip header lines that don't contain data
            if line.startswith("TLV493D") or line.startswith("Format:") or line.startswith("---"):
                print(f"Skipping header line: {line}")
                return axes
            
            data = parse_data(line)
            
            if data:
                x, y, z, strength, temp = data
                
                # Update histories (shift left and add new value at the end)
                x_history = np.roll(x_history, -1)
                y_history = np.roll(y_history, -1)
                z_history = np.roll(z_history, -1)
                strength_history = np.roll(strength_history, -1)
                temp_history = np.roll(temp_history, -1)
                time_history = np.roll(time_history, -1)
                
                x_history[-1] = x
                y_history[-1] = y
                z_history[-1] = z
                strength_history[-1] = strength
                temp_history[-1] = temp
                time_history[-1] = time.time()
                
                # Print the data for debugging
                print(f"Received data: X={x:.2f}, Y={y:.2f}, Z={z:.2f}, Strength={strength:.2f}, Temp={temp:.2f}")
                
                # Normalize time to start at 0
                if time_history[0] != 0:
                    rel_time = time_history - time_history[0]
                else:
                    rel_time = np.zeros_like(time_history)
                
                # Clear all axes
                for ax in axes:
                    ax.clear()
                
                # 3D vector plot (ax1)
                ax1 = axes[0]
                ax1.set_title('Magnetic Field Vector')
                ax1.set_xlabel('X (mT)')
                ax1.set_ylabel('Y (mT)')
                ax1.set_zlabel('Z (mT)')
                
                # Plot the vector
                ax1.quiver(0, 0, 0, x, y, z, color='r', arrow_length_ratio=0.1)
                
                # Set axis limits based on data
                max_val = max(abs(x), abs(y), abs(z), 1)  # At least 1 to avoid empty plot
                ax1.set_xlim([-max_val*1.2, max_val*1.2])
                ax1.set_ylim([-max_val*1.2, max_val*1.2])
                ax1.set_zlim([-max_val*1.2, max_val*1.2])
                
                # Field strength over time (ax2)
                ax2 = axes[1]
                ax2.set_title(f'Field Strength: {strength:.2f} mT')
                ax2.set_xlabel('Time (s)')
                ax2.set_ylabel('Field Strength (mT)')
                ax2.plot(rel_time, strength_history, 'g-')
                
                # XYZ components over time (ax3)
                ax3 = axes[2]
                ax3.set_title('Field Components')
                ax3.set_xlabel('Time (s)')
                ax3.set_ylabel('Field (mT)')
                ax3.plot(rel_time, x_history, 'r-', label='X')
                ax3.plot(rel_time, y_history, 'g-', label='Y')
                ax3.plot(rel_time, z_history, 'b-', label='Z')
                ax3.legend()
                
                # Temperature over time (ax4)
                ax4 = axes[3]
                ax4.set_title(f'Temperature: {temp:.2f} °C')
                ax4.set_xlabel('Time (s)')
                ax4.set_ylabel('Temperature (°C)')
                ax4.plot(rel_time, temp_history, 'r-')
                
                # Add current values as text
                fig.text(0.01, 0.01, f'X: {x:.2f} mT, Y: {y:.2f} mT, Z: {z:.2f} mT, Strength: {strength:.2f} mT, Temp: {temp:.2f} °C', 
                         fontsize=10, transform=fig.transFigure)
                
        except Exception as e:
            print(f"Error: {e}")
    
    return axes

def main():
    """Main function to run the visualization."""
    parser = argparse.ArgumentParser(description='Visualize TLV493D magnetometer data')
    parser.add_argument('--port', default=DEFAULT_PORT, help='Serial port')
    parser.add_argument('--baud', type=int, default=DEFAULT_BAUD, help='Baud rate')
    parser.add_argument('--force', action='store_true', help='Force open the port even if busy')
    args = parser.parse_args()
    
    serial_connection = None
    
    try:
        # Open serial connection
        print(f"Attempting to connect to {args.port} at {args.baud} baud...")
        
        # If force flag is set, try to handle busy port
        if args.force:
            try:
                # Try to close the port if it's already open by another instance
                temp_connection = serials.Serial(args.port)
                temp_connection.close()
                print("Closed existing connection to port")
                time.sleep(1)  # Give the system time to release the port
            except:
                pass
        
        serial_connection = serials.Serial(args.port, args.baud, timeout=1)
        print(f"Successfully connected to {args.port}")
        
        # Wait for Arduino to reset
        time.sleep(2)
        
        # Set up the plot
        fig, axes = setup_plot()
        
        # Create animation
        ani = FuncAnimation(fig, update_plot, fargs=(serial_connection, fig, axes), 
                           interval=100, save_count=100)  # Limit cache to 100 frames
        
        # Show the plot
        plt.tight_layout()
        plt.show()
        
    except serials.SerialException as e:
        if "Port is busy" in str(e) or "Permission denied" in str(e):
            print(f"Error: Port {args.port} is busy or permission denied.")
            print("This could be because:")
            print("  1. Another program is using the port")
            print("  2. The Arduino IDE Serial Monitor is open")
            print("  3. Another instance of this script is running")
            print("\nTry one of these solutions:")
            print("  - Close any programs using the serial port")
            print("  - Run this script with the --force flag to try to forcibly use the port")
            print("  - Try a different port from the list below")
        else:
            print(f"Error opening serial port {args.port}: {e}")
        
        print("\nAvailable ports:")
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            for port in ports:
                print(f"  {port.device}: {port.description}")
        else:
            print("  No ports found. Is the device connected?")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Close serial connection if it was opened
        if serial_connection is not None and serial_connection.is_open:
            serial_connection.close()
            print("Serial connection closed")

if __name__ == "__main__":
    main()
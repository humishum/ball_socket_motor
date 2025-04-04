"""
Matplotlib Live Plotter for TLV493D Magnetometer Data
- needs 10 seconds of buffer time to get proper plot
"""

import serial as serials# pyserial
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Default serial port settings
DEFAULT_PORT = '/dev/cu.usbmodem11201'
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
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle('TLV493D Magnetometer Visualization', fontsize=16)
    
    # 3D vector plot
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    ax1.set_title('Magnetic Field Vector')
    ax1.set_xlabel('X (mT)')
    ax1.set_ylabel('Y (mT)')
    ax1.set_zlabel('Z (mT)')
    ax1.set_box_aspect([1, 1, 1])
    
    # Field strength over time
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_title('Field Strength Over Time')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Field Strength (mT)')
    
    # XYZ field strength
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_title('Field Components Over Time')
    ax3.set_xlabel('Time (s)')
    ax3.set_ylabel('Field (mT)')
    
    # Temperature 
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_title('Temperature Over Time')
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Temperature (°C)')
    
    return fig, (ax1, ax2, ax3, ax4)

def update_plot(frame, ser, fig, axes):
    """Update function for animation."""
    global x_history, y_history, z_history, strength_history, temp_history, time_history
    
    # Clear buffer if too much data is waiting
    if ser.in_waiting > 100:  # If more than ~5 lines are waiting
        ser.reset_input_buffer()
        print("Buffer was getting full - cleared")
        time.sleep(0.01)  # Give a small pause to stabilize
    
    # Try to read multiple lines if available to catch up
    max_lines_per_update = 10  # Increased from 3 to 10
    lines_read = 0
    
    while ser.in_waiting and lines_read < max_lines_per_update:
        try:
            line = ser.readline().decode('utf-8').strip()
            
            # Skip header lines that don't contain data
            if line.startswith("TLV493D") or line.startswith("Format:") or line.startswith("---"):
                continue
            
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
                
                lines_read += 1
                
        except Exception as e:
            print(f"Error reading data: {e}")
            break
    
    # Only update the plots if we actually got new data
    if lines_read > 0:
        # Normalize time to start at 0
        if time_history[0] != 0:
            rel_time = time_history - time_history[0]
        else:
            rel_time = np.zeros_like(time_history)
        
        # Update 3D vector plot
        ax1 = axes[0]
        ax1.clear()
        ax1.set_title('Magnetic Field Vector')
        ax1.set_xlabel('X (mT)')
        ax1.set_ylabel('Y (mT)')
        ax1.set_zlabel('Z (mT)')
        
        # Plot the current vector
        ax1.quiver(0, 0, 0, x_history[-1], y_history[-1], z_history[-1], 
                  color='r', arrow_length_ratio=0.1)
        
        # Set equal aspect ratio and reasonable limits
        max_val = max(abs(x_history[-1]), abs(y_history[-1]), abs(z_history[-1]), 0.1)
        ax1.set_xlim([-max_val, max_val])
        ax1.set_ylim([-max_val, max_val])
        ax1.set_zlim([-max_val, max_val])
        
        # Update field strength plot
        ax2 = axes[1]
        ax2.clear()
        ax2.set_title('Field Strength Over Time')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Field Strength (mT)')
        ax2.plot(rel_time, strength_history, 'g-')
        
        # Update XYZ components plot
        ax3 = axes[2]
        ax3.clear()
        ax3.set_title('Field Components Over Time')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Field (mT)')
        ax3.plot(rel_time, x_history, 'r-', label='X')
        ax3.plot(rel_time, y_history, 'g-', label='Y')
        ax3.plot(rel_time, z_history, 'b-', label='Z')
        ax3.legend()
        
        # Update temperature plot
        ax4 = axes[3]
        ax4.clear()
        ax4.set_title('Temperature Over Time')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Temperature (°C)')
        ax4.plot(rel_time, temp_history, 'm-')
        
        # Adjust layout
        plt.tight_layout()
    
    return axes

def main():
    """Main function to run the visualization."""
    parser = argparse.ArgumentParser(description='Visualize TLV493D magnetometer data')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, help='Serial port')
    parser.add_argument('-b', '--baud', type=int, default=DEFAULT_BAUD, help='Baud rate')
    parser.add_argument('-f', '--force', action='store_true', help='Force open the port even if busy')
    args = parser.parse_args()
    
    serial_connection = None
    
    # Dirty try catch block
    try:
        # Open serial connection
        print(f"Attempting to connect to {args.port} at {args.baud} baud...")
        
        # Try to force a connection even if port is busy 
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
        
        # Wait for serial connection to stabilize 
        time.sleep(2)
        
        # Set up the plot
        fig, axes = setup_plot()
        
        # Create animation
        ani = FuncAnimation(fig, update_plot, fargs=(serial_connection, fig, axes), 
                           interval=50, save_count=100)  # 50ms interval, 100 frames cache
        
        # Show the plot
        plt.tight_layout()
        plt.show()
        
    except serials.SerialException as e:
        print(f"Error opening serial port: {e}")
        
        print("Available ports:")
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        if ports:
            for port in ports:
                print(f"  {port.device}: {port.description}")
        else:
            print("No serial ports found...")
    except KeyboardInterrupt:
        print("SIGINT received, exiting...")
    finally:
        # Close serial connection if it was opened
        if serial_connection is not None and serial_connection.is_open:
            serial_connection.close()
            print("Serial connection closed...")

if __name__ == "__main__":
    main()
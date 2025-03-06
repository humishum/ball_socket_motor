import serial
print("Serial module imported successfully!")
print(f"Serial version: {serial.__version__}")

# List available ports
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
print("Available ports:")
for port in ports:
    print(f"  {port.device}: {port.description}")

Replace `YOUR_PORT` with the appropriate serial port (e.g., `/dev/ttyACM0` on Linux, `COM3` on Windows).

If you're not sure which port to use, the script will list available ports if it fails to connect.

## Usage

Once running, the visualization will show:
- A 3D vector representing the current magnetic field direction and magnitude
- A graph of the total field strength over time
- A graph showing the X, Y, and Z components over time
- A graph of the sensor temperature over time

Move a magnet near the sensor to see the visualization respond to changes in the magnetic field.

## Troubleshooting

- If you see no data or errors in the visualization, check your serial port and ensure the Arduino is properly connected.
- If the visualization is too slow or too fast, you can adjust the delay in the Arduino sketch or the animation interval in the Python script.
- Make sure you have the Infineon TLx493D library installed in your Arduino IDE.
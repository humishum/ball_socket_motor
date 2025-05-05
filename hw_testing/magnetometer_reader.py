import serial as serials
from logging import Logger
from threading import Thread
import time
from queue import Queue
import numpy as np


class MagnetometerReader(Thread):
    def __init__(self, port, baudrate, logger: Logger, plot_data_queue: Queue, log_data_queue: Queue):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.logger = logger
        self.plot_data_queue = plot_data_queue
        self.log_data_queue = log_data_queue

        self.logger.info(f"Attempting to connect to {port} at {baudrate} baud...")
        self.ser = serials.Serial(port, baudrate, timeout=0)  # Non-blocking reads
        self.logger.info(f"Successfully connected to {port}")
        
        # Clear any startup messages
        self.ser.reset_input_buffer()
        logger.info(f"Initialized MagnetometerReader on {port} with baudrate {baudrate}")

        self.running = True

    def run(self):
        """Main thread loop"""
        buffer = ""
        while self.running:
            if self.ser.in_waiting:
                # Read all available bytes
                data = self.ser.read(self.ser.in_waiting).decode('utf-8')
                buffer += data
                
                # Process complete lines
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    
                    # Skip header lines
                    if any(line.startswith(x) for x in ["TLV493D", "Format:", "---"]):
                        continue
                    
                    try:
                        parsed_data = parse_data(line)
                        if not any(np.isnan(x) for x in parsed_data):
                            self.plot_data_queue.put(parsed_data)
                            self.log_data_queue.put(parsed_data)
                    except Exception as e:
                        self.logger.error(f"Error processing line: {e}")
            else:
                # Small sleep to prevent CPU spinning
                time.sleep(0.001)  # 1ms sleep when no data

    def stop(self):
        """Safely stop the thread and close the serial connection"""
        self.logger.info("Stopping magnetometer reader...")
        self.running = False
        self.join(timeout=1.0)
        if self.ser.is_open:
            self.ser.close()
            self.logger.info("Closed serial connection")


def parse_data(line):
    """Parse a line of CSV data from the Arduino."""
    try:
        parts = line.strip().split(",")
        if len(parts) == 6:
            timestamp = float(parts[0]) /1e6
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            strength = float(parts[4])
            temp = float(parts[5])
            return timestamp, x, y, z, strength, temp
    except (ValueError, IndexError) as e:
        print(f"Error parsing data: {e}")
        return np.nan, np.nan, np.nan, np.nan, np.nan

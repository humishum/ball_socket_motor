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
        self.ser = serials.Serial(port, baudrate, timeout=1)
        self.logger.info(f"Successfully connected to {port}")
        time.sleep(2)

        if self.ser.in_waiting > 100:  # If more than ~5 lines are waiting
            self.ser.reset_input_buffer()
            print("Buffer was getting full - cleared")
            time.sleep(0.01)  # Give a small pause to stabilize
        logger.info(
            f"Initialized MagnetometerReader on {port} with baudrate {baudrate}"
        )

        self.running = True

    def stop(self):
        """Safely stop the thread and close the serial connection"""
        self.logger.info("Stopping magnetometer reader...")
        self.running = False
        self.join(timeout=1.0)  # Wait for the thread to finish
        if self.ser.is_open:
            self.ser.close()
            self.logger.info("Closed serial connection")

    def run(self):
        """ run() is a method from Thread that needs to be overrided. Internally, 
        when start() is called on a thread, run() will be called"""
        # Try to read multiple lines if available to catch up
        max_lines_per_update = 10  # Increased from 3 to 10
        lines_read = 0
        while self.running:
            while self.ser.in_waiting and lines_read < max_lines_per_update:
                try:
                    line = self.ser.readline().decode("utf-8").strip()

                    # Skip header lines that don't contain data
                    if (
                        line.startswith("TLV493D")
                        or line.startswith("Format:")
                        or line.startswith("---")
                    ):
                        continue

                    data = parse_data(line)
                    # self.logger.info(f"Time:{time.perf_counter()} Data: {data}")
                    self.plot_data_queue.put(data)
                    self.log_data_queue.put(data)

                except Exception as e:
                    print(f"Error reading data: {e}")
                    break


def parse_data(line):
    """Parse a line of CSV data from the Arduino."""
    try:
        parts = line.strip().split(",")
        if len(parts) == 5:
            x = float(parts[0])
            y = float(parts[1])
            z = float(parts[2])
            strength = float(parts[3])
            temp = float(parts[4])
            return x, y, z, strength, temp
    except (ValueError, IndexError) as e:
        print(f"Error parsing data: {e}")
    return np.nan, np.nan, np.nan, np.nan, np.nan

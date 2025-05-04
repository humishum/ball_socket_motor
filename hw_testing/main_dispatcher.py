from hw_testing.magnetometer_reader import MagnetometerReader

from matplotlib.animation import FuncAnimation # Using matplotlib in main thread for now. can switch to pyqtgraph later if we want in a thread
import numpy as np
import matplotlib.pyplot as plt

import logging
from logging.handlers import RotatingFileHandler
import click 
import time 
from queue import Empty
from queue import Queue


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler('logs/magnetometer_reader.log', maxBytes=50000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


MAG_PORT = '/dev/cu.usbmodem1301' 
MAG_BAUD = 115200
EM_PORT = '/dev/cu.usbmodem1201'
EM_BAUD = 115200

test_data =  (1.0, 1.0, 1.0, 1.0, 1.0)


# Data buffer for plotting history
MAX_HISTORY = 100
x_history = np.zeros(MAX_HISTORY)
y_history = np.zeros(MAX_HISTORY)
z_history = np.zeros(MAX_HISTORY)
strength_history = np.zeros(MAX_HISTORY)
temp_history = np.zeros(MAX_HISTORY)
time_history = np.zeros(MAX_HISTORY)
initial_timestamp = None


@click.command()
@click.option("--plot", is_flag=True, help="Enable plotting")
@click.option("--log", is_flag=True, help="log to csv")
def main(plot, log):
    # later on we can make a broadcast system to keep queue update simpler in all threads
    plot_data_queue= Queue() 
    log_data_queue= Queue()

    handlers = [
        MagnetometerReader(MAG_PORT, MAG_BAUD, logger, plot_data_queue, log_data_queue)
    ]
    
    # if log: 
    #     handlers.append(LogHandler(logger))
    
    try:
        # Initialize handlers 
        for thread_handler in handlers: 
            thread_handler.start()
            
        # Keep the main thread running
        while True:
            time.sleep(0.1)  # Prevent CPU hogging

            if plot: 
                def update(frame):
                    # Process multiple items from queue if available
                    max_updates = 10
                    updates = 0
                    
                    while updates < max_updates:
                        try:
                            plot_data = plot_data_queue.get_nowait()
                            if plot_data is not Empty:
                                x, y, z, strength, temp = plot_data
                                # Update histories
                                global x_history, y_history, z_history, strength_history, temp_history, time_history, initial_timestamp
                                
                                current_time = time.time()
                                # Set initial timestamp if this is our first data point
                                if initial_timestamp is None:
                                    initial_timestamp = current_time

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
                                time_history[-1] = current_time - initial_timestamp  # Store relative time directly
                                
                                updates += 1
                        except Empty:
                            break
                    
                    if updates > 0:
                        # Find the last zero value from the end of the array
                        valid_data_end = np.where(time_history == 0)[0][-1] + 1 if np.any(time_history == 0) else 0
                        plot_slice = slice(valid_data_end, None)
                        
                        print(f"Time history last few values: {time_history[-5:]}")
                        print(f"Valid data starts at index: {valid_data_end}")

                        ax1 = ax[0]
                        ax1.clear()
                        ax1.set_title("Magnetic Field Vector")
                        ax1.set_xlabel("X (mT)")
                        ax1.set_ylabel("Y (mT)")
                        ax1.set_zlabel("Z (mT)")

                        # Plot the current vector
                        ax1.quiver(
                            0,
                            0,
                            0,
                            x_history[-1],
                            y_history[-1],
                            z_history[-1],
                            color="r",
                            arrow_length_ratio=0.1,
                        )
                        # Set equal aspect ratio and reasonable limits
                        max_val = max(abs(x_history[-1]), abs(y_history[-1]), abs(z_history[-1]), 0.1)
                        ax1.set_xlim([-max_val, max_val])
                        ax1.set_ylim([-max_val, max_val])
                        ax1.set_zlim([-max_val, max_val])

                        # Update field strength plot
                        ax2 = ax[1]
                        ax2.clear()
                        ax2.set_title("Field Strength Over Time")
                        ax2.set_xlabel("Time (s)")
                        ax2.set_ylabel("Field Strength (mT)")
                        ax2.plot(time_history[plot_slice], strength_history[plot_slice], "g-")

                        # Update XYZ components plot
                        ax3 = ax[2]
                        ax3.clear()
                        ax3.set_title("Field Components Over Time")
                        ax3.set_xlabel("Time (s)")
                        ax3.set_ylabel("Field (mT)")
                        ax3.plot(time_history[plot_slice], x_history[plot_slice], "r-", label="X")
                        ax3.plot(time_history[plot_slice], y_history[plot_slice], "g-", label="Y")
                        ax3.plot(time_history[plot_slice], z_history[plot_slice], "b-", label="Z")
                        ax3.legend()

                        # Update temperature plot
                        ax4 = ax[3]
                        ax4.clear()
                        ax4.set_title("Temperature Over Time")
                        ax4.set_xlabel("Time (s)")
                        ax4.set_ylabel("Temperature (°C)")
                        ax4.plot(time_history[plot_slice], temp_history[plot_slice], "m-")

                        # Adjust layout
                        plt.tight_layout()




                fig, ax = setup_plot()
                ani = FuncAnimation(fig, update, interval=50, save_count=100)
                plt.show()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        # Cleanup all handlers
        for thread_handler in handlers:
            try:
                thread_handler.stop()  # Assuming each handler has a stop method
                logger.info(f"Stopped handler: {thread_handler.__class__.__name__}")
            except Exception as e:
                logger.error(f"Error stopping handler {thread_handler.__class__.__name__}: {str(e)}")


def setup_plot():
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle("TLV493D Magnetometer Visualization", fontsize=16)

    # 3D vector plot
    ax1 = fig.add_subplot(2, 2, 1, projection="3d")
    ax1.set_title("Magnetic Field Vector")
    ax1.set_xlabel("X (mT)")
    ax1.set_ylabel("Y (mT)")
    ax1.set_zlabel("Z (mT)")
    ax1.set_box_aspect([1, 1, 1])

    # Field strength over time
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_title("Field Strength Over Time")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Field Strength (mT)")

    # XYZ field strength
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_title("Field Components Over Time")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Field (mT)")

    # Temperature
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_title("Temperature Over Time")
    ax4.set_xlabel("Time (s)")
    ax4.set_ylabel("Temperature (°C)")

    return fig, (ax1, ax2, ax3, ax4)

if __name__ == "__main__":
    logger.info("Starting main dispatcher...")
    main()

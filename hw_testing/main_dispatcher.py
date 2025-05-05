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
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'))
logger.addHandler(handler)


MAG_PORT = '/dev/cu.usbmodem11301' 
MAG_BAUD = 115200
EM_PORT = '/dev/cu.usbmodem1201'
EM_BAUD = 115200

test_data =  (1.0, 1.0, 1.0, 1.0, 1.0)


# Data buffer for plotting history
MAX_HISTORY = 1000
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
            time.sleep(0.01)  # Prevent CPU hogging

            if plot: 
                def update(frame):
                    global x_history, y_history, z_history, strength_history, temp_history, time_history, initial_timestamp
                    # Process multiple items from queue if available
                    max_updates = 100  # Reduced from 100 to avoid processing too many at once
                    updates = 0
                    
                    while updates < max_updates:
                        try:
                            plot_data = plot_data_queue.get_nowait()
                            if plot_data is not None:
                                timestamp, x, y, z, strength, temp = plot_data
                                
                                if initial_timestamp is None:
                                    logger.debug(f"Set Initial Timestamp: {timestamp} s")
                                    initial_timestamp = timestamp
                                
                                # Calculate time difference in seconds
                                time_diff = timestamp - initial_timestamp
                                
                                # Update histories (only roll once!)
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
                                time_history[-1] = time_diff
                                
                                updates += 1
                        except Empty:
                            break
                    
                    if updates > 0:
                        # Always show a fixed number of points
                        window_size = 200  # Adjust this to your preference
                        plot_slice = slice(-window_size, None)
                        
                        # Get the arrays for plotting
                        x_plot = x_history[plot_slice]
                        y_plot = y_history[plot_slice]
                        z_plot = z_history[plot_slice]
                        strength_plot = strength_history[plot_slice]
                        temp_plot = temp_history[plot_slice]
                        time_plot = time_history[plot_slice]
                        
                        # Now proceed with plotting using these arrays
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
                            x_plot[-1],
                            y_plot[-1],
                            z_plot[-1],
                            color="r",
                            arrow_length_ratio=0.1,
                        )
                        # Set equal aspect ratio and reasonable limits
                        max_val = max(abs(x_plot[-1]), abs(y_plot[-1]), abs(z_plot[-1]), 0.1)
                        ax1.set_xlim([-max_val, max_val])
                        ax1.set_ylim([-max_val, max_val])
                        ax1.set_zlim([-max_val, max_val])

                        # Update field strength plot
                        ax2 = ax[1]
                        ax2.clear()
                        ax2.set_title("Field Strength Over Time")
                        ax2.set_xlabel("Time (s)")
                        ax2.set_ylabel("Field Strength (mT)")
                        ax2.plot(time_plot, strength_plot, "g-")

                        # Update XYZ components plot
                        ax3 = ax[2]
                        ax3.clear()
                        ax3.set_title("Field Components Over Time")
                        ax3.set_xlabel("Time (s)")
                        ax3.set_ylabel("Field (mT)")
                        ax3.plot(time_plot, x_plot, "r-", label="X")
                        ax3.plot(time_plot, y_plot, "g-", label="Y")
                        ax3.plot(time_plot, z_plot, "b-", label="Z")
                        ax3.legend()

                        # Update FFT plot
                        ax4 = ax[3]
                        ax4.clear()
                        dt = np.mean(np.diff(time_plot))
                        fs = 1/dt  # Sampling frequency
                        ax4.set_title(f"Freq Domain(fs={fs:.2f} Hz)")
                        ax4.set_xlabel("Frequency (Hz)")
                        ax4.set_ylabel("Magnitude")
                        
                        # Calculate FFT for each component
                        n = len(time_plot)
                        # print(f"n: {n}")
                        freq = np.fft.fftfreq(n, dt)[:n//2]  # Only positive frequencies
                        
                        # Calculate and plot magnitude of FFT for each component
                        fft_x = np.abs(np.fft.fft(x_plot))[:n//2]
                        fft_y = np.abs(np.fft.fft(y_plot))[:n//2]
                        fft_z = np.abs(np.fft.fft(z_plot))[:n//2]
                        
                        ax4.plot(freq, fft_x, 'r-', label='X')
                        ax4.plot(freq, fft_y, 'g-', label='Y')
                        ax4.plot(freq, fft_z, 'b-', label='Z')
                        ax4.legend()
                        ax4.grid(True)

                        # Adjust layout
                        plt.tight_layout()

                fig, ax = setup_plot()
                ani = FuncAnimation(fig, update, interval=20, save_count=100)
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

    # Frequency domain
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_title("FFT")
    

    return fig, (ax1, ax2, ax3, ax4)

if __name__ == "__main__":
    logger.info("Starting main dispatcher...")
    main()

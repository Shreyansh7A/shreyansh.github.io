import csv
from datetime import datetime
from scapy.all import *
import time
import asyncio
from sense_hat import SenseHat
import statistics
sense = SenseHat()
import pandas as pd
import matplotlib.pyplot as plt
"""
Run monitor_mode.sh first to set up the network adapter to monitor mode and to
set the interface to the right channel.
To get RSSI values, we need the MAC Address of the connection 
of the device sending the packets.
"""

# Variables to be modified
dev_mac = "e4:5f:01:d4:a0:6b"  # Change to a hidden camera's MAC"
iface_n = "wlan1"  # Interface for network adapter (do not modify)
duration = 20  # Number of seconds to sniff for
rssi_file_name = "rssi_realtime.csv"  # Output RSSI CSV file name
joystick_file_name = "joystick.csv"  # Output joystick CSV file name

q_rssi = []  # Queue for RSSI values


def create_rssi_file():
    """Create and prepare a file for RSSI values"""
    header = ["timestamp", "dest", "src", "rssi"]
    with open(rssi_file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def create_joystick_file():
    """Create and prepare a file for joystick input"""
    header = ["timestamp", "key"]
    with open(joystick_file_name, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def write_to_file(file_name, data):
    """Write data to a file"""
    with open(file_name, "a", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(data)

rssi_data = {
    "up": [],
    "right": [],
    "down": [],
    "left": []
}
directions = ["up", "right", "down", "left"]
current_direction = None
collecting_data = False

def captured_packet_callback(pkt):
    global current_direction
    global collecting_data

    try:
        if(pkt.addr2 == dev_mac and pkt.dBm_AntSignal):
            if(current_direction and collecting_data):
                print(pkt.dBm_AntSignal)
                rssi_data[current_direction].append(pkt.dBm_AntSignal)
    except AttributeError:
        return  # Ignore packet without RSSI field


def prompt_user_to_turn(direction):
    """Display an arrow in the specified direction."""
    sense.clear()  # Clear the display
    if direction == "up":
        sense.set_pixel(3, 0, (255, 255, 255)) 
    elif direction == "right":
        sense.set_pixel(7, 3, (255, 255, 255)) 
    elif direction == "down":
        sense.set_pixel(3, 7, (255, 255, 255)) 
    elif direction == "left":
        sense.set_pixel(0, 3, (255, 255, 255)) 
    global collecting_data
    collecting_data = True
    #set true so it can go in cap packet loop and add to list
    time.sleep(4) 
    collecting_data = False

def display_best_direction():
    """Calculate averages and display the direction with the highest RSSI."""
    averages = {}
    for direction in directions:
        if rssi_data[direction]:
            print(rssi_data[direction])
            averages[direction] = statistics.mean(rssi_data[direction])
        else:
            averages[direction] = float('-inf')  # No data case

    best_direction = max(averages, key=averages.get)
    sense.clear()  # Clear the display for the final arrow
    if best_direction == "up":
        sense.set_pixel(3, 0, (255, 255, 255)) 
    elif best_direction == "right":
        sense.set_pixel(7, 3, (255, 255, 255)) 
    elif best_direction == "down":
        sense.set_pixel(3, 7, (255, 255, 255)) 
    elif best_direction == "left":
        sense.set_pixel(0, 3, (255, 255, 255)) 


async def record_joystick() -> str:
    """Record joystick input to CSV file"""
    # @TODO: Get joystick input, if you want it
    for event in sense.stick.get_events():
        if event.direction == 'middle' and event.action == 'pressed':
            return event.direction
    return ""


async def main_loop():
    """Main loop to record joystick input and IMU data (in Lab 3)"""
    start = time.time()
    sense.clear()
    
    while (time.time() - start) < duration:
        # Record joystick input
        key_pressed = await record_joystick()
        if key_pressed:
            # Write (timestamp, key) to the CSV file
            write_to_file(joystick_file_name, [time.time(), key_pressed])

        # await display_rssi()


if __name__ == "__main__":
    create_rssi_file()
    create_joystick_file()

    start_date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S.%f") #Get current date and time
    print("Start Time: ", start_date_time)

    t = AsyncSniffer(iface=iface_n, prn=captured_packet_callback, store=0)
    t.daemon = True
    t.start()
    for direction in directions:
        prompt_user_to_turn(direction)

    display_best_direction()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())
    loop.close()
    
    df_rssi = pd.read_csv(rssi_file_name)
    df_joystick = pd.read_csv(joystick_file_name)
    plt.plot(df_rssi['timestamp'], df_rssi['rssi'], label = 'rssi')
    #plt.plot(df_joystick['timestamp'],df_joystick['key'], label="keypress")
    #plt.axvline(x = df_joystick['timestamp'].iloc[0], color = 'red', linestyle = '--', label = 'keypress')
    plt.legend(loc="upper left")
    plt.ylabel("rssi")
    plt.xlabel("timestamp")
    plt.show()
    
    
    
    
    
    
    
    # @TODO: Start IMU data collection loop here
    ## Hint: in the loop, pop latest value from RSSI queue and put in CSV file if available, else write None or -100
    ### Hint: Use write_to_file(file_name, data) function to write a list of values to the CSV file




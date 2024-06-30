import os
import threading
import time
import numpy as np
from pyfirmata import ArduinoMega, util

# Mock Board Initializations
board = ArduinoMega('/dev/tty.usbmodem14401')
# it = util.Iterator(board)
# it.start()
FSRpins = [board.get_pin(f'a:{i}:i') for i in range(10)]
print("FSRread:", FSRpins[0].read())
OngoingSensorThread = True

# os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Functions --------------------------------------------------------------
def NormalOperation():
    board.digital[2].write(1)
    board.digital[3].write(1)
    board.digital[4].write(1)
    board.digital[5].write(1)
    board.digital[6].write(0)
    board.digital[7].write(0)
    board.digital[8].write(1)
    board.digital[9].write(1)
    board.digital[10].write(1)
    board.digital[11].write(0)
    print("Normal operation.")

NormalOperation()


# Harder task in Cooling Mode (Cut wire from Contactor to Duplex) (Blue Bulb and Fan OFF)
def NoPower2Duplex():
    board.digital[11].write(1)
    print("No power to duplex.")

# Harder task in Heating Mode (Cut DPDT) (Red Bulb and Fan OFF)
def CutDPDT2Heater():
    board.digital[3].write(0)
    # board.digital[8].write(0)
    print("No power from DPDT.")

# Easier task 1 in Cooling Mode
def CondenserFanOFF():
    board.digital[4].write(0)
    print("Condenser fan off.")

# Easier task 2 in Cooling Mode
def CompressorOFF():
    board.digital[9].write(0)
    print("Compressor off.")

# Functions for FSRs
SensorData = {i: [] for i in range(10)} # assuming 10 sensors

def readSensors():
    # Slight pause to allow the Arduino to initialize all the pins
    time.sleep(1)

    while OngoingSensorThread:
        for i, FSRpin in enumerate(FSRpins):
            # Read the value from the FSR
            FSRreading = FSRpin.read()
            if FSRreading is None:
                continue

            print(f"Analog reading FSR {i} = {FSRreading}")

            # Convert the reading to millivolts
            FSRvoltage = FSRreading * 5000  # 5V reference
            print(f"Voltage reading in mV FSR {i} = {FSRvoltage}")

            if FSRvoltage == 0:
                FSRforces = 0
                print(f"No pressure on FSR {i}")
            else:
                FSRresistances = 5000 - FSRvoltage
                FSRresistances *= 10000  # 10K resistor
                FSRresistances /= FSRvoltage
                print(f"FSR resistance in ohms FSR {i} = {FSRresistances}")
                FSRconductances = 1000000  # we measure in micromhos so 
                FSRconductances /= FSRresistances
                print(f"Conductance in microMhos FSR {i} = {FSRconductances}")
                if FSRconductances <= 1000:
                    FSRforces = FSRconductances / 80
                    print(f"Force in Newtons FSR {i} = {FSRforces}")
                else:
                    FSRforces = FSRconductances - 1000
                    FSRforces /= 30
                    print(f"Force in Newtons FSR {i} = {FSRforces}")
            print("--------------------")
            # append new timestamp and force reading to the list for sensor i
            SensorData[i].append((time.time(), FSRforces)) 

        # Wait a skosh before the next reading
        time.sleep(0.5)

    return SensorData


def identify_components_based_on_force_changes(differences, z_threshold=2):
    componentsDepressed = []

    for i in differences:
        # skip if no differences recorded
        if not differences[i]:  
            continue
            
        mean = np.mean(differences[i])
        std_dev = np.std(differences[i])

        # A component is identified as pressed if any force change is greater than mean + z_threshold * std_dev
        if any(diff > mean + z_threshold * std_dev for diff in differences[i]):
            componentsDepressed.append(i)
            
    return componentsDepressed


def computeDifferences(time_window=3):
    differences = {}

    for i in SensorData:
        readings = SensorData[i]
        # ensure readings are in chronological order
        readings.sort()

        # Only consider readings within the last 3 seconds
        currentTime = time.time()
        recentReadings = [r for r in readings if currentTime - r[0] <= time_window]
        
        diffs = []
        for j in range(1, len(recentReadings)):
            # get all readings that are within time_window seconds before the current reading
            previousReadings = [r for r in recentReadings if 0 < recentReadings[j][0] - r[0] <= time_window]
            if previousReadings:
                # compute difference between the current reading and the average of previous readings
                diff = recentReadings[j][1] - sum(r[1] for r in previousReadings) / len(previousReadings)
                diffs.append(diff)

        differences[i] = diffs

    print("Differences:", differences)

    componentsDepressed = identify_components_based_on_force_changes(differences)
    print(f"Components pressed: {componentsDepressed}")

    # Queue the next computation if the sensor thread is still running
    if OngoingSensorThread:  
        threading.Timer(time_window, computeDifferences).start()

    return differences

# Create a thread that runs readSensors
SensorThread = threading.Thread(target=readSensors)

# Start the thread
SensorThread.start()

# Schedule the first computation of differences
threading.Timer(3, computeDifferences).start()

# CutDPDT2Heater()
# NoPower2Duplex()
# CompressorOFF()
# CondenserFanOFF()
NormalOperation()
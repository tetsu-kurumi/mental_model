import tkinter as tk, tkinter.messagebox as messagebox
from pyfirmata import ArduinoMega, util
import time
import threading
import numpy as np

# Initializations
board = ArduinoMega('/dev/tty.usbmodem114401')
it = util.Iterator(board)
it.start()
FSRpins = [board.get_pin(f'a:{i}:i') for i in range(10)]
OngoingSensorThread = True


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

NormalOperation()

def REDbulbON():
    board.digital[10].write(1)
def REDbulbOFF():
    board.digital[10].write(0)

def BLOWERfanON():
    board.digital[8].write(1)
def BLOWERfanOFF():
    board.digital[8].write(0)

def BLUEfanON():
    board.digital[4].write(1)
def BLUEfanOFF():
    board.digital[4].write(0)

def BLUEbulbON():
    board.digital[9].write(1)
def BLUEbulbOFF():
    board.digital[9].write(0)

# Mode: F-AUTO/S-OFF…(F~A) & (S~O)
def SCENARIO1BLOWERfanON():
    board.digital[11].write(1)
def SCENARIO1BLOWERfanOFF():
    board.digital[11].write(0)

# Mode: F-AUTO/S-HEAT…(F~A) & (S~H)
def SCENARIO2HEATfanLightON():
    board.digital[2].write(1)
    BLOWERfanON()
def SCENARIO2HEATfanLightOFF():
    board.digital[2].write(0)
    BLOWERfanOFF()

# Mode: F-AUTO/S-HEAT…(F~A) & (S~H)
def SCENARIO3HEATfanLightON():
    board.digital[3].write(1)
    BLOWERfanON()
def SCENARIO3HEATfanLightOFF():
    board.digital[3].write(0)
    BLOWERfanOFF()

# Mode: F-AUTO/S-COOL…(F~A) & (S~C)
def SCENARIO4COOLfanON():
    BLUEfanON()
def SCENARIO4COOLfanOFF():
    BLUEfanOFF()

# Mode: F-AUTO/S-COOL…(F~A) & (S~C)
def SCENARIO5COOLfanLightON():
    BLUEfanON()
    BLUEbulbON()
def SCENARIO5COOLfanLightOFF():
    BLUEfanOFF()
    BLUEbulbOFF()

# Mode: F-AUTO/S-COOL…(F~A) & (S~C)
def SCENARIO6closedCB():
    board.digital[6].write(1)
def SCENARIO6openCB():
    board.digital[6].write(0)

# (F~A) & ((S~O) or (S~H))
def SCENARIO7closedCB():
    board.digital[7].write(1)
def SCENARIO7openCB():
    board.digital[7].write(0)

# Mode: (F-A) & (S~H)
def SCENARIO8redBulbON():
    REDbulbON()
def SCENARIO8redBulbOFF():
    REDbulbOFF()

# Mode: F-AUTO/S-HEAT…(F-A) & (S~H)
def SCENARIO9blowerFanON():
    BLOWERfanON()
def SCENARIO9blowerFanOFF():
    BLOWERfanOFF()

def SCENARIO10blueFanON():
    BLUEfanON()
def SCENARIO10blueFanOFF():
    BLUEfanOFF()

#-----------------------------------------
def aboutMsg():
    messagebox.showinfo("About",
    "Scenario Control Interface\nNovember 2023")
#------------------------------------------------------------------
def quitApp():
    global OngoingSensorThread
    OngoingSensorThread = False
    board.exit()
    win.destroy()


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



# GUI design -------------------------------------------------------------
win = tk.Tk()
win.title("Scenario Control Interface")
win.minsize(390, 390)

# Button widgets
label = tk.Label(win, text="Scenario 1: Blower Fan ON")
label.grid(column=1, row=1)

ONbtn = tk.Button(win, bg='green', bd=4, text="BLOWER FAN ON", command=SCENARIO1BLOWERfanON)
ONbtn.grid(column=1, row=2)
OFFbtn = tk.Button(win, bg='red', bd=4, text="BLOWER FAN OFF", command=SCENARIO1BLOWERfanOFF)
OFFbtn.grid(column=2, row=2)


label = tk.Label(win, text="Scenario 2: No 'RED' Lamp nor Fan")
label.grid(column=1, row=3)

ONbtn = tk.Button(win, bg='green', bd=4, text="Red lamp & Fan ON", command=SCENARIO2HEATfanLightON)
ONbtn.grid(column=1, row=4)
OFFbtn = tk.Button(win, bg='red', bd=4, text="Red lamp & Fan OFF", command=SCENARIO2HEATfanLightOFF)
OFFbtn.grid(column=2, row=4)


label = tk.Label(win, text="Scenario 3: No 'RED' Lamp nor Fan")
label.grid(column=1, row=9)
# Different fault thrown than scenario 2
ONbtn = tk.Button(win, bg='green', bd=4, text="Red light & Fan ON", command=SCENARIO3HEATfanLightON)
ONbtn.grid(column=1, row=10)
OFFbtn = tk.Button(win, bg='red', bd=4, text="Red lamp & Fan OFF", command=SCENARIO3HEATfanLightOFF)
OFFbtn.grid(column=2, row=10)


label = tk.Label(win, text="Scenario 4: 'BLUE' Fan Stops")
label.grid(column=1, row=11)

ONbtn = tk.Button(win, bg='green', bd=4, text="'BLUE' Fan Spins", command=SCENARIO4COOLfanON)
ONbtn.grid(column=1, row=12)
OFFbtn = tk.Button(win, bg='red', bd=4, text="'BLUE' Fan Stops", command=SCENARIO4COOLfanOFF)
OFFbtn.grid(column=2, row=12)


label = tk.Label(win, text="Scenario 5: 'BLUE' Lamp and Fan Stop")
label.grid(column=1, row=13)

ONbtn = tk.Button(win, bg='green', bd=4, text="'BLUE' Fan & lamp Stop", command=SCENARIO5COOLfanLightON)
ONbtn.grid(column=1, row=14)
OFFbtn = tk.Button(win, bg='red', bd=4, text="'BLUE' Fan & Lamp Stop", command=SCENARIO5COOLfanLightOFF)
OFFbtn.grid(column=2, row=14)


label = tk.Label(win, text="Scenario 6: Circuit Breaker Trips")
label.grid(column=1, row=15)

ONbtn = tk.Button(win, bg='green', bd=4, text="Closed CB", command=SCENARIO6closedCB)
ONbtn.grid(column=1, row=16)
OFFbtn = tk.Button(win, bg='red', bd=4, text="Open CB", command=SCENARIO6openCB)
OFFbtn.grid(column=2, row=16)


label = tk.Label(win, text="Scenario 7: Circuit Breaker Trips")
label.grid(column=1, row=17)

ONbtn = tk.Button(win, bg='green', bd=4, text="Closed CB", command=SCENARIO7closedCB)
ONbtn.grid(column=1, row=18)
OFFbtn = tk.Button(win, bg='red', bd=4, text="Open CB", command=SCENARIO7openCB)
OFFbtn.grid(column=2, row=18)


label = tk.Label(win, text="Scenario 8: RED Bulb fault")
label.grid(column=1, row=19)

ONbtn = tk.Button(win, bg='green', bd=4, text="RED Bulb ON", command=SCENARIO8redBulbON)
ONbtn.grid(column=1, row=20)
OFFbtn = tk.Button(win, bg='red', bd=4, text="RED Bulb OFF", command=SCENARIO8redBulbOFF)
OFFbtn.grid(column=2, row=20)


label = tk.Label(win, text="Scenario 9: BLOWER Fan fault")
label.grid(column=1, row=21)

ONbtn = tk.Button(win, bg='green', bd=4, text="BLOWER Fan ON", command=SCENARIO9blowerFanON)
ONbtn.grid(column=1, row=22)
OFFbtn = tk.Button(win, bg='red', bd=4, text="BLOWER Fan OFF", command=SCENARIO9blowerFanOFF)
OFFbtn.grid(column=2, row=22)


label = tk.Label(win, text="Scenario 10: BLUE Fan fault")
label.grid(column=1, row=23)

ONbtn = tk.Button(win, bg='green', bd=4, text="BLUE Fan ON", command=SCENARIO10blueFanON)
ONbtn.grid(column=1, row=24)
OFFbtn = tk.Button(win, bg='red', bd=4, text="BLUE Fan OFF", command=SCENARIO10blueFanOFF)
OFFbtn.grid(column=2, row=24)


label = tk.Label(win, text="Set normal operations")
label.grid(column=4, row=2)

ONbtn = tk.Button(win, bg='green', bd=4, text="Normal Operation", command=NormalOperation)
ONbtn.grid(column=4, row=3)


aboutBtn = tk.Button(win, bg='yellow', text="About", command=aboutMsg)
aboutBtn.grid(column=4, row=1)
quitBtn = tk.Button(win, bg='red', text="QUIT", command=quitApp)
quitBtn.grid(column=4, row=26)

win.mainloop()
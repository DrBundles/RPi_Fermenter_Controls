#!/usr/bin/env python3

# For debugging
import pdb
#pdb.set_trace()

# Imports for plotting
import matplotlib
matplotlib.use('TkAgg') #Needed to make matplotlib work in unix / anaconda virtual env
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import pyplot as plt
#import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Imports for UI
import tkinter as tk
import numpy as np

# make the masterUI UI
masterUI = tk.Tk()
masterUI.title("Fermenter Controls")

f = plt.figure(figsize=(2.7,2), dpi=120)
subplotTop = 111# 211

# -----------------------------------------------------------
# Import DS18B20 python library and setup sensors
# -----------------------------------------------------------
from w1thermsensor import W1ThermSensor


# -----------------------------------------------------------
# Import RPi GPIO library
# -----------------------------------------------------------
import RPi.GPIO as GPIO
import time # needed?
GPIO.setmode(GPIO.BCM)



class PlotData():
  """Store and format data for subsequent plotting
  """
  def __init__(self, plot_fig, subplot_axes):
    """Constructor for PlotData Class

    Args:
      plot_fig (matplotlib fiure): Figure which will eventuall plot the data
      subplot_axes (int): Integer defining subplot
    """

    self._fig = plot_fig
    self._subplot = subplot_axes
    self._dataNew = 0
    self._dataTest = [0] * 100
    self._setpoint = 19
    self._dataSetpoint  = [self._setpoint] * 100
    self._ymin = 0
    self._ymax = 50

    plt.subplot(self._subplot)
    self._lineDataTest = plt.plot(self._dataTest, 'rs', label='Plot Data')
    self._lineDataSetpoint  = plt.plot(self._dataSetpoint, 'bs', label='Setpoint')
    plt.ylim([self._ymin, self._ymax])
    #plt.legend(loc='upper left')

  def updatePlotVals(self):
    """Update plot
    """
    plt.subplot(self._subplot)
    #self._dataTest.append(float(self._dataNew[0])) # Add new data to end of existing data array
    self._dataTest.append(float(self._dataNew)) # Add new data to end of existing data array
    del self._dataTest[0] # Drop the first array element
    # Build setpoint line data as a straight line
    self._dataSetpoint  = [self._setpoint] * 100
    # Plot data
    self._ymin = float(min(self._dataTest+self._dataSetpoint)-10)
    self._ymax = float(max(self._dataTest+self._dataSetpoint)+10)
    plt.ylim([self._ymin, self._ymax])
    self._lineDataTest[0].set_xdata(np.arange(len(self._dataTest)))
    self._lineDataTest[0].set_ydata(self._dataTest)
    self._lineDataSetpoint[0].set_xdata(np.arange(len(self._dataSetpoint)))
    self._lineDataSetpoint[0].set_ydata(self._dataSetpoint)
    #print(self._dataSetpoint)
    #pdb.set_trace()

  @property
  def setpoint(self):
    return self._setpoint

  @setpoint.setter
  def setpoint(self, newsetpoint):
    #if type(a) is float:
    #  print("Change setpoint")
    self._setpoint = newsetpoint
    self.dataSetpoint = [self._setpoint] * 100
    #  self._dataSetpoint  = [self._setpoint] * 100



# ------------------------------------------
# Code for Temperature Control
# ------------------------------------------
class TemperatureControl():
  """Temperature Control class

  """
  def __init__(self, initTemp, lowTrigger = 2, highTrigger = 2, lowOffset = 0.2, highOffset = 0.2):
    """Constructor for PlotData Class

    Args:
      initTemp (float): Initial temperature value
      lowTrigger (float): Low temperature offset below which system heats
      highTrigger (float): High temperature offset above which system cools
      lowOffset (float): Low temperature hysteresis offset below which system goes to standby
      highOffset (float): High temperature hysteresis offset above which system goes to standby
      lowTrigger (float): 
    """

    self._tempSetpoint = initTemp
    self._lowTrigger = lowTrigger       #Temperature offset needed to turn on heater
    self._highTrigger = highTrigger     #Temperature offset needed to turn on cooler
    self._lowOffset = lowOffset         #Temperature overshoot of cooling
    self._highOffset = highOffset       #Temperature overshoot of heating
    self._tempBuffer = np.zeros(10)     #Ring buffer to hold temperature measurements
    self._tempBuffer.fill(self._tempSetpoint)
    self._mean_temp = self._tempSetpoint #Start with mean temp equal to initial temp
    self._heat_cool_FLAG = 1            #0: Cooling, 1: Heating
    # Setup temp sensors
    self._sensor = self.setup_temp_sensors()
    # Setup GPIO
    self._heatingpin = 23               #Heating relay pin on gpio BCM-23, wiringPi-4
    self._coolingpin = 24               #Cooling relay pin on gpio BCM-24, wiringPi-5
    #pdb.set_trace()
    GPIO.setup(self._coolingpin, GPIO.OUT) #Cooling pin set to output
    GPIO.setup(self._heatingpin, GPIO.OUT) #Heating pin set to output
    self.standby_mode()

  @property
  def tempSetpoint(self):
    return self._tempSetpoint

  @tempSetpoint.setter
  def tempSetpoint(self, newsetpoint):
    self._tempSetpoint = newsetpoint

  def setup_temp_sensors(self):
    # Get ID of DS18B20 sensor(s)
    THERM_ID = W1ThermSensor.get_available_sensors([W1ThermSensor.THERM_SENSOR_DS18B20])[0].id
    # Create a W1ThermSensor object
    sensor = W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, THERM_ID)
    # Get temperatures in Celsius:   sensor.get_temperature()
    # Get temperatures in Farenheit: sensor.get_temperature(W1ThermSensor.DEGREES_F)
    return sensor
  
  def standby_mode(self):
    # Turn both heating and cooling off
    GPIO.output(self._coolingpin, GPIO.LOW)
    GPIO.output(self._heatingpin, GPIO.LOW)
    self._heat_cool_FLAG = 'standby'

  def heat_on(self):
    # Turn off cooler
    # Turn on heater
    GPIO.output(self._coolingpin, GPIO.LOW)
    GPIO.output(self._heatingpin, GPIO.HIGH)
    self._heat_cool_FLAG = 'heating'

  def cool_on(self):
    # Turn on cooler
    # Turn off heater
    GPIO.output(self._coolingpin, GPIO.HIGH)
    GPIO.output(self._heatingpin, GPIO.LOW)
    self._heat_cool_FLAG = 'cooling'

  def calc_mean_temp(self):
    self._mean_temp = np.mean(self._tempBuffer)

  def update_temp(self):
    # Get temperature value
    tempVal = self._sensor.get_temperature()
    # Shift temperature buffer of index 9 is not index 0 
    self._tempBuffer = np.roll(self._tempBuffer, 1)
    # Push temperature value into ring buffer
    self._tempBuffer[0] = tempVal

  def get_mean_temp(self):
    # Update the temperature buffer, calc and return the average
    self.update_temp()
    self.calc_mean_temp()
    return self._mean_temp

  def heat_cool_logic(self):
    # Update the temperature 
    # Check if the system is in a state that requires heating, cooling or standby
    if self._mean_temp <= self._tempSetpoint - self._lowTrigger:
      # Turn on Heater
      self.heat_on()
      heatOnOff.set('heat')
    elif self._mean_temp >= self._tempSetpoint + self._highTrigger:
      # Turn on Cooler
      self.cool_on()
      heatOnOff.set('cool')
    elif self._mean_temp <= self._tempSetpoint - self._lowOffset and self._heat_cool_FLAG is 'cooling' :
      # Temperature has cooled to a point lower to the setpoint minus the offset
      # Place system into standby mode
      self.standby_mode()
      heatOnOff.set('hold')
    elif self._mean_temp >= self._tempSetpoint + self._highOffset and self._heat_cool_FLAG is 'heating' :
      # Temperature has heated to a point higher to the setpoint plus the offset
      # Place system into standby mode
      self.standby_mode()
      heatOnOff.set('hold')
    else:
      pass

  def updatePlotVals(self):
    """Update plot
    """
    self._dataTest.append(float(self._dataNew)) # Add new data to end of existing data array
    testDataPlot.setpoint=float(temperatureSP.get())



# ------------------------------------------
# Code to animate plot
# ------------------------------------------
def AnimatePlot(frameNum):
  """Update data in PlotData objects and draw plot

  AnimatePlot runs in the masterUI.mainloop() method. The interval for running the AnimatePlot method
  is set in the call "ani = animation.FuncAnimation(f, AnimatePlot, interval=1000)"

  Args:
    frameNum (automatically assigned by mainloop method)
  """
  #import random
  #testDataPlot.dataNew = [random.gauss(15, 1.4)]
  #testDataPlot.dataNew = [random.gauss(float(temperatureSP.get()), 1.4)]

  # Get temperature value
  #tempVal = tempController.sensor.get_temperature()
  tempVal = tempController.get_mean_temp()

  # Run logic to control heater / cooler
  tempController.heat_cool_logic()

  # Update temperature ring buffers
  #pid.update(tempVal)


  testDataPlot._dataNew = tempVal
  testDataPlot.updatePlotVals()
  plt.draw()

def updateTempSetpoint(newSetpoint):
  # Update setpoint values for both the controller and plot objects
  tempController.tempSetpoint=float(temperatureSP.get())
  testDataPlot.setpoint=float(temperatureSP.get())


def increaseTens():
  numData = temperatureSP.get()
  incData = str(float(numData)+10)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def increaseOnes():
  numData = temperatureSP.get()
  incData = str(float(numData)+1)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def increasePointOnes():
  numData = temperatureSP.get()
  incData = str(float(numData)+0.1)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def decreaseTens():
  numData = temperatureSP.get()
  incData = str(float(numData)-10)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def decreaseOnes():
  numData = temperatureSP.get()
  incData = str(float(numData)-1)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def decreasePointOnes():
  numData = temperatureSP.get()
  incData = str(float(numData)-0.1)
  temperatureSP.delete(0, "end")
  temperatureSP.insert(0, incData)
  updateTempSetpoint(float(temperatureSP.get()))

def stopProgram():
  masterUI.destroy()
  exit()

# ----------------------------------------------------
# >>------------->> UI CANVAS >>-------------------->>
# ----------------------------------------------------
# Region to draw the plots
canvas = FigureCanvasTkAgg(f, master=masterUI)
canvas.get_tk_widget().grid(row=1, column=1, columnspan=2, rowspan=10)
# canvas.show()

# ----------------------------------------------------
# >>--------->> LABELS, SLIDERS, BUTTONS >>--------->>
# ----------------------------------------------------
tk.Label(masterUI, text="Plot Rate Control").grid(row=1, column=3, columnspan=3)

temperatureSP = tk.Entry(masterUI)
temperatureSP.insert(0, '20')
#temperatureSP.bind('<Return>', lambda event: setPlotRateSlider())
temperatureSP.grid(row=2,column=3, columnspan=3)

tensButtonInc = tk.Button(masterUI, text='+10', width=4, command=increaseTens)
tensButtonInc.grid(row=3, column=3)

tensButtonDec = tk.Button(masterUI, text='-10', width=4, command=decreaseTens)
tensButtonDec.grid(row=4, column=3)

onesButtonInc = tk.Button(masterUI, text='+1', width=4, command=increaseOnes)
onesButtonInc.grid(row=3, column=4)

onesButtonDec = tk.Button(masterUI, text='-1', width=4, command=decreaseOnes)
onesButtonDec.grid(row=4, column=4)

pointOnesButtonInc = tk.Button(masterUI, text='+0.1', width=4, command=increasePointOnes)
pointOnesButtonInc.grid(row=3, column=5)

pointOnesButtonDec = tk.Button(masterUI, text='-0.1', width=4, command=decreasePointOnes)
pointOnesButtonDec.grid(row=4, column=5)

heatOnOff = tk.StringVar()
heatOnOff.set('hold')
heatRadiobuttonHeat = tk.Radiobutton(masterUI, text="Heat", value='heat', variable=heatOnOff)
heatRadiobuttonCool = tk.Radiobutton(masterUI, text="Cool", value='cool', variable=heatOnOff)
heatRadiobuttonHold = tk.Radiobutton(masterUI, text="Hold", value='hold', variable=heatOnOff)
heatRadiobuttonHeat.grid(row=6, column=3)
heatRadiobuttonCool.grid(row=7, column=3)
heatRadiobuttonHold.grid(row=8, column=3)

stopButton = tk.Button(masterUI, text="Stop", command=stopProgram)
stopButton.grid(row=10, column=3, columnspan=3)

# ----------------------------------------------------
# >>--------->> MAIN PLOTTING AREA >>--------------->>
# ----------------------------------------------------
# Create plot objects to hold data and manage plotting functions
testDataPlot = PlotData(f, subplotTop)

#tempController = TemperatureControl( float( temperatureSP.get() ) )
tempController = TemperatureControl(21)

ani = animation.FuncAnimation(f, AnimatePlot, interval=1000)

masterUI.mainloop()

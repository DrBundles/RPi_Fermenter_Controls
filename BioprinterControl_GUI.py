#/usr/bin/python3

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backend_bases import key_press_handler

import tkinter as tk
from tkinter import ttk

import serial
import numpy as np
from g_code_generator import gen_gcode_cube

# Start Serial
# ser = serial.Serial('/dev/cu.usbmodemfa121', 9600)
# serPeltier = serial.Serial('/dev/cu.usbmodemfd131', 9600)
ser = serial.Serial('/dev/ttyACM1', 9600)
serPeltier = serial.Serial('/dev/ttyACM2', 9600)

counter = 0
def counter_label(label):
  def count():
    global counter
    counter += 1
    label.config(text=str(counter))
    label.after(1000, count)

counter = 0
def counter_label(label):
  def count():
    global counter
    counter += 1
    label.config(text=str(counter))
    label.after(1000, count)
  count()

root = tk.Tk()
root.title("Bioprinter Controls")

f = plt.figure(figsize=(5,5), dpi=100)
subplotTop    = 211
subplotBottom = 212

'''
class PlotFrame():
  def __init__(self):
    plt.subplot(211)
    self.lineSyringe, = self.axes.plot(self.dataSyringe, 'rs', label='Syringe Temp')
    self.lineTube,    = self.axes.plot(self.dataTube,    'bs', label='Tube Temp')
    self.lineNeedle,  = self.axes.plot(self.dataNeedle,  'gs', label='Needle Temp')
    self.plt.ylim([20,45])
    self.plt.legend(loc='upper left')
'''

class PlotData():

  def __init__(self,plot_fig, subplot_axes):
    self.fig = plot_fig
    self.subplot = subplot_axes
    self.data = [0,0,0]
    self.dataSyringe = [0] * 60 * 3
    self.dataTube    = [0] * 60 * 3
    self.dataNeedle  = [0] * 60 * 3
    self.ymin = 0
    self.ymax = 45

    plt.subplot(self.subplot)
    self.lineSyringe, = plt.plot(self.dataSyringe, 'rs', label='Syringe Temp')
    self.lineTube,    = plt.plot(self.dataTube,    'bs', label='Tube Temp')
    self.lineNeedle,  = plt.plot(self.dataNeedle,  'gs', label='Needle Temp')
    plt.ylim([self.ymin,self.ymax])
    plt.legend(loc='upper left')
 
  def updatePlotVals(self):
    # Update tempData values
    plt.subplot(self.subplot)
    self.dataSyringe.append(float(self.data[0]))
    del self.dataSyringe[0]
    self.dataTube.append(float(self.data[1]))
    del self.dataTube[0]
    self.dataNeedle.append(float(self.data[2]))
    del self.dataNeedle[0]
    ymin = float(min(self.dataSyringe+self.dataTube+self.dataNeedle))-10
    ymax = float(max(self.dataSyringe+self.dataTube+self.dataNeedle))+10
    #plt.ylim([ymin,ymax])
    plt.ylim([self.ymin,self.ymax])
    self.lineSyringe.set_xdata(np.arange(len(self.dataSyringe)))
    self.lineSyringe.set_ydata(self.dataSyringe)  # update the data
    self.lineTube.set_xdata(np.arange(len(self.dataTube)))
    self.lineTube.set_ydata(self.dataTube)  # update the data
    self.lineNeedle.set_xdata(np.arange(len(self.dataNeedle)))
    self.lineNeedle.set_ydata(self.dataNeedle)  # update the data
    #print 'The value of self.dataSyringe[end] is: ' + repr(self.dataSyringe[-1])
    #print 'The value of self.dataTube[end] is: ' + repr(self.dataTube[-1])
    #print 'The value of self.dataNeedle[end] is: ' + repr(self.dataNeedle[-1])




# Code to draw the plot
#def animatePlot(i, ser):
def animatePlot(frameNum):

  # If the serial line is recognized as valid, update plot values and redraw plot
  serData = ser.readline().decode("utf-8").rstrip() # read data from serial 
                                 # format should be [tempSyringe,pidSyringe,tempTube,pidTube,tempNeedle,pidNeedle]
                                 # port and strip line endings
  #serData="10,12,14,20,22,24"                               
  if len(serData.split(",")) == 6:
    temperaturePlot.data = serData.split(",")[::2] # even vals
    temperaturePlot.ymin = 20
    temperaturePlot.ymax = 45
    temperaturePlot.updatePlotVals()
    
    pidPlot.data = serData.split(",")[1::2] # odd vals
    pidPlot.ymin = 0
    pidPlot.ymax = 260
    pidPlot.updatePlotVals()

    plt.draw() # update the plot


# Send serial command f to Fast Forward extruder stepper
def moveForward():
  print('Fast Forward')
  ser.write(b"f\r\n")

def moveBackward():
  print('Fast Backward')
  ser.write(b"b\r\n")

def movePause():
  print('Pause')
  ser.write(b"p\r\n")

def moveWrite():
  print('Write')
  ser.write(b"w\r\n")

def moveExtrude():
  print('Extrude')
  ser.write(b"e\r\n")

def moveStop():
  print('Stop')
  ser.write(b"s\r\n")

def stopProgram():
  ser.close()
  root.destroy()
  exit()

def updatePeltier(i):
  tempNum = '{num:03d}'.format(num=peltierSlider.get())
  serPeltier.write(b'x'+tempNum.encode('ascii'))
  # update the associated tk.Entry
  peltierEntry.delete(0,tk.END)
  peltierEntry.insert(0,peltierSlider.get())

def setPeltierSlider():
  print('Set Peltier Slider to: "%s"' % (peltierEntry.get())) 
  peltierSlider.set(peltierEntry.get())
  updatePeltier(0)
  
def updateFan(i):
  tempNum = '{num:03d}'.format(num=fanSlider.get())
  serPeltier.write(b'f'+tempNum.encode('ascii'))
  # update the associated tk.Entry
  fanEntry.delete(0, tk.END)
  fanEntry.insert(0, fanSlider.get())

def setFanSlider():
  print('Set Fan Slider to: "%s"' % (fanEntry.get())) 
  fanSlider.set(fanEntry.get())
  updateFan(0)

def updateExtrude(i):
  tempNum = '{num:03d}'.format(num=extrudeSlider.get())
  ser.write(b'p'+tempNum.encode('ascii'))
  # update the associated tk.Entry
  extrudeEntry.delete(0, tk.END)
  extrudeEntry.insert(0, extrudeSlider.get())

def setExtrudeSlider():
  print('Set Extrude Slider to: "%s"' % (extrudeEntry.get())) 
  extrudeSlider.set(extrudeEntry.get())
  updateExtrude(0)

def setTempSyringeEntry():
  tempNum = '{num:03d}'.format(num=int(tempSyringeEntry.get()))
  ser.write(b'y'+tempNum.encode('ascii'))

def setTempTubeEntry():
  tempNum = '{num:03d}'.format(num=int(tempTubeEntry.get()))
  ser.write(b'u'+tempNum.encode('ascii'))

def setTempNeedleEntry():
  tempNum = '{num:03d}'.format(num=int(tempNeedleEntry.get()))
  ser.write(b'n'+tempNum.encode('ascii'))

def fetch(entries):
  for entry in entries:
    field = entry[0]
    text  = entry[1].get()
    print('%s: "%s"' % (field, text)) 

def writeGcodeFile(entries):
  #gcodeFields = 'Filename', 'H-offset', 'Rows-H', 'V-offset', 'Rows-V', 'Z-offset', 'Layers'
  dictEntries = dict(entries)
  print("filename sent: ", dictEntries['Filename'].get())
  gen_gcode_cube( gcode_filename = dictEntries['Filename'].get(), 
                  vert_offset = float( dictEntries['H-offset'].get() ), 
                  horz_offset = float( dictEntries['V-offset'].get() ), 
                  z_offset = float( dictEntries['Z-offset'].get() ), 
                  number_rows_vert = float( dictEntries['Rows-V'].get() ), 
                  number_rows_horz = float( dictEntries['Rows-H'].get() ), 
                  number_rows_z = float( dictEntries['Layers'].get()) )
  print("G-code file created")
  

# Setup the GUI 
#
# Region to draw the plots
canvas = FigureCanvasTkAgg(f, master=root)
canvas.get_tk_widget().grid(row=1, column=1, columnspan=2, rowspan=20)
#canvas.show()

forwardButton = tk.Button(root, text="Fast Forward", width=25,  command=moveForward)
forwardButton.grid(row=22,column=1)
backButton = tk.Button(root, text="Fast Backward", width=25,  command=moveBackward)
backButton.grid(row=23,column=1)
pauseButton = tk.Button(root, text="Pause", width=25,  command=movePause)
pauseButton.grid(row=22,column=2)
writeButton = tk.Button(root, text="Write", width=25,  command=moveWrite)
writeButton.grid(row=23,column=2)
extrudeButton = tk.Button(root, text="Extrude", width=25,  command=moveExtrude)
extrudeButton.grid(row=24,column=1)
stopExtrudeButton = tk.Button(root, text="Stop Extrusion", width=25,  command=moveStop)
stopExtrudeButton.grid(row=24,column=2)

# >>---------->>---------->>Sliders for peltier, fan and extruder speed controls >>---------->>---------->>
tk.Label(root, text="Peltier Control").grid(row=26, column=1)
peltierSlider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=updatePeltier)
peltierSlider.grid(row=26,column=2)
peltierSlider.set(60)

peltierEntry = tk.Entry(root)
peltierEntry.bind('<Return>', lambda event: setPeltierSlider())
peltierEntry.grid(row=26,column=3)

tk.Label(root, text="Fan Control").grid(row=27, column=1)
fanSlider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=updateFan)
fanSlider.grid(row=27,column=2)
fanSlider.set(200)

fanEntry = tk.Entry(root)
fanEntry.bind('<Return>', lambda event: setFanSlider())
fanEntry.grid(row=27,column=3)

tk.Label(root, text="Extruder Syringe Control").grid(row=28, column=1)
extrudeSlider = tk.Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, command=updateExtrude)
extrudeSlider.grid(row=28,column=2)
extrudeSlider.set(165)

extrudeEntry = tk.Entry(root)
extrudeEntry.bind('<Return>', lambda event: setExtrudeSlider())
extrudeEntry.grid(row=28,column=3)

# <<----------<<----------<<Sliders for peltier, fan and extruder speed controls <<----------<<----------<<

# >>---------->>---------->>Syringe Pump Temperature Controls >>---------->>---------->>
tk.Label(root, text="Syringe Temp (C)").grid(row=10, column=3)
tempSyringeEntry = tk.Entry(root)
tempSyringeEntry.bind('<Return>', lambda event: setTempSyringeEntry())
tempSyringeEntry.grid(row=10,column=4)
tempSyringeEntry.delete(0,tk.END)
tempSyringeEntry.insert(0, '38')

tk.Label(root, text="Tube Temp (C)").grid(row=11, column=3)
tempTubeEntry = tk.Entry(root)
tempTubeEntry.bind('<Return>', lambda event: setTempTubeEntry())
tempTubeEntry.grid(row=11,column=4)
tempTubeEntry.delete(0,tk.END)
tempTubeEntry.insert(0, '38')

tk.Label(root, text="Tube Needle (C)").grid(row=12, column=3)
tempNeedleEntry = tk.Entry(root)
tempNeedleEntry.bind('<Return>', lambda event: setTempNeedleEntry())
tempNeedleEntry.grid(row=12,column=4)
tempNeedleEntry.delete(0,tk.END)
tempNeedleEntry.insert(0, '38')

# <<----------<<----------<<Syringe Pump Temperature C`ontrols <<----------<<----------<<

# >>--->>--->> Frame to generate g-code >>--->>--->>--->>--->>-
gcodeFields = 'Filename', 'H-offset', 'Rows-H', 'V-offset', 'Rows-V', 'Z-offset', 'Layers'
gcodeFields_Default = {'Filename': "testPrint_01.gcode",
    'H-offset': 2.0, 
    'Rows-H': 6, 
    'V-offset':2.0, 
    'Rows-V':6, 
    'Z-offset':0.15, 
    'Layers':4 }

def makeGcodeForm(root, fields):
  entries=[]
  rows = [1,2,3,4,5,6,7]
  cols = [3,4]
  for idx, field in enumerate(fields):
    lab = tk.Label(root, text=field)
    lab.grid(row=rows[idx], column=cols[0])
    ent = tk.Entry(root)
    ent.delete(0,tk.END)
    ent.insert(0,gcodeFields_Default[field])
    ent.grid(row=rows[idx], column=cols[1])
    entries.append((field,ent))
  return entries
'''
tk.Label(root, text="Filename").grid(row=1,column=3)
g_filename = tk.Entry(root).grid(row=1, column=4)

tk.Label(root, text="H-offset").grid(row=2,column=3)
g_h_offset = tk.Entry(root).grid(row=2, column=4)

tk.Label(root, text="Rows H").grid(row=3,column=3)
g_rows_h = tk.Entry(root).grid(row=3, column=4)

tk.Label(root, text="V-offset").grid(row=4,column=3)
g_v_offset = tk.Entry(root).grid(row=4, column=4)

tk.Label(root, text="Rows V").grid(row=5,column=3)
g_rows_v = tk.Entry(root).grid(row=5, column=4)

tk.Label(root, text="Z-offset").grid(row=6,column=3)
g_z_offset = tk.Entry(root).grid(row=6, column=4)

tk.Label(root, text="Layers").grid(row=7,column=3)
g_layers = tk.Entry(root).grid(row=7, column=4)
'''

ents = makeGcodeForm(root,gcodeFields)
#root.bind('<Return>', (lambda event, e=ents: fetch(e)))

genGcodeButton = tk.Button(root, text="Gen G-code", width=25, command= lambda: writeGcodeFile(ents))
genGcodeButton.grid(row=8,column=3)
# <<---<<---<< Frame to generate g-code <<---<<---<<---<<---<<-


stopButton = tk.Button(root, text="Stop", width=25, command=stopProgram)
stopButton.grid(row=28, column=4)

#root.configure(background='gray')

'''
logo = tk.PhotoImage(file="scope.gif")
w1 = tk.Label(root, image=logo).pack(side="right")

w2 = tk.Label(root, 
           padx = 10,
           fg="green")
w2.pack(side="left")

counter_label(w2)
'''

# Instantiate plot objects
temperaturePlot = PlotData(f, subplotTop)
pidPlot = PlotData(f, subplotBottom)


#ani = animation.FuncAnimation(f, animatePlot(ser), interval=1000)
ani = animation.FuncAnimation(f, animatePlot, interval=1000)

root.mainloop()

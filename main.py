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

f = plt.figure(figsize=(2,1), dpi=100)
subplotTop = 111# 211

class PlotData():
  """Store and format data for subsequent plotting
  """
  def __init__(self, plot_fig, subplot_axes):
    """Constructor for PlotData Class

    Args:
      plot_fig (matplotlib fiure): Figure which will eventuall plot the data
      subplot_axes (int): Integer defining subplot
    """

    self.fig = plot_fig
    self.subplot = subplot_axes
    self.dataNew = [0]
    self.dataTest = [0] * 100
    self.ymin = 0
    self.ymax = 50

    plt.subplot(self.subplot)
    self.lineDataTest = plt.plot(self.dataTest, 'rs', label='Plot Data')
    plt.ylim([self.ymin, self.ymax])
    plt.legend(loc='upper left')

  def updatePlotVals(self):
    """Update plot
    """
    plt.subplot(self.subplot)
    self.dataTest.append(float(self.dataNew[0])) # Add new data to end of existing data array
    del self.dataTest[0] # Drop the first array element
    self.ymin = float(min(self.dataTest)-10)
    self.ymax = float(max(self.dataTest)+10)
    plt.ylim([self.ymin, self.ymax])
    self.lineDataTest[0].set_xdata(np.arange(len(self.dataTest)))
    self.lineDataTest[0].set_ydata(self.dataTest)


# Code to animate plot
def animatePlot(frameNum):
  """Update data in PlotData objects and draw plot

  animatePlot runs in the masterUI.mainloop() method. The interval for running the animatePlot method
  is set in the call "ani = animation.FuncAnimation(f, animatePlot, interval=1000)"

  Args:
    frameNum (automatically assigned by mainloop method)
  """
  import random
  testDataPlot.dataNew = [random.gauss(15, 1.4)]
  testDataPlot.updatePlotVals()
  plt.draw()

def updatePlotRate(i):
  tempNum = 'num:03d'.format(num=plotRateSlider.get())

#def setPlotRateSlider():
#
#def plotRate():
#

def stopProgram():
  masterUI.destroy()
  exit()

# ----------------------------------------------------
# >>------------->> UI CANVAS >>-------------------->>
# ----------------------------------------------------
# Region to draw the plots
canvas = FigureCanvasTkAgg(f, master=masterUI)
canvas.get_tk_widget().grid(row=1, column=1, columnspan=2, rowspan=2)
# canvas.show()

# ----------------------------------------------------
# >>--------->> LABELS, SLIDERS, BUTTONS >>--------->>
# ----------------------------------------------------
tk.Label(masterUI, text="Plot Rate Control").grid(row=1, column=1)
#plotRateSlider = tk.Scale(masterUI, from_=0, to=255, orient=tk.HORIZONTAL, command=updatePlotRate)
#plotRateSlider.grid(row=1, column=2)
#plotRateSlider.set(60)


stopButton = tk.Button(masterUI, text="Stop", width=5, command=stopProgram)
stopButton.grid(row=2, column=3)


# ----------------------------------------------------
# >>--------->> MAIN PLOTTING AREA >>--------------->>
# ----------------------------------------------------
# Create plot objects to hold data and manage plotting functions
testDataPlot = PlotData(f, subplotTop)

ani = animation.FuncAnimation(f, animatePlot, interval=1000)

masterUI.mainloop()

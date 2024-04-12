from WF_SDK import device, scope, wavegen, static
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Thread
import time
import tkinter as tk
import sys
import numpy as np
from scipy import optimize

# create gui window
gui = tk.Tk()
gui.title("Coulometry")
gui.geometry('850x500')
gui.config(background="white")

# set default measurement parameters
generator_potential = 5.0   # volts 
indicator_potential = 3.0   # volts
generator_resistor  = 100.1 # ohms
indicator_resistor  = 100.2 # ohms
measure_period      = 0.5   # seconds
measure_duration    = 30.0  # seconds
generator_channel   = 1
indicator_channel   = 2
generator_dio_channel = 0
indicator_dio_channel = 1

# parameter inputs for gui
# > > > >
# generator potential
generator_potential_lbl = tk.Label(gui,width=20,text="Generator Potential (V):",background="white",justify="left",anchor="w")
generator_potential_txt = tk.StringVar()
generator_potential_txt.set("{:.2f}".format(generator_potential))
generator_potential_ent = tk.Entry(gui,width=10,textvariable=generator_potential_txt,justify="right")
generator_potential_lbl.grid(row=0,column=0,padx=(10,0))
generator_potential_ent.grid(row=0,column=1)

# indicator potential
indicator_potential_lbl = tk.Label(gui,width=20,text="Indicator Potential (V):",background="white",justify="left",anchor="w")
indicator_potential_txt = tk.StringVar()
indicator_potential_txt.set("{:.2f}".format(indicator_potential))
indicator_potential_ent = tk.Entry(gui,width=10,textvariable=indicator_potential_txt,justify="right")
indicator_potential_lbl.grid(row=1,column=0,padx=(10,0))
indicator_potential_ent.grid(row=1,column=1)

# generator resistor
generator_resistor_lbl = tk.Label(gui,width=20,text="Generator Resistor (Ohm):",background="white",justify="left",anchor="w")
generator_resistor_txt = tk.StringVar()
generator_resistor_txt.set("{:.2f}".format(generator_resistor))
generator_resistor_ent = tk.Entry(gui,width=10,textvariable=generator_resistor_txt,justify="right")
generator_resistor_lbl.grid(row=2,column=0,padx=(10,0))
generator_resistor_ent.grid(row=2,column=1)

# indicator resistor
indicator_resistor_lbl = tk.Label(gui,width=20,text="Indicator Resistor (Ohm):",background="white",justify="left",anchor="w")
indicator_resistor_txt = tk.StringVar()
indicator_resistor_txt.set("{:.2f}".format(indicator_resistor))
indicator_resistor_ent = tk.Entry(gui,width=10,textvariable=indicator_resistor_txt,justify="right")
indicator_resistor_lbl.grid(row=3,column=0,padx=(10,0))
indicator_resistor_ent.grid(row=3,column=1)

# measurement period
measure_period_lbl = tk.Label(gui,width=20,text="Measurement Period (s):",background="white",justify="left",anchor="w")
measure_period_txt = tk.StringVar()
measure_period_txt.set("{:.2f}".format(measure_period))
measure_period_ent = tk.Entry(gui,width=10,textvariable=measure_period_txt,justify="right")
measure_period_lbl.grid(row=4,column=0,padx=(10,0))
measure_period_ent.grid(row=4,column=1)

# measurement duration
measure_duration_lbl = tk.Label(gui,width=20,text="Measurement Duration (s):",background="white",justify="left",anchor="w")
measure_duration_txt = tk.StringVar()
measure_duration_txt.set("{:.2f}".format(measure_duration))
measure_duration_ent = tk.Entry(gui,width=10,textvariable=measure_duration_txt,justify="right")
measure_duration_lbl.grid(row=5,column=0,padx=(10,0))
measure_duration_ent.grid(row=5,column=1)

# measurement name
measure_name_lbl = tk.Label(gui,width=20,text="Measurement Name:",background="white",justify="left",anchor="w")
measure_name_txt = tk.StringVar()
measure_name_txt.set("Run")
measure_name_ent = tk.Entry(gui,width=20,textvariable=measure_name_txt,justify="right")
measure_name_lbl.grid(row=7,column=0,padx=(10,0))
measure_name_ent.grid(row=7,column=1)
# > > > >

# results for gui
# > > > >
# endpoint result
endpoint_txt = tk.StringVar()
endpoint_txt.set("Endpoint (s):")
endpoint_lbl = tk.Label(gui,width=20,textvariable=endpoint_txt,background="white",justify="left",anchor="w")
endpoint_lbl.grid(row=8,column=0,padx=(10,0))

endpoint_res_txt = tk.StringVar()
endpoint_res_txt.set("")
endpoint_res_lbl = tk.Label(gui,width=20,textvariable=endpoint_res_txt,background="white",justify="right",anchor="e")
endpoint_res_lbl.grid(row=8,column=1)

# total charge
charge_txt = tk.StringVar()
charge_txt.set("Charge Delivered (mC):")
charge_lbl = tk.Label(gui,width=20,textvariable=charge_txt,background="white",justify="left",anchor="w")
charge_lbl.grid(row=9,column=0,padx=(10,0))

charge_res_txt = tk.StringVar()
charge_res_txt.set("")
charge_res_lbl = tk.Label(gui,width=20,textvariable=charge_res_txt,background="white",justify="right",anchor="e")
charge_res_lbl.grid(row=9,column=1)

# moles Ag+
moleag_txt = tk.StringVar()
moleag_txt.set("Ag+ Delivered (uMol):")
moleag_lbl = tk.Label(gui,width=20,textvariable=moleag_txt,background="white",justify="left",anchor="w")
moleag_lbl.grid(row=10,column=0,padx=(10,0))

moleag_res_txt = tk.StringVar()
moleag_res_txt.set("")
moleag_res_lbl = tk.Label(gui,width=20,textvariable=moleag_res_txt,background="white",justify="right",anchor="e")
moleag_res_lbl.grid(row=10,column=1)
# > > > >

# create a graph to plot the data live
# > > > >
font = 9
plt.rcParams["font.size"] = font
plt.rcParams["font.family"] = 'Segoe UI'
figure, ax = plt.subplots(figsize=(5,4))
ax.set_xlabel("Time (s)")
ax.set_ylabel("Current (mA)")
ax.set_ylim(-1,15)
ax.set_xlim(0,measure_duration)

# make initial plots of data; these will be updated when collecting the data
times               = []
indicator_currents  = []
generator_currents  = []
indicator_markers,  = ax.plot(times,indicator_currents,marker="o",markersize=3,color="red",linestyle="",label="Indicator")
generator_markers,  = ax.plot(times,generator_currents,marker="o",markersize=3,color="black",linestyle="",label="Generator")
fit_line,           = ax.plot(times,[],color="blue",linestyle="--",label="Fit")
ax.legend(loc="upper right",frameon=False)
ax.plot()
figure.tight_layout()

# include graph in gui window
graph = FigureCanvasTkAgg(figure,master=gui)
graph.get_tk_widget().grid(row=0,column=3,rowspan=7)
# > > > >

# variables for saving multiple runs in the same session
saved_times = []
saved_indicator_currents = []
saved_generator_currents = []
saved_results = []

# define piecewise linear fitting function to fit data and find endpoint
def piecewise_linear(x, x0, y0, k1, k2):
    # the fitting function is
    # y = k1*x + y0-k1*x0 for x < x0
    # y = k2*x + y0-k2*x0 for x > x0
    # the endpoint is x0
    return np.piecewise(x, [x<x0], [lambda x:k1*x + y0-k1*x0, lambda x:k2*x + y0-k2*x0])

# take the measurement
def on_start():
    global times
    global indicator_currents
    global generator_currents
    global saved_times
    global saved_indicator_currents
    global saved_generator_currents
    global running
    
    # set running variable
    running = True
    
    # get parameters from gui
    generator_potential = float(generator_potential_ent.get())
    indicator_potential = float(indicator_potential_ent.get())
    generator_resistor  = float(generator_resistor_ent.get())
    indicator_resistor  = float(indicator_resistor_ent.get())
    measure_period      = float(measure_period_ent.get())
    measure_duration    = float(measure_duration_ent.get())
    measure_name        = measure_name_ent.get()
    print("Generator Potential (V): {:.2f}".format(generator_potential))
    print("Indicator Potential (V): {:.2f}".format(indicator_potential))
    print("Generator Resistor (Ohm): {:.2f}".format(generator_resistor))
    print("Indicator Resistor (Ohm): {:.2f}".format(indicator_resistor))
    print("Measure Period (s): {:.2f}".format(measure_period))
    print("Measure Duration (s): {:.2f}".format(measure_duration))
    print("Measure Name: {:}".format(measure_name))
    
    # reset graph
    indicator_markers.set_xdata([])
    generator_markers.set_xdata([])
    indicator_markers.set_ydata([])
    generator_markers.set_ydata([])
    fit_line.set_xdata([])
    fit_line.set_ydata([])
    ax.set_xlim(0,measure_duration)
    
    # reset results
    endpoint_res_txt.set("")
    charge_res_txt.set("")
    moleag_res_txt.set("")
    
    # connect to device
    device_data = device.open()
    
    # initialize the dio channels and turn both off
    static.set_mode(device_data, generator_dio_channel, True)
    static.set_mode(device_data, indicator_dio_channel, True)
    static.set_state(device_data, generator_dio_channel, False)
    static.set_state(device_data, indicator_dio_channel, False) 
    
    # initialize the scope with default settings
    scope.open(device_data)
    
    # initialize variables (using global variables
    times              = []
    indicator_currents = []
    generator_currents = []

    # start the timer
    starttime = time.monotonic()
    
    # set generator and indicator potentials and turn them on
    wavegen.generate(device_data,channel=indicator_channel,function=wavegen.function.dc,offset=indicator_potential)
    wavegen.generate(device_data,channel=generator_channel,function=wavegen.function.dc,offset=generator_potential)
    
    # turn on generator channel
    static.set_state(device_data, generator_dio_channel, True)
    
    # main loop for measuring the signal
    # > > > >
    print("Time (s), Indicator Current (mA), Generator Current (mA)")
    while True:
        # exit the loop if the stop button is pressed
        if (not running): 
            break
                        
        # measure the signals
        timenow = time.monotonic()-starttime
        
        # measure generator signal with indicator circuit off
        generator_resistor_potential = scope.measure(device_data,channel=generator_channel)
        
        # turn  on indicator circuit and off generator circuit
        static.set_state(device_data, generator_dio_channel, False)
        static.set_state(device_data, indicator_dio_channel, True)
        
        # measure indicator signal with generator off
        indicator_resistor_potential = scope.measure(device_data,channel=indicator_channel)
        
        # turn off indicator circuit and on generator circuit
        static.set_state(device_data, indicator_dio_channel, False)
        static.set_state(device_data, generator_dio_channel, True)
        
        # calculate current in mA
        indicator_resistor_current = indicator_resistor_potential/indicator_resistor*1.0E3
        generator_resistor_current = generator_resistor_potential/generator_resistor*1.0E3
        print("{:.4f} {:.4f} {:.4f}".format(timenow, indicator_resistor_current, generator_resistor_current))
        
        # save data
        times.append(timenow)
        indicator_currents.append(indicator_resistor_current)
        generator_currents.append(generator_resistor_current)
        
        # update graph
        indicator_markers.set_xdata(times)
        generator_markers.set_xdata(times)
        indicator_markers.set_ydata(indicator_currents)
        generator_markers.set_ydata(generator_currents)
        figure.canvas.draw()
        figure.canvas.flush_events()
        
        if (timenow >= measure_duration):
            break
            
        # pause loop until next measurement time
        time.sleep(measure_period - ((time.monotonic()-starttime)%measure_period))
    # > > > >
    
    # turn off generator switch
    static.set_state(device_data, generator_dio_channel, False)
    
    # reset the scope
    scope.close(device_data)

    # reset the wavegen
    wavegen.close(device_data)

    # close the connection
    device.close(device_data)
    
    # fit the data to a piecewise linear function to determine the time
    # when indicator current started rising
    p, e = optimize.curve_fit(piecewise_linear, times, indicator_currents, p0=[np.mean(times),np.mean(indicator_currents),0,0])
    
    # plot the fit on the graph
    fit_line.set_xdata(times)
    fit_line.set_ydata(piecewise_linear(times, *p))
    figure.canvas.draw()
    figure.canvas.flush_events()
  
    # print the results
    endpoint = p[0]
    endpoint_res_txt.set("{:.3f}".format(endpoint))
    charge_delivered = np.ma.masked_where( times > endpoint, generator_currents ).mean()*endpoint
    charge_res_txt.set("{:.3f}".format(charge_delivered))
    ag_delivered = charge_delivered/96485.33212*1000 # divide charge by faraday's constant and convert to uMol
    moleag_res_txt.set("{:.3f}".format(ag_delivered))
    
    # save data to write to file
    saved_times.append(times.copy())
    saved_indicator_currents.append(indicator_currents.copy())
    saved_generator_currents.append(generator_currents.copy())
    saved_results.append([measure_name,endpoint,charge_delivered,ag_delivered])

# stop button function
def on_stop():
    global running
    running = False
    
# save the data as a csv file
def save_file():
    global saved_results
    global saved_times
    global saved_indicator_currents
    global saved_generator_currents
    
    filename = tk.filedialog.asksaveasfilename(initialfile="untitled.csv",defaultextension=".csv",filetypes=[("All Files","*.*")])
    if (filename == ""): 
        return
    with open(filename, "w") as f:
        for i in range(len(saved_times)):
            f.write("Run Name: {:}\n".format(saved_results[i][0]))
            f.write("Endpoint (s):,{:.3f}\n".format(saved_results[i][1]))
            f.write("Charge Delivered (mC):,{:.3f}\n".format(saved_results[i][2]))
            f.write("Ag+ Delivered (uMol):,{:.3f}\n".format(saved_results[i][3])) 
            f.write("Time (s), Indicator Current (mA), Generator Current (mA)\n")
            for j in range(len(saved_times[i])):
                f.write("{:},{:},{:}\n".format(saved_times[i][j],saved_indicator_currents[i][j],saved_generator_currents[i][j]))
            f.write("\n\n")
        
# exit the program
def on_exit():
    sys.exit()
    
# start button
start_btn = tk.Button(gui,text="Start",command=lambda: Thread(target=on_start).start())
start_btn.grid(row=6,column=0)

# stop button
stop_btn = tk.Button(gui,text="Stop",command=on_stop)
stop_btn.grid(row=6,column=1)

# make a file menu
menubar = tk.Menu(gui)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Save",command=save_file)
filemenu.add_command(label="Exit",command=on_exit)
menubar.add_cascade(label="File",menu=filemenu)
gui.config(menu=menubar)

# run the gui
gui.mainloop()
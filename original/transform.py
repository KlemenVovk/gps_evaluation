import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd
from math import *
import matplotlib.pyplot as plt
from fitter import Fitter
from pyproj import Geod
from scipy.stats import t
import datetime

# pip install pandas, numpy, fitter, pyproj, matplotlib, openpyxl

# Transforms coordinates of the form [long, lat] to distance to reference point (d) and angle from north (phi) in rad
# Takes as input the coordinates of the reference point (zero) and of the point to transform (coords)
# Both points are to be formatted as follows [long, lat]
# Returns [d, phi] of coords
def transform_to_rad(zero, coords):
    g = Geod(ellps='WGS84') # Initiate Geode based on WGS84
    a, phi, d = g.inv(zero[1], zero[0], coords[1], coords[0]) #! TODO: This is wrong
    #print(phi)
    return [d, radians(phi)]


def write_log(path, text):
    with open(path, 'a') as file:
        file.write(text + '\n')
    return


def read_reference_data(path):
    report_raw = pd.read_excel(path).values.tolist()[1:]
    report = []
    for i in range(len(report_raw)):
        id = report_raw[i][0]
        name = report_raw[i][1]
        lat = report_raw[i][9]
        long = report_raw[i][10]
        if i > 0:
            if (report_raw[i-1][9] != lat) | (report_raw[i-1][10] != long):
                # Remove entries where location was not updated
                report.append([id, name, long, lat])
        else:
            report.append([id, name, long, lat])
    return report


# Function returning the probability of E given P
# Inputs:
# P: Coordinates of point P in form [long, lat]
# E: Coordinates of point E in form [long, lat]
# hw: half of the wedge size used to calculate the angular probability
# Ref: list of reference measures from point P in form [[x0,y0],...]
# Returns list of probabilities in form [pphi, pdist] where
# pphi: the probability to observe a measurement in a (2 * hw) wedge centered around the angle of the evidence
# pdist: the probability to observe a measurement at the distance of the evidence given it is within the given wedge
def get_probabilities(P, E, Ref, hw, n, op):
    E_rad = transform_to_rad(P,E)
    Ref_rad = []

    for i in Ref:
        Ref_rad.append(transform_to_rad(P, [float(i[2]), float(i[3])]))

    phi_c = 0 # Initialise counter for measurement points within angle
    wedge = [] # Initialise list of distances within the wedge
    for i in Ref_rad:
        if (i[1] >= E_rad[1] - hw) & (i[1] <= E_rad[1] + hw):
            wedge.append(i[0])
            phi_c += 1

    write_log(op + '/logfile.txt', "Fraction within wedge for P" + n + ": " + str(len(wedge)))
    write_log(op + '/logfile.txt', "Distances within wedge for P" + n + ": " + str(wedge))
    if wedge:
        f = Fitter(wedge, distributions='t')
        f.fit()
        t_par = f.get_best()['t']
        pd = t.pdf(E_rad[0], t_par['df'], t_par['loc'], t_par['scale'])
        plot_wedge(wedge, E_rad[0], n, op)
    else:
        pd = 0
    return [float(phi_c) / float(len(Ref_rad)), pd]


# Draws a histogram of the inputted reference data collection (wedge) and the observed Evidence value (d_E)
def plot_wedge(wedge, d_E, n, op):
    plt.clf()
    plt.cla()
    plt.hist(wedge, color='darkgray', bins=np.arange(0, 160, 5), density=True)
    plt.plot(2 * [d_E], [0, 0.15], c='red')
    plt.savefig(op + '\hist_Wedge' + n + '.png', bbox_inches='tight')


# function for browsing file in the UI
def browse_file(entry):
    filename = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, filename)


# function for browsing folder in the UI
def browse_folder(entry):
    foldername = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, foldername)


def run_script():
    # Code to run the script with user input

    hw = float(wedge_entry.get()) * pi / 180 # Half of the wedge size used for the angular probability
    output_path = output_folder_entry.get()
    log_path = output_path + '/logfile.txt'

    P1 = [float(p1_long_entry.get()), float(p1_lat_entry.get())] # Coordinates of P1
    P2 = [float(p2_long_entry.get()), float(p2_lat_entry.get())] # Coordinates of P2

    E = [float(e_long_entry.get()), float(e_lat_entry.get())] # Coordinates of E

    P1_measurements = read_reference_data(p1_file_entry.get())
    P2_measurements = read_reference_data(p2_file_entry.get())

    with open(log_path, 'w') as file:
        file.write("Log for the Evaluation of Location Evidence\n")
        file.write("===========================================\n\n")
        file.write("Script started at : " + str(datetime.datetime.now()))
        file.write("\n\nLocation E: " + str(E))
        file.write("\nLocation P1: " + str(P1))
        file.write("\nLocation P2: " + str(P2))
        file.write("\n\nAmount of reference data:")
        file.write("\nP1: " + str(len(P1_measurements)))
        file.write("\nP2: " + str(len(P2_measurements)))

    e_p1 = transform_to_rad(E, P1)
    e_p2 = transform_to_rad(E, P2)

    write_log(log_path, "\n\nDistance and Angle of the Observation")
    write_log(log_path, "=====================================")
    write_log(log_path, "E -> P1" + str(e_p1))
    write_log(log_path, "E -> P2" + str(e_p2))

    write_log(log_path, "\nAngular Data")
    write_log(log_path, "============")
    P1_probs = get_probabilities(P1, E, P1_measurements, hw, "1", output_path)
    P2_probs = get_probabilities(P2, E, P2_measurements, hw, "2", output_path)

    write_log(log_path, "\n\nObtained probabilities\n=======================")
    write_log(log_path, "Angular probability given P1: " + str(P1_probs[0]))
    write_log(log_path, "Angular probability given P2: " + str(P2_probs[0]))
    write_log(log_path, "Distance probability given P1 and phi1: " + str(P1_probs[1]))
    write_log(log_path, "Distance probability given P2 and phi2: " + str(P2_probs[1]))

    LR = (P1_probs[0] * P1_probs[1]) / (P2_probs[0] * P2_probs[1])
    write_log(log_path, "LR in favour of P1: " + str(LR))

    # This section draws the scatter plot
    plt.cla()
    plt.clf()

    x_val = []
    y_val = []
    for i in P1_measurements:
        x_val.append(float(i[2]))
        y_val.append(float(i[3]))

    plt.scatter(x_val, y_val, s=15, c='darkgray', marker='x', label='P1 reference')

    x_val = []
    y_val = []
    for i in P2_measurements:
        x_val.append(float(i[2]))
        y_val.append(float(i[3]))

    plt.scatter(x_val, y_val, c='dimgray', s=15, marker='x', label='P2 reference')
    plt.scatter(P1[0], P1[1], c='darkgray', s=7, label='P1')
    plt.annotate("P1", (float(P1[0]) + 0.00002, P1[1]), c='darkgray')
    plt.scatter(P2[0], P2[1], c='dimgray', s=7, label='P2')
    plt.annotate("P2", (float(P2[0]) + 0.00002, P2[1]), c='dimgray')
    plt.scatter(E[0], E[1], c='black', s=7, label='E1')
    plt.annotate("E1", (float(E[0]) - 0.0001, float(E[1]) - 0.00005), c='black')
    plt.legend()

    plt.savefig(output_path + '/Scatter.png', bbox_inches='tight')

    # Update the output label to indicate success
    output_label.config(text="Script run successfully.")
    return


if __name__ == "__main__":
    # Create the main window
    window = tk.Tk()
    window.title("Location Evaluator")

    # Create the input fields for P1 coordinates
    p1_lat_label = tk.Label(window, text="P1 Lat:")
    p1_lat_entry = tk.Entry(window, width=20)
    p1_lat_label.grid(row=0, column=0)
    p1_lat_entry.grid(row=0, column=1)

    p1_long_label = tk.Label(window, text="Long:")
    p1_long_entry = tk.Entry(window, width=20)
    p1_long_label.grid(row=0, column=2)
    p1_long_entry.grid(row=0, column=3)

    # Create the input fields for P2 coordinates
    p2_lat_label = tk.Label(window, text="P2 Lat:")
    p2_lat_entry = tk.Entry(window, width=20)
    p2_lat_label.grid(row=1, column=0)
    p2_lat_entry.grid(row=1, column=1)

    p2_long_label = tk.Label(window, text="Long:")
    p2_long_entry = tk.Entry(window, width=20)
    p2_long_label.grid(row=1, column=2)
    p2_long_entry.grid(row=1, column=3)

    # Create the input fields for E coordinates
    e_lat_label = tk.Label(window, text="E Lat:")
    e_lat_entry = tk.Entry(window, width=20)
    e_lat_label.grid(row=2, column=0)
    e_lat_entry.grid(row=2, column=1)

    e_long_label = tk.Label(window, text="Long:")
    e_long_entry = tk.Entry(window, width=20)
    e_long_label.grid(row=2, column=2)
    e_long_entry.grid(row=2, column=3)

    wedge_label = tk.Label(window, text="Angle of Wedge (Deg)")
    wedge_entry = tk.Entry(window, width=20)
    wedge_label.grid(row=3, column=0)
    wedge_entry.grid(row=3, column=1)
    wedge_entry.insert(0,60)

    # Create the input fields for the file paths
    p1_file_label = tk.Label(window, text="P1 File:")
    p1_file_entry = tk.Entry(window)
    p1_file_label.grid(row=4, column=0)
    p1_file_entry.grid(row=4, column=1, columnspan=2)

    p2_file_label = tk.Label(window, text="P2 File:")
    p2_file_entry = tk.Entry(window)
    p2_file_label.grid(row=5, column=0)
    p2_file_entry.grid(row=5, column=1, columnspan=2)

    output_folder_label = tk.Label(window, text="Output Folder:")
    output_folder_entry = tk.Entry(window)
    output_folder_label.grid(row=6, column=0)
    output_folder_entry.grid(row=6, column=1, columnspan=2)

    # Create the "Browse" buttons
    p1_file_button = tk.Button(window, text="Browse", command=lambda: browse_file(p1_file_entry))
    p1_file_button.grid(row=4, column=3)

    p2_file_button = tk.Button(window, text="Browse", command=lambda: browse_file(p2_file_entry))
    p2_file_button.grid(row=5, column=3)

    output_folder_button = tk.Button(window, text="Browse", command=lambda: browse_folder(output_folder_entry))
    output_folder_button.grid(row=6, column=3)

    # Create the "Run" button
    run_button = tk.Button(window, text="Run", command=run_script)
    run_button.grid(row=7, column=1)

    # Create the output field
    output_label = tk.Label(window, text="")
    output_label.grid(row=8, column=1)

    # Run the main loop
    window.mainloop()
import numpy as np
import time
import scipy.signal as signal
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns # visualization

test_csv ="/home/gerald/imu_collect.csv"
filename= test_csv



## CSV file template:
# time in seconds, timestamp (H:M:S), X-Acceleration, Y-Acceleration, Z-Acceleration, X-Gyroscope,Y-Gyro,Z-Gyro,X-Gyro, Y-Gyro, Z-gyro



df =pd.read_csv(filename, header=None)
df=df.dropna()

timestamp = df[0]
x_axis=df[2]
y_axis=df[3]
z_axis=df[4]

## Visualize your Accelerometer Values
plt.plot(x_axis)
plt.plot(y_axis)
plt.plot(z_axis)
plt.show()



## CALIBERATION
# caliberate x,y,z to reduce the bias in accelerometer readings.
#Subtracting it from the mean means that in the absence of motion,
#the accelerometer reading is centered around zero to reduce the
#effect of integrigation drift or error.
# change the upper and lower bounds for computing the mean
#where the RPi is in static position at the begining of the experiment

lower, upper = 0, 40

x_calib_mean = np.mean(x_axis[lower:upper])
x_calib = x_axis - x_calib_mean


y_calib_mean = np.mean(y_axis[lower:upper])
y_calib = y_axis - y_calib_mean

z_calib_mean = np.mean(z_axis[lower:upper])
z_calib = z_axis - z_calib_mean

real_df = df[4][40:]

accel = signal.savgol_filter(z_calib, 3, 1)
# Enter function here to smooth z-axis acceleration,
#https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html
## Same as rolling average --> Savitzky-Golay smoothing
## change the window size as it seems fit.
#If you keep window size too high it will not capture the
#relevant peaks/steps

# Plot the original and smoothed data
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(z_calib)
plt.title("Original Data")
plt.subplot(2, 1, 2)
plt.plot(accel)
plt.title("Smoothed Data")
plt.show()


## Step Detection: The instantaneous peaks in the accelerometer readings correspond to the steps. We use thresholding technique to decide the range of peak values for step detection
# Set a minimum threshold (e.g., 1.0) for peak detection

min_threshold = 1.04  ## Change the threshold based on the peak accelerometer values that you observe in your plot above

# Calculate the upper threshold for peak detection as the maximum value in the data
upper_threshold = np.max(accel)

# Define the range for peak detection
my_range = (min_threshold, upper_threshold)
print("range of Accel. values  for peak detection",my_range)
## Visualize the detected peaks in the accelerometer readings based on the selected range
plt.plot(accel)

#Use this link to find the peaks: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html
peak_array, properties = signal.find_peaks(accel, height = 0.1) # Enter function here
print(peak_array)
plt.plot(peak_array, accel[peak_array], "x", color="r", label='Steps (Peaks)')
plt.title('Z Acceleration Peaks Tracking')
plt.xlabel('timestamp')
plt.ylabel('accel (m/s^2)')

# Adding the legend
plt.legend(loc='upper left')
for i, peak_index in enumerate(peak_array):
    plt.text(peak_index, accel[peak_index], str(i + 1), fontsize=8, color='black')
plt.show()

# Peak array indices -> peak_array
# Accel values at high peaks --> accel[peak_array]


# Set the orientation/direction of motion (walking direction).
# walking_direction is an angle in degrees with global frame x-axis.
# It can be from 0 degrees to 360 degrees.
# for e.g. if walking direction is 90 degrees, user is walking in
# the positive y-axis direction.
# Assuming you are moving along the +X-axis with minor
# deviations/drifts in Y, we set the orientation to 5
# (ideally it should be 0 but to take into account the drifts we keep 5)

# Integrate the orientation data to get the walking direction
walking_dir = df[7] # radians of each thing


# To compute the step length, we estimate it to be propertional to the height of the user.

height= 1.82 # in meters # Change the height of the user as needed
step_length= 0.4 * height # in meters

# Convert walking direction into a 2D unit vector representing motion in X, Y axis:
angle = np.array([np.cos(walking_dir), np.sin(walking_dir)]) # this is components of each moment of movement

## Start position of the user i.e. (0,0)

t = [[0.0, 0.0]]

for i in range(len(peak_array)): # peak array has times of each peak
    #need to get orientation at that time
    x_vector = angle[0][peak_array[i]] * step_length
    y_vector = angle[1][peak_array[i]] * step_length
    t.append([x_vector + t[i][0],y_vector + t[i][1]])

print(t)
print(f"final position is {t[-1]}")
t = np.array(t)

trajectory_data = pd.DataFrame({
    'timestamp': timestamp[peak_array].values,
    'x': t[1:, 0],
    'y': t[1:, 1]
    })
trajectory_data.to_csv('imu_data.csv', index = False)
print("data saved to csv")

plt.figure(figsize=(8, 8))
plt.quiver(t[:-1, 0], t[:-1, 1], 
           t[1:, 0] - t[:-1, 0], t[1:, 1] - t[:-1, 1], 
           angles='xy', scale_units='xy', scale=1, color='r')

plt.scatter(t[:, 0], t[:, 1], color='b', label='Positions')
plt.plot(t[:, 0], t[:, 1], color='g', linestyle='--', label='Path')

plt.title('Vector Representation in XY Plane')
plt.xlabel('X Position (meters)')
plt.ylabel('Y Position (meters)')

final_position = t[-1]
plt.annotate(f'Final Position: {final_position}', 
             xy=final_position, xytext=(final_position[0] + 0.5, final_position[1] + 0.5),
             arrowprops=dict(facecolor='black', shrink=0.05))
plt.grid()
plt.legend()
plt.axis('equal')
plt.show()

# Trajectory positions are stored in t, plot it for the submission with good plot labels as specified in the lab manual


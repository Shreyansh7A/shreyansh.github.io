#save x, y at each timestamp

import numpy as np
import time
import scipy.signal as signal
from datetime import datetime,date
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns # visualization
from scipy.interpolate import interp1d

df_rssi = pd.read_csv('/home/gerald/rssi_real.csv')
print(df_rssi['timestamp'])
imu_data = pd.read_csv('imu_data.csv')
rssi_interp = interp1d(df_rssi['timestamp'], df_rssi['rssi'], kind = 'linear', fill_value= 'extrapolate')
imu_data['rssi'] = rssi_interp(imu_data['timestamp'])

plt.scatter(imu_data['x'], imu_data['y'], c = imu_data['rssi'], cmap = 'hot', marker = 'o', label = 'Trajectory', edgecolors = 'k')
plt.colorbar(label = 'RSSI')

plt.xlabel('X position')
plt.ylabel('Y position')
plt.legend()
plt.show()

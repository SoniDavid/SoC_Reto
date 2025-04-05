import random
import time
import pandas as pd
import math
import matplotlib.pyplot as plt

def calc_rpm(ang_vel_, rad_, transmission_rel_):
    return round((ang_vel_ * 60) / (2 * math.pi * rad_ * transmission_rel_), 2)

# CONSTANTS
FILE_PATH = "rpm_data.csv"
TRANSMISSION_REL = 10

# CSV header init
columns = [
    "angular_velocity",
    "radius",
    "transmission_relation",
    "RPM",
    "time"
]
pd.DataFrame(columns=columns).to_csv(FILE_PATH, index=False)

# Rt plot init
plt.ion()
fig, axs = plt.subplots(2, 2, figsize=(12, 8)) # 2 x 2 grid for all the data
fig.suptitle('RPM Data Visualization', fontsize=16)

#PLOT
plots = {
    'angular_velocity': {'ax': axs[0,0], 'line': None, 'data': [], 'color': 'b', 'ylabel': 'Angular Velocity (rad/s)'},
    'radius': {'ax': axs[0,1], 'line': None, 'data': [], 'color': 'r', 'ylabel': 'Radius (m)'},
    'transmission_relation': {'ax': axs[1,0], 'line': None, 'data': [], 'color': 'g', 'ylabel': 'Transmission Relation'},
    'RPM': {'ax': axs[1,1], 'line': None, 'data': [], 'color': 'm', 'ylabel': 'RPM'}
}

for key in plots:
    ax = plots[key]['ax']
    ax.set_title(f'{key.replace("_", " ").title()}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(plots[key]['ylabel'])
    ax.grid(True)
    plots[key]['line'], = ax.plot([], [], plots[key]['color'] + '-')

times = []
start_time = time.time()

try:
    while True:
        # Data generation
        ang_vel = round(random.uniform(0, 5.0), 2)
        radius = round(random.uniform(0.2, 0.5), 3)  
        transmission = TRANSMISSION_REL
        current_time = time.time() - start_time
        rpm = calc_rpm(ang_vel, radius, transmission)
        
        # CSV data apend
        new_row = [ang_vel, radius, transmission, rpm, current_time]
        pd.DataFrame([new_row]).to_csv(FILE_PATH, mode='a', header=False, index=False)
        
        # Update data buffers (keep last 50 points in memory for plotting)
        times.append(current_time)
        for key, value in zip(['angular_velocity', 'radius', 'transmission_relation', 'RPM'], 
                            [ang_vel, radius, transmission, rpm]):
            plots[key]['data'].append(value)
            if len(plots[key]['data']) > 50:
                plots[key]['data'].pop(0)
        
        # Trim time buffer
        if len(times) > 50:
            times.pop(0)
        
        # Update plots
        for key in plots:
            plots[key]['line'].set_data(times, plots[key]['data'])
            plots[key]['ax'].relim()
            plots[key]['ax'].autoscale_view()
        
        # Redraw fig
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        # Console output
        print(f"T: {current_time:.1f}s | ω: {ang_vel} rad/s | R: {radius} m | RPM: {rpm}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nProgram stopped. Final data saved to:", FILE_PATH)
    plt.close()
    # Create final dataframe with proper types
    final_df = pd.DataFrame({
        'angular_velocity': plots['angular_velocity']['data'],
        'radius': plots['radius']['data'],
        'transmission_relation': [TRANSMISSION_REL]*len(times),
        'RPM': plots['RPM']['data'],
        'time': times
    })
    final_df.to_csv(FILE_PATH, index=False)
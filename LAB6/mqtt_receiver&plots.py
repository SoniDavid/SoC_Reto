import paho.mqtt.client as mqtt
import json
import csv
from datetime import datetime
import random
import time
import math
import matplotlib.pyplot as plt


# Rt plot init
plt.ion()
fig, axs = plt.subplots(1, 2, figsize=(8, 8)) # 2 x 2 grid for all the data
fig.suptitle('RPM Data Visualization', fontsize=16)

#PLOT
plots = {
    'Velocidad_lineal': {'ax': axs[0], 'line': None, 'data': [], 'color': 'g', 'ylabel': 'Velocidad Lineal'},
    'RPM': {'ax': axs[1], 'line': None, 'data': [], 'color': 'm', 'ylabel': 'RPM'}
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

CSV_FILENAME = "motor_data.csv"
CSV_HEADER = ["timestamp", "rpm", "velocidad_lineal"]

def plot_data(lineal_vel, rpm):
    current_time = round(time.time() - start_time, 2)
    # Update data buffers (keep last 50 points in memory for plotting)
    times.append(current_time)
    for key, value in zip(['RPM', 'Velocidad_lineal'], 
                        [rpm, lineal_vel]):
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

def write_to_csv(timestamp, rpm, vl):
	with open(CSV_FILENAME, 'a', newline='') as csvfile:
		writer = csv.writer(csvfile)
		if csvfile.tell() == 0:
			writer.writerow(CSV_HEADER)
		writer.writerow([timestamp, f"{rpm:.2f}", f"{vl:.2f}"])

def on_connect(client, userdata, flags, rc):
	print("Conectado con codigo de resultado " + str(rc))
	client.subscribe("motor/data")

def on_message(client, userdata, msg):
	print(msg.topic + " " + str(msg.payload.decode()))
	try:
		data = json.loads(msg.payload.decode())
		rpm = data.get("rpm")
		vl = data.get("vl")
		if rpm is  not None and vl is not None:
			timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			write_to_csv(timestamp, rpm, vl)
			plot_data(vl, rpm)
			print(f"Datos guardados en {CSV_FILENAME} Timestamp={timestamp}, RPM={rpm:.2f}, Velocidad Lineal={vl:.2f} m/s")
		else:
			print("Error: Datos RPM o velocidad lineal no encontrados en el JSON")
	except json.JSONDecodeError:
		print("Error: No se pudo decodificar el mensaje JSON")
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.100.72", 1883, 60)
client.loop_forever()

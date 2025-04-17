import paho.mqtt.client as mqtt
import json
import csv
from datetime import datetime

CSV_FILENAME = "motor_data.csv"
CSV_HEADER = ["timestamp", "rpm", "velocidad_lineal"]

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
			print(f"Datos guardados en {CSV_FILENAME} Timestamp={timestamp}, RPM={rpm:.2f}, Velocidad Lineal={vl:.2f} m/s")
		else:
			print("Error: Datos RPM o velocidad lineal no encontrados en el JSON")
	except json.JSONDecodeError:
		print("Error: No se pudo decodificar el mensaje JSON")
	
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("127.0.0.1", 1883, 60)
client.loop_forever()

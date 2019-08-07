import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time, math, datetime

mqtt_ip = "your ip"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_ip, 1883, 60)

time = datetime.datetime.now()
timeshort_str = time.strftime("%H:%M")
timelong_str = time.strftime("%H:%M:%S")

client.publish('information/time/time_local_hhmm', timeshort_str)
client.publish('information/time/time_local_hhmmss', timelong_str)

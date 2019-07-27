# coding: utf-8

# just run this script via a cronjob every X Minutes
# this script pushes the actual weather from your choosen city to MQTT Channels (weather provided from openweathermap.org, you need a free account)

import json, requests, logging, traceback, datetime, time
import paho.mqtt.client as mqtt

#Settings
mqttip = "<IP FROM THE MQTT SERVER>"
cityID = '<OPENWEATHERMAP CITY ID>'  #this is the ID from the City we want the weather from, just check out their list: http://bulk.openweathermap.org/sample/
appID = '<OPENWEATHERMAP APP ID - CREATE AN FREE ACCOUNT AND SETUP AN APP AT OPENWEATHERMAP.ORG>'
mqttchannel = "information/actualweather/"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.connect(mqttip, 1883, 60)  #here you can change the Port of your MQTT Server, not needed for default settings

url = 'http://api.openweathermap.org/data/2.5/weather?id=' + cityID + '&appid=' + appID

#get data and parse it
resp = requests.get(url)
data = resp.json()

temp = data['main']['temp'] - 273.15
hum = data['main']['humidity']
pressure = data['main']['pressure']
rain = 'no rain'
snow = 'no snow'
thunderstorm = 'no thunderstorm'
clouds = data['clouds']['all']
windspeed = data['wind']['speed']

# I am converting the openweathermap weather-codes into small strings: (light/heavy) rain, etc. because I want to put them on a small display.
if data['weather'][0]['id'] >= 300 and data['weather'][0]['id'] < 400:
    rain = 'l. rain'
elif data['weather'][0]['id'] == 500:
    rain = 'l. rain'
elif data['weather'][0]['id'] >= 501 and data['weather'][0]['id'] <= 503:
    rain = 'rain'
elif data['weather'][0]['id'] >= 504 and data['weather'][0]['id'] < 600:
    rain = 'h. rain'

if data['weather'][0]['id'] >= 600 and data['weather'][0]['id'] < 700:
    snow = 'snow'

if data['weather'][0]['id'] >= 200 and data['weather'][0]['id'] < 211:
    thunderstorm = 'thunderstorm'
elif data['weather'][0]['id'] >= 211 and data['weather'][0]['id'] < 300:
    thunderstorm = 'h. thunderstorm'

try:
    weatherHourlyRain = data["rain"]["3h"]/3
except:
    weatherHourlyRain = 0
try:
    weatherHourlySnow = data["snow"]["3h"]/3
except:
    weatherHourlySnow = 0

client.publish(mqttchannel+"Temperature1", payload=temp, retain=True, qos=1)    # °C
time.sleep(1)
client.publish(mqttchannel+"Humidity1", payload=hum, retain=True, qos=1)    # %
time.sleep(1)
client.publish(mqttchannel+"Pressure", payload=pressure, retain=True, qos=1)    # hPa
time.sleep(1)
client.publish(mqttchannel+"Rain", payload=rain, retain=True, qos=1)    #only "l. rain", "rain", "h. rain", "no rain"
time.sleep(1)
client.publish(mqttchannel+"Snow", payload=snow, retain=True, qos=1)    #only "snow" or "no snow"
time.sleep(1)
client.publish(mqttchannel+"Thunderstorm", payload=thunderstorm, retain=True, qos=1)    #only "no thunderstorm", "thunderstorm", "h. thunderstorm"
time.sleep(1)
client.publish(mqttchannel+"Clouds", payload=clouds, retain=True, qos=1)    # %
time.sleep(1)
client.publish(mqttchannel+"Windspeed", payload=windspeed, retain=True, qos=1) # m/s
time.sleep(1)
client.publish(mqttchannel+"Rainamount", payload=weatherHourlyRain, retain=True, qos=1) # mm/h
time.sleep(1)
client.publish(mqttchannel+"Snowamount", payload=weatherHourlySnow, retain=True, qos=1) # mm/h


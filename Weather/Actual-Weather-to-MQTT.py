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

client.publish(mqttchannel+"Temperature", payload=temp, retain=True) # Temp in Celsius
client.publish(mqttchannel+"Humidity", payload=hum, retain=True) # Humidity in Percent
client.publish(mqttchannel+"Pressure", payload=pressure, retain=True) # Pressure
client.publish(mqttchannel+"Rain", payload=rain, retain=True) # Rain as a String
client.publish(mqttchannel+"Snow", payload=snow, retain=True) # Snow as a String
client.publish(mqttchannel+"Thunderstorm", payload=thunderstorm, retain=True) # Thunderstorm as a String
client.publish(mqttchannel+"Clouds", payload=clouds, retain=True) # Clouds in Percent
client.publish(mqttchannel+"Windspeed", payload=windspeed, retain=True) # Windspeed

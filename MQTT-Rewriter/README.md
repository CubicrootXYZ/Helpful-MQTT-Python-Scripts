## MQTT Rewriter

This script rewrites MQTT messages. I am using this to rewrite the ENERGY message from Sonoff-Tasmota, which is json formatted, into single topics for power, current, voltage...

You can add your own rules to this script.

The given rules will do the following:

For .../steckdose.../SENSOR => extract the JSON and push "Power", "Today", "Total", "Current", "Voltage" to ".../steckdose.../SENSOR/POWER", ".../steckdose.../SENSOR/TODAY" and so on. 

For .../steckdose.../POWER it will convert ON/OFF to 1/0 and publish it in ".../steckdose.../POWER/POWERBINARY".

**How to Install**
1. Download the whole folder
2. Add settings to the settings.ini, leave password and user for the MQTT-Server empty if not set
3. Change the working directory if you do not execute the script from it's initial folder (Not needed if you execute the script from it's folder). Therefore open run.py and uncomment the "#os.chdir("path to folder")", add the path to the folder where the run.py is located in. 
4. Exectue the run.py with python 3

**How to add rules**
1. Check for the right place in the code, it is commented
2. Create a 
```
if "your keyword" in msg.topic
```
or 
```
if "your keyword" in str(msg.payload, 'utf-8')
```
You can combine them with and, or ...

3. Do whatever you whant with the payload

4. Push your new messages into some other topics with
```
self.mqttPublish(topic, message)
```

### Known Issues

**Not able to fetch all messages**

This script will pass some messages if they are send to quickly and are not send with QOS 1. To avoid this set all messages to QOS 1 and use sleeps when pushing many messages at the same time. 1 sec delay is enough.

**Script does not execute, because the settings.ini file could not be read**

Check if the executing user has permission to read the ini file. Otherwise check if you are executing the run.py from it's folder or change the working directory (see the How to Install section).

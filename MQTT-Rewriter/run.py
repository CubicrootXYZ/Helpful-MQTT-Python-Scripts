import paho.mqtt.client as mqtt
import configparser, logging, os, json

# Set your working folder if it is not the same as the folder this file is located in
#print(os.getcwd())
#os.chdir("patho to folder")

config = configparser.ConfigParser()
config.readfp(open('settings.ini'))

mqttIp = config.get('mqtt', 'ip')
mqttPort = config.get('mqtt', 'port')
mqttUser = config.get('mqtt', 'user')
mqttPassword = config.get('mqtt', 'password')

class PowerplugRewriter():

    def __init__(self, mqttIp, mqttPort, mqttUser, mqttPassword):
        self.mqttIp = mqttIp
        self.mqttPort = mqttPort
        self.mqttUser = mqttUser
        self.mqttPassword = mqttPassword
        self.mqttClient = mqtt.Client()
        self.mqttTopic = mqttTopic

        # create logger
        self.logger = logging.getLogger('PowerplugRewriter')
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.log = logging.FileHandler('powerplugrewriter.log')
        self.log.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(formatter)
        self.log.setFormatter(formatter)
        self.logger.addHandler(self.ch)
        self.logger.addHandler(self.log) 

    def mqttSub(self):
        if len(self.mqttUser) > 1:
            self.mqttClient.username_pw_set(self.mqttUser, password=self.mqttPassword)
        self.mqttClient.connect(self.mqttIp, int(self.mqttPort), 60)
        
        self.mqttClient.on_connect = self.mqttConnect
        self.mqttClient.on_message = self.mqttMessage

        self.mqttClient.subscribe("#")
        self.mqttClient.loop_forever()
        

    def mqttMessage(self, client, userdata, msg):
        self.logger.debug("Got MQTT Message: %s at %s", str(msg.payload, 'utf-8'), msg.topic)

        if "steckdose" in msg.topic and "SENSOR" in msg.topic:
            try:
                data = json.loads(str(msg.payload, 'utf-8'))
                power = data['ENERGY']['Power']
                totalpower = data['ENERGY']['Total']
                todaypower = data['ENERGY']['Today']
                voltage = data['ENERGY']['Voltage']
                current = data['ENERGY']['Current']
            except Exception as e:
                self.logger.error("Could not get value Energy -> Power: %s", e)
                return False

            self.mqttPublish(msg.topic+"/POWER", power)      
            self.mqttPublish(msg.topic+"/TODAY", todaypower)
            self.mqttPublish(msg.topic+"/TOTALPOWER", totalpower)    
            self.mqttPublish(msg.topic+"/VOLTAGE", voltage)
            self.mqttPublish(msg.topic+"/CURRENT", current) 

        if "steckdose" in msg.topic and "stat/POWER" in msg.topic:
            if str(msg.payload, 'utf-8') == "ON":
                state = 1
            elif str(msg.payload, 'utf-8') == "OFF": 
                state = 0
            else: 
                return False
            
            self.mqttPublish(msg.topic+"/POWERBINARY", state)
            
         #INSERT YOUR OWN RULES HERE
         #msg.topic is the topic
         #msg.payload the payload
         #publish with self.mqttPublish(topic, message) 
                          

    def mqttConnect(self):
        self.logger.info('Connected to MQTT')

    def mqttPublish(self, topic, message):
        try:
            self.mqttClient.publish(topic, message, qos=1)
            self.logger.debug("Published at %s: %s", topic, message)
        except Exception as e: 
            self.logger.error("Could not publish: %s", e)
            return False

    def __exit__(self, type, value, tb):
        self.log.close()
        self.ch.close()
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()

run = PowerplugRewriter(mqttIp, mqttPort, mqttUser, mqttPassword)
run.mqttSub()

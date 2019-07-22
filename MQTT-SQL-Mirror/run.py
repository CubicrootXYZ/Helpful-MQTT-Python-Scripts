from includes import mysql
import paho.mqtt.client as mqtt
import configparser, logging, os

# Set your working folder if it is not the same as the folder this file is located in
#print(os.getcwd())
#os.chdir("path to folder")

config = configparser.ConfigParser()
config.readfp(open('settings.ini'))

dbHost = config.get('database', 'host')
dbDatabasePrefix = config.get('database', 'database_prefix')
dbDatabase = config.get('database', 'database')
dbUser = config.get('database', 'user')
dbPassword = config.get('database', 'Password')

mqttIp = config.get('mqtt', 'ip')
mqttPort = config.get('mqtt', 'port')
mqttUser = config.get('mqtt', 'user')
mqttPassword = config.get('mqtt', 'password')

class MqttSqlMirror():

    def __init__(self, dbHost, dbDatabase, dbDatabasePrefix, dbUser, dbPassword, mqttIp, mqttPort, mqttUser, mqttPassword):
        print('1')
        self.dbHost = dbHost
        self.dbDatabasePrefix = dbDatabasePrefix
        self.dbUser = dbUser
        self.dbPassword = dbPassword
        self.mqttIp = mqttIp
        self.mqttPort = mqttPort
        self.mqttUser = mqttUser
        self.mqttPassword = mqttPassword
        self.mqttClient = mqtt.Client()
        

        # create logger
        self.logger = logging.getLogger('MQTTSQLMIRROR')
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.log = logging.FileHandler('mqttsqlmirror.log')
        self.log.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(formatter)
        self.log.setFormatter(formatter)
        self.logger.addHandler(self.ch)
        self.logger.addHandler(self.log) 

        # Establish mysql connection
        self.mysqlCon = mysql.Database(dbHost, dbDatabase, dbUser, dbPassword, self.logger)

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
        channel = msg.topic.replace("/", "_")
        channel = self.dbDatabasePrefix + channel

        if self.mysqlCon.connect() == True:
            if self.mysqlCon.createTable(self.dbDatabasePrefix+channel, ['value VARCHAR(1000)']) == False:
                self.logger.error('Not able to create a new table')
                return False            

            insert = self.mysqlCon.insertInto(channel, ['value', str(msg.payload, 'utf-8')])

            if insert == False:
                self.logger.error('Not able to insert data')
                return False

            self.mysqlCon.close()
            return True    
        self.logger.error("Not able to connector to DB")
        return False

    def mqttConnect(self):
        self.logger.info('Connected to MQTT')

    def __exit__(self, type, value, tb):
        self.log.close()
        self.ch.close()
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()

run = MqttSqlMirror(dbHost, dbDatabase, dbDatabasePrefix, dbUser, dbPassword, mqttIp, mqttPort, mqttUser, mqttPassword)
run.mqttSub()

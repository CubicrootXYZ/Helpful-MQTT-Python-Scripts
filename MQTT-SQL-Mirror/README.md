## MQTT SQL Mirror

This script mirrors your whole MQTT-Traffic into a MySQL-Database. I am using this for 2 purposes: check if everything is working properly and to monitor home automation sensors with Grafana.

**How to Install**
1. Download the whole folder
2. Add settings to the settings.ini, leave password and user for the MQTT-Server empty if not set
3. Change the working directory if you do not execute the script from it's initial folder (Not needed if you execute the script from it's folder). Therefore open run.py and uncomment the "#os.chdir("path to folder")", add the path to the folder where the run.py is located in. 
4. Exectue the run.py with python 3

**The Database Structure**

This script adds a table for each MQTT-Channel. If there is a message pushed it will be saved to the corresponding table with time as a sql datetime object and value as the message stored as string.

**How to set up Grafana with this data**

The data that is aggregated here is also available for Grafana. Just follow these Instructions:
1. add the MySQL-Database as source in Grafana
2. add a new Dashboard
3. add a new item with this custom SQL-Query:
```
SELECT
  time,
  min(CAST(value as decimal(10,2))),
  'Name of the Values' as metric
FROM your_table_name
WHERE $__timeFilter(time)
GROUP BY time
ORDER BY time
```

### Known Issues

**Not able to fetch all messages**

This script will pass some messages if they are send to quickly and are not send with QOS 1. To avoid this set all messages to QOS 1 and use sleeps when pushing many messages at the same time. 1 sec delay is enough.

**Script does not execute, because the settings.ini file could not be read**

Check if the executing user has permission to read the ini file. Otherwise check if you are executing the run.py from it's folder or change the working directory (see the How to Install section).

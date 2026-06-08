import yaml
import time
import json
import os.path
import math

backups_data_filename = "backups_data.json"


# load timers settings

timers_settings_file = "settings_timers.yml"
timers_settings = []

with open(timers_settings_file, 'r') as f:
   data = yaml.load_all(f, Loader=yaml.FullLoader)

   for doc in data:
      timers_settings.append(doc)


# get the lowest timer

lowestTimer = None

for timer in timers_settings:
   if not lowestTimer:
      lowestTimer = timer
   else:
      if timer['timer_minutes'] < lowestTimer['timer_minutes']:
         lowestTimer = timer


# load paths settings

backups_settings_file = "settings_paths.yml"
backups_path = ""

with open(backups_settings_file, 'r') as f:
   data = yaml.load(f, Loader=yaml.FullLoader)

   backups_path = data['backups_path']

backups_data_path = backups_path + '/' + backups_data_filename

print(backups_path)


def getMinute():
   return math.floor(time.time() / 60)


def readBackupsData():
   with open(backups_data_path, 'r') as f:
      return json.load(f)

def writeBackupsData(data):
   json_str = json.dumps(data, indent=4)

   with open(backups_data_path, 'w') as f:
      f.write(json_str)


def initialiseBackupsData():
   data = {}
   minute = getMinute()

   for timer in timers_settings:
      data[timer['name']] = minute

   writeBackupsData(data)

   backup(lowestTimer)

def backup(timer):
   pass


# initialise the backups data file if it doesnt exist 
if not os.path.isfile(backups_data_path):
   initialiseBackupsData()


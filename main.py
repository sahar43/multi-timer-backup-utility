import yaml
import time
import datetime
import json
import os.path
import math
import lz4.frame
import tarfile

backups_data_filename = "backups_data.json"


# load timers settings

timers_settings_file = "settings_timers.yml"
timers_settings = []

with open(timers_settings_file, 'r') as f:
   data = yaml.load_all(f, Loader=yaml.FullLoader)

   for doc in data:
      timers_settings.append(doc)


# get the lowest timer

lowest_timer = None
lowest_timer_minutes = None

for timer in timers_settings:
   if not lowest_timer:
      lowest_timer = timer
   else:
      if timer['timer_minutes'] < lowest_timer['timer_minutes']:
         lowest_timer = timer

lowest_timer_minutes = lowest_timer['timer_minutes']


# load paths settings

backups_settings_file = "settings_paths.yml"
backups_path = ""
to_backup_path = ""

with open(backups_settings_file, 'r') as f:
   data = yaml.load(f, Loader=yaml.FullLoader)

   backups_path = data['backups_path']
   to_backup_path = data['to_backup_path']

backups_data_path = backups_path + '/' + backups_data_filename


def getMinute():
   return math.floor(time.time() / 60)

def getDateStr():
   return datetime.datetime.now().strftime("%H:%M %d-%m-%y")


def readBackupsData():
   with open(backups_data_path, 'r') as f:
      return json.load(f)

def writeBackupsData(timers_last_minute, timers_backups_ordered):
   data = {
      'timers_last_minute': timers_last_minute,
      'timers_backups_ordered': timers_backups_ordered
   }

   writeBackupsData(data)

def writeBackupsData(data):
   json_str = json.dumps(data, indent=4)

   with open(backups_data_path, 'w') as f:
      f.write(json_str)


def initialiseBackupsData():
   minute = getMinute()

   timers_last_minute = {}
   timers_backups_ordered = {}
   
   for timer in timers_settings:
      name = timer['name']
      timers_last_minute[name] = minute
      timers_backups_ordered[name] = []

   writeBackupsData(timers_last_minute, timers_backups_ordered)

   backup(lowest_timer)


def backup(timer):
   def createBackup(timer, data):
      # create the lz4 backup file

      filename = getDateStr() + " " + timer['name'] + ".tar.lz4"
      
      with open(backups_path + "/" + filename, mode='wb') as file: # get the file
         with lz4.frame.open(file, mode='wb') as lz4_file: # get the lz4 frame file
            with tarfile.open(fileobj=lz4_file, mode='w|') as tar: # open the lz4 frame file with streaming mode
               tar.add(to_backup_path, arcname=os.path.basename(to_backup_path)) # arcname ensures that the archive doesn't contain the full absolute path
      
      # add the backup file to the list



   def deleteLastBackup(data):
      def delete():
         pass ## TODO

      pass ## TODO
   
   def countBackups(timer, data):
      return len(data['timers_backups_ordered'][timer['name']])


   data = readBackupsData()

   createBackup(timer, data)

   if (countBackups(timer, data) > timer['keep_amount']):
      deleteLastBackup()
   
   writeBackupsData(data)
   
   print(countBackups(timer, data)) # TODO REMOVE


def clock():
   while True:
      time.sleep(lowest_timer_minutes*60)

      ## TODO: check and trigger backup


# initialise the backups data file if it doesnt exist 
if not os.path.isfile(backups_data_path):
   initialiseBackupsData()

#clock() # TODO ENABLE



#backup(lowest_timer)

from pathlib import Path

Path.rmdir(to_backup_path)
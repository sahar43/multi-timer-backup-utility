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

backups_data_path = os.path.join(backups_path, backups_data_filename)


def getMinute():
   return math.floor(time.time() / 60)

def getDateStr():
   return datetime.datetime.now().strftime("%H:%M %d-%m-%y")


def readBackupsData():
   with open(backups_data_path, 'r') as f:
      return json.load(f)

def writeBackupsDataExtended(timers_last_minute, timers_backups_ordered):
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
   timers_last_minute = {}
   timers_backups_ordered = {}
   
   for timer in timers_settings:
      name = timer['name']
      timers_last_minute[name] = 0 # set it to 0 be default to make the longest backups first
      timers_backups_ordered[name] = []

   writeBackupsDataExtended(timers_last_minute, timers_backups_ordered)

   backup(lowest_timer)


def backup(timer):
   def createBackup(timer, data):
      # create the lz4 backup file
      filename = getDateStr() + " " + timer['name'] + ".tar.lz4"
      
      with open(os.path.join(backups_path, filename), mode='wb') as file: # get the file
         with lz4.frame.open(file, mode='wb') as lz4_file: # get the lz4 frame file
            with tarfile.open(fileobj=lz4_file, mode='w|') as tar: # open the lz4 frame file with streaming mode
               tar.add(to_backup_path, arcname=os.path.basename(to_backup_path)) # arcname ensures that the archive doesn't contain the full absolute path
      
      # add the newest minute
      data['timers_last_minute'][timer['name']] = getMinute()

      # add the backup file to the list
      data['timers_backups_ordered'][timer['name']].append(filename)


   def countBackups(timer, data):
      return len(data['timers_backups_ordered'][timer['name']])


   def deleteOldestBackup(data):
      def delete(filepath):
         os.remove(filepath)
      
      delete(os.path.join(backups_path, data['timers_backups_ordered'][timer['name']][0]))

      data['timers_backups_ordered'][timer['name']].pop(0)


   data = readBackupsData()

   createBackup(timer, data)

   while (countBackups(timer, data) > timer['keep_amount']):
      deleteOldestBackup(data)
   
   writeBackupsData(data)


def clock():
   def chooseTimer():
      minute = getMinute()
      data = readBackupsData()

      def getTimerMinutes(timer):
         return timer['timer_minutes']

      # get the elapsed minutes since the latest backup of that timer
      def getLatestElapsed(timer):
         return minute - data['timers_last_minute'][timer['name']]

      # get the timers that can be chosen (elapsed time high enough)
      valids = [timer for timer in timers_settings if getLatestElapsed(timer) > getTimerMinutes(timer)]

      # choose the one with the highest timer minutes
      if (valids and len(valids) > 0):
         chosen = None

         for timer in valids:
            if not chosen:
               chosen = timer
            else:
               if getTimerMinutes(timer) > getTimerMinutes(chosen):
                  chosen = timer
         
         return chosen

   while True:
      timer = chooseTimer()

      if timer:
         backup(timer)

      time.sleep(lowest_timer_minutes*60) # TODO: move to front


# initialise the backups data file if it doesnt exist 
if not os.path.isfile(backups_data_path):
   initialiseBackupsData()

clock()
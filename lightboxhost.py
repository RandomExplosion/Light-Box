from datetime import datetime, timedelta, time #Timestamps
import subprocess
import json

#Load alarm configuration
userconfig = json.load(open("MedicationInfo.json", "r"))

remHost = None

while True:
    now = datetime.now() #Get current time and date

    #Launch reminderhost.py
    remHost = subprocess.Popen("reminderhost.py")

    #Calculate seconds until next day
    tomorrow = now + datetime.timedelta(days=1)
    countdown = int(datetime.datetime.combine(tomorrow, datetime.time.min) - now)

    #Wait until next day
    time.sleep(countdown+1)

    #Kill reminderhost so we can reopen it
    remHost.kill()

    
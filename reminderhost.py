from datetime import datetime, timedelta, time #Timestamps
import subprocess
import json

#Load alarm configuration
userconfig = json.load(open("MedicationInfo.json", "r"))

def isscheduledholiday (config):


#Figure out if we are in a holiday or (weekend)
holiday = False

now = datetime.now;

#Check if it's a weekend
if now.strftime("%a") == "Sat" or now.strftime("%a") == "Sun":
    holiday = True #Weekends are usually holidays
elif 

#!/usr/bin/env python3
from datetime import datetime, timedelta, time #Timestamps
import subprocess
import json
from time import sleep

class LightBoxHost:
    """
        The root of the program, responsible for cycling the instance of ReminderHost at the start of every day
    """

    def __init__(self):

        #Load alarm configuration
        #lightBoxConfig = json.load(open("MedicationInfo.json", "r"))

        remHost = None

        while True:

            now = datetime.now() #Get current time and date

            #Launch reminderhost.py
            remHost = subprocess.Popen("py ReminderHost.py")

            #Calculate seconds until next day
            tomorrow = now + timedelta(days=1)
            countdown = (datetime.combine(tomorrow, time.min) - now)

            print("Time until next day: " + countdown.total_seconds() + "s")

            #Wait until next day
            sleep(countdown.total_seconds())

            #Kill reminderhost so we can reopen it
            remHost.kill()

current = LightBoxHost()
    
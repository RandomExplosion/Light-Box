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

        #Load reminder configuration
        config = json.load(open("MedicationInfo.json", "r"))

        remHost = None

        #Blink all LEDS at once so we know that they all work
        numButtons = len(config['users'])

        while True:

            now = datetime.now() #Get current time and date

            #Launch reminderhost.py
            remHost = subprocess.Popen("python3 ReminderHost.py")

            #Calculate seconds until next day
            tomorrow = now + timedelta(days=1)
            countdown = (datetime.combine(tomorrow, time.min) - now)

            print("Time until next day: " + str(countdown.total_seconds()) + "s")

            #Wait until next day
            sleep(countdown.total_seconds())

            #Kill reminderhost so we can reopen it
            remHost.kill()

#Init
current = LightBoxHost()
    
#!/usr/bin/env python3
from datetime import datetime, timedelta, time #Timestamps
import subprocess
import json
from operator import attrgetter
from time import sleep

class ReminderHost:
    #Summary
    """
        This class manages all the reminders that go off in a day.
        The class is instantiated as a subprocess by lightboxhost.py once per day,
        and is replaced at the end of the day by a new instance.
    """

    lightBoxConfig = None
    todaysReminders = []
    reminderProcesses = []

    def __init__(self):

        #Load alarm configuration
        lightBoxConfig = json.load(open('MedicationInfo.json', "r"))

        #Which reminder settings do we use (holiday or normal)
        reminderCollection = "alarms"

        #Determine if today is a holiday
        if ReminderHost.isScheduledHoliday(lightBoxConfig):
            #If so use holiday settings
            reminderCollection = "alarms-h"

        #Get all users
        users = lightBoxConfig["users"]

        #Loop through users by index
        for i in range(len(users)):
            
            #Add entry for user's current active reminder handle
            self.reminderProcesses.append(None)

            #Add each reminder to the list of reminders for today
            for reminder in users[i][reminderCollection]:
                
                #Mark reminder with user index for later reference
                reminder["user-id"] = i

                #Add to the list of reminders for today
                self.todaysReminders.append(reminder)
        
        #Sort by time
        self.todaysReminders.sort(key=lambda x: x["light-on"], reverse=False)

        for reminder in self.todaysReminders:

            #get current time
            now = datetime.now()

            #Skip if light on time has already passed (if this was started late)
            if datetime.strptime(reminder["light-on"], "%H:%M").time() < now.time():
                print(f'Skipping reminder: \"{reminder["label"]}\" at {reminder["light-on"]}')
                continue

            else:
                #Calculate time until next reminder
                nextReminderCountdown = (datetime.strptime(f'{now.strftime("%d/%m/%Y")} {reminder["light-on"]}', "%d/%m/%Y %H:%M") - now)

                #Log
                print(f'Next reminder ({reminder["label"]}) from user: \"{reminder["user-id"]}\" in {nextReminderCountdown.total_seconds()}s')
                
                #Sleep until such a time
                sleep(nextReminderCountdown.total_seconds())

                #Get process handle for user
                existingHandle  = self.reminderProcesses[reminder["user-id"]]

                #If the user has a reminder still active, kill it and set to None
                if existingHandle != None:
                    existingHandle.kill()
                    
                #Run the reminder and cache the process handle
                #self.reminderProcesses[reminder["user-id"]] = subprocess.Popen(["py", "Reminder.py", f"\"{reminder}\""])

            

    @staticmethod
    def isScheduledHoliday(config):
        #Figure out if we are in a holiday (or weekend)
        isHoliday = False

        #Get current time
        now = datetime.now()

        #Check if it's a weekend
        if now.strftime("%a") == "Sat" or now.strftime("%a") == "Sun":
            isHoliday = True #Weekends are usually holidays

        #Loop through determined public holidays, check if today matches any of them
        for day in config["public-holidays"]:
            if now.strftime("%d/%m") == day["date"]:
                isHoliday = True

        #Check if we are in a scheduled break (between terms etc.)
        for holiday in config["holiday-seasons"]:
            #Retrieve start and end dates so we can compare now to them
            startDate = datetime.strptime(str(holiday["start-date"]), "%d/%m")
            endDate = datetime.strptime(str(holiday["start-date"]), "%d/%m")

            #If the date is between the start and end of a holiday
            if startDate < now < endDate:
                isHoliday = True

        return isHoliday

remHost = ReminderHost()
#!/usr/bin/env python3
from datetime import datetime, timedelta, time #Timestamps
import subprocess
import json
from Reminder import Reminder
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

    def __init__(self):

        #Load alarm configuration
        lightBoxConfig = json.load(open('MedicationInfo.json', "r"))

        #Which reminder settings do we use (holiday or normal)
        reminderCollection = "alarms"

        #Determine if today is a holiday
        if ReminderHost.isScheduledHoliday(lightBoxConfig):
            #If so use holiday settings
            reminderCollection = "alarms-h"

        #Loop through users and cache all alarms for today
        for user in lightBoxConfig["users"]:
            for reminder in user[reminderCollection]:
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

                print(f'Next reminder ({reminder["label"]}) in {nextReminderCountdown.total_seconds()}s')

                sleep(nextReminderCountdown.total_seconds())

                print('TODO: REMINDER SCRIPT')

            

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

testhost = ReminderHost()
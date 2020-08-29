#!/usr/bin/env python3
from datetime import datetime, timedelta, time  #Timestamps
#Multiprocessing
from multiprocessing import Process, parent_process, current_process, log_to_stderr  
import logging                                  #For error routing
import json                                     #Json Integration    
from gpiozero import LEDBoard                   #Mass LED control
from operator import attrgetter                 #Janky attribute fetching
from time import sleep                          #Thread blocking
from sys import argv                            #CLI arguments
import Reminder                                 #For reminder handling
import atexit                                   #Reminder class
from Util import printfl                        #For flushed printing

class ReminderHost:
    #Summary
    """
        This class manages all the reminders that go off in a day.
        The class is instantiated as a process by lightboxhost.py once per day,
        and is replaced at the end of the day by a new instance. (Courtesy of LightBoxHost.py)
    """

    lightBoxConfig = None
    todaysReminders = []
    reminderProcesses = []

    def __init__(self, lightBoxConfig):
        #Set up error passing
        log_to_stderr(logging.CRITICAL)

        #Set up onexit
        atexit.register(self.onExit)

        #Get list of all the user's leds
        ledpins = []
        for user in lightBoxConfig["users"]:
            ledpins.append(user["pins"]["led"])
        
        #Assemble LEDBoard from all led pins
        leds = LEDBoard(*ledpins)

        #Turn on all the leds for the duration of the init phase
        leds.on()

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
            
            #Add entry for user's current active reminder handle (so we can set it later without having index out of range)
            self.reminderProcesses.append(None)

            #Add each reminder to the list of reminders for today
            for reminder in users[i][reminderCollection]:
                
                #Mark reminder with user index for later reference
                reminder["user-id"] = i
                #Add Pinout information for use in Reminder.Reminder
                reminder["pins"] = users[i]["pins"]

                #Add to the list of reminders for today
                self.todaysReminders.append(reminder)
        
        #TODO: Launch Sound Player Script and establish link with reminderProcesses over shared memory

        #Sort by time
        self.todaysReminders.sort(key=lambda x: x["light-on"], reverse=False)

        #Init is complete so disable leds
        leds.off()
        leds.close()
        #Log
        printfl("ReminderHost.py: Initialisation phase complete")

        for reminder in self.todaysReminders:

            #get current time
            now = datetime.now()

            #Skip if light on time has already passed (if this was started late) and that more than one second has passed (accounting for execution time of previous reminder)
            if datetime.strptime(reminder["light-on"], "%H:%M").time() < now.time() and now.time() > datetime.strptime(f'{reminder["light-on"]}:01', "%H:%M:%S").time():
                printfl(f'ReminderHost: Skipping reminder: \"{reminder["label"]}\" at {reminder["light-on"]}')

                continue

            else:
                #Calculate time until next reminder
                nextReminderCountdown = (datetime.strptime(f'{now.strftime("%d/%m/%Y")} {reminder["light-on"]}', "%d/%m/%Y %H:%M") - now)

                #Log
                printfl(f'ReminderHost: Next reminder ({reminder["label"]}) from user: \"{reminder["user-id"]}\" in {nextReminderCountdown.total_seconds()}s')

                #Sleep until such a time if we aren't behind schedule (if we are it is because two reminders are set for the same time)
                if nextReminderCountdown.total_seconds() > 0:
                    sleep(nextReminderCountdown.total_seconds())

                #Get process handle for user
                existingHandle  = self.reminderProcesses[reminder["user-id"]]

                #If the user has a reminder still active, kill it and set to None
                if existingHandle != None:
                    printfl(f'ReminderHost: Found undismissed reminder ({existingHandle.name}) for user \"{reminder["user-id"]}\"')
                    existingHandle.terminate()
                    
                #Run the reminder and cache the handle
                self.reminderProcesses[reminder["user-id"]] = Process(name=f'Reminder: \"{reminder["label"]}\"', target=Reminder.Reminder, args=(reminder,), daemon=True)
                self.reminderProcesses[reminder["user-id"]].start()

    @staticmethod
    def isScheduledHoliday(config):
        """
            Calculates based on config parameter whether or not today is a holiday (See ConfigurationSchema.json)
        """

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
            if startDate <= now <= endDate:
                isHoliday = True

        return isHoliday

    def onExit(self):
        for reminder in self.reminderProcesses:
            if reminder != None:
                reminder.terminate()
#!/usr/bin/env python3
from datetime import datetime, timedelta, time  #Timestamps
import json
from gpiozero import LED, Button                #Buttons
from multiprocessing import current_process     #Multiprocessing
#import playsound                               #Irritating reminder noises intensify (NYI)
from time import sleep
import atexit
from Util import printfl                #printfling and flushing to parent process
from signal import pause
from sys import exit

class Reminder:
    """
        This class represents a single reminder.
        It should be instantiated as a child process of ReminderHost.py.
        It Handles the execution of a single reminder.
    """

    #Properties
    label = "A Nameless Reminder ¯\\_(ツ)_/¯"    #Friendly name for the reminder 
    lightOn = time                              #Time to put the light on (24h time)
    gracePeriod = 5                             #Grace period before alarm (in minutes)

    #GPIO
    led = None
    button = None
    buttonheld = False
    snoozed = False     #Are we snoozed?
    process = None      #This process

    def __init__(self, data):
        
        #Sleep to ensure log order
        sleep(0.5)

        #Atexit registration
        atexit.register(self.dismiss)

        #Label
        #if hasattr(data, "label") and data["label"] != "":
        self.label = data["label"]

        #Light on time
        try:
            self.lightOn = datetime.strptime(data["light-on"], "%H:%M")

        except Exception as identifier:
            self.lightOn = time.min()

        #Grace period
        if hasattr(data, "grace-period") and data["grace-period"] > 0:
            self.gracePeriod = data["grace-period"]

        #Led and button init
        self.led = LED(data["pins"]["led"])
        self.button = Button(data["pins"]["button"], hold_time=2)

        #Led and button events
        self.button.when_released = self.released
        #self.button.when_held = self.when_held

        #Raise the reminder
        self.raiseReminder()

        #wait for button press
        self.button.wait_for_release()
        sleep(0.5)  #Sleep to allow for button press to be processed
        exit(0)


    #N.Y.I
    #def soundAlarm(self, ontime=1, offtime=1):
        # if not(self.snoozed):
        #     self.buzzer.on()    #Beep On
        # sleep(ontime) 
        # if not(self.snoozed):
        #     self.buzzer.off()   #Beep Off
        # sleep(offtime)

    def raiseReminder(self):
        printfl(f"Reminder[{self.label}]: Raising")
        self.led.blink(1, 1, 2)       #Blink Twice
        self.led.on()                   #Turn on Led
        sleep(self.gracePeriod)         #Allow Grace Period
       #while True:                     #Sound Alarm until script is terminated
       #    self.soundAlarm()

    def dismiss(self):
        """
        Kills the process and disables led
        """
        printfl(f"Reminder[{self.label}]: Dismissed")
        self.led.off()          #Cut led
        self.button.close()     #Free up button pin
        self.led.close()        #Free up led pin
        return                  #Terminate Script

    def snooze(self):
        self.snoozed = True
        printfl(f"Reminder[{self.label}]: User Snoozed for 5 minutes")
        sleep(60*5)
        self.snoozed = False

    #Update held
    def when_held(self, button):
        self.buttonheld = True

    #When button is released
    def released(self, button):
        #if not self.buttonheld:
        #    self.snooze()   #Snooze if the button was just pressed
        #else:
        self.dismiss()  #Dismiss if it wasn't held
        #self.buttonheld = False
#!/usr/bin/env python3
from datetime import datetime, timedelta, time #Timestamps
import json
from gpiozero import LED, Button    #Buttons
import playsound                    #Irritating reminder noises intensify
import sys
from time import sleep

class Reminder:

    #Properties
    label = ""          #Friendly name for the reminder 
    lightOn = time      #Time to put the light on (24h time)
    gracePeriod = 5     #Grace period before alarm (in minutes)

    #GPIO
    led = LED()
    button = Button(hold_time=5)
    
    snoozed = False     #Are we snoozed?

    def __init__(self, data):

        #Label
        if data["label"].label != "":
            self.label = data["label"]

        #Light on time
        try:
            self.lightOn = datetime.strptime(data["light-on"], "%H:%M")

        except Exception as identifier:
            self.lightOn = time.min()

        #Grace period
        if data["gracePeriod"] > 0:
            self.gracePeriod = data["gracePeriod"]

        self.led = LED(data["led"])
        self.button = Button(data["button"], hold_time=5)

        self.button.when_released = self.snooze
        self.button.when_held = self.dismiss

    def soundAlarm(self, ontime=1, offtime=1):
        if not(self.snoozed):
            self.buzzer.on()    #Beep On
        sleep(ontime) 
        if not(self.snoozed):
            self.buzzer.off()   #Beep Off
        sleep(offtime)


    def raiseReminder(self):
        self.led.blink(0.5, 0.5, 2)       #Blink Twice
        self.led.on()                   #Turn on Led
        sleep(self.gracePeriod)         #Allow Grace Period
        while True:                     #Sound Alarm until script is terminated
            self.soundAlarm()

    def dismiss(self):
        """
        Kills the task and disables led
        """
        self.led.off()  #Cut led
        sys.exit(0)     #Terminate Script

    def snooze(self):
        snoozed = True
        sleep(60*5)
        snoozed = False

#Init with command line arg validation
if len(sys.argv) == 1:
    #load args into constructor   
    rem = Reminder(json.loads(sys.argv[0]))

else:
    print("Invalid arg count")
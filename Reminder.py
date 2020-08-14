#!/usr/bin/env python3
from datetime import datetime, timedelta, time #Timestamps
import json

class Reminder:

    #Properties
    label = ""          #Friendly name for the reminder
    lightOn = time()    #Time to put the light on (24h time)
    gracePeriod = 5     #Grace period before alarm (in minutes)

    def __init__(self, _label, _lightOn, _gracePeriod):

        #Label
        if _label != "":
            self.label = _label

        #Light on time
        try:
            self.lightOn = datetime.strptime(_lightOn, "%H:%M")

        except Exception as identifier:
            self.lightOn = time.min()

        if _gracePeriod > 0:
            self.gracePeriod = _gracePeriod
        

        

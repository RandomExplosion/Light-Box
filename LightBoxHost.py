#!/usr/bin/env python3
from datetime import datetime, timedelta, time                          #Timestamps
from multiprocessing import Process, log_to_stderr, set_start_method    #Multiprocessing functions for handling ReminderHost
import json                                                             #Json Serialisation
import logging                                                          #Error routing
import ReminderHost                                                     #ReminderHost class               
from time import sleep                                                  #Thread blocking
import atexit                                                           #Exit callback
import sys                                                              #System utilities
from jsonschema import validate                                         #Json Validation

class LightBoxHost:
    """
        The root of the program, responsible for cycling the instance of ReminderHost at the start of every day
    """

    def __init__(self):

        log_to_stderr(logging.CRITICAL)
        
        #Load reminder configuration
        config = json.load(open("MedicationInfo.json", "r"))

        #Load schema
        schema = json.load(open("ConfigurationSchema.json"))

        #Check configuration against schema (Will error if formatted incorrectly)
        validate(instance=config, schema=schema)

        remHost = None

        while True:

            now = datetime.now() #Get current time and date

            #Launch ReminderHost
            remHost = Process(name="ReminderHost", target=ReminderHost.ReminderHost, args=(config,))
            remHost.start()
            sys.stdin.flush()

            #Calculate seconds until next day
            tomorrow = now + timedelta(days=1)
            countdown = (datetime.combine(tomorrow, time.min) - now)

            print("LightBoxHost: Time until next day: " + str(countdown.total_seconds()) + "s")

            #Wait until next day
            sleep(countdown.total_seconds())

            #Kill reminderhost so we can reopen it
            remHost.kill()

#INIT
current = LightBoxHost()    
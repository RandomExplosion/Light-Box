from gpiozero import LEDBoard
import json

"""
    Script to disable all leds if something goes wrong
"""

config = json.load(open("MedicationInfo.json"))
leds = []

for user in config["users"]:
    leds.append(user["pins"]["led"])

board = LEDBoard(*leds)
board.off()
board.close()
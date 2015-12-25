import requests
import time
import sys
import datetime
import csv
import random
import re
import json
import traceback
import os
import telegram
import gc
from threading import Thread

import builtins #I'm so sorry
from pydblite import Base #The PyDbLite stuff

import src.atbCommands as atbCommands
from src.atbCommands import atbBlaze

APIKEY = ''
with open('../apikey.csv', 'r+') as csvfile: #apikey is not stored on git, sorry
    reader = csv.DictReader(csvfile)
    APIKEY = list(reader)[0]['key']

atb = telegram.Bot(token=APIKEY)

updates = {}
currentMessage = {}

print("@AdamTestBot 3.5 - Ready to go!")
print("Written by Adam Gincel, rewritten by Matt Gomez, shoutouts to Smesh, KARMAT, Dank Meme Network, and SG(DC)^2")

newestOffset = 0
networkFailure = True
while networkFailure:
    try:
        updates = atb.getUpdates(offset=newestOffset)
        for u in updates:
            newestOffset = u.update_id
        networkFailure = False
    except Exception:
        print(traceback.format_exc())
        print("...", end=' ')
print("...Connected!")

startTime = datetime.datetime.now()

previousTime = datetime.datetime.now().time()
currentTime = 0

instanceAge = 0
user_id = 0

# persistent blaze information

builtins.blazeDB = Base('chatStorage/blaze.pdl') #The path to the database
builtins.blazeDB.create('id', 'name', 'score', 'AMtimestamp', 'PMtimestamp', 'streak', 'penalty', 'topThree', mode="open") #Create a new DB if one doesn't exist. If it does, open it

builtins.blazeNum = 0
builtins.groupsBlazed = ""

# END persistent blaze information

blacklist = [-23535579, -28477145]

running = True
while running:
    networkFailure = True
    while networkFailure:
        try:
            updates = atb.getUpdates(offset=newestOffset + 1)
            for u in updates:
                newestOffset = u.update_id
            networkFailure = False
        except Exception:
            print("...", end=' ')

    if instanceAge % 10 == 0: #print 1 X every ten ticks
        print("Y")
    else:
        print("X", end=' ')

    for u in updates:
        currentMessage = u.message
        try:
            user_id = currentMessage.chat.id
            if user_id not in blacklist:
                parsedCommand = re.split(r'[@\s:,\'*]', currentMessage.text.lower())[0]
                running = Thread(target=atbCommands.process, args=(atb, user_id, parsedCommand, currentMessage.text, currentMessage, u, datetime.datetime.now() - startTime))
                running.start()

        except Exception as myException:
            print(traceback.format_exc())

    currentTime = datetime.datetime.now().time()

    if previousTime.minute != currentTime.minute:
        if currentTime.hour == 16 and currentTime.minute == 19: #reset for PM blaze
            builtins.blazeDB.commit()
            builtins.blazeNum = 0
            builtins.groupsBlazed = ""
        if (currentTime.hour == 16 and currentTime.minute == 21) or (currentTime.hour == 4 and currentTime.minute == 21): #commit Blaze Database
            builtins.blazeDB.commit()
            atb.sendMessage(chat_id=-12788453, text="Successfully committed Blaze database.")
            atb.sendDocument(chat_id=-12788453, document=open("chatStorage/blaze.pdl", "rb"))

    previousTime = currentTime

    gc.collect()
    instanceAge += 1

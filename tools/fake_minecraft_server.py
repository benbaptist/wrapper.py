import time
import random
import os
import sys
import threading
import hashlib

from uuid import UUID

# Simulate a Minecraft server's console output. Useful for debugging
# wrapper.py's console output without running a bulky Java server.
# Yes, the code is ugly. I don't care. It's just a quick little
# dev tool, you know? Must use Python 3.x.

# Also, 'This Is Us'. You know what I mean. ;)

names = [
    "Kevin", "Kate", "Randall", "Jack", "BabyJack", "Rebecca", "Pearson",
    "benbaptist", "Toby", "DrK", "Sophie", "Nicky", "Beth", "William"
]

messages = [
    "I need a torch",
    "get the wood from the tree",
    "no man, get the wood from the chest",
    "ok fine",
    "I made a torch",
    "Use the force",
    "Eat a potato",
    "Crash at my place?",
    "Need diamonds",
    "dude man",
    "yo do you have any cows",
    "lol that man"
]

ONLINE_MODE = True

def get_offline_uuid(username):
    playername = "OfflinePlayer:%s" % username
    m = hashlib.md5()
    m.update(playername.encode("utf-8"))
    d = bytearray(m.digest())
    d[6] &= 0x0f
    d[6] |= 0x30
    d[8] &= 0x3f
    d[8] |= 0x80

    return UUID(bytes=bytes(d))

class Player:
    def __init__(self):
        self.username = random.choice(names) + str(random.randrange(0, 99))
        self.uuid = get_offline_uuid(self.username)

def fancy_print(msg, thread="Server thread", level="INFO", ts="11:12:13"):
    print("[%s] [%s/%s]: %s" % (ts, thread, level, msg))
    time.sleep(.1)

# global ABORT
ABORT = False
PAUSE = False

def read_console():
    global ABORT
    while not ABORT:
        blob = input("")

        if blob == "stop":
            ABORT = True
            fancy_print("Shutting down?")
            time.sleep(1)
            break

        if blob == "pause":
            PAUSE = True

        if blob == "resume":
            PAUSE = False

        if blob == "real":
            fancy_print("UUID of player benbaptist is 8e9a15c6-98c2-4cb8-8184-8d845085a846", thread="User Authenticator #1")
            fancy_print("benbaptist[/127.0.0.1:52068] logged in with entity id 270 at (-98.85761606250753, 5.0, 32.550918344641936)")

        if blob == "cmd":
            fancy_print("<benbaptist> .test")

        if blob == "cmd2":
            fancy_print("<benbaptist> .wrapper")

t = threading.Thread(target=read_console, args=())
t.daemon = True
t.start()

fancy_print("Starting minecraft server version 1.15.2")
# time.sleep(.5)
fancy_print("Starting Minecraft server on *:25565")
time.sleep(.5)
fancy_print("Preparing level \"flat\"")
if not ONLINE_MODE:
    fancy_print("The server will make no attempt to authenticate usernames. Beware.")
time.sleep(.5)
fancy_print("Done (17.526s)! For help, type \"help\"")

players = []

while not ABORT:
    if PAUSE:
        continue
    # random events

    if not ONLINE_MODE:
        # make player join
        if random.randrange(0, 10) == 2:
            player = Player()
            players.append(player)
            fancy_print(
                "UUID of player %s is %s"
                % ( player.username, player.uuid ),
                thread="User Authenticator #1"
            )

            fancy_print("%s[/127.0.0.1:12345] logged in with entity id 123 at (1, 2, 3)" % player.username)

        # make player chat
        if random.randrange(0, 4) == 2:
            if len(players) > 0:
                player = random.choice(players)
                message = random.choice(messages)
                fancy_print("<%s> %s" % (player.username, message))

        # make player leave
        if random.randrange(0, 10) == 2:
            if len(players) > 1:
                player = random.choice(players)
                fancy_print("%s lost connection: Disconnected" % player.username)
                players.remove(player)

    time.sleep(.5)

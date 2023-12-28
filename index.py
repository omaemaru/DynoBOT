import requests
import http.client
import json
import inspect
import asyncio
import sys

from colorama import Fore, Style
from requests import get
from discord import Intents
from discord.ext import commands

# Make sure that the user is running Python 3.8 or higher
if sys.version_info < (3, 8):
    exit("Python 3.8 or higher is required to run this bot!")

# Now make sure that the discord.py library is installed or/and is up to date
try:
    from discord import app_commands, Intents, Client, Interaction
except ImportError:
    exit(
        "Either discord.py is not installed or you are running an older and unsupported version of it."
        "Please make sure to check that you have the latest version of discord.py! (try reinstalling the requirements?)"
    )


# ASCII logo
logo = f"""                                                                                                                                                            
#  DDDDDDDDDDDDD                                                                    
#  D::::::::::::DDD                                                                 
#  D:::::::::::::::DD                                                               
#  DDD:::::DDDDD:::::D                                                              
#    D:::::D    D:::::D yyyyyyy           yyyyyyynnnn  nnnnnnnn       ooooooooooo   
#    D:::::D     D:::::D y:::::y         y:::::y n:::nn::::::::nn   oo:::::::::::oo 
#    D:::::D     D:::::D  y:::::y       y:::::y  n::::::::::::::nn o:::::::::::::::o
#    D:::::D     D:::::D   y:::::y     y:::::y   nn:::::::::::::::no:::::ooooo:::::o
#    D:::::D     D:::::D    y:::::y   y:::::y      n:::::nnnn:::::no::::o     o::::o
#    D:::::D     D:::::D     y:::::y y:::::y       n::::n    n::::no::::o     o::::o
#    D:::::D     D:::::D      y:::::y:::::y        n::::n    n::::no::::o     o::::o
#    D:::::D    D:::::D        y:::::::::y         n::::n    n::::no::::o     o::::o
#  DDD:::::DDDDD:::::D          y:::::::y          n::::n    n::::no:::::ooooo:::::o
#  D:::::::::::::::DD            y:::::y           n::::n    n::::no:::::::::::::::o
#  D::::::::::::DDD             y:::::y            n::::n    n::::n oo:::::::::::oo 
#  DDDDDDDDDDDDD               y:::::y             nnnnnn    nnnnnn   ooooooooooo   
#                             y:::::y                                               
#                            y:::::y                                                
#                           y:::::y                                                 
#                          y:::::y                                                  
#                         yyyyyyy                                                                                                                                                                                                           
"""

print(logo + inspect.cleandoc(f"""
{Style.DIM}Welcome to DynoBOT, if it is your first time ignore the errors on this console and run the command on your discord to initialise the setup.{Style.RESET_ALL}
\nPlease enter your bot's token below to continue."""))

try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}


while True:
    token = config.get("token", None)
    channelID = config.get("channelID", None)
    messageID = config.get("messageID", None)
    if token:
        print(f"\n--- Token detected in {Fore.GREEN}./config.json{Fore.RESET} (saved from previous session). ---")
    else:
        token = input("> ")

    try:
        data = requests.get("https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bot {token}"
        }).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord is commonly blocked on public networks, please make sure discord.com is reachable!")

        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"{Fore.RED}Timeout{Fore.RESET}: Connection to Discord's API has timed out (possibly being rate limited?)")

        # Tells python to quit, along with printing some info on the error that occured
        exit(f"Unknown error has occurred! Additional info:\n{e}")

    if channelID == "0":
        print(f"--- {Fore.RED} ChannelID {Fore.RESET} not detected in {Fore.GREEN}./config.json{Fore.RESET} you will need to initiate the setup using the /dynosetup command on your Discord channel. ---")
    else:
        print(f"--- {Fore.RED} ChannelID {Fore.RESET} not detected in {Fore.GREEN}./config.json{Fore.RESET} you will need to initiate the setup using the /dynosetup command on your Discord channel. ---")
    if messageID == "0":
        print(f"--- {Fore.RED} MessageID {Fore.RESET} not detected in {Fore.GREEN}./config.json{Fore.RESET} you will need to initiate the setup using the /dynosetup command on your Discord channel. ---\n")
    else:
        print(f"--- MessageID detected in {Fore.GREEN}./config.json{Fore.RESET} (saved from previous session). ---\n")

    if data.get("id", None):
        break  

    print(f"\nToken seems incorrect {Fore.RED}-invalid token-{Fore.RESET} try again.")

    # Resets the config so that it doesn't use the previous token again
    config.clear()

with open("config.json", "w") as f:
    # Check if 'token' key exists in the config.json file
    config["token"] = token
    config["channelID"] = channelID
    config["messageID"] = messageID

    json.dump(config, f, indent=2)

check_rate = 300  # seconds each check, 1.800 seconds - 30 minutes

channelID = config.get("channelID", None)
if channelID != "":
    channelid = int(channelID)
messageID = config.get("messageID", None)
if messageID != "":
    messageid = int(messageID)  

new_ip = None
previous_ip = None
is_running = False

intents = Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
    global is_running
    print()
    print(inspect.cleandoc(f"""Logged in, use the following URL to invite {client.user} to your Discord Server:
        {Fore.LIGHTBLUE_EX}https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot{Fore.RESET}
    """), end="\n\n")

    if not is_running:
        is_running = True
        channel = client.get_channel(channelid)
        if channel:
            check_clock = client.loop.create_task(check_ip_periodically(client.get_channel(channelid)))
            await check_ip(client.get_channel(channelid)) 
        else:
            print(f"Error: ID channel {Fore.RED}{channelid}{Fore.RESET} not found or the BOT has no access to it.")
            print()

@client.event
async def on_message(message):
    # Mensaje inicial necesario para que actualize editando el mensaje el cual contiene la IP
    if message.content.startswith("/" + "dynosetup"):
        await message.channel.send(f"""**DynoBOT** - *You need to enable developer mode on discord*

:white_small_square: To start with the setup and if you want this to be the channel where your bot will be updating your IP you should left click on this channel and copy the ID. Once you have copied the ID it has to be pasted into the config.json file.

:white_small_square: Repeat the process by clicking on this same message which will be updated by editing it with the current IP.

:white_small_square: Restart DynoBOT.""")
        print(f"Initialising setup...")
        print()
        print(f"{Style.DIM}Restart DynoBOT once you have pasted both IDs{Style.RESET_ALL}")

async def fetch_ip():
    try: 
        conn = http.client.HTTPConnection("api.ipify.org")
        conn.request("GET", "/")
        res = conn.getresponse()
        return res.read().decode("utf-8")
    except Exception as e:
        print("Error fetching IP:", e)
        return None

async def check_ip(channel):
    global new_ip, previous_ip

    new_ip = await fetch_ip()

    if new_ip is not None and new_ip != previous_ip:
        print("Current IP", new_ip)
        print()
        async for message in channel.history(limit=1):
            message = await channel.fetch_message(messageid)

        await message.edit(content="**IP:** " + new_ip)

    previous_ip = new_ip

async def check_ip_periodically(channel):
    while is_running:
        await asyncio.sleep(check_rate)
        await check_ip(channel)

        previous_ip = new_ip

client.run(token)

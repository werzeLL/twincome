import discord
import requests
from bs4 import BeautifulSoup
import asyncio
import browser_cookie3

TOKEN = "MTMzNzQxMTMxMDU2ODM0MTUwNQ.GFZtWh.1dwsBWrIlgvCl-tWMaSETpNpsQiyiaDZUy2e5A"
URL = "https://klanhaboru.hu/game.php?village=YOUR_VILLAGE_ID&screen=overview_villages"
CHANNEL_ID = YOUR_CHANNEL_ID  # Cseréld le a saját csatorna ID-ra

intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents=intents)

last_attacks = set()  # Utolsó ismert támadások listája

def is_logged_in():
    try:
        cookies = browser_cookie3.chrome(domain_name="klanhaboru.hu")
        response = requests.get(URL, cookies=cookies)
        return "logout" in response.text  # Ha az oldal tartalmazza a "logout" szót, be vagy jelentkezve
    except Exception as e:
        print(f"Error checking login status: {e}")
        return False

async def check_attacks():
    global last_attacks
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    
    while not client.is_closed():
        if not is_logged_in():
            print("Not logged in. Retrying in 60 seconds...")
            await asyncio.sleep(60)
            continue
        
        cookies = browser_cookie3.chrome(domain_name="klanhaboru.hu")
        response = requests.get(URL, cookies=cookies)
        soup = BeautifulSoup(response.text, "html.parser")
        
        new_attacks = set()
        for row in soup.find_all("tr", class_="nowrap"):
            attack_data = row.get_text(strip=True)
            new_attacks.add(attack_data)
        
        # Új támadás keresése
        new_entries = new_attacks - last_attacks
        if new_entries:
            for attack in new_entries:
                await channel.send(f"⚠️ **New Incoming Attack Detected!** ⚠️\n```{attack}```")
        
        last_attacks = new_attacks  # Frissítés
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(check_attacks())

client.run(TOKEN)

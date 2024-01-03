import datetime
import os
import discord
import logging
import sys
import json
from discord.ext import tasks
from dotenv import load_dotenv
from scraper import Scraper

load_dotenv()

WEBSITE_URL = os.getenv("CEKASDOSAN_WEBSITE_URL")
USERNAME = os.getenv("CEKASDOSAN_SIAK_USERNAME")
PASSWORD = os.getenv("CEKASDOSAN_SIAK_PASSWORD")
TOKEN = os.getenv("CEKASDOSAN_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CEKASDOSAN_CHANNEL_ID"))
KODE_KURIKULUM = os.getenv("CEKASDOSAN_KODE_KURIKULUM")

TIMEZONE = datetime.timezone(datetime.timedelta(hours=7))

bot = discord.Client(intents=discord.Intents.all())

log = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s: %(message)s",
                    datefmt="%d %b %Y %H:%M:%S",
                    handlers=[
                        logging.FileHandler("log"),
                        logging.StreamHandler(sys.stdout)])

scr = Scraper()
scr.login(WEBSITE_URL+"login/", USERNAME, PASSWORD)


@tasks.loop(minutes=30)
async def send_message():
    log.info("CHECK STARTED")
    channel = bot.get_channel(CHANNEL_ID)

    lowongans = scr.scrape(WEBSITE_URL+"lowongan/listLowongan/", KODE_KURIKULUM)

    embed = discord.Embed(
        title=f"CekAsdosan v2 - {lowongans.get('tahun_ajaran')}")

    if lowongans != bot.last_message:
        for lowongan in lowongans['lowongan']:
            kode_matkul = lowongan.get('kode_matkul')
            nama_matkul = lowongan.get('nama_matkul')
            dosen = lowongan.get('dosen')
            status = lowongan.get('status')
            jumlah_lowongan = lowongan.get('jumlah_lowongan')
            jumlah_pelamar = lowongan.get('jumlah_pelamar')
            jumlah_diterima = lowongan.get('jumlah_diterima')

            log.info(f"{kode_matkul} - {nama_matkul}")
            embed.add_field(name=kode_matkul,
                            value=f"{nama_matkul} - {dosen}\n\
                                    Status: {status}\n\
                                     Open: {jumlah_lowongan}\n\
                                    Registrants: {jumlah_pelamar}\n\
                                    Accepted: {jumlah_diterima}", 
                            inline=False)
    
        await channel.send(embed=embed)
        log.info("MESSAGE SENT")

        bot.last_message = lowongans
        with open("last_message.json", "w") as f:
            json.dump(lowongans, f)
    else:
        log.info("MESSAGE NOT SENT: MESSAGE SAME AS LAST MESSAGE")


@bot.event
async def on_ready():
    with open("last_message.json", "r") as f:
        bot.last_message = json.load(f)
    send_message.start()
    log.info("BOT READY")

bot.run(TOKEN, log_handler=None)

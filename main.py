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

WEBSITE_URL = os.getenv("CEKASDOSAN_WEBSITE_URL", "https://siasisten.cs.ui.ac.id/")
USERNAME = os.getenv("CEKASDOSAN_SIAK_USERNAME")
if not USERNAME:
    raise ValueError("CEKASDOSAN_SIAK_USERNAME is not set")

PASSWORD = os.getenv("CEKASDOSAN_SIAK_PASSWORD")
if not PASSWORD:
    raise ValueError("CEKASDOSAN_SIAK_PASSWORD is not set")

TOKEN = os.getenv("CEKASDOSAN_BOT_TOKEN")
try:
    CHANNEL_ID = int(os.getenv("CEKASDOSAN_CHANNEL_ID"))
except ValueError:
    raise ValueError("CEKASDOSAN_CHANNEL_ID is not set")

KODE_KURIKULUM = os.getenv("CEKASDOSAN_KODE_KURIKULUM", "")

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


@tasks.loop(minutes=5)
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
            link_daftar = lowongan.get('link_daftar')

            if status == "Buka":
                embed_message = f"{nama_matkul} - {dosen}\n\
                                    Status: {status}\n\
                                     Open: {jumlah_lowongan}\n\
                                    Registrants: {jumlah_pelamar}\n\
                                    Accepted: {jumlah_diterima}\n\
                                    Register Link: {WEBSITE_URL[:-1]}{link_daftar}"
            else:
                embed_message = f"{nama_matkul} - {dosen}\n\
                                    Status: {status}\n\
                                     Open: {jumlah_lowongan}\n\
                                    Registrants: {jumlah_pelamar}\n\
                                    Accepted: {jumlah_diterima}"

            log.info(f"{kode_matkul} - {nama_matkul}")
            embed.add_field(name=kode_matkul,
                            value=embed_message,
                            inline=False)

        await channel.send(embed=embed)
        log.info("MESSAGE SENT")

        with open("last_message.json", "w") as f:
            json.dump(lowongans, f)
    else:
        log.info("MESSAGE NOT SENT: MESSAGE SAME AS LAST MESSAGE")

    try:
        with open("last_message.json") as f:
            bot.last_message = json.load(f)
    except FileNotFoundError:
        bot.last_message = {}

@bot.event
async def on_ready():
    try:
        with open("last_message.json") as f:
            bot.last_message = json.load(f)
    except FileNotFoundError:
        bot.last_message = {}

    send_message.start()
    log.info("BOT READY")

bot.run(TOKEN, log_handler=None)

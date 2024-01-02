import datetime
import requests
import os
import re
import discord
import logging
import sys
from discord.ext import tasks
from bs4 import BeautifulSoup, NavigableString
from dotenv import load_dotenv

load_dotenv()

WEBSITE_URL = "https://siasisten.cs.ui.ac.id/"
USERNAME = os.getenv("SIAK_USERNAME")
PASSWORD = os.getenv("SIAK_PASSWORD")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1014578047028052048
TIMEZONE = datetime.timezone(datetime.timedelta(hours=7))

SEMESTER = "Genap"
KODE_KURIKULUM = "02.00.12.01-2020"

bot = discord.Client(intents=discord.Intents.all())
log = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s: %(message)s",
                    datefmt="%d %b %Y %H:%M:%S",
                    handlers=[
                        logging.FileHandler("log"),
                        logging.StreamHandler(sys.stdout)])

@tasks.loop(hours=1)
async def send_message():
    channel = bot.get_channel(CHANNEL_ID)

    with requests.session() as session:
        login_page = session.get(WEBSITE_URL+"login/")
        soup = BeautifulSoup(login_page.text, features="html.parser")

        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']

        payload = {
            "csrfmiddlewaretoken": csrf_token,
            "username": USERNAME,
            "password": PASSWORD,
            "next": ""
        }

        headers = {
            "Referer": WEBSITE_URL+"login/"
        }

        login_request = session.post(
            WEBSITE_URL+"login/", payload, headers=headers)
        soup = BeautifulSoup(login_request.text,
                             features="html.parser")

        tahun_ajaran: list[NavigableString] = list(dict.fromkeys(soup.findAll(
            string=re.compile(f"{SEMESTER} 2023/2024"))))
        table = tahun_ajaran[0].next_element.next_element

        embed = discord.Embed(title=f"CekAsdosan - {SEMESTER} 2023/2024")
        msgs = []

        lowongans = table.findAll(string=re.compile(KODE_KURIKULUM))
        for lowongan in lowongans:
            kode_matkul = str(lowongan).split("-")[0].strip()
            nama_matkul = str(lowongan.next_element.next_element).strip()
            dosen = str(
                lowongan.next_element.next_element.next_element.next_element.next_element).strip()
            lowongan_buka = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip()
            lowongan_buka = "Open" if lowongan_buka == "Buka" else "Closed"
            jumlah_lowongan = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]
            jumlah_pelamar = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]
            jumlah_diterima = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]

            msgs.append(f"{kode_matkul} {nama_matkul} {dosen} {lowongan_buka} {jumlah_lowongan} {jumlah_pelamar} {jumlah_diterima}")
            embed.add_field(name=kode_matkul, value=f"{nama_matkul} - {dosen}\nStatus: {lowongan_buka}\nOpen: {jumlah_lowongan}\nRegistrant: {jumlah_pelamar}\nAccepted: {jumlah_diterima}", inline=False)
            log.info(f"{kode_matkul} - {nama_matkul}")

        if "\n".join(msgs) != bot.last_message:
            with open("last_message.cekasdosan", "w") as f:
                bot.last_message = "\n".join(msgs)
                f.write(bot.last_message)
            await channel.send(embed=embed)

            log.info("MESSAGE SENT")
        else:
            log.info("MESSAEGE NOT SENT: MESSAGE SAME AS LAST MESSAGE")


@bot.event
async def on_ready():
    with open("last_message.cekasdosan", "r") as f:
        bot.last_message = f.read()
    send_message.start()
    log.info("BOT READY")

bot.run(TOKEN, log_handler=None)

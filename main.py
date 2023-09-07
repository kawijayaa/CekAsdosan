import random
import discord
import os
import datetime
import logging
import sys
from dotenv import load_dotenv
from discord.ext import tasks
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions

load_dotenv()

WEBSITE_URL = "https://siasisten.cs.ui.ac.id/login/"
USERNAME = os.getenv("SIAK_USERNAME")
PASSWORD = os.getenv("SIAK_PASSWORD")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 1014578047028052048

TIMEZONE = datetime.timezone(datetime.timedelta(hours=7))

chrome_options = Options()
chrome_options.add_argument("--headless")

bot = discord.Client(intents=discord.Intents.all())

log = logging.getLogger()
logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s: %(message)s", 
                    datefmt="%d %b %Y %H:%M:%S", 
                    handlers=[
                        logging.FileHandler("log"),
                        logging.StreamHandler(sys.stdout)])

def get_course_list(semester, kurikulum, tahun=datetime.datetime.now().year):
    log.info("CHECK STARTED")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(WEBSITE_URL)

    username_field = driver.find_element(By.ID, "id_username")
    password_field = driver.find_element(By.ID, "id_password")

    username_field.send_keys(USERNAME)
    password_field.send_keys(PASSWORD)

    login_button = driver.find_element(By.CLASS_NAME, "submit")
    login_button.click()

    log.info("LOGGED IN")

    WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, "/html/body/div[@class='container']/div[@id='content']/div[@id='content']/div[@id='main-content']/h2[@class='content-title']")))

    classes = driver.find_elements(By.XPATH, "//td[contains(text(), '" + kurikulum + "') and ancestor::table/preceding-sibling::h4[1][contains(text(), '" + f"{semester} {tahun}/{tahun+1}" + "')]]")

    if classes != []:
        log.info(f"{semester.upper()} {tahun}/{tahun+1} IS OPEN")

        msg = f"{semester} {tahun}/{tahun+1} is open.\n\n" + "\n".join(["- " + i.text.replace("\n", " ") for i in classes])
    else:
        log.info(f"{semester.upper()} {tahun}/{tahun+1} IS NOT OPEN")
        msg = f"{semester} {tahun}/{tahun+1} is not open."

    return discord.Embed(
        title="CekAsdosan",
        description=msg
    )


@bot.event
async def on_ready():
    os.system("clear")
    send_message.start()
    log.info("BOT READY")


@bot.event
async def on_message(msg: discord.Message):
    if not msg.author.bot and msg.content.lower() == "check" and msg.channel.id == CHANNEL_ID:
        log.info(f"CHECK REQUEST BY {msg.author.name}")
        await send_message()
    
    if msg.guild is None and not msg.author.bot and msg.content.lower().startswith("check"):
        log.info(f"DM CHECK REQUEST BY {msg.author.name}")

        user = bot.get_user(msg.author.id)

        if msg.content.lower() == "check":
            await user.send(embed=discord.Embed(
                title="CekAsdosan",
                description="Usage: check (ganjil/genap/pendek) (tahun) (ik/kki/any)"
            ))
        else:
            parsed_msg = msg.content.split(" ")
            semester = parsed_msg[1].capitalize()
            tahun = int(parsed_msg[2])
            prodi = parsed_msg[3].upper()

            if prodi == "IK":
                embed = get_course_list(semester, "01.00", tahun)
                await user.send(embed=embed)
                log.info(f"SENT TO {msg.author.name}")
            elif prodi == "SI":
                embed = get_course_list(semester, "06.00")
                await user.send(embed=embed)
                log.info(f"SENT TO {msg.author.name}")
            elif prodi == "KKI":
                embed = get_course_list(semester, "02.00", tahun)
                await user.send(embed=embed)
                log.info(f"SENT TO {msg.author.name}")
            else:
                embed = get_course_list(semester, "12.01", tahun)
                await user.send(embed=embed)
                log.info(f"SENT TO {msg.author.name}")


@tasks.loop(hours=3)
async def send_message():
    channel = bot.get_channel(CHANNEL_ID)
    embed = get_course_list("Ganjil", "02.00.12.01-2020")
    await channel.send(embed=embed)
    log.info(f"SENT TO {channel.guild}/{channel.name}")
    

bot.run(TOKEN, log_handler=None)
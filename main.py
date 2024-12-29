import io
import os.path
import time
import subprocess
from datetime import datetime
from pathlib import Path
import alsaaudio
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from gtts import gTTS
from lingua import Language, LanguageDetectorBuilder
from pydub import AudioSegment
from pydub.playback import play
from PIL import Image
import requests
from io import BytesIO


# Configurações do Selenium.
GECKO_DRIVER_PATH = "/usr/bin/geckodriver"                         # Caminho do driver no computador.
RADIO_URL = "https://socialradio.com.br/radio/verdeolivaresende/"  # URL da estação.
LOAD_TIME = 4                                                      # Tempo de carregamento da página, em segundos.
                                                                   # Use números maiores em conexões mais lentas.

# Configurações de voz.
READ_ALOUD = True    # Ativa ou desativa a leitura em voz alta.
VOICE_VOLUME = 60    # Volume do computador ao anunciar em voz alta.
SPEAK_HU3BR = False  # Ativa ou desativa o anúncio de nomes estrangeiros em português do Brasil.

# Configurações de notificação.
NOTIFY_DESKTOP = True                       # Ativa ou desativa a notificação da área de trabalho.
NOTIFY_KDE_CONNECT = True                   # Ativa ou desativa a notificação dos dispositivos no KDE Connect.
kde_connect_devices = ["61c24666ecf34a46"]  # Lista de device-ids dos dispositivos conectados ao KDE Connect.

home_dir = Path.home()
art_path = os.path.join(home_dir, "temp_art.png")
log_path = os.path.join(home_dir, "oliva_log.txt")

def create_webdriver():
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    service = Service(GECKO_DRIVER_PATH)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def fetch_webpage(driver, page):
    try:
        driver.get(page)
        time.sleep(LOAD_TIME)
        return driver.page_source
    except Exception as e:
        print(f"Erro ao carregar página: {e}")
        return None


def extract_tag_content(html_content, tag_name, tag_id):
    soup = BeautifulSoup(html_content, 'html.parser')
    tag = soup.find(tag_name, id=tag_id)
    if tag:
        return tag.get_text()
    else:
        return None


def extract_album_art(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    art_style = soup.find("div", id="lunaradiocoverwrapper2")

    try:
        art_url = art_style.get("style").split("\"")[1]
    except:
        return None

    return art_url


def assemble_time():
    hour_24 = int(datetime.now().strftime("%H"))
    hour = int(datetime.now().strftime("%I"))
    minute = int(datetime.now().strftime("%M"))

    if hour == 1:
        hour = "uma"
    elif hour == 2:
        hour = "duas"

    if minute == 0:
        moment = f"{hour} em ponto"
    elif minute == 30:
        moment = f"{hour} e meia"
    else:
        moment = f"{hour} e {minute}"

    if hour_24 == 0:
        moment = "meia noite"
    elif hour_24 == 12:
        moment = "meio dia"

    return moment


def log(info):
    with open(log_path, "a") as log_file:
        log_file.write(f"{datetime.now()}: {info}\n")


def read_aloud(song_info, language):
    log(song_info)
    if not READ_ALOUD:
        return None

    mixer = alsaaudio.Mixer()
    volume = mixer.getvolume(0)
    song_name = song_info.split(" - ")[1]
    artist_name = song_info.split(" - ")[0]

    if song_info == "Verde Oliva - Resende":
        time_now = assemble_time()
        texts = [f"Você está sintonizado na Verde Oliva FM. Agora, {time_now}."]
        languages = ["pt"]
    else:
        if SPEAK_HU3BR:
            language = "pt"
        texts = ["Você está ouvindo ", song_name, " na voz de ", artist_name, " na Verde Oliva."]
        languages = ["pt", language, "pt", language, "pt"]

    fp = io.BytesIO()

    for num, text in enumerate(texts):
        print(f"{num}: {text} ({languages[num]})")
        gTTS(text, lang=languages[num]).write_to_fp(fp)

    fp.seek(0)

    mixer.setvolume(VOICE_VOLUME)
    play(AudioSegment.from_file(fp, format="mp3"))
    mixer.setvolume(volume[0])


def detect_language(text):
    if SPEAK_HU3BR:
        return "Português", "pt"
    languages = [Language.ENGLISH, Language.PORTUGUESE, Language.SPANISH, Language.ITALIAN]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    lang = detector.detect_language_of(text)
    name = lang.name.title()
    code = lang.iso_code_639_1.name.lower()
    return name, code


def notify_devices(device_ids, message, art_url):
    if NOTIFY_DESKTOP:
        try:
            response = requests.get(art_url)
            art_file = Image.open(BytesIO(response.content)) #.resize((128, 128))
            art_file.save(art_path, "PNG")
        except:
            pass

        subprocess.run(
            ["kdialog",
                  "--passivepopup", message, "5",
                  "--icon", art_path,
                  "--title", "Tocando na Verde Oliva"],
            check=True)

    if NOTIFY_KDE_CONNECT:
        try:
            for device_id in device_ids:
                command = f"kdeconnect-cli --device {device_id} --ping-msg \"{message}\""
                subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to send notification: {e}")


def main():
    driver = create_webdriver()
    try:
        content = fetch_webpage(driver, RADIO_URL)
        if content:
            tag_content = extract_tag_content(content, "div", "lunaradiotexttitle").title()
            album_art = extract_album_art(content)

            if "�" in tag_content:  # For when the web player shows garbage data.
                tag_content = "Verde Oliva - Resende"

            language = detect_language(tag_content)
            notify_devices(kde_connect_devices, f"Song: {tag_content}\nLanguage: {language[0]} ({language[1]})", album_art)
            read_aloud(tag_content, language[1])

        else:
            print("Falha na extração do conteúdo da página.")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()

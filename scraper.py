import requests
import re
from bs4 import BeautifulSoup

class Scraper(object):
    def __init__(self):
        self.session = requests.session()

    def login(self, login_url, username, password):
        login_page = self.session.get(login_url)
        soup = BeautifulSoup(login_page.text, features="html.parser")

        csrf_token = soup.find(
            'input', {'name': 'csrfmiddlewaretoken'})['value']

        payload = {
            "csrfmiddlewaretoken": csrf_token,
            "username": username,
            "password": password,
            "next": ""
        }

        headers = {
            "Referer": login_url
        }

        self.session.post(
            login_url, payload, headers=headers)

    def scrape(self, url, kode_kurikulum):
        soup = BeautifulSoup(self.session.get(url).content,
                             features="html.parser")

        table = soup.findAll("table")[0]
        tahun_ajaran = table.previous_element.previous_element

        msgs = []

        lowongans = table.findAll(string=re.compile(kode_kurikulum))
        for lowongan in lowongans:
            kode_matkul = str(lowongan).split("-")[0].strip()
            nama_matkul = str(lowongan.next_element.next_element).strip()
            dosen = str(
                lowongan.next_element.next_element.next_element.next_element.next_element).strip()
            status = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip()
            jumlah_lowongan = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]
            jumlah_pelamar = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]
            jumlah_diterima = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element).strip().split()[0]
            link_daftar = str(
                lowongan.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element.next_element['href']
            )
            msgs.append(dict(kode_matkul=kode_matkul, nama_matkul=nama_matkul, dosen=dosen, status=status,
                        jumlah_lowongan=jumlah_lowongan, jumlah_pelamar=jumlah_pelamar, jumlah_diterima=jumlah_diterima, link_daftar=link_daftar))
        
        return dict(tahun_ajaran=tahun_ajaran, lowongan=msgs)

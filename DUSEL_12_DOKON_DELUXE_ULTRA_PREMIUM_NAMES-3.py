import urllib.request
import urllib.parse
import json
import time
import sqlite3
import traceback
import os
import re
import difflib
import zipfile
import tempfile
import html
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ============================================================
# DUSEL 12-DOKON - TELEGRAM BOT
# Standart Python kutubxonalari: urllib, json, time, sqlite3
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
def _env_int(name, default=0):
    try:
        return int(os.getenv(name, str(default)).strip() or str(default))
    except (TypeError, ValueError):
        return default

# Asosiy admin — foydalanuvchi bergan Telegram ID
MAIN_ADMIN_ID = 6033308194
# Asosiy admin har doim shu ID. Environment orqali qo‘shimcha adminlar ham berilishi mumkin.
ADMIN_ID = MAIN_ADMIN_ID
ADMIN_IDS = {MAIN_ADMIN_ID}
for _admin_value in (os.getenv("ADMIN_ID", ""), os.getenv("ADMIN_IDS", "")):
    for _item in _admin_value.split(","):
        if _item.strip().lstrip("-").isdigit():
            ADMIN_IDS.add(int(_item.strip()))

def is_admin(chat_id):
    try:
        return int(chat_id) in ADMIN_IDS
    except (TypeError, ValueError):
        return False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.getenv("DB_FILE", os.path.join(BASE_DIR, "dusel_shop.db"))

# Qidiruv natijalari: foydalanuvchi yozgan nom/kod bo‘yicha bevosita mahsulot tugmalari uchun.
SEARCH_CACHE = {}
API_URL = "https://api.telegram.org/bot" + BOT_TOKEN + "/"
WEBAPP_URL = (
    os.getenv("WEBAPP_URL", "").strip()
    or os.getenv("RENDER_EXTERNAL_URL", "").strip()
).rstrip("/")
if not WEBAPP_URL:
    _render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip()
    if _render_host:
        WEBAPP_URL = "https://" + _render_host.rstrip("/")

# ============================================================
# MAHSULOTLAR
# ============================================================

PRODUCTS = {
    "DUSEL": {
        "LED LAMPALAR": [
            ("Dusel LED 5W", 0.55),
            ("Dusel LED 7W", 0.65),
            ("Dusel LED 10W", 0.70),
            ("Dusel LED 12W", 0.80),
            ("Dusel LED 15W", 0.95),
            ("Dusel LED 18W", 1.10),
            ("Dusel LED 20W", 1.30),
            ("Dusel LED 30W", 2.10),
            ("Dusel LED 40W", 2.90),
            ("Dusel LED 50W", 3.70),
            ("Dusel LED 60W", 4.30),
            ("Dusel LED 80W", 6.00),
            ("Dusel LED 100W", 8.00),
            ("Dusel LED 150W", 11.00),
            ("Dusel LED 200W", 19.00),
            ("Flame Lamp", 1.90),
        ],
        "T5": [
            ("T5-PL 30cm 6W", 1.00),
            ("T5-PL 60cm 9W", 1.30),
            ("T5-PL 90cm 15W", 1.50),
            ("T5-PL 120cm 18W", 1.60),
            ("T5-AL 30cm 6W", 1.50),
            ("T5-AL 60cm 9W", 1.80),
            ("T5-AL 120cm 18W", 2.40),
        ],
        "T8": [
            ("T8-comp 9W 60cm", 1.90),
            ("T8-comp 18W 120cm", 2.30),
            ("T8 lampa 60cm 10W", 0.80),
            ("T8 lampa 120cm 20W", 1.10),
            ("T8 lampa 120cm 30W", 1.45),
            ("T8 lampa 120cm 50W", 1.70),
            ("T8 Alyumin 60cm 9W", 2.00),
            ("T8 Alyumin 120cm 18W", 2.80),
        ],
        "PATRONLI LAMPALAR": [
            ("C30/E14 5W", 0.60),
            ("C30/E27 5W", 0.60),
            ("C35/E14 7W", 0.65),
            ("C35/E27 7W", 0.65),
            ("C40/E14 9W", 0.70),
            ("C40/E27 9W", 0.70),
            ("G45/E14 5W", 0.65),
            ("B45/E27 5W", 0.65),
        ],
    },

    "VERAL": {
        "LED LAMPALAR": [
            ("VERAL LED 5W", 0.41),
            ("VERAL LED 7W", 0.50),
            ("VERAL LED 10W", 0.54),
            ("VERAL LED 12W", 0.61),
            ("VERAL LED 15W", 0.72),
            ("VERAL LED 18W", 0.95),
            ("VERAL LED 20W", 1.00),
            ("VERAL LED 30W", 1.45),
            ("VERAL LED 40W", 2.05),
            ("VERAL LED 50W", 2.50),
            ("VERAL LED 60W", 3.10),
        ],
        "LYUSTRA LAMPALAR": [
            ("LED 5W C30/E14", 0.55),
            ("LED 5W C30/E27", 0.55),
            ("Candle 9W E14", 0.70),
            ("Candle 12W E14", 0.75),
            ("Candle 16W E14", 0.60),
            ("Candle 16W E27", 0.60),
            ("LED Candle 12W E14 Small", 0.55),
            ("Candle 14W E14/E27 (3 color)", 0.80),
            ("Candle 18W E14/E27 (3 color)", 0.90),
            ("Candle 24W E27/E14", 1.10),
            ("LED Candle-2 12W E14", 1.00),
        ],
        "TO‘RT BURCHAK ICHKI AKRIL": [
            ("VAS-10 (10W - Ichki)", 0.89),
            ("VAS-18 (18W - Ichki)", 1.12),
            ("VAS-24 (24W - Ichki)", 1.69),
            ("VAS-36 (36W - Ichki)", 2.72),
            ("VAS-48 (48W - Ichki)", 4.75),
        ],
        "DUMALOQ ICHKI AKRIL": [
            ("VAR-10 (10W - Ichki)", 0.78),
            ("VAR-18 (18W - Ichki)", 1.02),
            ("VAR-24 (24W - Ichki)", 1.58),
            ("VAR-36 (36W - Ichki)", 2.26),
            ("VAR-48 (48W - Ichki)", 4.30),
        ],
        "TO‘RT BURCHAK TASHQI AKRIL": [
            ("VASS-18 (18W - Tashqi)", 1.37),
            ("VASS-24 (24W - Tashqi)", 2.05),
            ("VASS-36 (36W - Tashqi)", 2.90),
            ("VASS-48 (48W - Tashqi)", 5.00),
        ],
        "DUMALOQ TASHQI AKRIL": [
            ("VASR-18 (18W - Tashqi)", 1.26),
            ("VASR-24 (24W - Tashqi)", 1.85),
            ("VASR-36 (36W - Tashqi)", 2.73),
            ("VASR-48 (48W - Tashqi)", 4.52),
        ],
    },

    "SALID": {
        "RANGLI ROZETKA VA KLYUCHATELLAR": {
            "White": [
            ('1-lik klyuchatel', 1.00),
            ('2-lik klyuchatel', 1.25),
            ('3-lik klyuchatel', 1.65),
            ('Zvonok klyuchatel', 1.30),
            ('1-lik rozetka', 1.10),
            ('2-lik rozetka', 1.80),
            ('1-lik zazemleniyali rozetka', 1.20),
            ('2-lik zazemleniyali rozetka', 2.20),
            ('1-lik qopqoqli rozetka', 1.50),
            ('Telefon (domashniy)', 1.60),
            ('TV rozetka', 1.60),
            ('Internet rozetka', 1.60),
            ('2-lik internet rozetka', 2.65),
            ('TAPSI USB rozetka', 8.00),
            ('1-lik Reverser', 1.30),
            ('2-lik Reverser', 1.60),
            ('2-lik ramka', 0.70),
            ('3-lik ramka', 1.15),
            ('4-lik ramka', 1.60),
            ('5-lik ramka', 2.00)
            ],
            "Grey": [
            ('1-lik klyuchatel', 1.15),
            ('2-lik klyuchatel', 1.40),
            ('3-lik klyuchatel', 1.85),
            ('Zvonok klyuchatel', 1.50),
            ('1-lik rozetka', 1.30),
            ('2-lik rozetka', 2.30),
            ('1-lik zazemleniyali rozetka', 1.40),
            ('2-lik zazemleniyali rozetka', 2.60),
            ('1-lik qopqoqli rozetka', 1.80),
            ('Telefon (domashniy)', 1.70),
            ('TV rozetka', 1.70),
            ('Internet rozetka', 1.75),
            ('2-lik internet rozetka', 2.80),
            ('TAPSI USB rozetka', 8.10),
            ('1-lik Reverser', 1.45),
            ('2-lik Reverser', 1.80),
            ('2-lik ramka', 0.85),
            ('3-lik ramka', 1.30),
            ('4-lik ramka', 1.85),
            ('5-lik ramka', 2.30)
            ],
            "Black": [
            ('1-lik klyuchatel', 1.15),
            ('2-lik klyuchatel', 1.40),
            ('3-lik klyuchatel', 1.85),
            ('Zvonok klyuchatel', 1.50),
            ('1-lik rozetka', 1.30),
            ('2-lik rozetka', 2.30),
            ('1-lik zazemleniyali rozetka', 1.40),
            ('2-lik zazemleniyali rozetka', 2.60),
            ('1-lik qopqoqli rozetka', 1.80),
            ('Telefon (domashniy)', 1.70),
            ('TV rozetka', 1.70),
            ('Internet rozetka', 1.75),
            ('2-lik internet rozetka', 2.80),
            ('TAPSI USB rozetka', 8.10),
            ('1-lik Reverser', 1.45),
            ('2-lik Reverser', 1.80),
            ('2-lik ramka', 0.85),
            ('3-lik ramka', 1.30),
            ('4-lik ramka', 1.85),
            ('5-lik ramka', 2.30)
            ],
            "Dark Grey": [
            ('1-lik klyuchatel', 1.15),
            ('2-lik klyuchatel', 1.40),
            ('3-lik klyuchatel', 1.85),
            ('Zvonok klyuchatel', 1.50),
            ('1-lik rozetka', 1.30),
            ('2-lik rozetka', 2.30),
            ('1-lik zazemleniyali rozetka', 1.40),
            ('2-lik zazemleniyali rozetka', 2.60),
            ('1-lik qopqoqli rozetka', 1.80),
            ('Telefon (domashniy)', 1.70),
            ('TV rozetka', 1.70),
            ('Internet rozetka', 1.75),
            ('2-lik internet rozetka', 2.80),
            ('TAPSI USB rozetka', 8.10),
            ('1-lik Reverser', 1.45),
            ('2-lik Reverser', 1.80),
            ('2-lik ramka', 0.85),
            ('3-lik ramka', 1.30),
            ('4-lik ramka', 1.85),
            ('5-lik ramka', 2.30)
            ],
            "Gold": [
            ('1-lik klyuchatel', 1.15),
            ('2-lik klyuchatel', 1.40),
            ('3-lik klyuchatel', 1.85),
            ('Zvonok klyuchatel', 1.50),
            ('1-lik rozetka', 1.30),
            ('2-lik rozetka', 2.30),
            ('1-lik zazemleniyali rozetka', 1.40),
            ('2-lik zazemleniyali rozetka', 2.60),
            ('1-lik qopqoqli rozetka', 1.80),
            ('Telefon (domashniy)', 1.70),
            ('TV rozetka', 1.70),
            ('Internet rozetka', 1.75),
            ('2-lik internet rozetka', 2.80),
            ('TAPSI USB rozetka', 8.10),
            ('1-lik Reverser', 1.45),
            ('2-lik Reverser', 1.80),
            ('2-lik ramka', 0.85),
            ('3-lik ramka', 1.30),
            ('4-lik ramka', 1.85),
            ('5-lik ramka', 2.30)
            ]
        }
    }
}

# ============================================================
# USER-SUPPLIED DUSEL CATALOG ADDITIONS (2026-09-28)
# ============================================================
DUSEL_EXTRA_20260928 = {'SHITLAR': [('Shit IP-31 350x250x110 (Sh) 0.3mm', 2.55), ('Shit IP-31 300x250x110 0.5mm', 3.53), ('Shit IP-31 350x250x110 0.5mm', 3.72), ('Shit IP-31 350x250x110 0.5mm', 3.72), ('Shit IP-31 400x300x140 0.5mm', 4.98), ('Shit IP-31 400x400x140 0.5mm', 5.76), ('Shit IP-31 500x350x140 (Sh) 0.5mm', 6.67), ('Shit IP-31 500x350x140 0.5mm', 6.67), ('Shit SHMP IP-31 500x400x150 0.5mm', 8.21), ('Shit SHMP IP-31 500x400x200 0.5mm', 8.85), ('Shit SHMP IP-31 500x400x160 0.5mm', 9.21), ('Shit SHMP IP-31 700x500x200 0.5mm', 13.14), ('Shit SHMP IP-31 350x250x160 0.6mm', 8.03), ('Shit SHMP IP-31 400x300x160 0.6mm', 9.26), ('Shit SHMP IP-31 400x400x160 0.6mm', 10.68), ('Shit SHMP IP-31 500x350x160 0.6mm', 11.57), ('Shit SHMP IP-31 500x400x160 0.6mm', 12.39), ('Shit SHMP IP-31 600x400x160 0.6mm', 13.89), ('Shit SHMP IP-31 700x500x200 0.6mm', 15.88), ('Shit SHMP IP-31 800x600x200 0.6mm', 18.2), ('Shit SHMP IP-54 400x300x200 0.8mm', 18.2), ('Shit SHMP IP-54 (GER-MET) 400x400x200 0.8mm', 15.88), ('Shit SHMP IP-54 500x400x200 0.8mm', 18.2), ('Shit SHMP IP-54 600x400x200 0.8mm', 20.36), ('Shit SHMP IP-54 (GER-MET) 600x500x200 0.8mm', 23.15), ('Shit SHMP IP-54 (GER-MET) 600x500x200 0.8mm', 26.5), ('Shit SHMP IP-54 (GER-MET) 800x600x200 0.8mm', 35.52), ('Shit SHMP IP-54 (GER-MET) 1200x600x300 0.8mm', 58.2), ('Shit SHMP IP-54 (GER-MET) 1200x800x300 0.8mm', 69.65), ('Shit VRU IP-31 1240x620x250 0.8mm', 51.83), ('Shit VRU IP-31 1200x800x250 0.8mm', 60.82), ('Shit VRU IP-31 1500x800x350 0.8mm', 81.45), ('Shit VRU IP-31 1500x900x300 0.8mm', 112.3), ('Shit VRU IP-31 1700x1000x400 0.8mm', 156), ('Shit VRU IP-31 1800x800x400 0.8mm', 125.58), ('Shit SHE (vnutrenniy) 800x700x120 0.8mm', 36.1), ('Shit SHE (vnutrenniy) 900x900x140 0.8mm', 40.44)], 'AVTOMATLAR UCHUN SHITLAR': [('V-2', 0.9), ('V-4', 1.05), ('V-6', 1.9), ('V-8', 2.4), ('V-12', 3.6), ('V-16', 5.2), ('V-24', 8.2), ('V-36', 10.5), ('N-2', 1), ('N-4', 1.2), ('N-6', 1.9), ('N-8', 2.4), ('N-12', 3.6), ('N-16', 5.2), ('N-24', 8.2), ('N-36', 11.5), ('V-12 Gold', 6.2), ('V-12 Platinum', 6.2), ('V-12 Black', 3.9), ('V-16 Gold', 5.6), ('V-16 Platinum', 5.6), ('V-16 Black', 5.6), ('V-24 Gold', 5.6), ('V 24 Platinum', 13.5), ('V-24 Black', 8.5), ('N-12 Black', 4), ('N-16 Black', 5.7), ('N-24 Black', 8.7)], 'GALOGEN — Xrustal': [('DU-1201', 1.8), ('DU-1202', 1.8), ('DU-1203', 1.8), ('DU-1204', 1.8), ('DU-1205', 1.8), ('DU-1206', 1.8), ('DU-1207', 1.8), ('DU-1208', 1.8), ('DU-1209', 1.8), ('DU-1210', 1.8), ('DU-1211', 1.8), ('DU-1212', 1.8), ('DU-1213', 1.8), ('DU-1214', 1.8), ('DU-1215', 1.8), ('DU-1216', 1.8), ('DU-1217', 1.8), ('DU-1218', 1.8), ('DU-1219', 1.8), ('DU-1220', 1.8), ('DU-1221', 1.8)], 'GALOGEN — Neoclassic 7W': [('Neoclassic 701', 2.0), ('Neoclassic 708', 2.0), ('Neoclassic 710', 2.2), ('Neoclassic 711', 2.2), ('Neoclassic 713', 2.2), ('Neoclassic 714', 2.0), ('Neoclassic 715', 2.0), ('Neoclassic 716', 2.2), ('Neoclassic 717', 2.2), ('Neoclassic 718', 2.2), ('Neoclassic 719', 2.2), ('Neoclassic 720', 2.2), ('Neoclassic 721', 2.2), ('Neoclassic 722', 2.2), ('Neoclassic 723', 2.0), ('Neoclassic 724', 2.2), ('Neoclassic 725', 2.2)], 'GALOGEN — Neoclassic 10W': [('Neoclassic 1001', 2.6), ('Neoclassic 1014', 2.4), ('Neoclassic 1015', 2.4), ('Neoclassic 1016', 2.9), ('Neoclassic 1017', 2.9), ('Neoclassic 1018', 2.9), ('Neoclassic 1019', 2.9), ('Neoclassic 1020', 2.4), ('Neoclassic 1021', 2.6), ('Neoclassic 1022', 2.9), ('Neoclassic 1023', 2.4)], 'MAGNIT TREKLAR — aksessuarlar': [('Aks. MA1 Soedinitel vhodnoy', 0.7), ('Aks. MA2 Soedinitel pryamoy', 0.7), ('Aks. MA3 Soedinitel uglovoy', 0.7), ('Aks. MA4 Blok pit. 48V 350W', 28), ('Aks. MA5 Blok pit. 48V 100W', 6), ('Aks. MA6 Blok pit. 48V', 8), ('Aks. MA9 Nabor', 1.6), ('Aks. MA10 Uglovoy', 2.5), ('Aks. MA13 naruj. rels 1m', 5), ('Aks. MA14 naruj. rels 2m', 9), ('Aks. MA15 Uglovoy Soedinitel', 2.5), ('Aks. MA16 Soedinitel relsov ks.', 0.5), ('Aks. MA17 Zaglushka Naruj rels', 0.5), ('Aks. MA18 Vnutrenniy Rels 2m', 10), ('Aks. MA19 Vnutrenniy Rels 3m', 15), ('Aks. MA20 Uglovoy Soedinitel', 1.5), ('Aks. MA21 T-obrazniy soedinitel', 3.5), ('Aks. MA22 Soedinitel relsov', 0.15), ('Aks. MA23 Vertikal soedinitel', 3), ('Aks. MA24 Vnutrenniy Rels 2m', 7.6), ('Aks. MA25 Vnutrenniy Rels 3m', 11.4), ('Aks. MA26 Blok 48V 400W', 14)], 'MAGNIT TREK YORITGICHLARI': [('MS1-12W 4000K', 1.8), ('MS1-12W 6500K', 1.8), ('MS1-24W 4000K', 2.8), ('MS1-14W 6500K', 2.8), ('MS1-36W 4000K', 5.5), ('MS1-12W 6500K', 5.5), ('MS2-6W 4000K', 2), ('MS2-6W 6500K', 2), ('MS2-12W 4000K', 2.2), ('MS2 12W 6500K', 2.2), ('MS2-18W 4000K', 2.9), ('MS2-18W 6500K', 2.9), ('MS2-24W 4000K', 4), ('MS2-24W 6500K', 4), ('MPS1-6W 4000K', 4), ('MPS1 6W 6500K', 4), ('MPS1-12W 4000K', 5), ('MPS1 12W 6500K', 5), ('MPS2-6W 4000K', 4), ('MPS2 6W 6500K', 4), ('MPS2-12W 4000K', 5), ('MPS2 -12W 6500K', 5), ('MS3-12W 4000K', 4.5), ('MS3 12W 6500K', 4.5), ('MS3-18W 4000K', 5.5), ('MS3-18W 6500K', 5.5), ('MS3-18 AB 4000K', 8), ('MS3-18 AB 6500K', 8), ('MS3-24 4000K', 7), ('MS3-24 6500K', 7), ('MS4-15W 4000K', 8), ('MS4 15W 6500K', 8), ('MS5-12W 6500K Black', 8.5), ('MS5-12W 6500K White', 8.5), ('MS5-18W 6500K Black', 8.5), ('MS5-18W 6500K White', 10.5), ('MS6-10W 6500K', 9.5), ('MS7-12W 6500K', 9.5), ('MS7-24W 6500K', 15)], 'EXIT': [('EX-1', 9.5), ('EX-2', 7), ('EX-3', 7), ('EX-4', 6.5), ('EX-5', 3.3), ('EX-6', 3.3), ('EX-O', 6), ('EX-EXIT', 1.6), ('EX-WI-Fi', 1.6), ('EX-TOILET', 1.6), ('EX-OPEN/CLOSED', 1.6), ('EX-Zanjir 2x50sm', 0.5)], 'VENTILYATOR': [('Dv 100 White', 4.7), ('Dv 100 Platinum', 7), ('Dv 100 Silver', 7), ('Dv 100 Black', 7), ('Dv 100 Gold', 7), ('Dv 150 White', 6.5), ('Dv2 100 White', 7.1), ('Dv2 150 White', 9.6), ('Dv3 100 White', 7), ('Dv3 150 White', 10), ('Dv3 100 Gold', 8.5), ('Dv3 100 Black', 8.5), ('Dv3 100 Silver', 8.5), ('Dv3 150 Silver', 11), ('Dv3 150 Gold', 11), ('Dv3 150 Black', 11), ('Dv4 100 White', 6), ('Dv3 100 Aqua', 7), ('Dv3 100 Vortex', 7)], 'ZVONOK': [('ZV01', 4.5), ('ZV02', 4.5), ('ZB01', 4), ('ZB02', 4), ('ZU01', 2.7), ('ZU02', 2.5)], 'LUXURY': [('Luxury 001', 14), ('Luxury 002', 9), ('Luxury 003', 11), ('Luxury 004', 7), ('Luxury 005', 14), ('Luxury 006', 10), ('Luxury 007', 11), ('Luxury 008', 7), ('Luxury 009', 12.5), ('Luxury 010', 10), ('Luxury 011', 12.5), ('Luxury 012', 10), ('Luxury 013', 12.5), ('Luxury 014', 10), ('Luxury 015', 16), ('Luxury 016', 12), ('Luxury 017', 16), ('Luxury 018', 12), ('Luxury 019', 16), ('Luxury 020', 12), ('Luxury 021', 16), ('Luxury 022', 12), ('Luxury 023', 16), ('Luxury 024', 12), ('Luxury 025', 16), ('Luxury 026', 12), ('Luxury 027', 16), ('Luxury 028', 12)], 'OFIS YORITGICHLARI': [('OS-50 Black 36W', 4.5), ('OS-70 Black 48W', 6.5), ('OS-100 Black 60W', 6.9), ('OS-150 Black 48W', 12.5), ('OS-180 Black 60W', 13.5), ('OS-280 Black 72W', 19), ('OS-70 White 48W', 6.5), ('OS-150 White 48W', 12.5), ('90 gradus 4 taraf', 1.8), ('90 gradus 5 taraf', 1.8), ('90 gradus 2 taraf', 1.8), ('60 gradus 6 taraf', 3.2), ('120 gradus 3 taraf', 1.8), ('120 gradus 2 taraf', 1.8), ('OS/6B-60', 30), ('OS/6B-80', 40), ('OS/3B-60', 30), ('OS/3B-80', 40), ('OS/D-60', 30), ('OS/D-80', 40), ('OS/Y-60', 25), ('OS/Y-80', 30), ('OS/4B-60', 30), ('OS/4B-80', 40), ('OS/B-60', 30), ('OS/B-80', 40), ('OS2-120 45W 4000K', 28), ('OS3-120 45W 4000K', 33), ('OS4-120 45W 4000K', 30), ('OS5-120 45W 4000K', 33), ('OS2-120 45W 6500K', 28), ('OS3-120 45W 6500K', 33), ('OS4-120 45W 6500K', 30), ('OS5-120 45W 6500K', 33)], 'POL ROZTKALAR': [('D 12 gold rozetka+2pin', 7), ('D 12 silver rozetka+2pin', 7), ('D 12 grey rozetka+2pin', 7), ('D 12 gold rozetka internet', 7), ('D 12 silver rozetka internet', 7), ('D 12 grey rozetka internet', 7), ('H 24 2-talik gold rozetka', 20), ('H 24 2-talik alyumin rozetka', 15)]}
PRODUCTS.setdefault("DUSEL", {}).update(DUSEL_EXTRA_20260928)


# ============================================================
# YANGI 2026 PDF KATALOG — DUSEL + VERAL
# Eski statik/dinamik mahsulotlar o'rniga yuklanadi.
# SALID katalogiga tegilmaydi.
# ============================================================

def apply_latest_pdf_catalogs():
    global PRODUCTS

    DUSEL_NEW = {
        "LED LAMPA": [
            ("D55 5W 6500/3000K", 0.52), ("D60 7W 6500/3000K", 0.62),
            ("D60 10W 6500/3000K", 0.66), ("D65 12W 6500/3000K", 0.75),
            ("D70 15W 6500/3000K", 0.90), ("D80 18W 6500/3000K", 1.05),
            ("5W C30/E14 6500K", 0.52), ("5W C30/E27 6500K", 0.62),
            ("7W C35/E14 6500K", 0.66), ("7W C35/E27 6500K", 0.75),
            ("9W C40/E14 6500/4000K", 0.90), ("9W C40/E27 6500K", 0.05),
            ("5W G45/E14 6500K", 0.65), ("5W B45/E27 6500K", 0.65),
            ("D20 20W 6500/4000K", 1.25), ("D30 30W 6500/4000K", 2.00),
            ("D40 40W 6500/4000K", 2.80), ("D50 50W 6500/4000K", 3.60),
            ("D60 60W 6500/4000K", 4.10), ("D80 80W", 6.00),
            ("D100 100W", 8.00), ("D150 150W", 11.00), ("D200 200W", 19.00),
            ("LED Candle 7W E14/E27", 0.75), ("LED Candle 9W E14/E27", 0.80),
            ("LED Candle 12W E14", 0.70),
            ("HL-F35-4W E14", 0.80), ("HL-F64-6W E27", 1.50),
            ("HL-F64-8W E27", 1.80), ("HL-F60-6W E27", 1.20),
            ("HL-F60-8W E27", 1.90), ("HL-F80-6W E27", 1.80),
            ("HL-F125-8W E27", 3.00), ("3W F STAR-3D", 4.10),
            ("3W F G95-3D", 3.30), ("6W STAR", 3.30),
            ("3W F LF95 Blue", 2.90), ("3W F LF95 Orange", 2.90),
            ("3W HEART", 3.10), ("3W F ST64-3D", 2.50),
            ("3W ST64-S Blue", 2.50), ("3W ST64-S Green", 2.50), ("3W ST64-S Pink", 2.50),
            ("Mr16 6W 6500K", 0.50), ("Mr16 6W 4000K", 0.68),
            ("Mr16 7W 6500/4000K", 0.70), ("Mr16 7W 6500/4000K", 0.70),
            ("Mr16 9 glass 6500/4000K", 0.75), ("Led flame lamp", 1.90),
        ],
        "LED AKRIL PANEL": [
            ("R6 6W", 1.10), ("R9 9W", 1.45), ("R12 12W", 1.70),
            ("R15 15W", 2.10), ("R18 18W", 2.30), ("R24 24W", 3.80),
            ("S6 6W", 1.20), ("S9 9W", 1.70), ("S12 12W", 2.00),
            ("S15 15W", 2.30), ("S18 18W", 2.75), ("S24 24W", 4.40),
            ("SR12 12W", 2.10), ("SR18 18W", 2.90), ("SR24 24W", 4.40),
            ("SS12 12W", 2.35), ("SS18 18W", 3.20), ("SS24 24W", 4.80),
            ("S-48 60x60", 6.50), ("S-60 60x60", 7.00), ("S-72 60x60", 7.50),
            ("SS48 60x60", 11.00), ("Art-72 6500K", 9.50), ("Art-96 6500K", 10.50),
            ("Ramka 60x60", 3.40),
            ("AR10 10W", 1.10), ("AR18 18W", 1.40), ("AR24 24W", 2.10),
            ("AR36 36W", 3.45), ("AR48 48W", 6.00),
            ("AS10 10W", 1.25), ("AS18 18W", 1.50), ("AS24 24W", 2.25),
            ("AS36 36W", 3.60), ("AS48 48W", 6.50),
            ("ASR18 18W", 1.90), ("ASR24 24W", 2.70), ("ASR36 36W", 4.00), ("ASR48 48W", 7.40),
            ("ASS18 18W", 2.00), ("ASS24 24W", 2.90), ("ASS36 36W", 4.50), ("ASS48 48W", 7.60),
            ("UR6 6W krug", 1.60), ("UR12 12W krug", 2.20), ("UR24 24W krug", 3.30), ("UR36 36W krug", 4.80),
            ("US6 6W kvadrat", 1.70), ("US12 12W kvadrat", 2.40), ("US24 24W kvadrat", 3.60), ("US36 36W kvadrat", 5.00),
            ("DAXR 18W 6500K", 2.00), ("DAXR 24W 6500K", 2.90), ("DAXR 36W 6500K", 4.30),
        ],
        "SLIM LED T5 LAMPA": [
            ("T9-ir120 6500K", 4.70), ("T9-ir60 6500K", 3.20),
            ("T8-comp 9W", 1.90), ("T8-comp 18W", 2.30),
            ("T8 Derjatel 60cm", 0.60), ("T8 Derjatel 120cm", 0.90),
            ("T8 Derjatel 2x60cm", 0.90), ("T8 Derjatel 2x120cm", 1.00),
            ("T8 60 10W", 0.80), ("T8 120 20W", 1.10), ("T8 120 30W", 1.45), ("T8 120 50W", 1.70),
            ("Slim 20W 60cm", 2.00), ("Slim 30W 90cm", 2.50), ("Slim 40W 120cm", 2.80),
            ("Slim-30W 60cm", 2.80), ("Slim-40W 60cm", 3.00), ("Slim 50W 6500K 60cm", 4.00),
            ("Slim 60W 6500K 60cm", 4.10), ("Slim 80W 6500K 60cm", 4.40),
            ("Slim 60W Black", 4.10), ("Slim 80W Black", 4.40),
            ("T8-B60 18W", 6.30), ("T8-B90 24W", 7.20), ("T8-B120 36W", 8.00),
            ("T5-AL 6W", 1.50), ("T5-AL 9W", 1.80), ("T5-AL 18W", 2.40),
            ("T5-PL 6W", 1.00), ("T5-PL 9W", 1.30), ("T5-PL 15W", 1.50), ("T5-PL 18W", 1.60),
            ("T5-PL30 6W", 1.20), ("T5-PL60 9W", 1.40), ("T5-PL90 15W", 1.70), ("T5-PL120 18W", 1.90),
            ("T6-PL30 6W", 0.90), ("T6-PL60 9W", 1.10), ("T6-PL90 15W", 1.40), ("T6-PL120 18W", 1.60),
            ("T8-AL 9W", 2.00), ("T8-AL 18W", 2.80),
            ("T8-120 1X", 8.00), ("T8-120 2X", 9.00),
            ("Slim 40W IP65", 4.80), ("Slim 40W IP65 Black", 4.80), ("Slim 60W IP65", 6.20),
            ("Slim G60 60W", 5.00), ("Slim G80 80W", 5.30), ("Slim PS60 Black", 3.20), ("Slim PS80 Black", 4.10),
        ],
        "PLAFONLAR": [
            ("BR8 8W", 1.60), ("BR17 17W", 2.50), ("BR23 23W", 3.80),
            ("BS8 8W", 1.80), ("BS17 17W", 2.90), ("BS23 23W", 4.30),
            ("YR9 9W 6500K", 1.90), ("YR9 9W 4000K", 1.90), ("YR18 18W 6500K", 2.60),
            ("YR18 18W 4000K", 2.60), ("YR24 24W 6500K", 3.80), ("YR24 24W 4000K", 3.80),
            ("YR36 36W 6500K", 5.50), ("YR36 36W 4000K", 5.50),
            ("YNR18 18W 6500K", 2.80), ("YNR24 24W 6500K", 4.10), ("YNR36 36W 6500K", 5.80),
            ("SASS18W", 4.30), ("SASS24W", 5.20), ("SASS36W", 6.30),
            ("SASR18W", 4.20), ("SASR24W", 5.10), ("SASR36W", 6.20),
            ("PR12 12W", 2.20), ("PR18 18W", 2.60), ("PR24 24W", 3.40),
            ("PS12 12W", 2.20), ("PS18 18W", 2.60), ("PS24 24W", 3.40),
            ("RPR18 18W", 2.50), ("RPR24 24W", 3.40), ("RPS18 18W", 2.50), ("RPS24 24W", 3.40),
            ("SP-30 White", 3.30), ("SP-40 White", 4.80), ("SP-40 Gold", 5.00),
            ("DSS-12 12W", 5.70), ("DSS-18 18W", 6.40), ("DSS-24 24W", 8.50),
            ("DSR-12 12W", 5.20), ("DSR-18 18W", 5.70), ("DSR-24 24W", 8.00),
        ],
        "PROJECTORLAR": [
            ("P1 10W", 1.80), ("P1 20W", 2.80), ("P1 30W", 4.50), ("P1 50W", 5.80), ("P1 100W", 10.50), ("P1 150W", 16.00), ("P1 200W", 21.00),
            ("P6 50W", 6.50), ("P6 100W", 11.00), ("P6 200W", 18.00), ("P6 300W", 26.00), ("P6 400W", 33.00), ("P6 500W", 42.00), ("P6 600W", 63.00),
            ("P7 10W", 1.70), ("P7 20W", 2.70), ("P7 30W", 3.10), ("P7 50W", 4.70), ("P7 100W", 8.20), ("P7 150W", 13.30), ("P7 200W", 16.80),
            ("PB 50W", 8.00), ("PB 100W", 14.00), ("PB 200W", 22.00), ("PB 300W", 32.00), ("PB 400W", 42.00), ("PB 500W", 65.00), ("PB 600W", 95.00), ("PB 1000W", 125.00),
            ("PP2 100W", 12.00), ("PP2 200W", 17.00), ("PP2 300W", 24.00), ("PP3 500W", 50.00), ("PP3 1000W", 65.00), ("PP3 2000W", 125.00),
            ("UFO 100W", 12.00), ("UFO 150W", 16.00), ("UFO 200W", 24.00),
            ("PD7-50 dachniy", 6.50), ("PD7-50 sht", 5.00),
        ],
        "FASAD PROJECTORLAR": [
            ("RKU2-150W", 24.00), ("RKU1-50W", 12.00), ("RKU1-100W", 17.00), ("RKU1-150W", 20.00), ("RKU1-300W", 27.00), ("RKU1-400W", 35.00),
            ("RKU2-50W", 17.00), ("RKU3-50W", 24.00), ("RKU3-100W", 32.00),
            ("FP1-30 12W 3000K", 12.00), ("FP1-50 18W 3000K", 17.00), ("FP1-100 36W 3000K", 27.00),
            ("FP2-30 12W", 12.00), ("FP2-50 18W", 17.00), ("FP2-100 36W", 27.00),
            ("FP3-30 2000K", 8.00), ("FP3-30 4500K", 8.00), ("FP3-50 2000K", 10.00), ("FP3-50 4500K", 10.00),
            ("FP3-100 2000K", 14.00), ("FP3-100 4500K", 14.00), ("FP3-10 10W", 10.00),
            ("FP8-9 9W", 10.00), ("FP8-36 36W", 21.00),
            ("RGBP-50", 11.00), ("RGBP-100", 16.00), ("RGBP-150", 16.00), ("RGBP-200", 19.00), ("RGBP-300", 24.50),
        ],
        "AKSESSUARLAR": [
            ("Dusel Perehodnik", 0.45), ("Universal", 0.70), ("Vilka DU-S", 0.25), ("Vilka DU-60", 0.25), ("Vilka DU-70", 0.30),
            ("DU-69 Perenoska", 1.50), ("DU-50 sotka", 1.00), ("DU-51 Cardos sotka", 1.50), ("DU-52 Pele sotka", 1.50),
            ("DU-53 sotka 4tali", 1.00), ("DU-54 sotka 4tali USB", 2.00), ("Udlinitel 3m", 2.00), ("Udlinitel 5m", 2.00), ("Udlinitel 10m", 7.00),
            ("Troynik DU-67", 1.30), ("Troynik DU-68", 1.10), ("DU-128 Perehodnik", 0.25),
            ("DD-01", 4.00), ("DD-02", 4.30), ("DD-03", 4.00), ("DD-04 White", 4.10), ("DD-05", 4.10), ("DD-06", 3.50),
            ("FR-06", 1.50), ("FR-10", 2.00), ("FR-25", 2.90), ("Patron E27 White", 0.25), ("Patron E27 Black", 0.25), ("Patron E14 White", 0.25), ("Patron E14 Black", 0.25),
        ],
        "TREK YORITGICH": [
            ("TS1 20W Black 6500K", 2.40), ("TS1 30W Black 6500K", 3.00), ("TS1 40W Black 6500K", 4.40),
            ("TS1 20W White 6500K", 2.40), ("TS1 30W White 6500K", 3.00), ("TS1 40W White 6500K", 4.40),
            ("TS2 20W Black 6500K", 3.30), ("TS2 30W Black 6500K", 4.50), ("TS2 40W Black 6500K", 7.00),
            ("TS2 20W White 6500K", 3.30), ("TS2 30W White 6500K", 4.50), ("TS2 40W White 6500K", 7.00),
            ("TS3 30W Black 6500K", 5.80), ("TS4-40 Black M", 7.00), ("TS4-30 White M", 5.50), ("TS4-40 Black T", 7.50), ("TS4-30 White T", 6.00),
            ("Rels 1M Black", 1.30), ("Rels 1.5M Black", 1.90), ("Rels 2M Black", 2.60), ("Rels 3M Black", 3.90),
        ],
        "STABILIZATOR": [
            ("DRS95-500VA",33), ("DRS95-1000VA",37), ("DRS95-1500VA",43), ("DRS95-2000VA",50), ("DRS95-3000VA",80), ("DRS95-5KVA",120), ("DRS95-10KVA",163), ("DRS95-12KVA",177), ("DRS95-15KVA",205), ("DRS95-20KVA",240),
            ("DRS45-5KVA",135), ("DRS45-10KVA",181), ("DRS45-12KVA",200), ("DRS45-15KVA",242), ("DRS45-20KVA",279), ("DRS45-30KVA",511),
            ("DSS-500VA",48), ("DSS-1000VA",60), ("DSS-1500VA",63), ("DSS-2000VA",84), ("DSS-5KVA",154), ("DSS-10KVA",211), ("DSS-15KVA",302), ("DSS-20KVA",465), ("DSS-30KVA",630), ("DSS-50KVA",1050),
            ("DSO-30KVA",763), ("DSO-50KVA",1350), ("DSO-60KVA",1440), ("DTS-1KVA",90), ("DTS-3KVA",135), ("DTS-5KVA",200), ("DTS-15KVA",450), ("DTS-20KVA",540), ("DTS-30KVA",950),
        ],
        "GALOGEN": [
            *[(f"DU-{i}", 1.80) for i in range(1201,1222)],
            ("Neoclassic 701",2.00),("Neoclassic 708",2.00),("Neoclassic 710",2.20),("Neoclassic 711",2.20),("Neoclassic 713",2.20),("Neoclassic 714",2.00),("Neoclassic 715",2.00),("Neoclassic 716",2.20),("Neoclassic 717",2.20),("Neoclassic 718",2.20),("Neoclassic 719",2.20),("Neoclassic 720",2.20),("Neoclassic 721",2.20),("Neoclassic 722",2.20),("Neoclassic 723",2.00),("Neoclassic 724",2.20),("Neoclassic 725",2.20),
            ("DU-1210 30W 6500K",3.20),("DU-1211 30W 4000K",3.20),("DU-1212 30W 6500K",3.20),("DU-1213 30W 4000K",3.20),
        ],
        "LUXURY": [(f"Luxury {i:03d}", p) for i,p in [(1,14),(2,9),(3,11),(4,7),(5,14),(6,10),(7,11),(8,7),(9,12.5),(10,10),(11,12.5),(12,10),(13,12.5),(14,10),(15,16),(16,12),(17,16),(18,12),(19,16),(20,12),(21,16),(22,12),(23,16),(24,12),(25,16),(26,12),(27,16),(28,12)]],
        "RICH SERIYA": [("Vikyuchatel 1",0.90),("Vikyuchatel 2",1.20),("Vikyuchatel 3",1.30),("Zvanok",1.00),("Rozetka 1",0.80),("Rozetka 2",1.10),("Rozetka zazem 1",0.95),("Rozetka zazem 2",1.30),("TEL",1.20),("INTERNET",1.50),("INTERNET + TEL",2.50),("TV+internet",2.40),("USB",2.70),("PERMUTATOR",1.70),("RAMKA 1",0.50),("RAMKA 2",0.70),("RAMKA 3",0.70),("RAMKA 4",0.90),("RAMKA 5",1.10)],
        "EXIT VENTILYATORLAR": [("EX-1",9.50),("EX-2",7.00),("EX-3",7.00),("EX-4",6.50),("EX-5",3.30),("EX-6",3.30),("EX-O",6.00),("EX-EXIT",1.60),("EX-WI-Fi",1.60),("EX-TOILET",1.60),("EX-OPEN/CLOSED",1.60),("EX-Zanjir 2x50sm",0.50),("ZV01",4.50),("ZV02",4.50),("ZB01",4.00),("ZB02",4.00),("ZU01",2.70),("ZU02",2.50)],
        "OFIS YORITGICHLARI": [("OS-50 Black 36W",4.50),("OS-70 Black 48W",6.50),("OS-100 Black 60W",6.90),("OS-150 Black 48W",12.50),("OS-180 Black 60W",13.50),("OS-280 Black 72W",19.00),("OS-70 White 48W",6.50),("OS-150 White 48W",12.50),("OS2-120 45W 4000K",28), ("OS3-120 45W 4000K",33),("OS4-120 45W 4000K",30),("OS5-120 45W 4000K",33)],
        "SHITLAR": [("Shit IP-31 350x250x110 0.3mm",2.55),("Shit IP-31 300x250x110 0.5mm",3.53),("Shit IP-31 350x250x110 0.5mm",3.72),("Shit IP-31 400x300x140 0.5mm",4.98),("Shit IP-31 400x400x140 0.5mm",5.76),("Shit IP-31 500x350x140 0.5mm",6.67),("Shit SHMP IP-31 500x400x150 0.5mm",8.21),("Shit SHMP IP-31 500x400x200 0.5mm",8.85),("Shit SHMP IP-31 700x500x200 0.5mm",13.14),("Shit SHMP IP-54 1200x600x300 0.8mm",58.20),("Shit SHMP IP-54 1200x800x300 0.8mm",69.65),("Shit VRU IP-31 1240x620x250 0.8mm",51.83),("Shit VRU IP-31 1200x800x250 0.8mm",60.82),("Shit VRU IP-31 1500x800x350 0.8mm",81.45),("Shit VRU IP-31 1700x1000x400 0.8mm",156.00)],
    }

    VERAL_NEW = {
        "LED LAMPALAR": [
            ("LED 5W 4000K/6500K",0.41),("LED 7W 4000K/6500K",0.50),("LED 10W 4000K/6500K",0.54),
            ("LED 12W 4000K/6500K",0.61),("LED 15W 4000K/6500K",0.72),("LED 18W 4000K/6500K",0.95),
            ("LED 20W",1.25),("LED 30W",2.00),("LED 40W",2.80),("LED 50W",3.60),("LED 60W",4.10),
            ("LED 5W C30/E14 6500K VERAL",0.52),("LED 5W C30/E27 6500K VERAL",0.62),
        ],
        "ICHKI AKRIL LED PANEL": [("VAS-10",0.89),("VAS-18",1.12),("VAS-24",1.69),("VAS-36",2.72),("VAS-48",4.75)],
        "TASHQI AKRIL LED PANEL": [("VASR-18",1.26),("VASR-24",1.85),("VASR-36",2.73),("VASR-48",4.52)],
        "TASHQI LED PANEL": [("VASS-18",1.37),("VASS-24",2.05),("VASS-36",2.90),("VASS-48",5.00)],
        "DUMALOQ ICHKI AKRIL": [("VAR-10",0.78),("VAR-18",1.02),("VAR-24",1.58),("VAR-36",2.26),("VAR-48",4.30)],
        "VERAL CANDLE": [("Candle 9W E14",0.70),("Candle 12W E14",0.75),("Candle 16W E14",0.60),("Candle 16W E27",0.60),("LED Candle 12W E14 Small",0.55),("Candle 14W E14/E27 3 color",0.80),("Candle 18W E14/E27 3 color",0.90),("Candle 24W E27/E14",1.10),("LED Candle-2 12W E14",1.00)],
        "SLIM": [("Vslim PS 60W 120cm",2.00),("Vslim PS 80W 120cm",2.40),("Vslim PS 100W 120cm",3.00),("Vslim PR 60W 120cm",2.20),("Vslim PR 80W 120cm",3.90),("Vslim PR 100W 120cm",4.50)],
        "LED PANEL 60X60": [("DS-48 48W 6500K/4000K",5.00),("DS-48 48W 4000K",5.00),("DS96 96W",11.00),("DS120 120W",13.00)],
        "P5": [("P5 50W",5.00),("P5 100W",6.00),("P5 200W",7.00),("P5 300W",10.50),("P5 400W",14.00),("P5 500W",18.00),("P5 600W",21.00),("P5 800W",23.00),("P5 1000W",27.00)],
        "P10": [("P10-50W",2.50),("P10-100W",5.00),("P10-200W",7.00),("P10-300W",14.00),("P10-500W",23.00)],
        "SAUNA PLAFON": [("VPR12 12W",1.70),("VPR18 18W",2.00),("VPR24 24W",2.70),("VPS12 12W",1.70),("VPS18 18W",2.00),("VPS24 24W",2.70)],
        "KO‘CHA YORITGICHI": [("RKU-50W",8.50),("RKU-100W",10.00),("RKU-150W",14.70),("RKU-200W",20.00)],
        "AKSESSUARLAR": [("Vika 10",0.42),("Vika 12",0.17),("Vika 08",0.17),("Vika 04",0.23),("Vika 03",0.29),("Vika 01",0.20),("Vika 07",0.18),("Vika 05",0.15),("Vika 06",0.12), ("O‘lchov tasmasi 1m",0.50),("O‘lchov tasmasi 3m",0.60),("O‘lchov tasmasi 5m",0.90)],
        "TREK YORITGICHI": [("VIS-1 30W white 4500K",2.40),("VIS-1 30W white 6500K",2.40),("VIS-1 30W black 4500K",2.40),("VIS-1 30W black 6500K",2.40),("VIS-1 40W white 4500K",3.00),("VIS-1 40W white 6500K",3.00),("VIS-1 40W black 4500K",3.00),("VIS-1 40W black 6500K",3.00)],
        "LED LENTA": [("2835 240LED 0.2W 12V 5m",2.00),("2025 288LED 0.2W 12V 5m",2.50),("COB 320LED 0.2W 12V 5m",3.00),("5050 60L RGB 12V 5m",3.00),("360C NEON",0.65),("2Mian NEON",0.75),("1 Line 0.5W 20M 4000K",0.45),("2 Line 0.5W 20M 4000K",0.50)],
        "BLOK PITANIYA": [("12V 100W",5.50),("12V 200W",7.00),("12V 400W",9.00),("24V 400W",10.00),("12-48V 100W",7.50),("12-48V 200W",10.50),("12-48V 400W",14.00)],
        "SHTEKER": [("Shteker 15mm",2.00),("Shteker RGB 11mm white",1.50),("Shteker RGB 13mm white",1.50),("Shteker RGB 11mm black",1.50),("Shteker RGB 13mm black",1.50),("Shteker RGB 11mm yellow",1.50),("Shteker RGB 13mm yellow",1.50),("Shteker 360 NEON",0.50),("Shteker 2mian NEON",0.50),("Shteker simsiz 8mm",0.50),("Shteker simsiz 11mm",0.50),("Shteker simsiz 12mm",0.50),("Shteker simsiz 15mm",0.50),("Universal shteker",0.50),("Shteker COB 13mm 8A",0.50),("Wireless connector wire 8mm",0.50),("Shteker perehodnik 220V",0.50),("Shteker perehodnik 3535 220V",0.50),("Wireless connector wire 11mm",0.50)],
        "DEKORATIV DEVOR PATRONLARI VELUX": [("002/1",4.55),("003/1",4.55),("004/1",4.55),("005/1",4.55),("002/2",6.55),("003/2",4.05),("004/2",7.55),("005/2",7.55),("010/2",7.55),("011/2",7.55),("012/1",5.50),("012/2",8.00),("013/2",7.50),("014/2",7.50),("015/2",4.05),("016/2BK",6.05),("017/2",6.05),("018/1",3.55),("019/2",5.55),("020/1",6.05),("020/2",9.05)],
        "VERAL XRUSTAL PLAFON": [(f"BL-{x}",17.05) for x in [102,103,104,105,106,108,107,114,118,120,121,122,123,124,125,126]],
        "VERAL PLAFON": [("40-01",4.50),("40-02",5.50),("40-03",4.50),("40-04",5.50),("40-05",4.50),("40-06",5.50),("40-07",4.50),("40-08",5.50),("40-09",4.50),("40-10",5.50),("40-11",4.50),("40-12",5.50)],
        "KVADRAT PLAFONAR 72W": [("50-60",7.50),("50-61",8.50),("50-62",8.00),("50-63",8.00),("50-64",8.00),("50-65",8.00),("50-66",8.50),("50-68",8.50),("50-69",8.50),("50-70",8.50),("50-71",8.50),("50-74",8.50),("50-81",8.50),("50-82",8.50)],
        "HI-TECH PLAFON": [(f"VH-{i:02d}",6.50) for i in range(1,13)] + [(f"VHP-{i:02d}",6.50) for i in range(1,13)],
        "GALOGEN": [("VERAL Galogen 01",0.70),("VERAL Galogen 02",0.70),("VERAL Galogen 03",0.70),("VERAL Galogen 04",0.70),("VERAL Galogen 05",0.70),("VERAL Galogen 06",0.70),("VERAL Galogen 07",0.70),("VERAL Galogen 08",0.70),("VERAL Galogen 09",0.70),("VERAL Galogen 10",1.00),("VERAL Galogen 11",1.00),("VERAL Galogen 12",1.00),("VERAL Galogen 13",1.00),("VERAL Galogen 14",1.55),("VERAL Galogen 15",1.55),("VERAL Galogen 16",1.55),("VERAL Galogen 17",1.55),("VERAL Galogen 18",0.25),("VERAL Galogen 19",0.70),("VERAL Galogen 20",0.70)],
        "GOFRA": [("G16g",0.043),("G20g",0.061),("G25g",0.10),("G32g",0.128),("G40g",0.35),("G16o",0.043),("G20o",0.061),("G25o",0.10),("G32o",0.061),("G40o",0.32),("G16b",0.043),("G20b",0.061),("G25b",0.10),("G32b",0.061),("G40b",0.32),("G16r",0.043),("G20r",0.061),("G25r",0.10),("G32r",0.061),("G40r",0.32)],
        "KABEL KANAL KOROB": [("Korob 12x12",15.00),("Korob 12x16",15.00),("Korob 16x16",15.00),("Korob 20x20",15.00),("Korob 25x16",15.00),("Korob 25x25",15.00),("Korob 40x25",15.00),("Korob 40x40",15.00),("Korob 60x40",15.00),("Korob 60x60",15.00),("Korob 100x60",15.00)],
        "STABILIZATOR": [("SDW-500VA",37),("SDW-1KVA",45),("SDW-2KVA",54),("SDW-5KVA",100),("SDW-10KVA",160),("SDW-15KVA",2068),("SVC-D10KVA 80-250V",210),("SVC-D15KVA 80-250V",260),("SVC-D20KVA 80-250V",490),("SVC-D30KVA 80-250V",530),("VRS95-500VA",24),("VRS95-1000VA",27),("VRS95-1500VA",35),("VRS95-2000VA",37),("VRS95-3000VA",55),("VRS95-5KVA",75),("VRS95-10KVA",120),("VRS95-15KVA",160),("VRS95-20KVA",185),("VRS45-5KVA",90),("VRS45-10KVA",145),("VRS45-15KVA",185),("VRS45-20KVA",215),("VRS45-30KVA",375)],
    }

    # DUSELning qo'shimcha katalogi ham saqlanadi.
    # Avvalgi versiyada DUSEL_NEW bilan almashtirilgani uchun SHITLAR,
    # kvadrat galogenlar va boshqa qo'shimcha bo'limlar yo'qolib qolgan edi.
    # Endi yangi PDF katalog + qo'shimcha DUSEL katalogi birga ishlaydi.
    DUSEL_NEW.update(DUSEL_EXTRA_20260928)

    # SALIDga tegmaymiz: faqat DUSEL va VERAL kataloglari yangilanadi.
    PRODUCTS["DUSEL"] = DUSEL_NEW
    PRODUCTS["VERAL"] = VERAL_NEW

    conn = get_db()
    cur = conn.cursor()
    for brand in ("DUSEL", "VERAL"):
        cur.execute("DELETE FROM dynamic_products WHERE brand=?", (brand,))
        cur.execute("DELETE FROM dynamic_sections WHERE brand=?", (brand,))
        cur.execute("DELETE FROM dynamic_brands WHERE brand=?", (brand,))
        cur.execute("DELETE FROM section_groups WHERE brand=?", (brand,))
        cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)", (brand,))
        for section, rows in PRODUCTS[brand].items():
            cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", (brand,section))
            for product, price in rows:
                cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", (brand,section,product,float(price)))
    conn.commit(); conn.close()


# ============================================================
# DATABASE
# ============================================================

def get_db():
    return sqlite3.connect(DB_FILE, timeout=30)


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            chat_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            discount_percent INTEGER NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            qty INTEGER NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS states (
            chat_id INTEGER PRIMARY KEY,
            step TEXT NOT NULL,
            data TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalog_images (
            image_key TEXT PRIMARY KEY,
            file_id TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS catalog_image_slots (
            image_key TEXT NOT NULL,
            slot INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            PRIMARY KEY(image_key, slot)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            UNIQUE(brand, section, product)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS product_packaging (
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            color TEXT NOT NULL DEFAULT '',
            product TEXT NOT NULL,
            box_qty INTEGER NOT NULL DEFAULT 0,
            pack_qty INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(brand, section, color, product)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_brands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dynamic_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            UNIQUE(brand, section)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS section_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            group_name TEXT NOT NULL,
            child_section TEXT NOT NULL,
            UNIQUE(brand, group_name, child_section)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS shop_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_overrides (
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(brand, section, product)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS color_price_overrides (
            brand TEXT NOT NULL,
            section TEXT NOT NULL,
            color TEXT NOT NULL,
            product TEXT NOT NULL,
            price REAL NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY(brand, section, color, product)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin_contacts (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TEXT NOT NULL,
            order_day TEXT
        )
    """)

    # Eski bazalarni avtomatik moslashtiramiz.
    cur.execute("PRAGMA table_info(orders)")
    order_columns = {row[1] for row in cur.fetchall()}
    if "created_at" not in order_columns:
        cur.execute("ALTER TABLE orders ADD COLUMN created_at TEXT")
    if "order_day" not in order_columns:
        cur.execute("ALTER TABLE orders ADD COLUMN order_day TEXT")
    cur.execute("UPDATE orders SET order_day=substr(created_at,1,10) WHERE order_day IS NULL AND created_at IS NOT NULL")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_day ON orders(order_day)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_client ON orders(chat_id)")

    # Eski bazalarda discount_percent bo‘lmasa, avtomatik qo‘shiladi.
    cur.execute("PRAGMA table_info(clients)")
    client_columns = {row[1] for row in cur.fetchall()}
    if "discount_percent" not in client_columns:
        cur.execute("ALTER TABLE clients ADD COLUMN discount_percent INTEGER NOT NULL DEFAULT 0")

    # Eski cart jadvalida id ustuni bo‘lmasa ham kod rowid orqali ishlaydi.
    conn.commit()
    conn.close()


def load_dynamic_products():
    conn = get_db()
    cur = conn.cursor()

    # Admin qo‘shgan yangi brendlarni yuklaymiz.
    cur.execute("SELECT brand FROM dynamic_brands ORDER BY id ASC")
    for (brand,) in cur.fetchall():
        PRODUCTS.setdefault(brand, {})

    # Admin qo‘shgan bo‘limlarni, hatto hali mahsuloti bo‘lmasa ham, yuklaymiz.
    cur.execute("SELECT brand, section FROM dynamic_sections ORDER BY id ASC")
    for brand, section in cur.fetchall():
        PRODUCTS.setdefault(brand, {})
        PRODUCTS[brand].setdefault(section, [])

    # Dinamik mahsulotlarni yuklaymiz.
    cur.execute("SELECT brand, section, product, price FROM dynamic_products ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    for brand, section, product, price in rows:
        PRODUCTS.setdefault(brand, {})
        current = PRODUCTS[brand].get(section)
        # SALID rangli bo‘limlari alohida ranglar bilan ishlaydi.
        if isinstance(current, dict):
            continue
        PRODUCTS[brand].setdefault(section, [])
        item = (product, float(price))
        if item not in PRODUCTS[brand][section]:
            PRODUCTS[brand][section].append(item)

    apply_price_overrides()

def save_dynamic_brand(brand):
    brand = brand.strip()
    if not brand:
        return False
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)", (brand,))
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def save_dynamic_section(brand, section):
    brand = brand.strip()
    section = section.strip()
    if not brand or not section:
        return False
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand, section) VALUES(?,?)", (brand, section))
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def save_shop_location(latitude, longitude):
    conn = get_db()
    cur = conn.cursor()
    value = json.dumps({"latitude": float(latitude), "longitude": float(longitude)})
    cur.execute("INSERT OR REPLACE INTO shop_settings(key,value) VALUES('shop_location',?)", (value,))
    conn.commit()
    conn.close()


def get_shop_location():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT value FROM shop_settings WHERE key='shop_location'")
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None


def set_admin_contact(key, value):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO admin_contacts(key,value) VALUES(?,?)", (key, str(value).strip()))
    conn.commit()
    conn.close()


def get_admin_contacts():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT key,value FROM admin_contacts")
    rows = dict(cur.fetchall())
    conn.close()
    # Asosiy admin kontaktlari — oldindan tayyor.
    rows.setdefault("telegram", str(MAIN_ADMIN_ID))
    rows.setdefault("phone", "+998938682150")
    return rows


def show_admin_contacts(chat_id):
    if not is_admin(chat_id):
        return
    c = get_admin_contacts()
    telegram = c.get("telegram", "Kiritilmagan")
    phone = c.get("phone", "Kiritilmagan")
    send_message(chat_id,
        "📞 <b>ADMIN BILAN BOG‘LANISH</b>\n\n"
        "Telegram: <b>" + telegram + "</b>\n"
        "Telefon: <b>" + phone + "</b>",
        keyboard([
            ("✏️ Telegram", "contact_edit|telegram"),
            ("✏️ Telefon", "contact_edit|phone"),
            ("⬅️ Admin panel", "admin_home")
        ])
    )

def show_user_contacts(chat_id):
    c = get_admin_contacts()
    telegram = c.get("telegram", str(MAIN_ADMIN_ID))
    phone = c.get("phone", "+998938682150")
    # Telegram profiliga bevosita o'tish uchun ID asosidagi havola.
    tg_link = "tg://user?id=" + str(MAIN_ADMIN_ID)
    text = ("📞 <b>ADMIN BILAN BOG‘LANISH</b>\n\n"
            "💬 Telegram: <a href=\"" + tg_link + "\">" + telegram + "</a>\n"
            "📱 Telefon: <b>" + phone + "</b>")
    send_message(chat_id, text, main_menu())

def show_brand_manage(chat_id):
    if not is_admin(chat_id):
        return
    rows = []
    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT brand FROM dynamic_brands ORDER BY id ASC")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    if not rows:
        send_message(chat_id, "🛠 Hozircha admin qo‘shgan brend yo‘q.", admin_reply_keyboard()); return
    buttons=[]
    for brand in rows:
        buttons.append(("🏷 " + brand, "brandmanage|" + brand))
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "🛠 <b>BREND BOSHQARUVI</b>\n\nO‘zgartirish yoki o‘chirish uchun brendni tanlang:", keyboard(buttons))


def show_brand_manage_actions(chat_id, brand):
    if not is_admin(chat_id): return
    send_message(chat_id, "🏷 <b>" + brand + "</b>\n\nAmalni tanlang:", keyboard([
        ("✏️ Nomini o‘zgartirish", "brandrename|" + brand),
        ("🗑 O‘chirish", "branddelete|" + brand),
        ("📂 Bo‘limlarni boshqarish", "sectionmanage|" + brand),
        ("⬅️ Brendlar", "brand_manage")
    ]))


def show_section_manage(chat_id, brand):
    if not is_admin(chat_id): return
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT section FROM dynamic_sections WHERE brand=? ORDER BY id ASC", (brand,))
    sections=[r[0] for r in cur.fetchall()]
    cur.execute("SELECT group_name, child_section FROM section_groups WHERE brand=? ORDER BY id ASC", (brand,))
    groups={}
    for g,c in cur.fetchall(): groups.setdefault(g,[]).append(c)
    conn.close()
    grouped_children={c for arr in groups.values() for c in arr}
    if brand == "DUSEL":
        sections = ordered_dusel_sections(sections)
        preferred_groups = [
            "LED LAMPA", "Slim", "Akril-Panel", "PROYEKTORLAR",
            "AKSESSUARLAR", "TREK YORITGICH RELS", "STABILIZATOR"
        ]
        rank = {name: i for i, name in enumerate(preferred_groups)}
        groups = {g: groups[g] for g in sorted(groups, key=lambda x: (rank.get(x, 10000), x.casefold()))}
    buttons=[(f"📁 {g}", "sectiongroupadmin|"+brand+"|"+g) for g in groups]
    for sec in sections:
        if sec not in grouped_children:
            buttons.append((f"📂 {sec}", "sectionaction|"+brand+"|"+sec))
    if len(sections)>=2:
        buttons.append(("🔗 Bo‘limlarni birlashtirish", "sectionmerge|"+brand))
    buttons.append(("⬅️ Brend", "brandmanage|"+brand))
    send_message(chat_id, "📂 <b>"+brand+" BO‘LIMLARI</b>\n\nBo‘limni tanlang yoki istalgan bo‘limlarni bitta guruhga birlashtiring:", keyboard(buttons))


def show_section_group_admin(chat_id, brand, group):
    if not is_admin(chat_id): return
    conn=get_db(); cur=conn.cursor(); cur.execute("SELECT child_section FROM section_groups WHERE brand=? AND group_name=? ORDER BY id ASC", (brand,group)); children=[r[0] for r in cur.fetchall()]; conn.close()
    buttons=[("📂 "+c, "sectionaction|"+brand+"|"+c) for c in children]
    buttons.append(("✏️ Guruh nomini o‘zgartirish", "grouprename|"+brand+"|"+group))
    buttons.append(("🗑 Guruhni chiqarish", "groupungroup|"+brand+"|"+group))
    buttons.append(("⬅️ Bo‘limlar", "sectionmanage|"+brand))
    send_message(chat_id, "📁 <b>"+group+"</b>", keyboard(buttons))

def start_section_merge(chat_id, brand):
    if not is_admin(chat_id): return
    conn=get_db(); cur=conn.cursor(); cur.execute("SELECT section FROM dynamic_sections WHERE brand=? ORDER BY id ASC", (brand,)); sections=[r[0] for r in cur.fetchall()]; conn.close()
    buttons=[(sec, "mergesel|"+brand+"|"+sec) for sec in sections]
    buttons.append(("⬅️ Bo‘limlar", "sectionmanage|"+brand))
    set_state(chat_id,"admin_section_merge",{"brand":brand,"selected":[]})
    send_message(chat_id,"🔗 <b>Birlashtiriladigan bo‘limlarni tanlang</b>\n\nIstalgancha bo‘limni tanlang. Tanlangan bo‘limga yana bosib bekor qilishingiz mumkin.",keyboard(buttons))


def show_section_actions(chat_id, brand, section):
    if not is_admin(chat_id): return
    send_message(chat_id, "📂 <b>" + section + "</b>", keyboard([
        ("✏️ Nomini o‘zgartirish", "sectionrename|" + brand + "|" + section),
        ("🗑 O‘chirish", "sectiondelete|" + brand + "|" + section),
        ("⬅️ Bo‘limlar", "sectionmanage|" + brand)
    ]))


# ============================================================
# TELEGRAM API
# ============================================================

def api(method, data=None, attempts=3):
    url = API_URL + method

    for attempt in range(attempts):
        try:
            if data is None:
                req = urllib.request.Request(url)
            else:
                body = urllib.parse.urlencode(data).encode("utf-8")
                req = urllib.request.Request(url, data=body)

            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read().decode("utf-8")

            result = json.loads(raw)

            if result.get("ok"):
                return result

            print("Telegram API:", result)
            return result

        except Exception as e:
            print("Internet/API xatosi:", e)

            if attempt < attempts - 1:
                time.sleep(3)

    return None


def admin_reply_keyboard():
    # Toza va kerakli admin panel. Ortiqcha bo‘limlar klaviaturadan olib tashlangan.
    return {
        "keyboard": [
            [{"text": "👥 Mijozlar"}, {"text": "📦 Buyurtmalar"}],
            [{"text": "📋 Spiskalar"}, {"text": "🎁 Chegirmalar"}],
            [{"text": "📢 Xabar yuborish"}, {"text": "🛍 Mahsulotlar"}],
            [{"text": "🔎 Qidirish"}, {"text": "➕ Mahsulot qo‘shish"}],
            [{"text": "📦 Karobka/Pochka"}, {"text": "💵 Price boshqaruvi"}],
            [{"text": "📍 Location qo‘shish", "request_location": True}],
            [{"text": "🖼 Rasmlar"}, {"text": "📊 Excel"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }


def user_reply_keyboard():
    return {
        "keyboard": [
            [{"text": "🛍 Mahsulotlar"}, {"text": "🔎 Qidirish"}],
            [{"text": "🛒 Savat"}, {"text": "⚙️ Sozlamalar"}],
            [{"text": "📍 12-DOKON lokatsiyasi"}],
            [{"text": "📞 Admin bilan bog‘lanish"}],
            [{"text": "📩 Takliflar"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }


def send_photo(chat_id, file_id, caption="", keyboard=None):
    data = {
        "chat_id": str(chat_id),
        "photo": str(file_id),
        "caption": caption,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    return api("sendPhoto", data)

def send_media_group(chat_id, file_ids, caption=""):
    media = []
    for i, fid in enumerate(file_ids[:3]):
        item = {"type": "photo", "media": str(fid)}
        if i == 0 and caption:
            item["caption"] = caption
            item["parse_mode"] = "HTML"
        media.append(item)
    if not media:
        return None
    return api("sendMediaGroup", {"chat_id": str(chat_id), "media": json.dumps(media, ensure_ascii=False)})


def send_document(chat_id, file_id, caption="", keyboard=None):
    data = {"chat_id": str(chat_id), "document": str(file_id),
            "caption": caption, "parse_mode": "HTML"}
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    return api("sendDocument", data)


def send_broadcast_media(message, target_id):
    caption = message.get("caption", "")
    if message.get("photo"):
        file_id = message["photo"][-1].get("file_id")
        return send_photo(target_id, file_id, "📢 <b>YANGILIK</b>\n\n" + caption, user_reply_keyboard())
    if message.get("document"):
        file_id = message["document"].get("file_id")
        return send_document(target_id, file_id, "📢 <b>YANGILIK</b>\n\n" + caption, user_reply_keyboard())
    return None


def save_catalog_image(image_key, file_id, slot=1):
    slot = max(1, min(3, int(slot)))
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO catalog_images(image_key,file_id,updated_at) VALUES(?,?,?)",
        (image_key, file_id, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    cur.execute(
        "INSERT OR REPLACE INTO catalog_image_slots(image_key,slot,file_id,updated_at) VALUES(?,?,?,?)",
        (image_key, slot, file_id, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_catalog_image(image_key, slot=1):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT file_id FROM catalog_image_slots WHERE image_key=? AND slot=?", (image_key, int(slot)))
    row = cur.fetchone()
    if not row and int(slot) == 1:
        cur.execute("SELECT file_id FROM catalog_images WHERE image_key=?", (image_key,))
        row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def get_catalog_images(image_key):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT slot,file_id FROM catalog_image_slots WHERE image_key=? ORDER BY slot ASC", (image_key,))
    rows = cur.fetchall()
    if not rows:
        cur.execute("SELECT file_id FROM catalog_images WHERE image_key=?", (image_key,))
        row = cur.fetchone()
        rows = [(1, row[0])] if row else []
    conn.close()
    return [file_id for slot, file_id in rows if 1 <= int(slot) <= 3][:3]


def get_catalog_images_for(brand, section, color=None, model=None):
    found=[]
    for key in _image_key_candidates(brand, section, color, model):
        for fid in get_catalog_images(key):
            if fid not in found:
                found.append(fid)
            if len(found) >= 3:
                return found[:3]
    return found[:3]


def delete_catalog_image(image_key, slot):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM catalog_image_slots WHERE image_key=? AND slot=?", (image_key, int(slot)))
    conn.commit()
    conn.close()


def image_key(brand, section, color=None, model=None):
    # 2 qism: brend|bo‘lim; 3 qism: brend|bo‘lim|rang;
    # 4 qism: brend|bo‘lim|model|rang. Eski kalitlar ham ishlaydi.
    parts = [str(brand), str(section)]
    if model:
        parts.append(str(model))
    if color:
        parts.append(str(color))
    return "|".join(parts)


def _image_key_candidates(brand, section, color=None, model=None):
    keys = [image_key(brand, section, color, model)]
    if model:
        keys += [image_key(brand, section, color), image_key(brand, section + " / " + str(model), color)]
    if color:
        keys.append(image_key(brand, section, color))
    keys.append(image_key(brand, section))
    out=[]
    for k in keys:
        if k and k not in out:
            out.append(k)
    return out


def show_admin_brand_add(chat_id):
    if not is_admin(chat_id):
        return
    set_state(chat_id, "admin_brand_name", {})
    send_message(chat_id, "➕ <b>YANGI BREND QO‘SHISH</b>\n\nBrend nomini yozing.\nMasalan: <code>NEW BRAND</code>\n\nBekor qilish: /cancel")


def show_admin_section_add(chat_id):
    if not is_admin(chat_id):
        return
    buttons = [("🏷 " + brand, "addsecbrand|" + brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "➕ <b>BREND ICHIGA BO‘LIM QO‘SHISH</b>\n\nAvval brendni tanlang:", keyboard(buttons))


def start_section_add(chat_id, brand):
    if not is_admin(chat_id):
        return
    set_state(chat_id, "admin_section_name", {"brand": brand})
    send_message(chat_id, "🏷 Brend: <b>" + brand + "</b>\n\n📂 Yangi bo‘lim nomini yozing.\nMasalan: <code>ROZETKALAR</code>\n\nBekor qilish: /cancel")


def show_admin_location(chat_id):
    if not is_admin(chat_id):
        return
    send_message(chat_id, "📍 <b>DOKON LOKATSIYASI</b>\n\nQuyidagi Telegram tugmasi orqali do‘kon joylashuvini yuboring. Yuborilgach, bot uni saqlaydi va mijozlarga shu lokatsiyani ko‘rsatadi.\n\nAgar oldingi lokatsiyani almashtirmoqchi bo‘lsangiz, yangi lokatsiyani yuboring.", admin_reply_keyboard())


def shop_location_message(chat_id):
    loc = get_shop_location()
    if loc:
        url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(str(loc.get("latitude")) + "," + str(loc.get("longitude")))
        return "📍 <b>DUSEL 12-DOKON lokatsiyasi</b>\n\n<a href=\"" + url + "\">📍 Xaritada ochish</a>"
    url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote("DUSEL 2-blok 12-DOKON, Toshkent")
    return "📍 <b>DUSEL 12-DOKON</b>\n\n<a href=\"" + url + "\">📍 Xaritada ochish</a>"


def set_price_override(brand, section, product, price, deleted=0):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO price_overrides
                   (brand, section, product, price, deleted)
                   VALUES (?,?,?,?,?)""",
                (brand, section, product, float(price), int(deleted)))
    conn.commit()
    conn.close()


def set_color_price_override(brand, section, color, product, price, deleted=0):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO color_price_overrides
                   (brand, section, color, product, price, deleted)
                   VALUES (?,?,?,?,?,?)""",
                (brand, section, color, product, float(price), int(deleted)))
    conn.commit()
    conn.close()


def apply_price_overrides():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT brand,section,product,price,deleted FROM price_overrides")
    normal = cur.fetchall()
    cur.execute("SELECT brand,section,color,product,price,deleted FROM color_price_overrides")
    colors = cur.fetchall()
    conn.close()
    for brand,section,product,price,deleted in normal:
        if brand not in PRODUCTS or section not in PRODUCTS[brand] or isinstance(PRODUCTS[brand][section], dict):
            continue
        if deleted:
            PRODUCTS[brand][section] = [(p,pr) for p,pr in PRODUCTS[brand][section] if p != product]
        else:
            found=False
            for i,(p,pr) in enumerate(PRODUCTS[brand][section]):
                if p==product:
                    PRODUCTS[brand][section][i]=(product,float(price)); found=True; break
            if not found:
                PRODUCTS[brand][section].append((product,float(price)))
    for brand,section,color,product,price,deleted in colors:
        try:
            arr=PRODUCTS[brand][section][color]
            if deleted:
                PRODUCTS[brand][section][color]=[(p,pr) for p,pr in arr if p != product]
            else:
                found=False
                for i,(p,pr) in enumerate(arr):
                    if p==product:
                        arr[i]=(product,float(price)); found=True; break
                if not found: arr.append((product,float(price)))
        except Exception:
            pass


def show_admin_price_brands(chat_id):
    if not is_admin(chat_id):
        return
    buttons=[("🏷 "+brand,"pricebrand|"+brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel","admin_home"))
    send_message(chat_id,"💵 <b>PRICE BOSHQARUVI</b>\n\nBrendni tanlang:",keyboard(buttons))


def show_admin_price_sections(chat_id, brand):
    if not is_admin(chat_id): return
    buttons=[("📂 "+sec,"pricesec|"+brand+"|"+sec) for sec in PRODUCTS.get(brand,{})]
    buttons.append(("⬅️ Brendlar","admin_prices"))
    send_message(chat_id,"💵 <b>"+brand+"</b>\n\nBo‘limni tanlang:",keyboard(buttons))


def show_admin_price_products(chat_id, brand, section):
    if not is_admin(chat_id): return
    products=PRODUCTS.get(brand,{}).get(section,[])
    buttons=[]
    if isinstance(products,dict):
        for color,arr in products.items():
            for i,(product,price) in enumerate(arr):
                buttons.append(("💵 "+product+" ("+color+") — $"+format(price),
                                "priceedit|"+brand+"|"+section+"|"+color+"|"+str(i)))
    else:
        for i,(product,price) in enumerate(products):
            buttons.append(("💵 "+product+" — $"+format(price),
                            "priceedit|"+brand+"|"+section+"|"+str(i)))
    buttons.append(("⬅️ Bo‘limlar","pricebrand|"+brand))
    send_message(chat_id,"💵 <b>"+brand+" → "+section+"</b>\n\nMahsulotni tanlang:",
                 keyboard(buttons))


def show_admin_price_actions(chat_id, brand, section, index, color=None):
    if not is_admin(chat_id): return
    try:
        item=PRODUCTS[brand][section][color][index] if color else PRODUCTS[brand][section][index]
        product,price=item
    except Exception:
        send_message(chat_id,"❌ Mahsulot topilmadi."); return
    suffix="|"+color if color else ""
    buttons=[
        ("✏️ Narxni yangilash","priceupdate|"+brand+"|"+section+suffix+"|"+str(index)),
        ("🗑 O‘chirish","pricedelete|"+brand+"|"+section+suffix+"|"+str(index)),
        ("⬅️ Mahsulotlar","pricesec|"+brand+"|"+section)]
    send_message(chat_id,"💵 <b>PRICE</b>\n\n📦 "+product+"\n💰 Hozirgi narx: <b>$"+format(price)+"</b>\n\nAmalni tanlang:",
                 keyboard(buttons))


def get_price_item(brand,section,index,color=None):
    try:
        return PRODUCTS[brand][section][color][int(index)] if color else PRODUCTS[brand][section][int(index)]
    except Exception:
        return None


def show_admin_pack_brands(chat_id):
    if not is_admin(chat_id):
        return
    buttons = [("🏷 " + brand, "packbrand|" + brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "📦 <b>KAROBKA / POCHKA BOSHQARUVI</b>\n\nBrendni tanlang:", keyboard(buttons))


def show_admin_pack_sections(chat_id, brand):
    if not is_admin(chat_id):
        return
    buttons = [("📂 " + sec, "packsec|" + brand + "|" + sec) for sec in PRODUCTS.get(brand, {})]
    buttons.append(("⬅️ Brendlar", "admin_packaging"))
    send_message(chat_id, "📦 <b>" + html.escape(brand) + "</b>\n\nBo‘limni tanlang:", keyboard(buttons))


def show_admin_pack_products(chat_id, brand, section):
    if not is_admin(chat_id):
        return
    products = PRODUCTS.get(brand, {}).get(section, [])
    buttons = []
    if isinstance(products, dict):
        for color, arr in products.items():
            for i, (product, price) in enumerate(arr):
                box, pack = get_product_packaging(brand, section, product, color)
                buttons.append(("📦 " + product + " (" + color + ") — " + str(box) + "/" + str(pack),
                                "packedit|" + brand + "|" + section + "|" + color + "|" + str(i)))
    else:
        for i, (product, price) in enumerate(products):
            box, pack = get_product_packaging(brand, section, product, "")
            buttons.append(("📦 " + product + " — " + str(box) + "/" + str(pack),
                            "packedit|" + brand + "|" + section + "|" + str(i)))
    buttons.append(("⬅️ Bo‘limlar", "packbrand|" + brand))
    send_message(chat_id, "📦 <b>" + html.escape(brand) + " → " + html.escape(section) + "</b>\n\nMahsulotni tanlang:\n\n<b>Karobka / Pochka</b> ko‘rinishida: dona/dona", keyboard(buttons))


def show_admin_pack_actions(chat_id, brand, section, index, color=""):
    if not is_admin(chat_id):
        return
    item = get_price_item(brand, section, index, color)
    if not item:
        send_message(chat_id, "❌ Mahsulot topilmadi.")
        return
    product, price = item
    box, pack = get_product_packaging(brand, section, product, color)
    suffix = "|" + color if color else ""
    buttons = [
        ("📦 Karobka sonini kiritish", "packbox|" + brand + "|" + section + suffix + "|" + str(index)),
        ("📦 Pochka sonini kiritish", "packpack|" + brand + "|" + section + suffix + "|" + str(index)),
        ("⬅️ Mahsulotlar", "packsec|" + brand + "|" + section),
    ]
    send_message(chat_id,
                 "📦 <b>QADOQLASH</b>\n\n" +
                 "Mahsulot: <b>" + html.escape(product) + "</b>\n" +
                 "Narx: <b>$" + format(price) + "</b>\n" +
                 "Karobka: <b>" + str(box) + " dona</b>\n" +
                 "Pochka: <b>" + str(pack) + " dona</b>\n\n" +
                 "Kerakli amalni tanlang:", keyboard(buttons))


def show_admin_product_add(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    buttons = [("🏷 " + brand, "prodaddbrand|" + brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "➕ <b>MAHSULOT QO‘SHISH</b>\n\nAvval brendni tanlang:", keyboard(buttons))


def start_product_add(chat_id, brand):
    if not is_admin(chat_id):
        return
    set_state(chat_id, "admin_product_section", {"brand": brand})
    send_message(chat_id, "🏷 Brend: <b>" + brand + "</b>\n\n📂 <b>Bo‘lim nomini yozing.</b>\nMasalan: <code>YANGI LAMPALAR</code>\n\nMavjud bo‘lmasa avtomatik yaratiladi.\nBekor qilish: /cancel")


def seed_salid_light_catalog():
    """SALID LIGHT katalogi: SG va SN kodlarini alohida bo‘limlarga qo‘shadi."""
    sg = [
        ("SG01-10 white",5.0),("SG01-10 black",5.0),("SG02-10 white",3.2),("SG02-10 black",3.2),
        ("SG03-7 white",5.0),("SG03-7 black",5.0),("SG04-10 white",5.7),("SG04-10 black",5.7),
        ("SG04-10/2 white",11.0),("SG04-10/2 black",11.0),("SG04-10/3 white",17.0),("SG04-10/3 black",17.0),
        ("SG17-10 white",5.3),("SG17-10 black",5.3),("SG17-12 white",5.0),("SG17-12 black",5.0),
        ("SG18-10 white",5.3),("SG18-10 black",5.3),("SG18-12 white",5.0),("SG18-12 black",5.0),
        ("SG18-10/2 white",10.5),("SG18-10/2 black",10.5),("SG18-12/2 white",10.0),
        ("SG18-10/3 white",16.0),("SG18-10/3 black",16.0),("SG18-12/3 white",15.0),
        ("SG14-10 white+gold",4.2),("SG15-10 white+black",4.2),("SG16-10 white+black",6.0),
        ("SG16-10/2 white+black",11.0),("SG16-12/2 white+black",10.5),("SG16-10/3 white+black",16.0),("SG16-12/3 white+black",16.0),
        ("SG17-10 white",5.3),("SG17-10 black",5.3),("SG17-12 white",5.0),("SG17-12 black",5.0),
        ("SG18-10 white",5.3),("SG18-10 black",5.3),("SG18-12 white",5.0),("SG18-12 black",5.0),
        ("SG18-10/2 white",10.5),("SG18-10/2 black",10.5),("SG18-12/2 white",10.0),
        ("SG18-10/3 white",16.0),("SG18-10/3 black",16.0),("SG18-12/3 white",15.0),
        ("SG19-10 white",3.8),("SG19-10 black",3.8),("SG20-10 white",2.8),("SG20-10 black",2.8),
        ("SG21-10 white",5.0),("SG21-10 black",5.0),("SG21-20 white",8.0),("SG21-20 black",8.0),
        ("SG21-30 white",11.5),("SG21-30 black",11.5),("SG21-40 white",16.0),("SG21-40 black",16.0),
        ("SG22-12 white",7.0),("SG22-12 black",7.0),("SG23-7 white",4.3),("SG23-7 black",4.3),
        ("SG23-12 white",4.7),("SG23-12 black",4.7),("SG23-20 white",8.5),("SG23-20 black",8.5),("SG24-10 white",5.7),("SG24-10 black",5.7),
        ("SG24-12 white",5.7),("SG24-12 black",5.7),("SG24-10/2 white",10.5),("SG24-10/2 black",10.5),
        ("SG24-12/2 white",10.0),("SG24-12/2 black",10.0),("SG24-10/3 white",16.0),("SG24-10/3 black",16.0),
        ("SG24-12/3 white",15.0),("SG25-12 white+ gold",6.0),("SG25-12 black+white",6.0),
        ("SG25-12 black+chromium",6.0),("SG25-12*2 white+ gold",12.0),("SG25-12*2 black",12.0),
        ("SG25-12*2 black+chromium",12.0),("SG27-15 WH",7.0),("SG27-15 BK+BC",7.0),("SG27-15 WH+K GD",7.0),
        ("SG27-15 BK+K GD",7.0),("SG27-15*2 WH",14.0),("SG27-15*2 Bk+BC",14.0),("SG27-15*2 Wh +K GD",14.0),
        ("SG27-15*2 Bk+K GD",14.0),("SG28-15*2 Wh+PL",11.0),("SG28-15*2 Bk+BC",11.0),
        ("SG28-15*2 Wh+CH",11.0),("SG28-15*2 Wh+Rose GD",11.0),("SG29-15*2 WH",11.0),("SG29-15*2 BK",11.0),
        ("SG29-15*2 GY",11.0),("SG29-15*2 WH+Rose GD",11.0),("SG29-15*2 Wh +PL",11.0),("SG29-15*2 Bk+Rose GD",11.0),
        ("SG29-15*2 Bk +CH",11.0),("SG30-15 Wh +PL",5.5),("SG30-15 Gy+sl",5.5),("SG30-15*2 Wh +PL",11.0),
        ("SG30-15*2 Gy+sl",11.0),("SG31-15 Wh",10.0),("SG31-15 Black",10.0),("SG32-12 White",7.0),
        ("SG32-12 Bk +BC",7.0),("SG33-12 Wh+CH",8.0),("SG33-12 Bk +GD",8.0),("SG33-12*2 Wh+CH",15.0),
        ("SG33-12*2 Bk +GD",15.0),("SG34-15 Gy",7.0),("SG35-18 WH",8.0),("SG35-18 BK",8.0),
        ("SG35-18 WH+GY",8.0),("SG35-18 BK +GY",8.0),("SG35-24 WH",9.0),("SG35-24 BK",9.0),
        ("SG35-24 WH+GY",9.0),("SG35-24 BK +GY",9.0),("SG36-12 WH",5.5),("SG36-12 BC+GY",5.5),
    ]
    sn = [
        ("SN01-15 silver",5.0),("SN01-15 black",5.0),("SN01-20 silver",7.3),("SN01-20 gold",7.3),
        ("SN02-15 gold+silver",5.7),("SN02-15 chrome+silver",5.7),("SN02-15 gold+black",5.7),("SN02-20 gold+silver",7.3),("SN02-20 chrome+silver",7.3),
        ("SN03-15 black+gold",5.7),("SN03-15 silver+gold",5.7),("SN03-15 chrome+silver",5.7),("SN03-20 chromium+gold",7.3),("SN04-15 silver+gold",5.7),("SN04-20 black+gold",7.3),
        ("SN05-15 silver",5.5),("SN05-15 silver+gold",5.5),("SN05-15 chromium+gold",5.5),("SN05-15 black+gold",5.5),("SN05-20 silver+gold",7.3),("SN05-20 silver",7.3),
        ("SN06-15 silver+gold",5.7),("SN06-15 black+gold",5.7),("SN07-15 chromium+chromium",5.7),("SN07-15 silver+gold",5.7),
        ("SN08-15 gold+black",5.7),("SN08-15 black+silver",5.7),("SN08-15 black+gold",5.7),("SN08-15 chrome+silver",5.7),("SN08-15 chrome+gold",5.7),("SN08-20 chrome+gold",7.3),
        ("SN09-15 chromium",6.8),("SN09-15 bronze",6.8),("SN10-15 black",6.8),("SN10-15 silver",6.8),("SN10-15 gold",6.8),("SN10-15 chromium",6.8),
        ("SN11-15 bronze",5.6),("SN12-15 black",5.5),("SN13-15 silver",5.5),("SN14-20 chromium",7.3),
        ("SN06-15 black+gold",5.7),
    ]
    conn=get_db(); cur=conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)",("SALID",))
    for section, rows in (("SALID LIGEHT — SG", sg),("SALID LIGEHT — SN", sn)):
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)",("SALID",section))
        for product,price in rows:
            cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)",("SALID",section,product,price))
    conn.commit(); conn.close(); load_dynamic_products()





def seed_salid_pdf_catalogs():
    """SALID: PDF asosidagi GALOGEN va LYUSTRA kataloglarini noldan yuklaydi.
    DUSEL va VERAL ma'lumotlariga tegmaydi.
    """
    galogen_data = """SG03-7 white|5
SG03-7 black|5
SS01-12/2 white+black|15
SG07-12 black|4.2
SG07-18 black|6
SG07-24 black|9
SG07-30 white|12
SG09-12 white+gold|6
SG09-12 black +white chromium|6
SS02-12 white|6.3
SS02-12 black|6
SN02-20 chrome+silver|7.3
SN02-20 gold+black|7.3
SN03-15 chrome+silver|5
SN05-20 silver|7
SN08-15 chrome +gold|4.4
SN13-15 silver|5
SG13-12 black|4
SG13-12/2 black|8
SG13-15 black|6
SG13-15 white|6
SG13-15/2 black|12.5
SG13-15/2 white|12.5
SG13-15/2 white gold|12
SG16-12 white+black|5.3
SG18-10/2 white|10.5
SG18-10/2 black|10.5
SG18-12 black|5
SG18-12/3 white|15
SG21-40 white|12
SG21-40 black|12
Sg22-12 white+black|7
SG24-12/2 white|11
SS04-18 black+chromiu m|9
SS05-20 white|9.5
SS05-20 black|9.5
SS09-12 white|5.5
SS09-12 black|5.5
SN05-15 silver+gold|5
SN04-15 silver+gold|5
SN03-15 silver+gold|5.5
SN08-15 black+gold|5
SN02-15 gold+silver|5.5
SN07-15 silver+gold|5
SN07-15 chromium+chro mium|5
SN01-15 black|4.4
SN05-20 silver+gold|7.3
SN03-20 chromium+gold|7.3
SN02-20 gold+silver|7.3
SN01-20silver|7
SN01-20 gold|7
SN01-20 black|7
SN14-20 chromium|6.6
SN15-15 PL|6
SN16-15 CH|6
SN16-15 GD|6
SN16-15 GD+PL|6
SN18-15 CH+PL|6
SN18-20 GD+PL|8
SN18-20 CH+PL|8
SN19-15 BC|6
SN19-15 PL+BC|6
SN19-20 PL|8
SN21-10 GD|4
SN22-10 GD|4
SN23-10 GD|4
SN23-10 PL|4
SN25-10 CH|4
SN26-10 SV|4
SN27-12 BK+BC|5.5
SN27-12 PL+GD|5.5
SN28-12 WH+BC|5.5
SN28-12 BK+BC|5.5
SN28-12 PL+GD|5.5
SN29-15 BK|5.5
SN29-15 PL|5.5
SS10-15 black+gold|11
SS11-12 white|8
SS11-12 black|8
SS12-15 white|7
SS12-15 white+rose gold|7
SS12-15 white+chromiu m|7
SS12-15 black|7
SS12-15 black+rose gold|7
SS12-15 black+chromiu m|7
SS12-24 white|10.5
SS12-24 white+rose gold|10.5
SS12-24 white+chromiu m|10.5
SS12-24 black|10.5
SS14-12 white+gun black|6
SS14-12 white+gold|6
SS14-12 black+gold|6
SS15-12 black+gun black|11.5
SS16-6/18 black+gun black|17
SS16-9A/25 black+gun black|26
SS16-9B/25 black+gun black|18
SS19-12 white|8.5
SS19-12 black|8.5
SG27-15 BK+BC|6
SG27-15 WH +K GD|6
SG27-15*2 WH|12
SG27-15*2 Bk+BC|12
SG27-15*2 Wh +K GD|12
SG27-15*2 Bk+K GD|12
SG30-15*2 Wh|9
SG30-15 BK|5
SG30-15*2 BK|9
SG31-15 Wh|9
SG31-15 Black|9
SG32-12 White|6
SG33-12 Wh+CH|7
SG33-12 Bk +GD|7
SG33-12*2 Wh+CH|13
SG33-12*2 Bk +GD|13
SG34-15 WH|7
SG35-18 WH|8
SG35-18 BK|8
SG35-18 WH+GY|8
SG35-18 BK +GY|8
SG35-24 WH|9
SG35-24 WH+GY|9
SG37-12/2 WH|12
SG38-12 BK|5.7
SG38-18 WH|9
SG38-18/2 WH|20
SG38-18/2 BK|20
SG39-20 WH|10.5
SG39-20 BK|10.5
SG39-30 WH|14
SG39-30 BK|14
SG40-18/2 WH|16
SG40-18/2 BK|16
SG42-12 WH+CH|4.4
SG42-12 BK+GD|4
SG42-12/2 WH+GD|8.5
SG42-12/2 WH+CH|8
SG42-12/2 BK+GD|8
SG42-12/2 BK+CH|8.5
SG43-12 BK+CH|6.5
SG44-12/2 WH+GD|8
SG44-12/2 WH+SL|8
SG44-12/2 BK|8
SG45-12 BK+CH|4.4
SG45-12/2 WH+GD|8.8
SG45-12/2 BK+CH|8.8
SG46-24 WH|8.8
SG46-24 BK|8.8
SG47-12/2 BK|10.5
SS21-12 white|5.5
SS21-12 white+chromiu m|5.5
SS21-12 white+gold|5.5
SS22-15 white+black|8.5
SS22-15 black|8.5
SS23-15 white+gold|8
SS23-15 black|8
SS24-24 white+black|13
SS24-24 white+chromiu m|13
SS24-24 white+gold|13
SS24-24 black+gold|13
SS24-30 white+chromiu m|14
SS24-30 white+gold|14
SS24-30 black+chromiu m|14
SS25-20 WH|12
SS25-20 BK|12
SS26-12 WH+BK|5
SS26-12 WH+GD|5
SS26-12 BK|5
SS26-12 BK+CH|5
SS27-12 WH|6.5
SS27-15 WH|9.5
SS27-15 BK|9.5
SL12/6500|2.5
SL12/4500|2.5
SL15/6500|3"""
    lyustra_data = """SA54/2 WHI+FGD|6.7
SA54/3 WHI+FGD|10
SA55/2 YL+FG|6.3
SA55/3 YL+FG|9.2
SA62/2 CR|5.2
SA62/3 CR|7.7
SA62/5 CR|13.6
SA68/2 FGD|5.2
SA68/3 FGD|7.7
SA68/5 FGD|13.6
SA71/5 BK+CH|14.1
SA74/2 BK+CR|6.5
SA74/3 BK+CR|9.2
SA76/3 BK+FG|10.5
SA76/5 BK+FG|15.5
SA83/3 CH|13.1
SA85/2 BK+FG|7
SA85/3 BK+FG|10.9
SA85/4 BK+FG|14
SA89/2 CH|5.7
SA89/3 CH|8.3
SA12/2 WH+FG|5.7
SA12/3 WH+FG|8.3
SA12/5 WH+FG|14
SA42/6 BLK+CR|19.2
SA42/2 WH+FG|7.7
SA42/3 WH+FG|10.5
SA42/4 WH+FG|13.1
SA42/6 WH+FG|19.2
SA49/2 CH|7.7
SA49/3 CH|11.6
SA57/6 BLK+CR|14.6
SA57/8 BLK+CR|21.3
SA57/6 WHI+FG|14.6
SA57/8 WHI+FG|21.3
SA90/2 GD|5.7
SA90/3 GD|8.3
SA91/2 GD+WH|5.7
SA92/5 FG|17.5
SA92/5 CH|17.5
SA94/5 BK|19.2
SA95/3 CR|12.2
SA97/3 CR|12.2
SA98/2 BK|5.9
SA98/3 BK|8.4
SA99/2 GD+WH|5.9
SA99/3 GD+WH|8.4
SA100/2 BK+CH|5.9
SA100/3 BK+CH|8.4
SA101/2 BK+CH|5.9
SA101/3 BK+CH|8.4
SA102/2 BK|5.9
SA102/3 BK|8.4
SA103/2 WH|5.9
SA103/3 WH|8.4
SA104/2 CH|5.9
SA104/3 CH|8.4
SA105/2 CH+WH|5.9
SA105/3 CH+WH|8.4
SA106/2 CH+WH|5.9
SA106/3 CH+WH|8.4
SA107/2 CH|5.9
SA107/3 CH|8.4
SA80/4 BK+FG|12.6
SA81/5 BK+FG|14.6
SA01/5 GM|15.5
NC01/D550/8 BK+SD|18.5
NC01/800*300/8 BK+SD|24.3
NC01/1000*400/14 BK+SD|38
NC01/1800*600/35BK+SD|104.8
NC01/D550/8 GD+SD|18.5
NC01/D750/15 GD+SD|33.2
NC01/800*300/8 GD+SD|24.3
NC01/1000*400/14 GD+SD|38
NC01/1500*500/30 GD+SD|76.8
NC01/250*310B/2 SV+CH|7.8
NC01/D550/8 SV+CH|18.5
NC01/800*300/8 SV+CH|24.3
NC01/1000*400/14 SV+CH|38
NC01/1800*600/35 SV+CH|111.6
NC01/250*310B/2 WH+GD|7.8
NC01/D550/8 WH+GD|18.5
NC01/800*300/8 WH+GD|24.3
NC01/1000*400/14 WH+GD|38
NC01/250*310B/2 CHC+GD|7
NC01/D550/8 CHC+GD|18.5
NC01/D750/15 CHC+GD|33.2
NC01/800*300/8 CHC+GD|24.3
NC01/1000*400/14 CHC+GD|38
NC09/D400/5 GD SD|19.2
NC09/D500/8 GD SD|27.9
NC09/D750/12 GD SD|54.1
NC09/800*300/8 GD SD|37.5
NC09/W1000*L400/ 12 GD SD|51.5
NC09/D950/20 GD SD|87.3
NC09-W1800*L600 GD SD|174.6
NC09/W2000*L600/30 GD SD|174.6
NC09/D400/5 CH|19.2
NC09/D500/8 CH|27.9
NC09/D750/12 CH|54.1
NC09/D950/20 CH|87.3
NC09/800*300/8 CH|37.5
NC09/W1000*L400/12 CH|51.5
NC09/W1600*L500/24 CH|117.9
NC09/W2000*L600/30 CH|174.6
NC09/250x300/1 BK SD|7.7
NC09/D400/5 SD|19.2
NC09/D500/8 SD|27.9
NC09/D750/12 SD|54.1
NC09/800*300/8 SD|37.5
NC09/W1000*L400/12 SD|51.5
NC09/D950/20 SD|87.3
NC09-W1200*L600 BK SD|104.8
NC09/W1600*L500/24 SD|117.9
NC09/500*H1700 SD|96
NC09/650*H1800 SD|117.9
NC10/250x300B/1 SD|7.7
NC10/D400/5 SD|15.7
NC10/D500/8 SD|22.7
NC10/750/12 SD|48
NC10/800/16 BK+SD|61.1
NC10/D950/18 SD|76.8
NC10/800*300/8 SD|32.3
NC10/W1200*L500/14 SD|76.8
NC10/W1600*L500/24 SD|104.8
NC10/W2000*L600/30 SD|139.7
NC10/D400/5 CH|15.7
NC10/D500/8 CH|22.7
NC10/750/12 CH|48
NC10/D950/18 CH|76.8
NC10/W1200*L500/14 CH|76.8
NC10/W1600*L500/24 CH|104.8
NC10/W2000*L600/30 CH|139.7
NC10/GR800/16 SD|76.8
NC10/GR1000/24 SD|104.8
NC10/GR1200/36 SD|148.4
NC10/GR800/16 CH|76.8
NC10/GR1000/24 CH|104.8
NC10/GR1200/36 CH|148.4
NC10/D500*1700H SD|87.3
NC10/D650*1800H SD|113.5
NC34/D1000 GD|87.3
NC34/D1200*500 GD|96
NC34/D1600*500 GD|113.5
NC34/D800 BK|69.8
NC13/D800/16 SD|78.6
NC13/D1200/36 SD|165.9
NC13/D800/16 GD SD|78.6
NC31/800/20 GD|61.1
NC31/800/20 FGD|61.1
NC46/D500*H1700/21BK|87.3
NC46/D650*H1800/25 BK|113.5
NC47/D550*H1700/18 GD|116.4
NC47/D650*H1800/27 GD|131
NC52/2W/2 SD|16.5
NC52/D800/15 SD|131
NC52/D1000/22 SD|169.7
NC56/D600/11 SD|82.4
NC56/D800/15 SD|126.1
NC56/D1000/22 SD|179.5
NC56/L1200*500/16 SD|150.3
NC56/L1500*600/24 SD|218.3
NC57/D1000/22 SD|194
NC60/D800/15 SD|145.5
NC61/L1200*500/16 SD|140.6
NC62/D400/5 CH|19.2
NC62/D500/8 CH|34
NC62/D750/12 CH|52.4
NC62/800*300/8 CH|40.2
NC62/D950/18 CH|121.3
NC62/L1200*500/16 CH|111.6
NC62/GR1000/24 SD|135.3
NC62/GR1200/36 SD|174.6
NC63/D1000/22 SD|145.5
NC63/D1000/22 CH|145.5
NC63/L1000*400/16 CH|87.3
NC63/L1500*500/24 CH|135.8
NC64/D800/15 GD|165.9
NC64/D1000/22 GD|232.8
NC64/L1000*400/12 GD|135.8
NC64/L1200*500/16 GD|203.7
NC64/L1500*600/24 GD|291
NC65/2W/2 SD|14.6
NC65/L1200*500/16 SD|111.6
NC65/2W/2 CH|14.6
NC65/D800/15 CH|92.2
NC65/D1000/22 CH|126.1
NC65/L1200*500/16 CH|111.6
NC65/L1500*600/24 CH|174.6
NC66/D1000/22 CH|122.2
NC70/2w/2 SD|18.4
NC70/600*1800/22 SD|242.5
NC70/700*2500/30 SD|279.4
NC73/D500/8 SD|53.3
NC73/D600/11 SD|72.7
NC73/D800/15 SD|106.7
NC73/D1000/22 SD|145.5
NC73/L1000*400/12 SD|101.9
NC73/L1200*500/16 SD|135.8
NC73/2W/2 CH|17.5
NC73/D500/8 CH|53.3
NC73/D600/11 CH|72.7
NC73/D800/15 CH|106.7
NC73/D1000/22 CH|145.5
NC73/L1000*400/12 CH|101.9
NC73/L1200*500/16 CH|135.8
NC73/L1500*600/24 CH|194
NC74/D1000/22 CH|155.2
NC75/L1200*500/16 SD|218.3
NC76/D1000/22 SD|179.5
NC77/D600/11 SD|69.8
NC77/D800/15 SD|117.9
NC77/L1200*500/16 SD|117.9
NC77/L2000*600/36 SD|392.9
NC79/R2000*600/48 SD|405.9
bra NC80/2w/2 SD|19.4
NC81/2w/2 SD|19.4
NC81/630*2000/22 SD|281.3
NC84/D800/15 SD|122.2
NC84/L1200*500/16 SD|116.4
NC85/D800/15 SD|122.2
NC85/D1000/18 SD|174.6
NC85/L1200*500/16 SD|113.5
NC85/L1500*600/24 SD|194
NC86/D800/15 SD|82.4
NC86/D1000/18 SD|126.1
NC86/L1200*500/16 SD|106.7
NC86/L1500*600/24 SD|155.2
NC87/D600/11 SD|82.4
NC87/D1000/18 SD|184.3
NC87/L1200*500/16 SD|126.1
NC87/L1500*600/24 SD|194
NC88/D800/15 SD|96
NC89/D600/11 SD|87.3
NC89/D800/15 SD|131
NC89/D1000/18 SD|179.5
NC89/L1200*500/16 SD|145.5
NC89/L1500*600/24 SD|213.4
NC90/D800/15 SD|116.4
NC90/D1000/18 SD|155.2
NC90/L1500*600/24 SD|194
NC91/L1500*600/LED SD|213.4
NC102/D1000 GD+CL|125.7
NC102/D1500 GD+CL|288.1
NC102/D1000 CH+CL|125.7
NC102/D1500 CH+CL|288.1
NC102/L1200*550 CH+CL|96
NC102/L1600*650 CH+CL|135.3
NC102/L2000*800 CH+CL|209.5
NC102/B/3W CH+CL|13.1
NC103/D1000 GD+CL|125.7
NC103/D850 CH+CL|96
NC103/D1000 CH+CL|125.7
NC103/L1600*650 CH+CL|131
NC103/L2000*800 CH+CL|209.5
NC103/900*2100 CH+CL|349.2
NC103/B/3W CH+CL|13.1
NC103/D850 GD+CL+GC|96
NC103/D1000 GD+CL+GC|131
NC103/L1600*650 GD+CL+GC|131
NC103/L2000*800 GD+CL+GC|209.5
NC103/B/3W GD+CL+GC|13.1
NC103/D1000 CH+CL+BK|125.7
NC103/L1200*550 CH+CL+BK|96
NC103/L1600*650 CH+CL+BK|131
NC103/L2000*800 CH+CL+BK|209.5
NC103/B/3W CH+CL+BK|13.1
NC104/D800 GD+CL|86.4
NC104/D1000 GD+CL|113.5
NC104/L2000*800 GD+CL|192.1
NC104/B/3W GD+CL|13.1
NC104/D1000 CH+CL|113.5
NC104/L1200*550 CH+CL|86.4
NC104/L1600*650 CH+CL|122.2
NC104/L2000*800 CH+CL|192.1
NC104/B/3W CH+CL|13.1
NC105/D900*H2100 GD+CL|340.5
NC105/D1000 CH+CL|96
NC105/L1200*550 CH+CL|67.2
NC105/L1600*650 CH+CL|96
NC105/L2000*800 CH+CL|157.1
NC105/D900*H2100 CH+CL|288.1
NC105/B/3W CH+CL|11.3
NC105/L1600*650 GD+CL+GC|96
NC105/L2000*800 GD+CL+GC|157.1
NC105/B/3W GD+CL+GC|11.3
NC105/D850 CH+CL+BK|67.2
NC105/D1000 CH+CL+BK|96
NC105/L1200*550 CH+CL+BK|67.2
NC105/L1600*650 CH+CL+BK|96
NC105/L2000*800 CH+CL+BK|157.1
NC105/B/3W CH+CL+BK|11.3
NC111/W/2 SD|14
NC111/600/12 SD|61.1
NC111/800/18 SD|96
NC111/950/24 SD|135.3
NC111/1200/32 SD|240
NC111/1200*500/20 SD|109.1
NC111/1600*600/36 SD|190
NC114/600/12 SD|69.8
NC114/800/20 SD|113.5
NC114/1000/24 SD|165.9
NC114/1600*600/30 SD|218.3
NC114/2000*600/42 SD|305.6
NC117/D800*H2500 BL|218.3
NC117/D800*H2500 GN|218.3
NC118/D1000*H3000|698.4
NC121/D800/18 SD|139.7
NC122/D800/18 SD|113.5
NC122/D1000/21 SD|157.1
NC122/L1500*600/28 SD|205.2
NC123/L1200*500/18 SD|148.4
NC123/L2000*600/28 SD|349.2
NC124/D600/11 SD|74.2
NC125/D600/11 SD|76.8
NC125/L1200*500/18 SD|131
NC125/L2000*600/28 SD|349.2
NC126/750/18 SD|91.7
NC126/1200*500/18 SD|122.2
NC127/D800 SV+CL+BK|113.5
NC127/L1200 SV+CL+BK|148.4
NC127/L1600 SV+CL+BK|192.1
NC128/D800 GD+CL|113.5
NC128/L1200 GD+CL|148.4
NC128/L1600 GD+CL|192.1
NC129/D800 GD+CL|131
NC129/L1200 GD+CL|192.1
NC129/L1600 GD+CL|244.4
NC130/D800 GD+CL+GC|122.2
NC130/L1200 GD+CL+GC|165.9
NC130/L1600 GD+CL+GC|227
NC131/L1600*500 GD|288.1
NC131/L1200*500 GD|218.3
NC131/D800*2500 GD|218.3
NC132/550/10 SD|54.1
NC132/750/13 SD|87.3
NC132/1200*500/15 SD|117.9
NC133/600/9 SD|61.1
NC133/800/12 SD|96
NC133/1000/18 SD|144
NC133/800/12 CH|96
NC133/1000/18 CH|144
NC134/550/10 SD|46.3
NC134/750/13 SD|72.5
NC134/1200*500/15 SD|100.4
NC135/600/10 SD|54.1
NC135/800/13 SD|82.9
NC135/1000/18 SD|122.2
NC135/1200*500/15 SD|109.1
NC136/400/5 GD+SD|24.4
NC136/550/10 GD+SD|41.9
NC136/750/13 GD+SD|69.8
NC136/1200*500/15 GD+SD|91.7
NC136/400/5 CH+BK|24.4
NC136/550/10 CH+BK|41.9
NC136/750/13 CH+BK|69.8
NC136/1200*500/15 CH+BK|91.7
NC137/550/10 SD|61.1
NC137/750/13 SD|100.4
NC137/1200*500/15 SD|131
NC138/550/10 SD|65.5
NC138/750/13 SD|109.1
NC138/1200*500/15 SD|135.3
NC139/550/10 SD|55
NC139/750/13 SD|87.3
NC139/1200*500/15 SD|117.9
NC140/600/10 SD|61.1
NC140/800/13 SD|91.7
NC140/1000/18 SD|131
NC141/600 CH|55
NC141/800 CH|78.6
NC141/1200*400 CH|96
NC142/400/5 GD+SD|27.1
NC142/550/10 GD+SD|44.5
NC142/750/13 GD+SD|69
NC142/800*300/10 GD+SD|48.9
NC142/1000*400/12 GD+SD|67.2
NC142/400/5 CH+BK|27.1
NC142/550/10 CH+BK|44.5
NC142/750/13 CH+BK|69
NC142/800*300/10 CH+BK|48.9
NC142/1000*400/12 CH+BK|67.2
NC143/400/5 SD|21
NC143/550/10 SD|34
NC143/800*300/10 SD|40.2
NC143/1000*400/12 SD|55
NC144/600 SD|82.9
NC144/800 SD|117.9
NC144/1200*200 SD|113.5
NC144/1500*200 SD|192.1
NC146/600/11 SD|55
NC146/800/15 SD|82.9
NC147/600/8 SD|71.6
NC147/800/12 SD|100.4
NC147/1000/16 SD|157.1
NC147/1200*400/16 SD|174.6
NC147/1200/20 SD|192.1
NC149/800/17 SD|110.9
NC149/1000/24 SD|170.2
NC149/1200*500/20 SD|122.2
NC151/600/12 SD|82.9
NC151/800/19 SD|131
NC151/1200*500/20 SD|135.3
NC152/800 SD|113.5
NC153/600/6 SD|76.8
NC153/800/8 SD|113.5
NC153/800+500/13 SD|174.6
NC155/800/16 SD|104.8
NC155/1000/18 SD|144
NNC01/400/4 CH|28.8
NNC01/500/5 CH|39.3
NNC01/600/8 CH|57.6
NNC01/1000*350/8 CH|76.8
NNC02/400/4 CH|28.8
NNC02/500/5 CH|39.3
NNC02/600/8 CH|57.6
NNC02/1000*350/8 CH|76.8
NNC03/400/4 CH|30.6
NNC03/500/5 CH|43.7
NNC03/600/8 CH|61.1
NNC03/1000*350/8 CH|82.9
VenS01|20
VenS02|20
VenS03|20
VenS04|51
VenS07|36
HT04/5 FGD|27.1
HT04/5 BK|27.9
HT25/5/80 GD+BK|24.4
HT86/12 FGD+BK|49.8
HT86/8 FGD+BK|36.7
HT105 GD|22.1
HT106 GD|24
HT119/8 GR+GD+BK|48
HT124/12 GR+GD+BK|65.5
HT126/12 GD+BK|56.7
HT129/12 GR+GD+BK|66.3
HT131/6 GR+GD+BK|40.2
HT131/8 GR+GD+BK|54.1
HT131/12 GR+GD+BK|69.8
HT132/12 GR+GD+BK|78.6
HT133/8 GD+BK|54.1
HT133/12 GD+BK|69.8
HT135/12 GD+BK|68.1
HT138/800*300 GD+BK|33.2
HT139/800+600+400 WH|52.4
HT144/PRJ GD|61.1
HT161/1 GD SD BK|22.3
HT174/19 3D|58.2
HT175/7|29.1
HT175/19|82.4
HT176/s1+b1 GD|8.3
HT176/s6 GD|21.8
HT176/b6 GD|24.4
HT176/5+1 GD|21.8
HT176/s9 GD|30.6
HT176/b9 GD|41.9
HT177/s1 GD|4.8
HT178/L5 GD|17.5
HT178/L10 GD|26.2
HT176/s1 CH|3.9
HT176/s2 CH|7.4
HT176/s1+b1 CH|8.3
HT176/s3 CH|11.3
HT176/3 CH|11.3
HT176/4 CH|14.8
HT176/s5 CH|17.5
HT176/s3+b3 CH|21.8
HT176/s6 CH|21.8
HT176/b6 CH|24.4
HT176/5+1 CH|21.8
HT176/s9 CH|30.6
HT176/b9 CH|41.9
HT177/s1 CH|4.8
HT177/s5 CH|19.2
HT178/s4 CH|13.1
HT178/5 CH|17.5
HT178/b4+s4 CH|30.6
HT178/L4+S4 CH|22.7
HT178/L5 CH|17.5
HT178/L10 CH|26.2
HT179/21L BK|69.8
HT179/33L BK|104.8
HT179/27D BK|78.6
HT179/39D BK|113.5
HT179/54D BK|174.6
HT180/16|113.5
HT181/16|174.6
HT182/16|139.7
HT183/16|122.2
HT184/16|139.7
HT185/16|157.1
HT187/40|384.1
HT189/21|148.4
HT192/12 GD+GR|67.2
HT192/8 GD+GR|53.3
HT193/8 GR|67.2
HT195/12 GR|87.3
HT195/8 GR|62.9
HT219/T3|17.5
HT221/13|61.1
HT213/3 GR+CH|25.3
HT223/1 CF|33.2
HT225/3 GR|21.8
HT232/400 GD|30.6
HT232/500 GD|38.4
HT232/600 GD|45.4
HT233/400 BK|30.6
HT233/500 BK|38.4
HT233/600 BK|45.4
HT234/400 BK|28.8
HT234/500 BK|36.7
HT234/600 BK|48
HT236/6 BK|55
HT236/8 BK|74.2
HT236/10 BK|87.3
HT240/600/3 BK|57.6
HT242/800 GD|72.5
HT242/800 BK|72.5
HT243/4 BK|61.1
HT245/ GD|57.6
HT246/ BK|30.6
HT246/ WH|30.6
HT247/ BK|26.2
HT247/ WH|26.2
HT248/ BK|25.3
HT248/ WH|25.3
HT249/3 BK|28.8
HT249/3 WH|28.8
HT250/ WH+GD|28.8
HT251/ WH+GD|34.9
HT251/ BK|34.9
HT252/ WH+GD|32.3
HT252/ BK|32.3
HT253/ WH|20.1
HT253/ BK|20.1
HT254/3 WH+CH|25.3
HT255/ BK|32.3
HT255/ WH|32.3
HT256/ BK|28.8
HT256/ WH|28.8
HT257/ WH|30.6
HT257/ BK|30.6
HT258/3 BK|16.6
HT258/3 WH|16.6
HT259/ BK+GD|26.2
HT259/ WH+GD|26.2
HT260/ WH|27.9
HT261/3 BK|25.3
HT261/3 WH|25.3
HT262/ WH|31.4
HT262/ BK|31.4
HT262/ CF|31.4
HT264/20 BK+GD|100.4
HT272/6 CF+GD|31.4
HT272/8 CF+GD|38.4
HT272/12 CF+GD|52.4
HT273/6 CR|28.8
HT273/8 CR|36.7
HT273/12 CR|49.8
HT274/6 BK|34
HT274/8 BK|42.8
HT274/12 BK|56.7
HT275/9 GD|31.4
HT275/12 GD|41
HT275/15 GD|52.4
HT276/6 CR|33.2
HT276/8 CR|41
HT276/12 CR|55
HT277/6 BK|22.7
HT277/8 BK|26.2
HT277/12 BK|36.7
HT278/8 BK+GD|28.8
HT278/16 BK+GD|48
HT279/8 BK+GD|27.9
HT279/12 BK+GD|38.4
HT279/16 BK+GD|48
HT280/6 CR|29.7
HT280/8 CR|37.5
HT280/12 CR|53.3
HT281/6 CR|43.7
HT281/12 CR|65.5
HT282/6 CR|33.2
HT282/8 CR|41
HT283/6 WH+GD|25.3
HT283/8 WH+GD|31.4
HT283/12 WH+GD|43.7
HT284/6 BK+GD|34
HT284/8 BK+GD|41.9
HT284/12 BK+GD|56.7
HT285/6 BK+GD|21.8
HT285/8 BK+GD|25.3
HT285/12 BK+GD|34.9
HT286/6 CR|27.1
HT286/8 CR|32.3
HT286/12 CR|41.9
HT287/24 BK|61.1
HT287/24 CH|61.1
HT288/20 BK|48
HT288/20 CH|48
HT287/4 BK|12.2
HT287/4+1 BK|14
HT287/3+3 WH|14
HT287/4 WH|12.2
HT287/4+1 WH|14
HT288/4 BK|13.1
HT288/4+1 BK|14.8
HT288/2+2 WH|11.3
HT288/3+3 WH|14.8
HT288/4 WH|13.1
HT288/4+1 WH|14.8
HT289/3+3 GD|21.8
HT289/4 GD|19.2
HT289/4+1 GD|22.7
HT289/2+2 CH|16.6
HT289/3+3 CH|21.8
HT289/4+4 CH|27.1
HT289/4 CH|19.2
HT289/4+1 CH|22.7
HT290/2+2 GD|17.5
HT290/3+3 GD|22.7
HT290/4 GD|20.1
HT290/4+1 GD|23.6
HT290/2+2 CH|17.5
HT290/3+3 CH|22.7
HT290/4 CH|20.1
HT290/4+1 CH|23.6
HT290/4+4 CH|27.9
HT297/3 WH+GR|18
HT296/3 WH+GD|18
HT299/3 GR+CH|18
HT298/3 WH+GD|18
HT295/3 WH+GD|18
HT291/3 WH|18
HT292/3 GR+CH|18
HT293/3 WH+GD|18
DM15/1 PINK|8.7
DM15/1 L.BLU|8.7
WHITE DM16/1 WH|4.8
OQ RANG DM41/ R3 WH M|6.7
DM42/ R3 BK|15.5
DM42/ R3 WH|15.5
DM43/ R1 BK|14.6
DM43/ R1 WH|14.6
DM46/ 1 BK|34
DM46/ 1 WH|34
DM49/ R3 WH|14.6
DM51/ 1 WH|8.7
DM51/ 1 BK|7.9
DM53/ 1 BK|5.8
DM53/ 1 WH|5.8
DM54/ 1 WH|8.7
DM54/ 1 GR|8.7
DM55/ R1 BK|14.6
DM62/ 1 BK|9.6
DM63/ R3 BK|11.6
DM66/ 1 BK|17.5
DM68/ 1 BK|14.6
DM68/ 1 WH|14.6
DM78/ 1 WH|6.7
DM78/ 1 BK|6.7
DM80/3 BK|19.2
DM81/3 BK|19.2
DM82/3 BK|19.2
DM83/3 BK|19.2
DM84/3 BK|19.2
DM85/5 BK|34.9
DM88/5 BK|38.4
DM90/3 BK|19.2
DM91/1 BK|14
DM93/5 BK|33.2
DM94/1 BK|10.5
DM95/3 BK|19.2
DM96/3 BK|23.6
DM96/5 BK|38.4
DM96/7 BK|52.4
DM97/5 BK|30.6
DM98/3 BK|21.8
DM99/1 BK|21
DM100/1 BK|7.9
DM101/1 BK|7.9
DM102/1 BK|9.6
DM104/3 BK|21.8
DM104/7 BK|48
DM105/1 BK|7.9
DM106/1 BK|13.1
DM108/1 BK|13.1
DM109/3 BK|21
DM110/3 BK|21
DM111/5 BK|38.4
DM112/3 BK|28.8
DM113/5 BK|34.9
DM113/7 BK|43.7
DM114/1 BK|14.8
DM116/1 BK|10.5
DM117/1 BK|10.5
DM118/1 BK|19.2
DM119/3 BK|19.2
DM120/3 BK|19.2
DM121/1 BK|14.8
DM122/1 BK|13.1
DM123/1 BK|11.3
DM124/3 BK|10
DM124/3 WH|10
DM125/3 BK|10
DM125/3 WH+GD|11
DM126/3 BK|10
DM127/3 BK|10
DM127/3 WH|10
DM128/3 BK|10
DM129/3 BK|10
DM129/3 WH|10
DM130/3 BK|11
DM130/3 WH+GD|12
DM131/3 BK|12
DM132/3 BK|12
DM132/3 WH+GD|12
DM133/3 BK|12
DM133/3 WH|12
DM134/3 BK|12
DM134/3 WH|12
DM135/3 BK|12
DM135/3 WH|12
CL00/D1000/16 FGD+CL|76.8
CL00/D1000/16 FGD+GC|76.8
CL00/D1000/16 CH+CL|76.8
CL00/D400/6 CH+SMK|19.2
CL00/D500/7 CH+SMK|27.1
CL00/D600/9 CH+SMK|38.4
CL00/D800/12 CH+SMK|53.3
CL00/D1000/16 CH+SMK|76.8
CL01/D800/12 FGD+CL|36.7
CL01/D500/7 FGD+GC|20.1
CL01/D600/9 FGD+GC|28.8
CL01/D800/12 FGD+GC|38.4
CL01/D600/9 CH+CL|27.9
CL01/D800/12 CH+CL|36.7
CL01/D400/6 CH+SMK|15.7
CL01/D500/7 CH+SMK|20.1
CL02/D400/6 FGD+CL|15.9
CL02/D500/7 FGD+CL|22.7
CL02/D600/9 FGD+CL|32.3
CL02/D400/6 CH+CL|15.9
CL02/D500/7 CH+CL|22.7
CL02/D600/9 CH+CL|32.3
CL02/D400/6 FGD+GC|15.9
CL02/D500/7 FGD+GC|22.7
CL02/D600/9 FGD+GC|32.3
CL02/D800/12 FGD+GC|44.5
CL02/D1000/16 FGD+GC|81.6
CL02/D1000/16 CH+SMK|72.5
CL02/1200*500/22 FGD CL|76.8
CL02/1200*500/22 FGD GC|76.8
CL02/D400/6 WH+CL|15.9
CL02/D500/7 WH+CL|22.7
CL02/D600/9 WH+CL|32.3
CL02/D1000/16 WH+CL|69.8
CL02/D400/6 WH+GC|15.9
CL02/D500/7 WH+GC|22.7
CL02/D600/9 WH+GC|32.3
CL02/D800/12 WH+GC|44.5
CL02/D1000/16 WH+GC|69.8
CL11/D400/6 FGD+GC|15.9
CL11/D500/7 FGD+GC|22.7
CL11/D600/9 FGD+GC|32.3
CL12/D500/7 CH+CL|22.7
CL12/D600/9 CH+CL|32.3
CL12/D800/12 CH+CL|44.5
CL12/D400/6 FGD+CL|15.9
CL12/D500/7 FGD+CL|22.7
CL12/D600/9 FGD+CL|32.3
CL12/D800/12 FGD+CL|44.5
CL12/D400/6 FGD+GC|15.9
CL12/D500/7 FGD+GC|22.7
CL12/D600/9 FGD+GC|32.3
CL12/D800/12 FGD+GC|44.5
CL02/D500/7 CH+BL|22.7
CL02/D600/9 CH+BL|32.3
CL02/D800/12 CH+BL|44.5
BRA CL05/1W SI+WH+CL|10.5
BRA CL05/1W TI+WT+GY|10.5
BRA CL05/2W TI+WT+GY|14
BRA CL05/1W S+YE+BL+CL|10.5
BRA CL05/2W S+YE+BL+CL|14
BRA CL06/1B GD+WH+XB|13.6
BRA CL06/1B SI+WH+CL|13.6
BRA CL06/2B SI+WH+CL|19.4
BRA CL06/1B TI+WT+GY|13.6
BRA CL06/1B S+YE+BL+CL|10.5
CL07/1000 GD+WH+CL|192.1
CL10/1000/15 GD|86.4
CL10/1000/15 CH|86.4
BT01/600*600 CH|36.8
BT01/600*600 FGD|36.8
BT02/600*600 CH|36.8
BT02/600*600 FGD|36.8
BT04/600 FGD|24.3
BT06/600 FGD|24.3
BT07/600 CH|24.3
BT07/600 FGD|24.3
BT10/600 CH|34.9
BT10/600 FGD|34.9
BT13/500*500|27.2
BT13/600*600|36.8
BT15/500*500|27.2
BT15/600*600|36.8
BT17/400|16
BT17/500*500|27.2
BT17/600*600|36.8
BT19/400|16
BT20/400|16
BT21/400|16
TA08/5 BK|21.8
TA08/3 BK|16.6
TA09/5 FGD|21.8
TA09/3 FGD|16.6
TA10/5 FGD|21.8
TA10/3 FGD|16.6
TA11/5 FGD|21.8
TA11/3 FGD|16.6
TA12/5 FGD|21.8
TA12/3 FGD|16.6
TA13/5 FGD|21.8
TA13/3 FGD|16.6
TA14/5 FGD|21.8
TA14/3 FGD|16.6
TA15/5 FGD|21.8
TA15/3 FGD|16.6
TA16/5 FGD|21.8
TA16/3 FGD|16.6
TA17/5 FGD|21.8
TA17/3 FGD|16.6
TA18/5 FGD|21.8
TA18/3 FGD|16.6"""

    conn = get_db()
    cur = conn.cursor()

    old_salid_sections = [
        "RANGLI ROZETKA VA KLYUCHATELLAR",
        "SALID LIGEHT — SG",
        "SALID LIGEHT — SN",
        "GALOGEN",
        "GALOGEN — SG",
        "GALOGEN — SN",
        "LYUSTRA",
    ]
    for section in old_salid_sections:
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("SALID", section))
        cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("SALID", section))
        cur.execute("DELETE FROM section_groups WHERE brand=? AND child_section=?", ("SALID", section))

    cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)", ("SALID",))

    def add_catalog(section, raw):
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", ("SALID", section))
        for line in raw.splitlines():
            line=line.strip()
            if not line or "|" not in line:
                continue
            product,price=line.rsplit("|",1)
            cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", ("SALID", section, product.strip(), float(price)))

    # SG va SN kodli galogenlar alohida bo‘limlarda chiqadi.
    # SS va boshqa kodlar umumiy GALOGEN bo‘limida qoladi.
    sg_lines = []
    sn_lines = []
    other_lines = []
    for _line in galogen_data.splitlines():
        _code = _line.split("|", 1)[0].strip().upper()
        if _code.startswith("SG"):
            sg_lines.append(_line)
        elif _code.startswith("SN"):
            sn_lines.append(_line)
        else:
            other_lines.append(_line)
    if sg_lines:
        add_catalog("GALOGEN — SG", "\n".join(sg_lines))
    if sn_lines:
        add_catalog("GALOGEN — SN", "\n".join(sn_lines))
    if other_lines:
        add_catalog("GALOGEN", "\n".join(other_lines))
    add_catalog("LYUSTRA", lyustra_data)
    conn.commit()
    conn.close()
    load_dynamic_products()


def show_salid_pdf_catalog_page(chat_id, section, page=0):
    items=PRODUCTS.get("SALID", {}).get(section, [])
    if not isinstance(items,list) or not items:
        send_message(chat_id,"ℹ️ Bu bo‘limda mahsulot yo‘q.")
        return
    per_page=20
    total_pages=(len(items)+per_page-1)//per_page
    try: page=int(page)
    except Exception: page=0
    page=max(0,min(page,total_pages-1))
    start=page*per_page; end=min(start+per_page,len(items))

    # Rasm admin tomonidan saqlangan bo‘lsa, katalogni ochganda ham ko‘rsatamiz.
    # Avvalgi kodda rasm saqlanardi, lekin SALID GALOGEN sahifasida yuborilmas edi.
    send_catalog_photo_if_exists(chat_id, "SALID", section)

    buttons=[]
    for index in range(start,end):
        product,price=items[index]
        buttons.append((product+" — $"+format(price),"salidpdf|SALID|"+section+"|"+str(index)))
    nav=[]
    if page>0: nav.append(("⬅️ Oldingi","salidpage|SALID|"+section+"|"+str(page-1)))
    if page<total_pages-1: nav.append(("Keyingi ➡️","salidpage|SALID|"+section+"|"+str(page+1)))
    buttons.extend(nav)
    buttons.append(("⬅️ SALID","brand|SALID"))
    send_message(chat_id,"📦 <b>SALID — "+section+"</b>\n📄 <b>"+str(start+1)+"–"+str(end)+"</b> / "+str(len(items))+"\n\nMahsulotni tanlang:",keyboard(buttons))


def seed_salid_rozetkalar_catalog():
    """SALID -> ROZETKALAR -> DELUXE / ULTRA / SMART HOME -> rang -> mahsulotlar."""
    salid = PRODUCTS.setdefault("SALID", {})

    # Eski rangli SALID bo'limini olib tashlaymiz.
    salid.pop("RANGLI ROZETKA VA KLYUCHATELLAR", None)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("SALID", "RANGLI ROZETKA VA KLYUCHATELLAR"))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("SALID", "RANGLI ROZETKA VA KLYUCHATELLAR"))
    conn.commit()
    conn.close()

    # ---------------- DELUXE ----------------
    # Deluxe model kodlari mijozga ko'rsatilmaydi; nomlar Premium katalogidagi
    # tushunarli nomlar bilan bir xil qilindi. Kod -> nom mosligi Premium
    # model oilalariga mos ravishda berildi.
    deluxe_names = [
        "VIKLYUCHATEL 1 TALI",
        "VIKLYUCHATEL O'TUVCHI 1 TALI",
        "VIKLYUCHATEL 2 TALI",
        "VIKLYUCHATEL O'TUVCHI 2 TALI",
        "VIKLYUCHATEL 3 TALI",
        "ZVANOK",
        "ROZETKA 1 TALI ZAZEMLENIYALI",
        "ROZETKA 1 TALI",
        "USB TYPE-C",
        "TELEFON",
        "INTERNET",
        "INTERNET 2 TALI",
        "TV",
        "ROZETKA 1 TALI ZAZEMLENIYALI QOPQOQLI",
        "ROZETKA 2 TALI",
        "ROZETKA 2 TALI ZAZEMLENIYALI",
        "RAMKA 2 TALI",
        "RAMKA 3 TALI",
        "RAMKA 4 TALI",
        "RAMKA 5 TALI",
    ]
    deluxe_prices = {
        "White":  [1.10,1.40,1.35,1.70,1.80,1.40,1.35,1.25,4.20,1.65,1.65,2.70,1.65,1.90,2.20,2.50,.80,1.25,1.80,2.20],
        "Gold":   [1.15,1.45,1.40,1.80,1.85,1.50,1.40,1.30,4.30,1.70,1.75,2.80,1.70,2.00,2.30,2.60,.85,1.30,1.85,2.30],
        "Grey":   [1.15,1.45,1.40,1.80,1.85,1.50,1.40,1.30,4.30,1.70,1.75,2.80,1.70,2.00,2.30,2.60,.85,1.30,1.85,2.30],
        "Black":  [1.15,1.45,1.40,1.80,1.85,1.50,1.40,1.30,4.30,1.70,1.75,2.80,1.70,2.00,2.30,2.60,.85,1.30,1.85,2.30],
        "Dark Grey":[1.15,1.45,1.40,1.80,1.85,1.50,1.40,1.30,4.30,1.70,1.75,2.80,1.70,2.00,2.30,2.60,.85,1.30,1.85,2.30],
    }
    deluxe = {}
    for color, prices in deluxe_prices.items():
        deluxe[color] = [(name + " " + color, price) for name, price in zip(deluxe_names, prices)]
    # Tashqi modellar PDFda faqat White ko'rinishida berilgan.
    # Katalogdagi qo'shimcha tashqi modellar alohida manba mahsulotlari
    # bo'lib qoladi; ularga taxminiy Premium nomi berilmaydi.
    deluxe["White"] += [
        ("SD31 White", .90), ("SD32 White", 1.10), ("SD33 White", .80),
        ("SD34 White", 1.40), ("SD35 White", 1.05), ("SD36 White", 1.70)
    ]

    # ---------------- ULTRA ----------------
    # Ultra ham Premiumdagi mijozga tushunarli mahsulot nomlaridan foydalanadi.
    ultra_names = [
        "VIKLYUCHATEL 1 TALI",
        "VIKLYUCHATEL 2 TALI",
        "VIKLYUCHATEL 3 TALI",
        "ZVANOK",
        "VIKLYUCHATEL O'TUVCHI 1 TALI",
        "VIKLYUCHATEL O'TUVCHI 2 TALI",
        "ROZETKA 1 TALI",
        "ROZETKA 1 TALI ZAZEMLENIYALI",
        "ROZETKA 2 TALI",
        "ROZETKA 2 TALI ZAZEMLENIYALI",
        "TV",
        "TELEFON",
        "INTERNET",
        "USB TYPE-C",
        "INTERNET 2 TALI",
        "RAMKA 2 TALI",
        "RAMKA 3 TALI",
        "RAMKA 4 TALI",
        "RAMKA 5 TALI",
        "ROZETKA 1 TALI ZAZEMLENIYALI QOPQOQLI",
    ]
    # PDFda ranglar: White, Gold, Grey, Black, Dark Grey.
    ultra_prices = {
        "White":   [1.15,1.25,1.65,1.30,1.30,1.60,1.30,1.20,1.80,2.20,1.60,1.60,1.60,.80,2.65,.70,1.30,1.60,2.00,1.50],
        "Gold":    [1.15,1.40,1.85,1.50,1.65,1.60,1.30,1.40,2.30,2.60,1.70,1.70,1.75,.80,2.80,.85,1.30,1.85,2.30,2.00],
        "Grey":    [1.15,1.40,1.85,1.50,1.45,1.80,1.30,1.40,2.30,2.60,1.70,1.70,1.75,.81,2.80,.85,1.30,1.85,2.30,2.00],
        "Black":   [1.15,1.40,1.85,1.50,1.45,1.80,1.30,1.40,2.30,2.60,1.70,1.70,1.75,.81,2.80,.85,1.43,2.00,2.00,2.00],
        "Dark Grey":[1.15,1.40,1.85,1.50,1.45,1.80,1.30,1.40,2.30,2.60,1.70,1.85,1.75,.81,2.80,.85,1.30,1.85,2.30,2.00],
    }
    ultra = {c:[(n+" "+c,p) for n,p in zip(ultra_names,prices)] for c,prices in ultra_prices.items()}

    # VERTIKAL RAMKA: 2-5 talik. Alohida narx katalogda berilmaganligi uchun
    # tegishli oddiy RAMKA narxi ishlatiladi; mavjud manba narxlari saqlanadi.
    deluxe_frame_idx = {"2 TALI": 16, "3 TALI": 17, "4 TALI": 18, "5 TALI": 19}
    ultra_frame_idx = {"2 TALI": 15, "3 TALI": 16, "4 TALI": 17, "5 TALI": 18}
    for color, items in deluxe.items():
        frame_prices = {name: items[idx][1] for name, idx in deluxe_frame_idx.items()}
        items.extend([(f"VERTIKAL RAMKA {name}", price) for name, price in frame_prices.items()])
    for color, items in ultra.items():
        frame_prices = {name: items[idx][1] for name, idx in ultra_frame_idx.items()}
        items.extend([(f"VERTIKAL RAMKA {name}", price) for name, price in frame_prices.items()])

    # ---------------- SMART HOME ----------------
    # Katalogdagi asosiy Smart Home rozetka/klyuch va ramka modellar.
    smart_base = [
        ("SH07-1",6.0),("SH07-2",7.0),("SH07-3",9.0),("SH07-4",11.0),
        ("SH07-1 RV",11.0),("SH07-2 RV",13.0),("SH07-1D",13.0),("SH07-1ZV",12.0),
        ("SH07-1 WF",11.0),("SH07-2 WF",12.0),("SH07-3 WF",14.0),("SH07-4 WF",16.0),
        ("SH06 EL",25.0),("SH06 WAT",25.0),
        ("SH05",1.50),("SH05 WF",15.0),("SH05 WF-PM",16.0),("SH05 IP",2.0),
        ("SH05 USB",8.0),("SH05-2",3.0),("SH05 UN",1.50),("SH05 WF-UN",15.0),
        ("SH05 TEL 1/2",1.0),("SH05 INT 1/2",1.0),("SH05 TV 1/2",1.0),("SH05 1/2",1.0),
        ("SH01 1/2",1.0),("SH01 MW",1.5),("SH01",1.0),("SH01 REV",1.0),
        ("SH02",1.5),("SH02 REV",1.5),("SH03",2.0),("SH01 ZV",1.5),
        ("SH11 1W",2.5),("SH12 BS",7.0),
        ("SH09-1+1",6.0),("SH09-2+1",6.0),("SH09-2+2",6.0),("SH09-2+3",6.0),("SH09-2x3",9.0),
        ("SH08-1R",4.0),("SH08-2R",5.0),("SH08-3R",7.5),("SH08-4R",10.0),("SH08-5R",12.5),
        ("SH09-1+1R",5.5),("SH09-2+1R",5.5),("SH09-3+1R",5.5),
        ("SH09-1+2R",8.0),("SH09-2+2R",8.0),("SH09-3+2R",8.0),
        ("SH09-1+2+2R",8.5),("SH09-2+2+2R",8.5),
    ]
    smart = {}
    for color in ("White", "Black", "Golden", "Gray"):
        smart[color] = [(name + " " + color, price) for name, price in smart_base]

    salid["ROZETKALAR"] = {
        "SALID DELUXE": deluxe,
        "SALID ULTRA": ultra,
        "SALID SMART HOME": smart,
    }

def seed_rich_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)", ("DUSEL",))
    cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand, section) VALUES(?,?)", ("DUSEL", "Rich"))
    rich_products = [
        ('Rich vkl 1tali', 0.8),
        ('Rich vkl 2tali', 0.9),
        ('Rich vkl 3tali', 1.2),
        ('Rich vkl 1tali indikator', 1.0),
        ('Rich vkl 2tali indikator', 1.1),
        ('Rich zvanok', 1.0),
        ('Rich vkl 1tali revers', 1.0),
        ('Rich vkl 2tali revers', 1.3),
        ('Rich rozetka 1tali', 0.8),
        ('Rich rozetka 2tali', 1.1),
        ('Rich rozetka zazem 1tali', 0.95),
        ('Rich rozetka zazem 2tali', 1.3),
        ('Rich rozetka USB', 4.0),
        ('Rich TV', 1.2),
        ('Rich TEL', 1.2),
        ('Rich INTERNET', 1.5),
        ('Rich INTERNET + TEL', 2.5),
        ('Rich TV + Internet', 2.4),
        ('Rich INTERNET + INTERNET', 2.4),
        ('Rich TEL + TEL', 2.0),
        ('Rich USB', 2.7),
        ('Rich USB2', 3.5),
        ('Rich Permutator', 1.7),
    ]
    for product, price in rich_products:
        cur.execute("""INSERT OR IGNORE INTO dynamic_products
                       (brand, section, product, price) VALUES (?,?,?,?)""",
                    ("DUSEL", "Rich", product, price))
    conn.commit()
    conn.close()
    load_dynamic_products()

def save_dynamic_product(brand, section, product, price):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_products(brand, section, product, price) VALUES(?,?,?,?)", (brand, section, product, float(price)))
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def show_admin_images(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    buttons = [("🖼 " + brand, "imgbrand|" + brand) for brand in PRODUCTS if PRODUCTS.get(brand)]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "🖼 <b>KATALOG RASMLARI</b>\n\nRasm qo‘shiladigan brendni tanlang:", keyboard(buttons))


def show_admin_image_sections(chat_id, brand):
    if not is_admin(chat_id):
        return
    sections = PRODUCTS.get(brand, {})
    buttons = []
    for section in sections:
        buttons.append(("📂 " + str(section), "imgsec|" + brand + "|" + str(section)))
    buttons.append(("⬅️ Brendlar", "admin_images"))
    send_message(chat_id, "🖼 <b>" + html.escape(brand) + " — RASM JOYLASH</b>\n\nBo‘limni tanlang:", keyboard(buttons))


def start_image_upload(chat_id, brand, section, color=None, slot=1, model=None):
    key = image_key(brand, section, color, model)
    set_state(chat_id, "admin_image", {
        "key": key, "brand": brand, "section": section, "color": color or "",
        "model": model or "", "slot": int(slot)
    })
    target = section
    if model:
        target += " → " + model
    if color:
        target += " → " + color
    send_message(chat_id, "📸 <b>Rasm " + str(slot) + "/3</b>\n\n" + html.escape(target) + " uchun rasm yuboring.\n\nBekor qilish: /cancel")


def _dict_is_model_color_tree(value):
    return isinstance(value, dict) and any(isinstance(v, dict) for v in value.values())


def show_admin_image_models(chat_id, brand, section):
    models = PRODUCTS.get(brand, {}).get(section, {})
    buttons=[]
    for model, colors in models.items():
        buttons.append(("📦 " + str(model), "imgmodel|" + brand + "|" + section + "|" + str(model)))
    buttons.append(("⬅️ Bo‘limlar", "imgbrand|" + brand))
    send_message(chat_id, "📦 <b>" + html.escape(section) + "</b>\n\nModelni tanlang:", keyboard(buttons))


def show_admin_image_colors(chat_id, brand, section, model=None):
    data = PRODUCTS.get(brand, {}).get(section, {})
    colors = data.get(model, {}) if model else data
    if not isinstance(colors, dict):
        return show_admin_image_actions(chat_id, brand, section)
    buttons=[]
    for color in colors:
        exists = "✅" if get_catalog_images_for(brand, section, color, model) else "➕"
        cb = "imgcolor|" + brand + "|" + section + "|" + str(color)
        if model:
            cb = "imgcolor|" + brand + "|" + section + "|" + str(model) + "|" + str(color)
        buttons.append((exists + " " + str(color), cb))
    back = "imgmodel|" + brand + "|" + section + "|" + model if model else "imgsec|" + brand + "|" + section
    buttons.append(("⬅️ Orqaga", back))
    send_message(chat_id, "🎨 <b>Rangni tanlang</b>", keyboard(buttons))


def show_admin_image_actions(chat_id, brand, section):
    value = PRODUCTS.get(brand, {}).get(section)
    if isinstance(value, dict):
        if _dict_is_model_color_tree(value):
            show_admin_image_models(chat_id, brand, section)
        else:
            show_admin_image_colors(chat_id, brand, section)
        return
    key = image_key(brand, section)
    imgs = get_catalog_images_for(brand, section)
    buttons=[]
    for slot in range(1, 4):
        mark = "✅" if get_catalog_image(key, slot) else "➕"
        buttons.append((mark + " Rasm " + str(slot), "imgupload|" + brand + "|" + section + "|" + str(slot)))
    buttons.append(("⬅️ Bo‘limlar", "imgbrand|" + brand))
    send_message(chat_id, "🖼 <b>" + html.escape(brand) + " — " + html.escape(section) + "</b>\n\n📸 3 tagacha rasm. Hozirgi: <b>" + str(len(imgs)) + "/3</b>", keyboard(buttons))

def send_document(chat_id, file_path, caption=""):
    boundary = "----DuselBoundary7MA4YWxkTrZu0gW"
    with open(file_path, "rb") as f:
        file_data = f.read()
    fn = os.path.basename(file_path)
    parts = []
    parts.append(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n"+str(chat_id)+"\r\n").encode())
    parts.append(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"caption\"\r\n\r\n"+caption+"\r\n").encode("utf-8"))
    parts.append(("--"+boundary+"\r\nContent-Disposition: form-data; name=\"document\"; filename=\""+fn+"\"\r\nContent-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\r\n\r\n").encode())
    parts.append(file_data)
    parts.append(("\r\n--"+boundary+"--\r\n").encode())
    body=b"".join(parts)
    req=urllib.request.Request(API_URL+"sendDocument",data=body,method="POST",headers={"Content-Type":"multipart/form-data; boundary="+boundary})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print("DOCUMENT XATOSI:",e)
        return None


def send_message(chat_id, text, keyboard=None):
    data = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true"
    }

    if keyboard:
        data["reply_markup"] = json.dumps(
            keyboard,
            ensure_ascii=False
        )

    return api("sendMessage", data)


def send_reply_message(chat_id, text, reply_keyboard):
    data = {
        "chat_id": str(chat_id),
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(reply_keyboard, ensure_ascii=False)
    }
    return api("sendMessage", data)


def answer_callback(callback_id):
    return api("answerCallbackQuery", {
        "callback_query_id": callback_id
    })


# ============================================================
# KEYBOARD
# ============================================================

def keyboard(buttons, columns=1):
    rows = []

    for i in range(0, len(buttons), columns):
        row = []

        for text, callback in buttons[i:i + columns]:
            row.append({
                "text": text,
                "callback_data": callback
            })

        rows.append(row)

    return {"inline_keyboard": rows}


def main_menu():
    rows = [
        [{"text": "🛍 Mahsulotlar", "callback_data": "brands"}, {"text": "🔎 Qidirish", "callback_data": "search"}],
        [{"text": "🛒 Savat", "callback_data": "cart"}],
    ]
    if WEBAPP_URL:
        rows.append([{"text": "🌐 DO‘KON SAYTINI OCHISH", "web_app": {"url": WEBAPP_URL}}])
    rows += [
        [{"text": "⚙️ Sozlamalar", "callback_data": "settings"}],
        [{"text": "📍 12-DOKON lokatsiyasi", "callback_data": "location"}],
        [{"text": "📩 Takliflar", "callback_data": "suggestion"}],
    ]
    return {"inline_keyboard": rows}


def search_prompt(chat_id):
    clear_state(chat_id)
    set_state(chat_id, "search")
    send_message(
        chat_id,
        "🔎 <b>MAHSULOT QIDIRISH</b>\n\n"
        "Mahsulot nomi yoki kodini yozing.\n"
        "Masalan: <code>SG29</code>, <code>DU-1205</code>, <code>USB</code>"
    )


def _search_normalize(value):
    """Qidiruv uchun yozuvni bir xil ko‘rinishga keltiradi.
    Masalan: 'DU 1205', 'DU-1205' va 'DU1205' -> 'du1205'.
    """
    value = str(value or "").casefold()
    return "".join(ch for ch in value if ch.isalnum())


def _search_match(query, *parts):
    """Aniq, lekin qisqa qidiruv.
    To‘liq yozish shart emas: foydalanuvchi yozgan qism mahsulot/kod ichida
    ketma-ket uchrasa natija chiqadi. Fuzzy/typo qidiruv yo‘q.
    Masalan: SH07 -> SH07-1, SH07-2; SG2 -> SG29.
    Lekin SG28 -> SG29 chiqmaydi.
    """
    q = _search_normalize(query)
    if not q:
        return False
    for part in parts:
        field = _search_normalize(part)
        if q and q in field:
            return True
    return False


def search_products(chat_id, query):
    """Mahsulotni aniq substring bo‘yicha qidiradi.
    Bir xil nom + bir xil narx faqat bir marta chiqadi.
    Bir xil nomning narxi har xil bo‘lsa, ikkala natija ham saqlanadi.
    """
    q = (query or "").strip()
    nq = _search_normalize(q)
    if not nq:
        search_prompt(chat_id)
        return

    results = []

    def add_result(brand, section, color, index, product, price, model=None):
        if _search_match(q, product, model or "", color or "", section, brand):
            results.append((brand, section, color, index, product, float(price), model))

    # Statik katalogni qidirish.
    for brand, sections in PRODUCTS.items():
        for section, items in sections.items():
            if isinstance(items, dict):
                nested_is_model = any(isinstance(v, dict) for v in items.values())
                if nested_is_model:
                    for model, model_items in items.items():
                        if not isinstance(model_items, dict):
                            continue
                        for color, color_items in model_items.items():
                            for index, item in enumerate(color_items):
                                if isinstance(item, (list, tuple)) and len(item) >= 2:
                                    add_result(brand, section, color, index, item[0], item[1], model)
                else:
                    for color, color_items in items.items():
                        for index, item in enumerate(color_items):
                            if isinstance(item, (list, tuple)) and len(item) >= 2:
                                add_result(brand, section, color, index, item[0], item[1])
            else:
                for index, item in enumerate(items):
                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                        add_result(brand, section, None, index, item[0], item[1])

    # Dinamik katalogni ham qidiramiz.
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT brand,section,product,price FROM dynamic_products ORDER BY id ASC")
        for brand, section, product, price in cur.fetchall():
            if _search_match(q, product, section, brand):
                results.append((brand, section, None, None, product, float(price), None))
        conn.close()
    except Exception:
        pass

    # MUHIM: bir xil nom + bir xil narx takrorlanmasin.
    # Bo‘lim/rang/modelni keyga qo‘shmaymiz — aynan screenshotdagi kabi
    # bitta katalog bir necha joydan kelib qolsa ham faqat 1 ta chiqadi.
    unique = []
    seen_keys = set()
    for row in results:
        product = row[4]
        price = round(float(row[5]), 6)
        key = (_search_normalize(product), price)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(row)

    if not unique:
        send_message(
            chat_id,
            "❌ <b>Hech narsa topilmadi.</b>\n\n"
            "Mahsulot nomi yoki kodining bir qismini yozib ko‘ring.",
            main_menu()
        )
        return

    SEARCH_CACHE[chat_id] = unique
    buttons = []
    for i, row in enumerate(unique):
        brand, section, color, index, product, price, model = row
        label = "📦 " + str(product)
        if color:
            label += " — " + str(color)
        label += " — $" + format(float(price))
        buttons.append((label, "sr|" + str(i)))

    buttons.append(("🔎 Yangi qidiruv", "search"))
    buttons.append(("⬅️ Asosiy menyu", "back_menu"))
    send_message(
        chat_id,
        "🔎 <b>Qidiruv natijalari</b>\n\n"
        "So‘rov: <code>" + html.escape(q) + "</code>\n"
        "Topildi: <b>" + str(len(unique)) + " ta mahsulot</b>\n\n"
        "📦 <b>Mahsulotni tanlang:</b>",
        keyboard(buttons)
    )

def settings_menu():
    return keyboard([
        ("✏️ Ismni o‘zgartirish", "change_name"),
        ("📱 Telefonni o‘zgartirish", "change_phone"),
        ("⬅️ Orqaga", "back_menu")
    ])


# ============================================================
# CLIENT
# ============================================================

def get_client(chat_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT name, phone FROM clients WHERE chat_id=?",
        (chat_id,)
    )

    row = cur.fetchone()
    conn.close()
    return row


def get_discount_percent(chat_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT discount_percent FROM clients WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    conn.close()
    try:
        return int(row[0]) if row else 0
    except Exception:
        return 0


def set_discount(chat_id, percent):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE clients SET discount_percent=? WHERE chat_id=?", (percent, chat_id))
    conn.commit()
    conn.close()


def show_settings(chat_id):
    client = get_client(chat_id)
    if not client:
        send_message(chat_id, "❌ Avval ro‘yxatdan o‘ting.")
        return
    name, phone = client
    discount = get_discount_percent(chat_id)
    discount_text = "🎁 Chegirma: <b>5%</b>" if discount == 5 else "🎁 Chegirma: <b>yo‘q</b>"
    send_message(chat_id, "⚙️ <b>SOZLAMALAR</b>\n\n👤 Ism: <b>" + name + "</b>\n📞 Telefon: <b>" + phone + "</b>\n" + discount_text, settings_menu())


def get_discount_clients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT chat_id, name, phone, discount_percent FROM clients ORDER BY rowid DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def discount_client_keyboard(chat_id, current):
    buttons = []
    if current == 5:
        buttons.append(("❌ 5% chegirmani olib tashlash", "disc|0|" + str(chat_id)))
    else:
        buttons.append(("🎁 5% chegirma berish", "disc|5|" + str(chat_id)))
    return keyboard(buttons)


def show_admin_discounts(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    rows = get_discount_clients()
    if not rows:
        send_message(chat_id, "👥 Hozircha mijozlar yo‘q.", admin_reply_keyboard())
        return
    send_message(chat_id, "🎁 <b>5% CHEGIRMA BOSHQARUVI</b>\n\nHar bir mijoz uchun kerakli tugmani bosing.", admin_reply_keyboard())
    for cid, name, phone, discount in rows:
        status = "✅ 5% berilgan" if discount == 5 else "❌ Chegirma yo‘q"
        send_message(chat_id, f"👤 <b>{name}</b>\n📞 {phone}\n🆔 <code>{cid}</code>\n🎁 {status}", discount_client_keyboard(cid, discount))


def save_client(chat_id, name, phone):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO clients(chat_id, name, phone, discount_percent)
        VALUES (?, ?, ?, 0)
        ON CONFLICT(chat_id)
        DO UPDATE SET name=excluded.name, phone=excluded.phone
    """, (chat_id, name, phone))

    conn.commit()
    conn.close()



# ============================================================
# ADMIN — KUNLIK SPISKALAR / KLIENT TARIXI / XABARLAR
# ============================================================

def get_order_days(limit=60):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT COALESCE(order_day, substr(created_at,1,10)) FROM orders WHERE created_at IS NOT NULL ORDER BY 1 DESC LIMIT ?", (limit,))
    rows = [r[0] for r in cur.fetchall() if r[0]]
    conn.close()
    return rows

def show_admin_lists(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    days = get_order_days()
    buttons = []
    for day in days:
        buttons.append(("📅 " + day, "day|" + day))
    buttons.append(("👥 Klient bo‘yicha spiskalar", "admin_clients"))
    buttons.append(("⬅️ Admin panel", "admin_home"))
    if not days:
        send_reply_message(chat_id, "📋 <b>SPISKALAR</b>\n\nHozircha saqlangan buyurtma yo‘q.", admin_reply_keyboard())
    else:
        send_message(chat_id, "📋 <b>KUNLIK SPISKALAR</b>\n\nKun bo‘yicha alohida saqlangan buyurtmalar:", keyboard(buttons))

def show_daily_orders(chat_id, day):
    if not is_admin(chat_id):
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id,name,phone,items,total,created_at FROM orders WHERE COALESCE(order_day,substr(created_at,1,10))=? ORDER BY id ASC", (day,))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        send_message(chat_id, "📅 " + day + " uchun spiska topilmadi.", keyboard([("⬅️ Kunlar", "admin_lists")]))
        return
    text = "📋 <b>SPISKA — " + day + "</b>\n\n"
    for oid, name, phone, items, total, created_at in rows:
        text += f"🧾 <b>#{oid}</b>  🕐 {created_at or ''}\n👤 <b>{name}</b>\n📞 {phone}\n"
        # Buyurtmadagi qisqa mahsulotlar
        for block in [b for b in (items or '').split('\n\n') if b.strip()]:
            pm = re.search(r"\. <b>(.*?)</b>", block)
            qm = re.search(r"Miqdor: (\d+) dona", block)
            if pm:
                text += "   • " + html.unescape(pm.group(1)) + " × " + (qm.group(1) if qm else "?") + "\n"
        text += "💰 <b>$" + format(float(total or 0)) + "</b>\n\n"
    send_message(chat_id, text[:4000], keyboard([("⬅️ Kunlar", "admin_lists"), ("📊 Excel", "admin_excel")]))

def show_client_orders(chat_id, target_id):
    if not is_admin(chat_id):
        return
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name,phone FROM clients WHERE chat_id=?", (target_id,))
    client = cur.fetchone()
    cur.execute("SELECT id,total,created_at,items FROM orders WHERE chat_id=? ORDER BY id DESC", (target_id,))
    rows = cur.fetchall()
    conn.close()
    if not client:
        send_message(chat_id, "❌ Klient topilmadi.")
        return
    name, phone = client
    text = f"📋 <b>{name} — barcha spiskalar</b>\n📞 {phone}\n🆔 <code>{target_id}</code>\n\n"
    if not rows:
        text += "Hozircha bu klientning buyurtmasi yo‘q."
    else:
        for oid,total,created_at,items in rows:
            text += f"🧾 <b>#{oid}</b> — {created_at or ''} — <b>${format(float(total or 0))}</b>\n"
            for block in [b for b in (items or '').split('\n\n') if b.strip()]:
                pm = re.search(r"\. <b>(.*?)</b>", block)
                qm = re.search(r"Miqdor: (\d+) dona", block)
                if pm:
                    text += "   • " + html.unescape(pm.group(1)) + " × " + (qm.group(1) if qm else "?") + "\n"
            text += "\n"
    send_message(chat_id, text[:4000], keyboard([("📢 Shu klientga xabar", "msgclient|"+str(target_id)), ("⬅️ Klientlar", "admin_clients")]))

def show_admin_broadcast(chat_id):
    if not is_admin(chat_id):
        return
    send_message(chat_id, "📢 <b>XABAR YUBORISH</b>\n\nKimga yuborishni tanlang:", keyboard([
        ("📢 Barcha klientlarga", "msgall"),
        ("👤 Bitta klientga", "msgpick"),
        ("⬅️ Admin panel", "admin_home")
    ]))

def start_broadcast(chat_id, target_id=None):
    if not is_admin(chat_id):
        return
    if target_id is None:
        set_state(chat_id, "admin_broadcast_all")
        target_text = "barcha klientlarga"
    else:
        set_state(chat_id, "admin_broadcast_one", {"target_id": int(target_id)})
        target_text = "tanlangan klientga"
    send_message(chat_id, "✍️ <b>" + target_text + " xabarni yuboring.</b>\n\n📝 Matn, 🖼 rasm yoki 📎 fayl yuborish mumkin.\n\nBekor qilish: /cancel")

def send_broadcast_all(text):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM clients")
    ids = [r[0] for r in cur.fetchall()]
    conn.close()
    ok = 0
    for cid in ids:
        result = send_message(cid, "📢 <b>YANGILIK</b>\n\n" + text, user_reply_keyboard())
        if result and result.get("ok"):
            ok += 1
        time.sleep(0.05)
    return ok, len(ids)


# ============================================================
# ADMIN — MIJOZLAR VA BUYURTMALAR
# ============================================================

def _xlsx_col(n):
    out = ""
    while n:
        n, r = divmod(n-1, 26)
        out = chr(65+r) + out
    return out


def _xlsx_xml_text(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _xlsx_cell(ref, value, style=0):
    style_attr = ' s="%d"' % style if style else ''
    if isinstance(value, bool):
        return '<c r="%s" t="b"%s><v>%d</v></c>' % (ref, style_attr, 1 if value else 0)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return '<c r="%s"%s><v>%s</v></c>' % (ref, style_attr, value)
    return '<c r="%s" t="inlineStr"%s><is><t>%s</t></is></c>' % (ref, style_attr, _xlsx_xml_text(value))


def _xlsx_sheet_xml(rows, widths=None, freeze_row=1, autofilter=True):
    widths = widths or []
    xmlrows = []
    for ri, row in enumerate(rows, 1):
        cells = []
        for ci, value in enumerate(row, 1):
            cells.append(_xlsx_cell(_xlsx_col(ci) + str(ri), value, 1 if ri == 1 else 0))
        xmlrows.append('<row r="%d">%s</row>' % (ri, ''.join(cells)))
    cols = ''
    if widths:
        cols = '<cols>' + ''.join('<col min="%d" max="%d" width="%s" customWidth="1"/>' % (i, i, w) for i, w in enumerate(widths, 1)) + '</cols>'
    pane = '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/><selection pane="bottomLeft" activeCell="A2" sqref="A2"/></sheetView></sheetViews>'
    af = ''
    if autofilter and rows:
        af = '<autoFilter ref="A1:%s%d"/>' % (_xlsx_col(max(len(r) for r in rows)), len(rows))
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' + pane + cols + '<sheetData>' + ''.join(xmlrows) + '</sheetData>' + af + '</worksheet>'


def create_orders_excel():
    # Mukammal Excel: buyurtmalar va barcha kataloglar.
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id,name,phone,items,total,created_at FROM orders ORDER BY id ASC")
    orders = cur.fetchall()

    order_rows = [["Buyurtma №", "Sana", "Klient nomi", "Telefon raqami", "Brend", "Bo‘lim", "Mahsulot", "Miqdori", "Narxi ($)", "Mahsulot jami ($)", "Chegirma (%)", "Chegirma ($)", "Buyurtma jami ($)"]]
    for oid, name, phone, items, total, created_at in orders:
        blocks = [b for b in (items or "").split("\n\n") if b.strip()]
        product_total = 0.0
        parsed = []
        for block in blocks:
            pm = re.search(r"\. <b>(.*?)</b>", block)
            bm = re.search(r"Brend: (.*)", block)
            sm = re.search(r"Bo‘lim: (.*)", block)
            qm = re.search(r"Miqdor: (\d+) dona", block)
            prm = re.search(r"Narx: \\$([0-9.]+)", block)
            tm = re.search(r"Jami: \\$([0-9.]+)", block)
            if pm:
                qty = int(qm.group(1)) if qm else 0
                price = float(prm.group(1)) if prm else 0.0
                subtotal = float(tm.group(1)) if tm else price * qty
                product_total += subtotal
                parsed.append((html.unescape(pm.group(1)), bm.group(1).strip() if bm else "", sm.group(1).strip() if sm else "", qty, price, subtotal))
        final_total = float(total or 0)
        discount_amount = max(product_total - final_total, 0.0)
        discount_percent = round((discount_amount / product_total) * 100, 2) if product_total else 0
        for product, brand, section, qty, price, subtotal in parsed:
            order_rows.append([oid, created_at or "", name, phone, brand, section, product, qty, price, subtotal, discount_percent, discount_amount, final_total])

    catalog_rows = {}
    for brand in ("DUSEL", "VERAL", "SALID"):
        rows = [["№", "Bo‘lim", "Mahsulot", "Narxi ($)"]]
        n = 1
        for section, products in PRODUCTS.get(brand, {}).items():
            if isinstance(products, dict):
                for color, color_products in products.items():
                    for product, price in color_products:
                        rows.append([n, section + " / " + color, product, price])
                        n += 1
            else:
                for product, price in products:
                    rows.append([n, section, product, price])
                    n += 1
        catalog_rows[brand] = rows
    conn.close()

    path = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
              '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="D9EAF7"/><bgColor indexed="64"/></patternFill></fill></fills>'
              '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/><xf numFmtId="0" fontId="1" fillId="1" borderId="0" applyFont="1" applyFill="1"/></cellXfs>'
              '</styleSheet>')
    names = ["ZAKAZLAR", "DUSEL", "VERAL", "SALID"]
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
                ''.join('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (name, i, i) for i, name in enumerate(names, 1)) +
                '</sheets></workbook>')
    workbook = workbook.replace('<brk>', '')
    workbook_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
                     ''.join('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, i) for i in range(1,5)) +
                     '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
    workbook_rels = workbook_rels.replace('<brk>', '')
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    root_rels = root_rels.replace('<brk>', '')
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>' +
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
        ''.join('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i for i in range(1,5)) +
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>')
    content_types = content_types.replace('<brk>', '')
    sheets = [_xlsx_sheet_xml(order_rows, [13,20,22,18,12,28,34,10,12,18,14,14,18]), _xlsx_sheet_xml(catalog_rows["DUSEL"], [8,30,36,12]), _xlsx_sheet_xml(catalog_rows["VERAL"], [8,34,42,12]), _xlsx_sheet_xml(catalog_rows["SALID"], [8,30,36,12])]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        z.writestr("xl/styles.xml", styles)
        for i, sheet_xml in enumerate(sheets, 1):
            z.writestr("xl/worksheets/sheet%d.xml" % i, sheet_xml)
    return path


def show_admin_excel(chat_id):
    if not is_admin(chat_id): return send_message(chat_id,"❌ Sizda admin huquqi yo‘q.")
    path=create_orders_excel(); result=send_document(ADMIN_ID,path,"📊 DUSEL 12-DOKON buyurtmalar spiskasi")
    try: os.remove(path)
    except Exception: pass
    send_reply_message(chat_id,"✅ Excel tayyor va yuborildi." if result and result.get("ok") else "❌ Excel yuborishda xatolik.",admin_reply_keyboard())


def admin_menu():
    return keyboard([
        ("👥 Mijozlar", "admin_clients"),
        ("📦 Buyurtmalar", "admin_orders"),
        ("📊 Excel", "admin_excel")
    ])


def get_clients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT chat_id, name, phone
        FROM clients
        ORDER BY rowid DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def show_admin_clients(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    rows = get_clients()
    if not rows:
        send_reply_message(chat_id, "👥 <b>Mijozlar</b>\n\nHozircha ro‘yxatdan o‘tgan mijoz yo‘q.", admin_reply_keyboard())
        return
    send_message(chat_id, "👥 <b>MIJOZLAR</b>\n\nHar bir klientning barcha spiskasini ko‘rish yoki unga alohida xabar yuborish mumkin.", admin_reply_keyboard())
    for i, (cid,name,phone) in enumerate(rows,1):
        send_message(chat_id, f"<b>{i}. {name}</b>\n📞 {phone}\n🆔 <code>{cid}</code>", keyboard([
            ("📋 Spiskalari", "clientorders|"+str(cid)),
            ("📢 Xabar", "msgclient|"+str(cid))
        ]))


def show_admin_orders(chat_id):
    if not is_admin(chat_id):
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, phone, total, created_at
        FROM orders
        ORDER BY rowid DESC
        LIMIT 30
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        send_message(chat_id, "📦 Hozircha buyurtmalar yo‘q.", admin_menu())
        return

    text = "📦 <b>SO‘NGGI BUYURTMALAR</b>\n\n"
    for row in rows:
        oid, name, phone, total, created_at = row
        text += (
            f"🧾 <b>#{oid}</b>\n"
            f"👤 {name}\n"
            f"📞 {phone}\n"
            f"💰 ${float(total):.2f}\n"
            f"🕐 {created_at}\n\n"
        )

    send_message(chat_id, text[:4000], admin_menu())


# ============================================================
# STATE
# ============================================================

def set_state(chat_id, step, data=None):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO states(chat_id, step, data)
        VALUES (?, ?, ?)
        ON CONFLICT(chat_id)
        DO UPDATE SET step=excluded.step, data=excluded.data
    """, (
        chat_id,
        step,
        json.dumps(data or {}, ensure_ascii=False)
    ))

    conn.commit()
    conn.close()


def get_state(chat_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT step, data FROM states WHERE chat_id=?",
        (chat_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return None, {}

    try:
        data = json.loads(row[1] or "{}")
    except Exception:
        data = {}

    return row[0], data


def clear_state(chat_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM states WHERE chat_id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


# ============================================================
# CART
# ============================================================

def add_to_cart(chat_id, brand, section, product, price, qty):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT rowid, qty
        FROM cart
        WHERE chat_id=?
          AND brand=?
          AND section=?
          AND product=?
    """, (chat_id, brand, section, product))

    row = cur.fetchone()

    if row:
        cur.execute(
            "UPDATE cart SET qty=? WHERE rowid=?",
            (row[1] + qty, row[0])
        )
    else:
        cur.execute("""
            INSERT INTO cart(
                chat_id, brand, section, product, price, qty
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            chat_id, brand, section, product, price, qty
        ))

    conn.commit()
    conn.close()


def get_cart(chat_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT rowid, brand, section, product, price, qty
        FROM cart
        WHERE chat_id=?
        ORDER BY rowid
    """, (chat_id,))

    rows = cur.fetchall()
    conn.close()
    return rows


def clear_cart(chat_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM cart WHERE chat_id=?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


# DUSEL bo‘limlarining doimiy tartibi.
# Ro‘yxatda ko‘rsatilganlar avval chiqadi, qolgan yangi bo‘limlar esa
# avtomatik alifbo tartibida davom etadi.
DUSEL_SECTION_ORDER = [
    "SHITLAR",
    "AVTOMATLAR UCHUN SHITLAR",
    "GALOGEN — Xrustal",
    "GALOGEN — Neoclassic 7W",
    "GALOGEN — Neoclassic 10W",
    "MAGNIT TREKLAR — aksessuarlar",
    "MAGNIT TREK YORITGICHLARI",
    "EXIT",
    "VENTILYATOR",
    "ZVONOK",
    "LUXURY",
    "OFIS YORITGICHLARI",
    "POL ROZTKALAR",
]

def ordered_dusel_sections(sections):
    if not sections:
        return []
    rank = {name: i for i, name in enumerate(DUSEL_SECTION_ORDER)}
    # Tartib: belgilangan asosiy bo‘limlar -> qolgan bo‘limlar alifbo bo‘yicha.
    return sorted(sections, key=lambda x: (rank.get(x, 10000), x.casefold()))

# ============================================================
# MENUS
# ============================================================

def _brand_index(brand):
    brands = [b for b in ("DUSEL", "VERAL", "SALID") if b in PRODUCTS]
    try:
        return brands.index(brand)
    except ValueError:
        return -1

def _brand_from_index(index):
    brands = [b for b in ("DUSEL", "VERAL", "SALID") if b in PRODUCTS]
    try:
        return brands[int(index)]
    except Exception:
        return None

def _section_index(brand, section):
    sections = list(PRODUCTS.get(brand, {}).keys())
    try:
        return sections.index(section)
    except ValueError:
        return -1

def _section_from_index(brand, index):
    sections = list(PRODUCTS.get(brand, {}).keys())
    try:
        return sections[int(index)]
    except Exception:
        return None

def _section_cb(brand, section):
    return "s|" + str(_brand_index(brand)) + "|" + str(_section_index(brand, section))

def _group_index(brand, group):
    groups = [g for g, _ in _ui_groups_for_brand(brand)]
    try:
        return groups.index(group)
    except ValueError:
        return -1

def _group_from_index(brand, index):
    groups = [g for g, _ in _ui_groups_for_brand(brand)]
    try:
        return groups[int(index)]
    except Exception:
        return None

def _group_cb(brand, group):
    return "g|" + str(_brand_index(brand)) + "|" + str(_group_index(brand, group))

def show_brands(chat_id):
    buttons = []

    # Asosiy tartib: DUSEL → VERAL → SALID
    preferred = ["DUSEL", "VERAL", "SALID"]
    ordered = [b for b in preferred if b in PRODUCTS] + [b for b in PRODUCTS if b not in preferred]
    for brand in ordered:
        sections = PRODUCTS.get(brand, {})
        if sections:
            buttons.append((brand, "brand|" + brand))
        else:
            buttons.append((brand + " — hozircha yo‘q", "empty"))

    buttons.append(("🔎 Qidirish", "search"))
    buttons.append(("🛒 Savat", "cart"))

    send_message(
        chat_id,
        "🏷 <b>Brendni tanlang:</b>",
        keyboard(buttons)
    )


def _ui_groups_for_brand(brand):
    """Brend menyusini ixcham ierarxiyaga yig‘adi.
    Bir xil prefiksdagi MODEL/ichki bo‘limlar bitta papkaga kiradi.
    Hech qanday mahsulot o‘chirilmaydi; faqat ko‘rinishi guruhlanadi.
    """
    sec = list(PRODUCTS.get(brand, {}) or {})
    sec_set = set(sec)
    groups = []
    used = set()

    def add_group(name, children):
        children = [x for x in children if x in sec_set and x not in used]
        if children:
            groups.append((name, [(x, "section") for x in children]))
            used.update(children)

    if brand == "DUSEL":
        add_group("💡 LAMPALAR", [x for x in ["LED LAMPALAR", "OQ LAMPALAR", "LIMON LAMPALAR", "LYUSTRA LAMPALAR"] if x in sec_set])
        add_group("🔲 AKRIL PANEL", [x for x in sec if x.startswith("AKRIL-PANEL /") or x.startswith("AKRIL VA PANEL /")])
        add_group("📽 PROJEKTORLAR", [x for x in sec if x.startswith("PRAJECKTOC-RKU /")])
        add_group("💡 GALOGENLAR", [x for x in sec if x == "GALOGEN" or x.startswith("GALOGEN —") or x.startswith("GALOGEN / ")])
        # Premium bitta ota bo‘lim: ranglar uning ichida.
        add_group("⭐ PREMIUM SERIYA", [x for x in ["PREMIUM SERIYA"] if x in sec_set])
        # Rich ham bitta ota bo‘lim: RICH OQ / RICH RANGLI / AKRIL RAMKALAR ichida.
        rich_children = [x for x in sec if x in (
            "RICH SERIYA / RICH OQ",
            "RICH SERIYA / RICH RANGLI",
            "RICH SERIYA / AKRIL RAMKALAR",
        )]
        add_group("🔌 RICH SERIYA", rich_children)
        # Eski yassi RICH SERIYA bo‘limi hech qachon rootda ko‘rinmasin.
        if "RICH SERIYA" in sec_set:
            used.add("RICH SERIYA")
    elif brand == "VERAL":
        # LAMPALAR faqat bitta ota bo‘lim bo‘lsin: OQ / LIMON / LYUSTRA
        # ichida ko‘rinadi, o‘zi tashqarida qayta chiqmaydi.
        add_group("💡 LAMPALAR", [x for x in ["OQ LAMPALAR", "LIMON LAMPALAR", "LYUSTRA LAMPALAR"] if x in sec_set])
        add_group("🔲 AKRIL PANEL", [x for x in ["ICHKI AKRIL LED PANEL", "TASHQI AKRIL LED PANEL", "TASHQI LED PANEL", "DUMALOQ ICHKI AKRIL", "TO‘RT BURCHAK ICHKI AKRIL", "TO‘RT BURCHAK TASHQI AKRIL", "DUMALOQ TASHQI AKRIL"] if x in sec_set])
        add_group("📽 PROJEKTORLAR", [x for x in sec if "P5" in x.upper() or "P10" in x.upper()])
        add_group("⬜ PANEL 60×60", [x for x in sec if "60X60" in x.upper() or "60×60" in x.upper()])
    elif brand == "SALID":
        add_group("💡 GALOGENLAR", [x for x in ["GALOGEN — SG", "GALOGEN — SN", "GALOGEN"] if x in sec_set])
        add_group("✨ LYUSTRA", [x for x in ["LYUSTRA"] if x in sec_set])
        add_group("🔌 ROZETKALAR", [x for x in ["ROZETKALAR"] if x in sec_set])

    # Qolgan bo‘limlarni prefiks bo‘yicha avtomatik guruhlaymiz.
    # Masalan: SLIM NABOR / ..., MIRANDA / ..., IP44 ... / ...
    prefix_map = {}
    for x in sec:
        if x in used:
            continue
        if " / " in x:
            prefix = x.split(" / ", 1)[0].strip()
            if prefix:
                prefix_map.setdefault(prefix, []).append(x)

    for prefix, children in prefix_map.items():
        if len(children) >= 1:
            add_group("📁 " + prefix, children)

    # Hali guruhlanmagan bo‘limlarni bitta ixcham papkaga yig‘amiz.
    remaining = [x for x in sec if x not in used]
    if remaining:
        groups.append(("📦 BOSHQA BO‘LIMLAR", [(x, "section") for x in remaining]))
        used.update(remaining)

    return groups

def show_brand_sections_safe(chat_id, brand):
    """DUSEL/VERAL brend tugmasi uchun DBsiz, xavfsiz menyu.
    Brend tugmasi hech qachon SQLite guruh jadvaliga bog‘liq bo‘lmaydi.
    """
    brand = str(brand or '').strip()
    real_brand = next((b for b in PRODUCTS if str(b).casefold() == brand.casefold()), None)
    if not real_brand:
        send_message(chat_id, "❌ Brend topilmadi. /start bosing.")
        return
    brand = real_brand
    sections = PRODUCTS.get(brand, {}) or {}
    if not sections:
        send_message(chat_id, "ℹ️ Bu brendda hozircha mahsulot yo‘q.")
        return

    buttons = []
    try:
        custom = _ui_groups_for_brand(brand)
        grouped = {target for _, children in custom for target, typ in children}
        for group, _children in custom:
            buttons.append((group, _group_cb(brand, group)))
        for section in sections:
            if section not in grouped:
                buttons.append((str(section), _section_cb(brand, str(section))))
    except Exception:
        # Ierarxiya funksiyasida xato bo‘lsa ham oddiy katalog ochilsin.
        buttons = [(str(section), _section_cb(brand, str(section))) for section in sections]

    buttons.append(("🔎 Qidirish", "search"))
    buttons.append(("⬅️ Brendlar", "brands"))
    send_message(chat_id, "🏷 <b>" + html.escape(brand) + "</b>\n\n📂 <b>Bo‘limni tanlang:</b>", keyboard(buttons))


def show_sections(chat_id, brand):
    sections = PRODUCTS.get(brand, {})
    if not sections:
        send_message(chat_id, "ℹ️ Bu brendda hozircha mahsulot yo‘q.")
        return
    custom = _ui_groups_for_brand(brand)
    grouped = {target for _, children in custom for target, typ in children}
    buttons=[]
    for group, _children in custom:
        buttons.append((group, _group_cb(brand, group)))
    # Eski DB guruhlari ham ishlaydi, lekin custom guruhlarga tegmaganlarini ko‘rsatamiz.
    # DB vaqtincha band/lock bo‘lsa ham brend menyusi ochilishi shart.
    # DB guruhlari faqat qo‘shimcha UI sifatida olinadi; katalogning o‘zi PRODUCTSda.
    db_groups={}
    try:
        conn=get_db(); cur=conn.cursor()
        cur.execute("SELECT group_name, child_section FROM section_groups WHERE brand=? ORDER BY id ASC", (brand,))
        for g,c in cur.fetchall(): db_groups.setdefault(g,[]).append(c)
        conn.close()
    except Exception:
        db_groups={}
    custom_labels={g for g,_ in custom}
    for g in db_groups:
        if g not in custom_labels and not any(c in grouped for c in db_groups[g]):
            buttons.append(("📁 " + g, "sectiongroup|"+brand+"|"+g))
    for section in sections:
        if section not in grouped and not any(section in children and typ == "section" for _, children in custom for _target, typ in children):
            buttons.append((str(section), _section_cb(brand, str(section))))
    buttons.append(("🔎 Qidirish", "search"))
    buttons.append(("⬅️ Brendlar", "brands"))
    send_message(chat_id, "🏷 <b>"+html.escape(str(brand))+"</b>\n\n📂 <b>Bo‘limni tanlang:</b>", keyboard(buttons))


def show_section_group(chat_id, brand, group):
    # Avval yangi, aniq ierarxiyani tekshiramiz.
    for group_name, children in _ui_groups_for_brand(brand):
        if group == group_name:
            buttons=[]
            for child, typ in children:
                label = str(child)
                if " / " in label:
                    label = label.split(" / ", 1)[1]
                buttons.append(("📂 " + label, _section_cb(brand, child)))
            buttons.append(("⬅️ "+brand, "brand|"+brand))
            send_message(chat_id, "📁 <b>"+html.escape(group)+"</b>\n\n<b>Ichki bo‘limni tanlang:</b>", keyboard(buttons))
            return

    children=[]
    try:
        conn=get_db(); cur=conn.cursor()
        cur.execute("SELECT child_section FROM section_groups WHERE brand=? AND group_name=? ORDER BY id ASC", (brand,group))
        children=[r[0] for r in cur.fetchall()]; conn.close()
    except Exception:
        children=[]
    buttons=[]
    prefix=str(group).strip()+" / "
    for child in children:
        label=child[len(prefix):] if child.startswith(prefix) else child
        buttons.append(("📂 "+label, _section_cb(brand, child)))
    buttons.append(("⬅️ "+brand, "brand|"+brand))
    send_message(chat_id, "📁 <b>"+html.escape(group)+"</b>\n\n<b>Model / ichki bo‘limni tanlang:</b>", keyboard(buttons))

def send_catalog_photo_if_exists(chat_id, brand, section, color=None, model=None):
    fids = get_catalog_images_for(brand, section, color, model)
    if fids:
        caption = "🛍 <b>" + html.escape(str(brand)) + "</b>\n📂 <b>" + html.escape(str(section)) + "</b>"
        if model:
            caption += "\n📦 <b>" + html.escape(str(model)) + "</b>"
        if color:
            caption += "\n🎨 <b>" + html.escape(str(color)) + "</b>"
        if len(fids) == 1:
            send_photo(chat_id, fids[0], caption)
        else:
            send_media_group(chat_id, fids, caption)


def set_product_packaging(brand, section, product, box_qty=0, pack_qty=0, color=""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO product_packaging(brand,section,color,product,box_qty,pack_qty) VALUES(?,?,?,?,?,?)",
        (str(brand), str(section), str(color or ""), str(product), int(box_qty or 0), int(pack_qty or 0))
    )
    conn.commit()
    conn.close()


def get_product_packaging(brand, section, product, color=""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT box_qty, pack_qty FROM product_packaging WHERE brand=? AND section=? AND color=? AND product=?",
        (str(brand), str(section), str(color or ""), str(product))
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0, 0
    return int(row[0] or 0), int(row[1] or 0)


def packaging_text(brand, section, product, color=""):
    box_qty, pack_qty = get_product_packaging(brand, section, product, color)
    box = str(box_qty) + " dona" if box_qty > 0 else "Kiritilmagan"
    pack = str(pack_qty) + " dona" if pack_qty > 0 else "Kiritilmagan"
    return "📦 Karobka: <b>" + box + "</b>\n📦 Pochka: <b>" + pack + "</b>"


def show_products(chat_id, brand, section):
    # SALID ROZETKALAR: avval 3 ta model, keyin rang, keyin mahsulot.
    if brand == "SALID" and section == "ROZETKALAR":
        buttons = [
            ("DELUXE", "salidmodel|SALID|ROZETKALAR|DELUXE"),
            ("ULTRA", "salidmodel|SALID|ROZETKALAR|ULTRA"),
            ("SMART HOME", "salidmodel|SALID|ROZETKALAR|SMART HOME"),
            ("⬅️ SALID", "brand|SALID"),
        ]
        send_message(chat_id, "🔌 <b>SALID — ROZETKALAR</b>\n\nModelni tanlang:", keyboard(buttons))
        return

    # SALID PDF kataloglari katta bo‘lgani uchun sahifalab ko‘rsatiladi.
    if brand == "SALID" and (section == "LYUSTRA" or section.startswith("GALOGEN")):
        show_salid_pdf_catalog_page(chat_id, section, 0)
        return

    items = PRODUCTS.get(brand, {}).get(section, [])

    # SALID rangli seriyasi: avval rang tanlanadi
    if isinstance(items, dict):
        buttons = []
        for color in items:
            emoji = {"White":"⚪", "Grey":"🩶", "Black":"⚫", "Dark Grey":"🌑", "Gold":"🥂"}.get(color, "🎨")
            buttons.append((emoji + " " + color, "color|" + brand + "|" + section + "|" + color))
        send_catalog_photo_if_exists(chat_id, brand, section)
        buttons.append(("⬅️ Bo‘limlar", "brand|" + brand))
        send_message(chat_id, "🎨 <b>SALID — Rangni tanlang</b>\n\nKerakli rangni tanlang:", keyboard(buttons))
        return

    if not items:
        send_message(chat_id, "ℹ️ Bu bo‘limda mahsulot yo‘q.")
        return

    buttons = []
    for index, item in enumerate(items):
        product, price = item
        buttons.append((product + " — $" + format(price), "product|" + brand + "|" + section + "|" + str(index)))
    buttons.append(("🔎 Qidirish", "search"))
    buttons.append(("⬅️ Bo‘limlar", "brand|" + brand))
    send_message(chat_id, "📦 <b>" + brand + "</b>\n📂 <b>" + section + "</b>\n\nMahsulotni tanlang:", keyboard(buttons))


def show_salid_model_colors(chat_id, brand, section, model):
    models = PRODUCTS.get(brand, {}).get(section, {})
    colors = models.get(model, {}) if isinstance(models, dict) else {}
    if not colors:
        send_message(chat_id, "ℹ️ Bu model topilmadi.")
        return
    emojis = {"White":"⚪", "Grey":"🩶", "Black":"⚫", "Dark Grey":"🌑", "Gold":"🥇", "Golden":"🟡", "Gray":"🩶"}
    buttons = [(emojis.get(c, "🎨") + " " + c, "salidcolor|" + brand + "|" + section + "|" + model + "|" + c) for c in colors]
    buttons.append(("⬅️ Modellar", "section|" + brand + "|" + section))
    send_message(chat_id, "🎨 <b>" + model + "</b>\n\nRangni tanlang:", keyboard(buttons))


def show_salid_model_products(chat_id, brand, section, model, color):
    items = PRODUCTS.get(brand, {}).get(section, {}).get(model, {}).get(color, [])
    if not items:
        send_message(chat_id, "ℹ️ Bu rangda mahsulot yo‘q.")
        return
    send_catalog_photo_if_exists(chat_id, brand, section, color, model)
    buttons = []
    for index, item in enumerate(items):
        product, price = item
        buttons.append((product + " — $" + format(price), "salidproduct|" + brand + "|" + section + "|" + model + "|" + color + "|" + str(index)))
    buttons.append(("⬅️ Ranglar", "salidmodel|" + brand + "|" + section + "|" + model))
    send_message(chat_id, "🎨 <b>" + color + "</b>\n\nMahsulotni tanlang:", keyboard(buttons))


def show_color_products(chat_id, brand, section, color):
    items = PRODUCTS.get(brand, {}).get(section, {}).get(color, [])
    if not items:
        send_message(chat_id, "ℹ️ Bu rangda mahsulot yo‘q.")
        return
    send_catalog_photo_if_exists(chat_id, brand, section, color)
    buttons = []
    for index, item in enumerate(items):
        product, price = item
        buttons.append((product + " — $" + format(price), "product|" + brand + "|" + section + "|" + color + "|" + str(index)))
    buttons.append(("⬅️ Ranglar", "section|" + brand + "|" + section))
    send_message(chat_id, "🎨 <b>" + color + "</b>\n\nMahsulotni tanlang:", keyboard(buttons))


def format(price):
    return "{:.2f}".format(price)


# ============================================================
# PRODUCT -> QUANTITY
# ============================================================

def select_product(chat_id, brand, section, index, color=""):
    try:
        index = int(index)
        if color:
            product, price = PRODUCTS[brand][section][color][index]
        else:
            product, price = PRODUCTS[brand][section][index]
    except Exception:
        send_message(chat_id, "❌ Mahsulot topilmadi.")
        return

    set_state(chat_id, "quantity", {
        "brand": brand,
        "section": section,
        "product": product,
        "price": price,
        "color": color or ""
    })

    title = product + ((" — " + color) if color else "")
    info = (
        "📦 <b>" + title + "</b>\n"
        "💵 Narxi: <b>$" + format(price) + "</b>\n"
        + packaging_text(brand, section, product, color) + "\n\n"
        "🔢 Nechta dona kerak?\n"
        "Masalan: <b>10</b>"
    )

    # Bo‘lim/rang rasmi mavjud bo‘lsa, mahsulot ma’lumotini rasm ostida ko‘rsatamiz.
    try:
        send_catalog_photo_if_exists(chat_id, brand, section, color or None)
    except Exception:
        pass
    send_message(chat_id, info)


# ============================================================
# CART
# ============================================================

def show_cart(chat_id):
    rows = get_cart(chat_id)

    if not rows:
        send_message(
            chat_id,
            "🛒 <b>Savat bo‘sh.</b>",
            main_menu()
        )
        return

    text = "🛒 <b>SAVAT</b>\n\n"
    total = 0

    for number, row in enumerate(rows, 1):
        cart_id, brand, section, product, price, qty = row

        subtotal = price * qty
        total += subtotal

        text += (
            str(number) + ". <b>" + product + "</b>\n"
            "   " + str(qty) + " dona × $" + format(price)
            + " = <b>$" + format(subtotal) + "</b>\n\n"
        )

    text += "━━━━━━━━━━━━━━\n"
    discount = get_discount_percent(chat_id)
    discount_amount = total * discount / 100.0
    final_total = total - discount_amount
    if discount > 0:
        text += "💵 Oraliq jami: <b>$" + format(total) + "</b>\n"
        text += "🎁 Chegirma: <b>-" + str(discount) + "%</b> (-$" + format(discount_amount) + ")\n"
    text += "💰 <b>JAMI: $" + format(final_total) + "</b>"

    send_message(
        chat_id,
        text,
        keyboard([
            ("✅ Buyurtmani tasdiqlash", "confirm"),
            ("➕ Yana mahsulot qo‘shish", "brands"),
            ("🗑 Savatni tozalash", "clearcart")
        ])
    )


# ============================================================
# ORDER CONFIRMATION
# ============================================================

def confirm_order(chat_id):
    rows = get_cart(chat_id)

    if not rows:
        send_message(chat_id, "🛒 Savat bo‘sh.")
        return

    client = get_client(chat_id)

    if not client:
        set_state(chat_id, "name")
        send_message(chat_id, "👤 Ismingizni kiriting:")
        return

    name, phone = client

    text = "📋 <b>BUYURTMA</b>\n\n"
    total = 0

    for number, row in enumerate(rows, 1):
        cart_id, brand, section, product, price, qty = row
        subtotal = price * qty
        total += subtotal

        text += (
            str(number) + ". <b>" + product + "</b>\n"
            "   Brend: " + brand + "\n"
            "   Bo‘lim: " + section + "\n"
            "   Miqdor: " + str(qty) + " dona\n"
            "   Jami: $" + format(subtotal) + "\n\n"
        )

    discount = get_discount_percent(chat_id)
    discount_amount = total * discount / 100.0
    final_total = total - discount_amount
    text += "━━━━━━━━━━━━━━\n"
    text += "💵 Oraliq jami: <b>$" + format(total) + "</b>\n"
    if discount > 0:
        text += "🎁 Chegirma: <b>-" + str(discount) + "%</b> (-$" + format(discount_amount) + ")\n"
    text += "💰 <b>JAMI: $" + format(final_total) + "</b>\n\n"
    text += "👤 Ism: <b>" + name + "</b>\n"
    text += "📞 Telefon: <b>" + phone + "</b>\n\n"
    text += "Buyurtmani yuboraymi?"

    send_message(
        chat_id,
        text,
        keyboard([
            ("✅ HA, BUYURTMA BERISH", "sendorder"),
            ("⬅️ Savatga qaytish", "cart")
        ])
    )


# ============================================================
# SEND ORDER
# ============================================================

def send_order(chat_id):
    rows = get_cart(chat_id)
    client = get_client(chat_id)

    if not rows:
        send_message(chat_id, "🛒 Savat bo‘sh.")
        return

    if not client:
        send_message(chat_id, "❌ Mijoz ma’lumotlari topilmadi. /start bosing.")
        return

    name, phone = client
    total = 0
    items_text = ""

    for number, row in enumerate(rows, 1):
        cart_id, brand, section, product, price, qty = row
        subtotal = price * qty
        total += subtotal

        items_text += (
            str(number) + ". <b>" + product + "</b>\n"
            "   Brend: " + brand + "\n"
            "   Bo‘lim: " + section + "\n"
            "   Miqdor: " + str(qty) + " dona\n"
            "   Narx: $" + format(price) + "\n"
            "   Jami: $" + format(subtotal) + "\n\n"
        )

    discount = get_discount_percent(chat_id)
    discount_amount = total * discount / 100.0
    final_total = total - discount_amount
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    # Avval bazaga saqlaymiz
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO orders(
            chat_id, name, phone, items, total, created_at, order_day
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        chat_id,
        name,
        phone,
        items_text,
        final_total,
        created_at,
        created_at[:10]
    ))

    order_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Adminga yuboriladigan xabar
    admin_text = (
        "🔔 <b>YANGI BUYURTMA!</b>\n\n"
        "📋 Buyurtma: <b>#" + str(order_id) + "</b>\n"
        "📅 Sana: <b>" + created_at + "</b>\n\n"
        "👤 Klient: <b>" + name + "</b>\n"
        "📞 Telefon: <b>" + phone + "</b>\n"
        "🆔 Telegram ID: <code>" + str(chat_id) + "</code>\n\n"
        "━━━━━━━━━━━━━━\n"
        + items_text +
        "━━━━━━━━━━━━━━\n"
        "💰 <b>UMUMIY: $" + format(total) + "</b>"
    )

    result = send_message(ADMIN_ID, admin_text, admin_menu())

    if not result or not result.get("ok"):
        print("ADMIN XABAR XATOSI:", result)

        send_message(
            chat_id,
            "⚠️ Buyurtma bazaga saqlandi, "
            "ammo admin xabarida muammo bo‘ldi.\n"
            "Administrator bilan bog‘laning."
        )
        return

    clear_cart(chat_id)

    send_message(
        chat_id,
        "✅ <b>BUYURTMANGIZ QABUL QILINDI!</b>\n\n"
        "📋 Buyurtma № <b>" + str(order_id) + "</b>\n"
        "💰 Jami: <b>$" + format(final_total) + "</b>\n\n"
        "Tez orada siz bilan bog‘lanamiz. 😊",
        main_menu()
    )


# ============================================================
# TEXT HANDLER
# ============================================================

def start_suggestion(chat_id):
    clear_state(chat_id)
    set_state(chat_id, "suggestion")
    send_message(
        chat_id,
        "📩 <b>TAKLIFLAR</b>\n\n"
        "Taklif yoki fikringizni yozib yuboring.\n"
        "Xabaringiz administratorga yuboriladi."
    )


def handle_text(chat_id, text):
    step, data = get_state(chat_id)

    if step == "search":
        query = text.strip()
        clear_state(chat_id)
        search_products(chat_id, query)
        return

    if step == "name":
        name = text.strip()

        if len(name) < 2:
            send_message(
                chat_id,
                "❌ Ism noto‘g‘ri.\n\n"
                "Iltimos, ismingizni qaytadan kiriting:"
            )
            return

        set_state(chat_id, "phone", {"name": name})

        send_message(
            chat_id,
            "👤 Ism: <b>" + name + "</b>\n\n"
            "📞 Telefon raqamingizni kiriting.\n\n"
            "Masalan: <code>+998901234567</code>"
        )
        return

    if step == "phone":
        phone = text.strip()
        digits = "".join(c for c in phone if c.isdigit())

        if len(digits) < 9:
            send_message(
                chat_id,
                "❌ Telefon raqami noto‘g‘ri.\n\n"
                "Masalan: <code>+998901234567</code>"
            )
            return

        name = data.get("name", "")
        save_client(chat_id, name, phone)

        send_message(
            ADMIN_ID,
            "👤 <b>YANGI MIJOZ RO‘YXATDAN O‘TDI</b>\n\n"
            "Ism: " + name + "\n"
            "Telefon: " + phone + "\n"
            "Chat ID: <code>" + str(chat_id) + "</code>"
        )

        clear_state(chat_id)

        send_message(
            chat_id,
            "✅ <b>Ro‘yxatdan o‘tish tugadi!</b>\n\n"
            "👤 " + name + "\n"
            "📞 " + phone + "\n\n"
            "Endi mahsulot tanlang.",
            main_menu()
        )
        return

    if step == "change_name":
        name = text.strip()
        if len(name) < 2:
            send_message(chat_id, "❌ Ism juda qisqa. Qaytadan kiriting:")
            return
        client = get_client(chat_id)
        if not client:
            clear_state(chat_id)
            send_message(chat_id, "❌ Mijoz topilmadi. /start bosing.")
            return
        save_client(chat_id, name, client[1])
        clear_state(chat_id)
        send_message(chat_id, "✅ Ismingiz yangilandi: <b>" + name + "</b>", settings_menu())
        return

    if step == "change_phone":
        phone = text.strip()
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 9:
            send_message(chat_id, "❌ Telefon raqami noto‘g‘ri. Masalan: <code>+998901234567</code>")
            return
        client = get_client(chat_id)
        if not client:
            clear_state(chat_id)
            send_message(chat_id, "❌ Mijoz topilmadi. /start bosing.")
            return
        save_client(chat_id, client[0], phone)
        clear_state(chat_id)
        send_message(chat_id, "✅ Telefon raqamingiz yangilandi: <b>" + phone + "</b>", settings_menu())
        return

    if step == "admin_contact_edit" and is_admin(chat_id):
        key=(data or {}).get("key","")
        if key not in ("telegram","email","phone"):
            clear_state(chat_id); return
        value=text.strip()
        if len(value)<3:
            send_message(chat_id,"❌ Qiymat juda qisqa. Qaytadan yozing:"); return
        set_admin_contact(key,value); clear_state(chat_id)
        send_reply_message(chat_id,"✅ " + key + " saqlandi.",admin_reply_keyboard()); return

    if step == "admin_brand_rename" and is_admin(chat_id):
        old=(data or {}).get("old",""); new=text.strip()
        if len(new)<2: send_message(chat_id,"❌ Nom juda qisqa."); return
        conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE dynamic_brands SET brand=? WHERE brand=?",(new,old)); cur.execute("UPDATE dynamic_sections SET brand=? WHERE brand=?",(new,old)); cur.execute("UPDATE dynamic_products SET brand=? WHERE brand=?",(new,old)); conn.commit(); conn.close()
        load_dynamic_products(); clear_state(chat_id); send_reply_message(chat_id,"✅ Brend nomi o‘zgartirildi: " + new,admin_reply_keyboard()); return

    if step == "admin_group_rename" and is_admin(chat_id):
        brand=(data or {}).get("brand",""); old=(data or {}).get("old",""); new=text.strip()
        if len(new)<2: send_message(chat_id,"❌ Nom juda qisqa."); return
        conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE section_groups SET group_name=? WHERE brand=? AND group_name=?",(new,brand,old)); conn.commit(); conn.close(); clear_state(chat_id); send_reply_message(chat_id,"✅ Guruh nomi o‘zgartirildi.",admin_reply_keyboard()); return

    if step == "admin_section_merge_name" and is_admin(chat_id):
        group=text.strip(); brand=(data or {}).get("brand",""); selected=(data or {}).get("selected",[])
        if len(group)<2 or len(selected)<2:
            send_message(chat_id,"❌ 2–3 ta bo‘lim tanlanishi va nom kamida 2 belgidan iborat bo‘lishi kerak."); return
        conn=get_db(); cur=conn.cursor()
        for sec in selected:
            cur.execute("DELETE FROM section_groups WHERE brand=? AND child_section=?",(brand,sec))
            cur.execute("INSERT OR IGNORE INTO section_groups(brand,group_name,child_section) VALUES(?,?,?)",(brand,group,sec))
        conn.commit(); conn.close(); clear_state(chat_id)
        send_reply_message(chat_id,"✅ <b>Bo‘limlar birlashtirildi!</b>\n\n📁 "+group+"\n"+"\n".join("• "+x for x in selected),admin_reply_keyboard()); return

    if step == "admin_section_rename" and is_admin(chat_id):
        brand=(data or {}).get("brand",""); old=(data or {}).get("old",""); new=text.strip()
        if len(new)<2: send_message(chat_id,"❌ Nom juda qisqa."); return
        conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE dynamic_sections SET section=? WHERE brand=? AND section=?",(new,brand,old)); cur.execute("UPDATE dynamic_products SET section=? WHERE brand=? AND section=?",(new,brand,old)); conn.commit(); conn.close()
        load_dynamic_products(); clear_state(chat_id); send_reply_message(chat_id,"✅ Bo‘lim nomi o‘zgartirildi: " + new,admin_reply_keyboard()); return

    if step == "admin_brand_name" and is_admin(chat_id):
        brand = text.strip()
        if len(brand) < 2:
            send_message(chat_id, "❌ Brend nomi juda qisqa. Qaytadan yozing:")
            return
        if brand in PRODUCTS:
            send_message(chat_id, "⚠️ Bu brend allaqachon mavjud. Boshqa nom yozing:")
            return
        inserted = save_dynamic_brand(brand)
        load_dynamic_products()
        clear_state(chat_id)
        if inserted:
            send_reply_message(chat_id, "✅ <b>Brend qo‘shildi!</b>\n\n🏷 <b>" + brand + "</b>\n\nEndi \"➕ Bo‘lim qo‘shish\" orqali shu brend ichiga bo‘lim qo‘shishingiz mumkin.", admin_reply_keyboard())
        else:
            send_reply_message(chat_id, "⚠️ Bu brend allaqachon mavjud.", admin_reply_keyboard())
        return

    if step == "admin_section_name" and is_admin(chat_id):
        section = text.strip()
        brand = (data or {}).get("brand", "")
        if len(section) < 2:
            send_message(chat_id, "❌ Bo‘lim nomi juda qisqa. Qaytadan yozing:")
            return
        if isinstance(PRODUCTS.get(brand, {}).get(section), dict):
            send_message(chat_id, "⚠️ Bu nom SALID rangli bo‘lim sifatida mavjud. Boshqa nom yozing:")
            return
        inserted = save_dynamic_section(brand, section)
        load_dynamic_products()
        clear_state(chat_id)
        if inserted:
            send_reply_message(chat_id, "✅ <b>Bo‘lim qo‘shildi!</b>\n\n🏷 Brend: <b>" + brand + "</b>\n📂 Bo‘lim: <b>" + section + "</b>\n\nEndi \"➕ Mahsulot qo‘shish\" orqali shu bo‘limga mahsulot kiriting.", admin_reply_keyboard())
        else:
            send_reply_message(chat_id, "⚠️ Bu bo‘lim allaqachon mavjud.", admin_reply_keyboard())
        return

    if step == "admin_product_section" and is_admin(chat_id):
        section = text.strip()
        if len(section) < 2:
            send_message(chat_id, "❌ Bo‘lim nomi juda qisqa. Qaytadan yozing:")
            return
        brand = (data or {}).get("brand", "")
        if isinstance(PRODUCTS.get(brand, {}).get(section), dict):
            send_message(chat_id, "⚠️ Bu bo‘lim rangli SALID bo‘limi. Boshqa yangi bo‘lim nomini yozing yoki /cancel bosing.")
            return
        set_state(chat_id, "admin_product_name", {"brand": brand, "section": section})
        send_message(chat_id, "📦 <b>Mahsulot nomini yozing.</b>\nMasalan: <code>Dusel LED 25W</code>")
        return

    if step == "admin_product_name" and is_admin(chat_id):
        product = text.strip()
        if len(product) < 2:
            send_message(chat_id, "❌ Mahsulot nomi juda qisqa. Qaytadan yozing:")
            return
        set_state(chat_id, "admin_product_price", {"brand": data.get("brand", ""), "section": data.get("section", ""), "product": product})
        send_message(chat_id, "💵 <b>Mahsulot narxini yozing.</b>\nMasalan: <code>2.50</code>")
        return

    if step == "admin_product_price" and is_admin(chat_id):
        try:
            price = float(text.strip().replace(",", ".").replace("$", ""))
        except Exception:
            send_message(chat_id, "❌ Narx noto‘g‘ri. Masalan: <code>2.50</code>")
            return
        if price < 0:
            send_message(chat_id, "❌ Narx manfiy bo‘lmasin.")
            return
        new_data = dict(data or {})
        new_data["price"] = price
        set_state(chat_id, "admin_product_box", new_data)
        send_message(chat_id, "📦 <b>Karobkada nechta dona?</b>\nMasalan: <code>100</code>\nAgar noma’lum bo‘lsa: <code>0</code>")
        return

    if step == "admin_product_box" and is_admin(chat_id):
        raw = text.strip().lower()
        match = re.search(r"\d+", raw)
        if not match:
            send_message(chat_id, "❌ Son kiriting. Masalan: <code>100</code>")
            return
        box_qty = int(match.group(0))
        new_data = dict(data or {})
        new_data["box_qty"] = box_qty
        set_state(chat_id, "admin_product_pack", new_data)
        send_message(chat_id, "📦 <b>Pochkada nechta dona?</b>\nMasalan: <code>10</code>\nAgar noma’lum bo‘lsa: <code>0</code>")
        return

    if step == "admin_product_pack" and is_admin(chat_id):
        raw = text.strip().lower()
        match = re.search(r"\d+", raw)
        if not match:
            send_message(chat_id, "❌ Son kiriting. Masalan: <code>10</code>")
            return
        pack_qty = int(match.group(0))
        brand = data.get("brand", "")
        section = data.get("section", "")
        product = data.get("product", "")
        price = float(data.get("price", 0))
        inserted = save_dynamic_product(brand, section, product, price)
        set_product_packaging(brand, section, product, int(data.get("box_qty", 0)), pack_qty)
        load_dynamic_products()
        clear_state(chat_id)
        if inserted:
            status = "Mahsulot qo‘shildi"
        else:
            status = "Mahsulot allaqachon mavjud, qadoqlash ma’lumoti yangilandi"
        send_reply_message(
            chat_id,
            "✅ <b>" + status + "!</b>\n\n"
            "🏷 Brend: <b>" + brand + "</b>\n"
            "📂 Bo‘lim: <b>" + section + "</b>\n"
            "📦 Mahsulot: <b>" + product + "</b>\n"
            "💵 Narx: <b>$" + format(price) + "</b>\n"
            "📦 Karobka: <b>" + str(int(data.get("box_qty", 0))) + " dona</b>\n"
            "📦 Pochka: <b>" + str(pack_qty) + " dona</b>",
            admin_reply_keyboard()
        )
        return

    if step in ("admin_pack_box", "admin_pack_pack") and is_admin(chat_id):
        raw = text.strip().lower()
        match = re.fullmatch(r"\d+", raw)
        if not match:
            send_message(chat_id, "❌ Faqat butun son kiriting. Masalan: <code>100</code>")
            return
        qty = int(match.group(0))
        brand = data.get("brand", "")
        section = data.get("section", "")
        color = data.get("color", "")
        product = data.get("product", "")
        box, pack = get_product_packaging(brand, section, product, color)
        if step == "admin_pack_box":
            box = qty
        else:
            pack = qty
        set_product_packaging(brand, section, product, box, pack, color)
        clear_state(chat_id)
        send_reply_message(chat_id,
            "✅ <b>Qadoqlash saqlandi!</b>\n\n" +
            "📦 Mahsulot: <b>" + html.escape(product) + "</b>\n" +
            ("🎨 Rang: <b>" + html.escape(color) + "</b>\n" if color else "") +
            "📦 Karobka: <b>" + str(box) + " dona</b>\n" +
            "📦 Pochka: <b>" + str(pack) + " dona</b>",
            admin_reply_keyboard())
        return

    if step == "admin_image":
        send_message(chat_id, "📸 Rasmni aynan surat sifatida yuboring.\n\nBekor qilish: /cancel")
        return

    if step == "suggestion":
        suggestion = text.strip()

        if not suggestion:
            send_message(chat_id, "❌ Iltimos, taklifingizni yozing.")
            return

        client = get_client(chat_id)
        if client:
            name, phone = client
        else:
            name, phone = "Noma’lum", "Noma’lum"

        admin_text = (
            "📩 <b>YANGI TAKLIF</b>\n\n"
            "👤 Ism: <b>" + name + "</b>\n"
            "📞 Telefon: <b>" + phone + "</b>\n"
            "🆔 Chat ID: <code>" + str(chat_id) + "</code>\n\n"
            "💬 <b>Taklif:</b>\n" + suggestion
        )

        result = send_message(ADMIN_ID, admin_text, admin_reply_keyboard())
        clear_state(chat_id)

        if result and result.get("ok"):
            send_message(
                chat_id,
                "✅ <b>Taklifingiz adminga yuborildi!</b>\n\nRahmat. 🙏",
                main_menu()
            )
        else:
            send_message(
                chat_id,
                "⚠️ Taklifni yuborishda xatolik bo‘ldi. Keyinroq urinib ko‘ring.",
                main_menu()
            )
        return

    if step == "admin_price_update" and is_admin(chat_id):
        try:
            new_price=float(text.strip().replace(",",".").replace("$",""))
        except Exception:
            send_message(chat_id,"❌ Narx noto‘g‘ri. Masalan: <code>2.50</code>"); return
        if new_price < 0:
            send_message(chat_id,"❌ Narx manfiy bo‘lmasin."); return
        d=data or {}
        brand,section,product=d.get("brand",""),d.get("section",""),d.get("product","")
        color=d.get("color","")
        if color:
            set_color_price_override(brand,section,color,product,new_price,0)
            try: PRODUCTS[brand][section][color][int(d.get("index",-1))]=(product,new_price)
            except Exception: pass
        else:
            set_price_override(brand,section,product,new_price,0)
            try: PRODUCTS[brand][section][int(d.get("index",-1))]=(product,new_price)
            except Exception: pass
            conn=get_db(); cur=conn.cursor()
            cur.execute("UPDATE dynamic_products SET price=? WHERE brand=? AND section=? AND product=?",
                        (new_price,brand,section,product))
            conn.commit(); conn.close()
        clear_state(chat_id)
        send_reply_message(chat_id,"✅ Narx yangilandi: <b>"+product+" — $"+format(new_price)+"</b>",admin_reply_keyboard())
        return

    if step == "admin_broadcast_all" and is_admin(chat_id):
        message_text = text.strip()
        if not message_text:
            send_message(chat_id, "❌ Xabar bo‘sh bo‘lmasin.")
            return
        ok, total = send_broadcast_all(message_text)
        clear_state(chat_id)
        send_reply_message(chat_id, f"✅ Xabar yuborildi.\n\n📨 Yetkazildi: <b>{ok}</b> / <b>{total}</b> klient", admin_reply_keyboard())
        return

    if step == "admin_broadcast_one" and is_admin(chat_id):
        message_text = text.strip()
        target_id = (data or {}).get("target_id")
        if not message_text or not target_id:
            send_message(chat_id, "❌ Xabar yuborilmadi.")
            clear_state(chat_id)
            return
        result = send_message(int(target_id), "📢 <b>YANGILIK</b>\n\n" + message_text, user_reply_keyboard())
        clear_state(chat_id)
        if result and result.get("ok"):
            send_reply_message(chat_id, "✅ Tanlangan klientga xabar yuborildi.", admin_reply_keyboard())
        else:
            send_reply_message(chat_id, "⚠️ Xabar yuborilmadi. Klient botni bloklagan bo‘lishi mumkin.", admin_reply_keyboard())
        return

    if step == "admin_pick_client" and is_admin(chat_id):
        send_message(chat_id, "👤 Klientni pastdagi tugmalardan tanlang.")
        return

    if step == "quantity":
        # 10, 10ta, 10 dona kabi yozuvlarni ham qabul qiladi.
        raw_qty = text.strip().lower()
        match = re.search(r"\d+", raw_qty)

        if not match:
            send_message(
                chat_id,
                "❌ Miqdor topilmadi. Masalan: <b>10</b> yoki <b>10ta</b>"
            )
            return

        try:
            qty = int(match.group())
        except Exception:
            send_message(
                chat_id,
                "❌ Miqdorni qaytadan kiriting. Masalan: <b>10</b>"
            )
            return

        if qty <= 0:
            send_message(chat_id, "❌ Miqdor 0 dan katta bo‘lishi kerak.")
            return

        brand = data["brand"]
        section = data["section"]
        product = data["product"]
        price = float(data["price"])

        add_to_cart(
            chat_id,
            brand,
            section,
            product,
            price,
            qty
        )

        clear_state(chat_id)

        subtotal = price * qty

        send_message(
            chat_id,
            "✅ <b>Savatga qo‘shildi!</b>\n\n"
            "📦 " + product + "\n"
            "🔢 " + str(qty) + " dona\n"
            "💰 Jami: <b>$" + format(subtotal) + "</b>",
            keyboard([
                ("🛒 Savatni ko‘rish", "cart"),
                ("➕ Yana mahsulot", "brands")
            ])
        )
        return

    # Oddiy mijoz uchun qidiruv doim faol: botga mahsulot nomi/kodini
    # yozishning o‘zi yetadi. ADMIN uchun esa erkin matn qidiruvga tushmasin,
    # aks holda “Otabek”, “Registratsiya” kabi admin yozuvlari mahsulot qidiruviga
    # aylanib ketadi.
    if text and len(text.strip()) >= 2:
        if is_admin(chat_id):
            send_reply_message(chat_id,
                "🛠 <b>ADMIN PANEL</b>\n\nPastdagi klaviaturadan bo‘limni tanlang.",
                admin_reply_keyboard())
            return
        search_products(chat_id, text.strip())
        return

    send_message(
        chat_id,
        "Kerakli bo‘limni tanlang:",
        main_menu()
    )


# ============================================================
# CALLBACK HANDLER
# ============================================================

def handle_callback(callback):
    callback_id = callback.get("id")
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    data = callback.get("data", "")

    if callback_id:
        answer_callback(callback_id)

    if not chat_id:
        return

    try:
        # Qidiruv
        if data == "search":
            search_prompt(chat_id)
            return

        # Qidiruvdan bevosita mahsulotni tanlash
        if data.startswith("sr|"):
            try:
                idx = int(data.split("|", 1)[1])
                rows = SEARCH_CACHE.get(chat_id, [])
                row = rows[idx]
                brand, section, color, index, product, price, model = row
                if model:
                    # Nested SALID mahsulotlari
                    item = PRODUCTS[brand][section][model][color][int(index)]
                    set_state(chat_id, "quantity", {
                        "brand": brand, "section": section + " / " + model,
                        "product": item[0], "price": item[1], "color": color or ""
                    })
                    send_catalog_photo_if_exists(chat_id, brand, section, color, model)
                    send_message(chat_id, "📦 <b>" + html.escape(str(item[0])) + (" — " + html.escape(str(color)) if color else "") + "</b>\n💵 Narxi: <b>$" + format(float(item[1])) + "</b>\n" + packaging_text(brand, section + " / " + model, item[0], color or "") + "\n\n🔢 Nechta dona kerak?\nMasalan: <b>10</b>")
                elif index is not None:
                    select_product(chat_id, brand, section, int(index), color or "")
                else:
                    # Dinamik mahsulot: PRODUCTS ichidan nomi bo‘yicha topamiz.
                    items = PRODUCTS.get(brand, {}).get(section, [])
                    found = None
                    if isinstance(items, dict):
                        for c, vals in items.items():
                            for j, it in enumerate(vals):
                                if it[0] == product:
                                    found = (j, c); break
                            if found: break
                    else:
                        for j, it in enumerate(items):
                            if it[0] == product:
                                found = (j, ""); break
                    if found:
                        select_product(chat_id, brand, section, found[0], found[1])
                    else:
                        send_message(chat_id, "❌ Mahsulot topilmadi.")
            except Exception:
                send_message(chat_id, "❌ Mahsulotni ochib bo‘lmadi.")
            return

        if data.startswith("qsec|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                brand = _brand_from_index(parts[1])
                section = _section_from_index(brand, parts[2]) if brand else None
                if brand and section:
                    show_products(chat_id, brand, section)
            return

        if data.startswith("g|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                brand = _brand_from_index(parts[1])
                group = _group_from_index(brand, parts[2]) if brand else None
                if brand and group:
                    show_section_group(chat_id, brand, group)
            return

        # Takliflar
        if data == "suggestion":
            start_suggestion(chat_id)
            return

        # Brendlar
        if data == "brands":
            show_brands(chat_id)
            return

        # 12-DOKON lokatsiyasi
        if data == "location":
            send_message(chat_id, shop_location_message(chat_id), main_menu())
            return

        # Savat
        if data == "cart":
            show_cart(chat_id)
            return

        # Savatni tozalash
        if data == "clearcart":
            clear_cart(chat_id)
            send_message(
                chat_id,
                "🗑 <b>Savat tozalandi.</b>",
                main_menu()
            )
            return

        if data == "admin_clients":
            show_admin_clients(chat_id)
            return

        if data == "admin_lists":
            show_admin_lists(chat_id)
            return

        if data.startswith("day|"):
            if is_admin(chat_id):
                show_daily_orders(chat_id, data.split("|",1)[1])
            return

        if data.startswith("clientorders|"):
            if is_admin(chat_id):
                show_client_orders(chat_id, int(data.split("|",1)[1]))
            return

        if data == "admin_broadcast":
            show_admin_broadcast(chat_id)
            return

        if data == "msgall":
            start_broadcast(chat_id)
            return

        if data == "msgpick":
            if is_admin(chat_id):
                rows = get_clients()
                buttons = [("👤 " + name, "msgclient|" + str(cid)) for cid,name,phone in rows]
                buttons.append(("⬅️ Xabar menyusi", "admin_broadcast"))
                send_message(chat_id, "👤 <b>Klientni tanlang:</b>", keyboard(buttons))
            return

        if data.startswith("msgclient|"):
            if is_admin(chat_id):
                start_broadcast(chat_id, int(data.split("|",1)[1]))
            return

        if data == "admin_orders":
            show_admin_orders(chat_id)
            return

        if data == "admin_excel":
            show_admin_excel(chat_id)
            return

        if data == "admin_products_add":
            show_admin_product_add(chat_id)
            return

        if data == "admin_brand_add":
            show_admin_brand_add(chat_id)
            return

        if data == "admin_section_add":
            show_admin_section_add(chat_id)
            return

        if data.startswith("addsecbrand|"):
            parts = data.split("|", 1)
            if len(parts) == 2 and is_admin(chat_id):
                start_section_add(chat_id, parts[1])
            return

        if data == "admin_packaging" and is_admin(chat_id):
            show_admin_pack_brands(chat_id)
            return
        if data.startswith("packbrand|") and is_admin(chat_id):
            show_admin_pack_sections(chat_id, data.split("|", 1)[1])
            return
        if data.startswith("packsec|") and is_admin(chat_id):
            parts = data.split("|", 2)
            if len(parts) == 3:
                show_admin_pack_products(chat_id, parts[1], parts[2])
            return
        if data.startswith("packedit|") and is_admin(chat_id):
            parts = data.split("|")
            try:
                if len(parts) == 4:
                    show_admin_pack_actions(chat_id, parts[1], parts[2], int(parts[3]), "")
                elif len(parts) == 5:
                    show_admin_pack_actions(chat_id, parts[1], parts[2], int(parts[4]), parts[3])
            except Exception:
                send_message(chat_id, "❌ Mahsulot topilmadi.")
            return
        if data.startswith("packbox|") and is_admin(chat_id):
            parts = data.split("|")
            try:
                if len(parts) == 4:
                    brand, section, idx, color = parts[1], parts[2], int(parts[3]), ""
                elif len(parts) == 5:
                    brand, section, color, idx = parts[1], parts[2], parts[3], int(parts[4])
                else:
                    return
                item = get_price_item(brand, section, idx, color)
                if not item: raise ValueError()
                set_state(chat_id, "admin_pack_box", {"brand":brand,"section":section,"color":color,"index":idx,"product":item[0]})
                send_message(chat_id, "📦 <b>Karobkada nechta dona?</b>\n\nFaqat son yozing. Masalan: <code>100</code>\n0 = kiritilmagan\n\nBekor qilish: /cancel")
            except Exception:
                send_message(chat_id, "❌ Mahsulot topilmadi.")
            return
        if data.startswith("packpack|") and is_admin(chat_id):
            parts = data.split("|")
            try:
                if len(parts) == 4:
                    brand, section, idx, color = parts[1], parts[2], int(parts[3]), ""
                elif len(parts) == 5:
                    brand, section, color, idx = parts[1], parts[2], parts[3], int(parts[4])
                else:
                    return
                item = get_price_item(brand, section, idx, color)
                if not item: raise ValueError()
                set_state(chat_id, "admin_pack_pack", {"brand":brand,"section":section,"color":color,"index":idx,"product":item[0]})
                send_message(chat_id, "📦 <b>Pochkada nechta dona?</b>\n\nFaqat son yozing. Masalan: <code>10</code>\n0 = kiritilmagan\n\nBekor qilish: /cancel")
            except Exception:
                send_message(chat_id, "❌ Mahsulot topilmadi.")
            return

        if data == "admin_prices":
            if is_admin(chat_id): show_admin_price_brands(chat_id)
            return
        if data.startswith("pricebrand|") and is_admin(chat_id):
            show_admin_price_sections(chat_id,data.split("|",1)[1]); return
        if data.startswith("pricesec|") and is_admin(chat_id):
            parts=data.split("|",2)
            if len(parts)==3: show_admin_price_products(chat_id,parts[1],parts[2])
            return
        if data.startswith("priceedit|") and is_admin(chat_id):
            parts=data.split("|")
            try:
                if len(parts)==4:
                    show_admin_price_actions(chat_id,parts[1],parts[2],int(parts[3]))
                elif len(parts)==5:
                    show_admin_price_actions(chat_id,parts[1],parts[2],int(parts[4]),parts[3])
            except Exception: pass
            return
        if data.startswith("priceupdate|") and is_admin(chat_id):
            parts=data.split("|")
            try:
                if len(parts)==4:
                    brand,section,idx=parts[1],parts[2],int(parts[3]); color=""
                elif len(parts)==5:
                    brand,section,color,idx=parts[1],parts[2],parts[3],int(parts[4])
                else: return
                item=get_price_item(brand,section,idx,color)
                if not item: raise ValueError()
                set_state(chat_id,"admin_price_update",{"brand":brand,"section":section,"color":color,"index":idx,"product":item[0]})
                send_message(chat_id,"💵 Yangi narxni yozing. Masalan: <code>2.50</code>\n\nBekor qilish: /cancel")
            except Exception:
                send_message(chat_id,"❌ Mahsulot topilmadi.")
            return
        if data.startswith("pricedelete|") and is_admin(chat_id):
            parts=data.split("|")
            try:
                if len(parts)==4:
                    brand,section,idx=parts[1],parts[2],int(parts[3]); color=""
                elif len(parts)==5:
                    brand,section,color,idx=parts[1],parts[2],parts[3],int(parts[4])
                else: return
                item=get_price_item(brand,section,idx,color)
                if not item: raise ValueError()
                product,old_price=item
                if color:
                    set_color_price_override(brand,section,color,product,old_price,1)
                    PRODUCTS[brand][section][color].pop(idx)
                else:
                    set_price_override(brand,section,product,old_price,1)
                    PRODUCTS[brand][section].pop(idx)
                    conn=get_db(); cur=conn.cursor()
                    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=? AND product=?",(brand,section,product))
                    conn.commit(); conn.close()
                send_reply_message(chat_id,"🗑 O‘chirildi: <b>"+product+"</b>",admin_reply_keyboard())
            except Exception:
                send_message(chat_id,"❌ Mahsulotni o‘chirib bo‘lmadi.")
            return

        if data == "brand_manage":
            show_brand_manage(chat_id); return
        if data.startswith("brandmanage|"):
            show_brand_manage_actions(chat_id, data.split("|",1)[1]); return
        if data == "sectionmanage_back":
            show_brand_manage(chat_id); return
        if data.startswith("sectionmanage|"):
            show_section_manage(chat_id, data.split("|",1)[1]); return
        if data.startswith("sectiongroup|"):
            parts=data.split("|",2); show_section_group(chat_id,parts[1],parts[2]); return
        if data.startswith("sectiongroupadmin|") and is_admin(chat_id):
            parts=data.split("|",2); show_section_group_admin(chat_id,parts[1],parts[2]); return
        if data.startswith("sectionmerge|") and is_admin(chat_id):
            start_section_merge(chat_id,data.split("|",1)[1]); return
        if data.startswith("mergesel|") and is_admin(chat_id):
            parts=data.split("|",2); brand,sec=parts[1],parts[2]; st=USER_STATES.get(chat_id,{}) ; selected=st.get("data",{}).get("selected",[])
            if sec in selected: selected.remove(sec)
            elif len(selected)<3: selected.append(sec)
            st["data"]={"brand":brand,"selected":selected}; USER_STATES[chat_id]=st
            conn=get_db(); cur=conn.cursor(); cur.execute("SELECT section FROM dynamic_sections WHERE brand=? ORDER BY id ASC",(brand,)); secs=[r[0] for r in cur.fetchall()]; conn.close()
            buttons=[(("✅ " if x in selected else "")+x,"mergesel|"+brand+"|"+x) for x in secs]
            if 2<=len(selected)<=3: buttons.append(("➡️ Guruh nomini kiritish","mergefinish|"+brand))
            buttons.append(("⬅️ Bekor qilish","sectionmanage|"+brand))
            send_message(chat_id,"🔗 Tanlandi: <b>"+str(len(selected))+" ta</b>",keyboard(buttons)); return
        if data.startswith("mergefinish|") and is_admin(chat_id):
            brand=data.split("|",1)[1]; st=USER_STATES.get(chat_id,{}) ; selected=st.get("data",{}).get("selected",[])
            if 2<=len(selected)<=3:
                set_state(chat_id,"admin_section_merge_name",{"brand":brand,"selected":selected}); send_message(chat_id,"✏️ Yangi umumiy bo‘lim nomini yozing:\nMasalan: <code>YORITGICHLAR</code>");
            return
        if data.startswith("sectionaction|"):
            parts=data.split("|",2)
            if len(parts)==3: show_section_actions(chat_id, parts[1], parts[2])
            return
        if data.startswith("branddelete|") and is_admin(chat_id):
            brand=data.split("|",1)[1]
            conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM dynamic_products WHERE brand=?",(brand,)); cur.execute("DELETE FROM dynamic_sections WHERE brand=?",(brand,)); cur.execute("DELETE FROM dynamic_brands WHERE brand=?",(brand,)); conn.commit(); conn.close()
            PRODUCTS.pop(brand, None); load_dynamic_products()
            send_reply_message(chat_id, "🗑 <b>Brend o‘chirildi:</b> " + brand, admin_reply_keyboard()); return
        if data.startswith("brandrename|") and is_admin(chat_id):
            brand=data.split("|",1)[1]; set_state(chat_id,"admin_brand_rename",{"old":brand}); send_message(chat_id,"✏️ Yangi brend nomini yozing:\n\nBekor qilish: /cancel"); return
        if data.startswith("groupungroup|") and is_admin(chat_id):
            parts=data.split("|",2); brand,group=parts[1],parts[2]; conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM section_groups WHERE brand=? AND group_name=?",(brand,group)); conn.commit(); conn.close(); send_reply_message(chat_id,"✅ Guruh chiqarildi. Ichki bo‘limlar saqlanib qoldi.",admin_reply_keyboard()); return
        if data.startswith("grouprename|") and is_admin(chat_id):
            parts=data.split("|",2); set_state(chat_id,"admin_group_rename",{"brand":parts[1],"old":parts[2]}); send_message(chat_id,"✏️ Yangi guruh nomini yozing:"); return
        if data.startswith("sectiondelete|") and is_admin(chat_id):
            parts=data.split("|",2); brand,section=parts[1],parts[2]
            conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?",(brand,section)); cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?",(brand,section)); conn.commit(); conn.close(); load_dynamic_products()
            send_reply_message(chat_id,"🗑 <b>Bo‘lim o‘chirildi:</b> " + section, admin_reply_keyboard()); return
        if data.startswith("sectionrename|") and is_admin(chat_id):
            parts=data.split("|",2); set_state(chat_id,"admin_section_rename",{"brand":parts[1],"old":parts[2]}); send_message(chat_id,"✏️ Yangi bo‘lim nomini yozing:"); return
        if data.startswith("contact_edit|") and is_admin(chat_id):
            key=data.split("|",1)[1]; set_state(chat_id,"admin_contact_edit",{"key":key}); send_message(chat_id,"✏️ Yangi " + key + "ni yozing:"); return
        if data == "admin_contacts":
            show_admin_contacts(chat_id); return
        if data == "admin_location":
            show_admin_location(chat_id)
            return

        if data.startswith("prodaddbrand|"):
            parts = data.split("|", 1)
            if len(parts) == 2 and is_admin(chat_id):
                start_product_add(chat_id, parts[1])
            return

        if data == "admin_images":
            show_admin_images(chat_id)
            return

        if data == "admin_home":
            send_reply_message(chat_id, "⚙️ <b>ADMIN PANEL</b>", admin_reply_keyboard())
            return

        if data.startswith("imgbrand|"):
            show_admin_image_sections(chat_id, data.split("|", 1)[1])
            return

        if data.startswith("imgsec|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                show_admin_image_actions(chat_id, parts[1], parts[2])
            return

        if data.startswith("imgmodel|"):
            parts = data.split("|", 3)
            if len(parts) == 4:
                show_admin_image_colors(chat_id, parts[1], parts[2], parts[3])
            return

        if data.startswith("imgcolor|"):
            parts = data.split("|")
            if len(parts) == 4:
                brand, section, color = parts[1], parts[2], parts[3]
                model = None
            elif len(parts) == 5:
                brand, section, model, color = parts[1], parts[2], parts[3], parts[4]
            else:
                return
            buttons=[]
            for slot in range(1,4):
                cb = "imgupload|" + brand + "|" + section
                if model:
                    cb += "|" + model + "|" + color + "|" + str(slot)
                else:
                    cb += "|" + color + "|" + str(slot)
                buttons.append(("Rasm " + str(slot), cb))
            back = "imgmodel|" + brand + "|" + section + "|" + model if model else "imgsec|" + brand + "|" + section
            buttons.append(("⬅️ Orqaga", back))
            send_message(chat_id, "📸 <b>" + html.escape(str(color)) + "</b> — 3 tagacha rasm", keyboard(buttons))
            return

        if data.startswith("imgupload|"):
            parts = data.split("|")
            try:
                if len(parts) == 4:
                    start_image_upload(chat_id, parts[1], parts[2], slot=int(parts[3]))
                elif len(parts) == 5:
                    start_image_upload(chat_id, parts[1], parts[2], parts[3], int(parts[4]))
                elif len(parts) == 6:
                    start_image_upload(chat_id, parts[1], parts[2], parts[4], int(parts[5]), model=parts[3])
                return
            except Exception:
                send_message(chat_id, "❌ Rasm joylash tugmasida xatolik.")
                return

        if data == "settings":
            show_settings(chat_id)
            return

        if data == "back_menu":
            send_message(chat_id, "🏠 <b>Asosiy menyu</b>", main_menu())
            return

        if data == "change_name":
            set_state(chat_id, "change_name")
            send_message(chat_id, "✏️ Yangi ismingizni kiriting:")
            return

        if data == "change_phone":
            set_state(chat_id, "change_phone")
            send_message(chat_id, "📱 Yangi telefon raqamingizni kiriting:\n\nMasalan: <code>+998901234567</code>")
            return

        if data == "admin_discounts":
            show_admin_discounts(chat_id)
            return

        if data.startswith("disc|"):
            if not is_admin(chat_id):
                send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                return
            parts = data.split("|", 2)
            if len(parts) == 3:
                percent = int(parts[1])
                target = int(parts[2])
                set_discount(target, percent)
                client = get_client(target)
                if percent == 5:
                    send_message(target, "🎁 Sizga <b>5% chegirma</b> berildi! Keyingi buyurtmalarda avtomatik hisoblanadi.", main_menu())
                    msg = "✅ 5% chegirma berildi: " + (client[0] if client else str(target))
                else:
                    send_message(target, "ℹ️ 5% chegirmangiz olib tashlandi.", main_menu())
                    msg = "❌ 5% chegirma olib tashlandi: " + (client[0] if client else str(target))
                send_message(chat_id, msg, admin_reply_keyboard())
                return

        # Buyurtmani ko‘rish/tasdiqlash
        if data == "confirm":
            confirm_order(chat_id)
            return

        # Buyurtmani yuborish
        if data == "sendorder":
            send_order(chat_id)
            return

        # Bo‘sh brend
        if data == "empty":
            send_message(
                chat_id,
                "ℹ️ Bu brendda hozircha mahsulot yo‘q."
            )
            return

        # Brend
        if data.startswith("brand|"):
            parts = data.split("|", 1)
            if len(parts) == 2:
                brand_name = parts[1].strip()
                # Brend tugmasi bosilganda DBni qayta yuklash shart emas.
                # Aks holda SQLite lock/timeout sabab DUSEL yoki VERAL jim qolishi mumkin.
                real_brand = next((b for b in PRODUCTS if str(b).casefold() == brand_name.casefold()), None)
                if real_brand is None:
                    send_message(chat_id, "❌ Brend topilmadi. /start bosing.")
                    return
                # DUSEL/VERAL uchun brend menyusini DBdan butunlay mustaqil ochamiz.
                try:
                    show_brand_sections_safe(chat_id, real_brand)
                except Exception:
                    print("BRAND MENU ERROR:")
                    traceback.print_exc()
                    send_message(chat_id, "❌ Brend menyusi ochilmadi. Qayta urinib ko‘ring.")
            return

        # SALID ROZETKALAR -> model
        if data.startswith("salidmodel|"):
            parts = data.split("|", 3)
            if len(parts) == 4:
                show_salid_model_colors(chat_id, parts[1], parts[2], parts[3])
            return

        # SALID ROZETKALAR -> rang
        if data.startswith("salidcolor|"):
            parts = data.split("|", 4)
            if len(parts) == 5:
                show_salid_model_products(chat_id, parts[1], parts[2], parts[3], parts[4])
            return

        # SALID ROZETKALAR -> mahsulot
        if data.startswith("salidproduct|"):
            parts = data.split("|")
            if len(parts) == 6:
                try:
                    index = int(parts[5])
                    brand, section, model, color = parts[1], parts[2], parts[3], parts[4]
                    product, price = PRODUCTS[brand][section][model][color][index]
                    set_state(chat_id, "quantity", {"brand": brand, "section": section, "product": product, "price": price, "color": color})
                    send_catalog_photo_if_exists(chat_id, brand, section, color, model)
                    send_message(chat_id, "📦 <b>" + product + " — " + color + "</b>\n💵 Narxi: <b>$" + format(price) + "</b>\n" + packaging_text(brand, section + " / " + model, product, color) + "\n\n🔢 Nechta dona kerak?\nMasalan: <b>10</b>")
                except Exception:
                    send_message(chat_id, "❌ Mahsulot topilmadi.")
            return

        # SALID GALOGEN / LYUSTRA -> sahifa
        if data.startswith("salidpage|"):
            parts=data.split("|",3)
            if len(parts)==4:
                try: show_salid_pdf_catalog_page(chat_id,parts[2],int(parts[3]))
                except Exception: send_message(chat_id,"❌ Sahifa ochilmadi.")
            return

        # SALID GALOGEN / LYUSTRA -> mahsulot
        if data.startswith("salidpdf|"):
            parts=data.split("|",3)
            if len(parts)==4:
                try:
                    index=int(parts[3])
                    brand, section = parts[1], parts[2]
                    product,price=PRODUCTS[brand][section][index]
                    set_state(chat_id,"quantity",{"brand":brand,"section":section,"product":product,"price":price,"color":""})
                    send_catalog_photo_if_exists(chat_id, brand, section)
                    send_message(chat_id,"📦 <b>"+product+"</b>\n💵 Narxi: <b>$"+format(price)+"</b>\n"+packaging_text(brand, section, product)+"\n\n🔢 Nechta dona kerak?\nMasalan: <b>10</b>")
                except Exception: send_message(chat_id,"❌ Mahsulot topilmadi.")
            return

        # Yangi qisqa bo‘lim callbacki — Telegram 64-byte limitiga xavfsiz.
        if data.startswith("s|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                brand = _brand_from_index(parts[1])
                section = _section_from_index(brand, parts[2]) if brand else None
                if brand and section:
                    show_products(chat_id, brand, section)
            return

        # Eski callback formatini ham saqlaymiz.
        # Bo‘lim
        if data.startswith("section|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                show_products(
                    chat_id,
                    parts[1],
                    parts[2]
                )
            return

        # SALID rang
        if data.startswith("color|"):
            parts = data.split("|", 3)
            if len(parts) == 4:
                show_color_products(chat_id, parts[1], parts[2], parts[3])
            return

        # Mahsulot
        if data.startswith("product|"):
            parts = data.split("|")
            if len(parts) == 4:
                select_product(chat_id, parts[1], parts[2], parts[3])
            elif len(parts) == 5:
                try:
                    select_product(chat_id, parts[1], parts[2], parts[4], parts[3])
                except Exception:
                    send_message(chat_id, "❌ Mahsulot topilmadi.")
            return

    except Exception:
        print("CALLBACK XATOSI:")
        traceback.print_exc()

        send_message(
            chat_id,
            "❌ Xatolik yuz berdi. /start bosing."
        )


# ============================================================
# UPDATE
# ============================================================

def process_update(update):
    try:
        # Oddiy xabar
        message = update.get("message")

        if message:
            chat = message.get("chat") or {}
            chat_id = chat.get("id")

            if chat_id:
                # Telegram ID ni tekshirish uchun.
                incoming_text = (message.get("text") or "").strip()
                if incoming_text in ("/id", "/myid"):
                    send_reply_message(
                        chat_id,
                        "🆔 <b>Sizning Telegram ID:</b> <code>" + str(chat_id) + "</code>",
                        admin_reply_keyboard() if is_admin(chat_id) else main_menu()
                    )
                    return

                # Admin do‘kon lokatsiyasini Telegram Location orqali yuborsa, saqlaymiz.
                if is_admin(chat_id) and message.get("location"):
                    loc = message.get("location") or {}
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    if lat is not None and lon is not None:
                        save_shop_location(lat, lon)
                        clear_state(chat_id)
                        send_reply_message(
                            chat_id,
                            "✅ <b>Do‘kon lokatsiyasi saqlandi!</b>\n\n📍 Endi mijozlar \"12-DOKON lokatsiyasi\" tugmasini bosganda shu joy ochiladi.",
                            admin_reply_keyboard()
                        )
                        return

                # Admin katalog rasmi yuborsa, tanlangan joyga saqlaymiz.
                if is_admin(chat_id) and message.get("photo"):
                    state_step, state_data = get_state(chat_id)
                    if state_step == "admin_image":
                        photos = message.get("photo") or []
                        if photos:
                            file_id = photos[-1].get("file_id")
                            key = (state_data or {}).get("key")
                            slot = int((state_data or {}).get("slot", 1))
                            if file_id and key:
                                save_catalog_image(key, file_id, slot)
                                clear_state(chat_id)
                                send_reply_message(chat_id, "✅ <b>Rasm " + str(slot) + "/3 saqlandi!</b>\n\n" + key.replace("|", " → ") + "\n\n🖼 Rasmlar bo‘limidan 2- va 3-rasmni ham qo‘shishingiz mumkin.", admin_reply_keyboard())
                                return
                if is_admin(chat_id) and (message.get("photo") or message.get("document")):
                    state_step, state_data = get_state(chat_id)
                    if state_step in ("admin_broadcast_all", "admin_broadcast_one"):
                        if state_step == "admin_broadcast_one":
                            target_ids = [int((state_data or {}).get("target_id"))] if (state_data or {}).get("target_id") else []
                        else:
                            conn = get_db()
                            cur = conn.cursor()
                            cur.execute("SELECT chat_id FROM clients")
                            target_ids = [r[0] for r in cur.fetchall()]
                            conn.close()
                        ok = 0
                        for target_id in target_ids:
                            result = send_broadcast_media(message, target_id)
                            if result and result.get("ok"):
                                ok += 1
                            time.sleep(0.05)
                        clear_state(chat_id)
                        send_reply_message(chat_id,
                            "✅ Media xabar yuborildi.\n\n📨 Yetkazildi: <b>" +
                            str(ok) + "</b> / <b>" + str(len(target_ids)) + "</b>",
                            admin_reply_keyboard())
                        return

                text = message.get("text", "")

                if text == "/admin":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        send_reply_message(
                            chat_id,
                            "⚙️ <b>ADMIN PANEL</b>\n\n"
                            "Pastdagi klaviaturadan bo‘limni tanlang.",
                            admin_reply_keyboard()
                        )
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                    return

                if text == "/start":
                    clear_state(chat_id)

                    if is_admin(chat_id):
                        send_reply_message(
                            chat_id,
                            "⚙️ <b>ADMIN PANEL</b>\n\n"
                            "Pastdagi klaviaturadan bo‘limni tanlang.",
                            admin_reply_keyboard()
                        )
                        return

                    client = get_client(chat_id)

                    if client:
                        send_message(
                            chat_id,
                            "👋 Assalomu alaykum!\n\n"
                            "🛍 <b>DUSEL 12-DOKON</b>",
                            main_menu()
                        )
                    else:
                        clear_state(chat_id)
                        set_state(chat_id, "name")

                        send_message(
                            chat_id,
                            "👋 Assalomu alaykum!\n\n"
                            "🛍 <b>DUSEL 12-DOKON</b>\n\n"
                            "Avval ismingizni kiriting:"
                        )
                elif text == "👥 Mijozlar":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_clients(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📋 Spiskalar":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_lists(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📢 Xabar yuborish":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_broadcast(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📦 Buyurtmalar":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_orders(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🎁 Chegirmalar":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_discounts(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "⚙️ Sozlamalar":
                    clear_state(chat_id)
                    show_settings(chat_id)
                elif text == "➕ Mahsulot qo‘shish":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_product_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📦 Karobka/Pochka":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_pack_brands(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🖼 Rasmlar":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_images(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📊 Excel":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_excel(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📍 12-DOKON lokatsiyasi":
                    clear_state(chat_id)
                    send_message(chat_id, shop_location_message(chat_id), user_reply_keyboard())
                elif text == "➕ Brend qo‘shish":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_brand_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "➕ Bo‘lim qo‘shish":
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_section_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text in ("📍 Dokon lokatsiyasi", "📍 Location qo‘shish"):
                    if is_admin(chat_id):
                        clear_state(chat_id)
                        show_admin_location(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "💵 Price boshqaruvi":
                    if is_admin(chat_id):
                        clear_state(chat_id); show_admin_price_brands(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🛠 Brend/bo‘lim boshqaruvi":
                    if is_admin(chat_id):
                        clear_state(chat_id); show_brand_manage(chat_id)
                    else: send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📞 Admin bilan bog‘lanish":
                    if is_admin(chat_id):
                        clear_state(chat_id); show_admin_contacts(chat_id)
                    else:
                        clear_state(chat_id); show_user_contacts(chat_id)
                elif text == "📩 Takliflar":
                    start_suggestion(chat_id)
                elif text == "🔎 Qidirish":
                    clear_state(chat_id)
                    search_prompt(chat_id)
                elif text == "🛍 Mahsulotlar":
                    clear_state(chat_id)
                    show_brands(chat_id)
                elif text == "🛒 Savat":
                    clear_state(chat_id)
                    show_cart(chat_id)
                elif text == "/menu":
                    clear_state(chat_id)
                    send_message(
                        chat_id,
                        "🏠 <b>Asosiy menyu</b>",
                        main_menu()
                    )
                elif text == "/cancel":
                    clear_state(chat_id)
                    send_message(
                        chat_id,
                        "❌ Amal bekor qilindi.",
                        main_menu()
                    )
                elif text:
                    handle_text(chat_id, text)

        # Inline tugma
        callback = update.get("callback_query")

        if callback:
            handle_callback(callback)

    except Exception:
        print("UPDATE XATOSI:")
        traceback.print_exc()


# ============================================================
# RENDER WEB SERVICE — HEALTH SERVER
# ============================================================

class RenderHealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index-1.html")
            if os.path.exists(html_path):
                try:
                    with open(html_path, "rb") as f:
                        body = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                except Exception as e:
                    print("WEBAPP XATOSI:", e)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"DUSEL 12-DOKON BOT OK")

    def log_message(self, format, *args):
        return

def start_render_server():
    # Render PORT environment variable beradi.
    try:
        port = int(os.environ.get("PORT", "10000"))
    except (TypeError, ValueError):
        port = 10000
    server = ThreadingHTTPServer(("0.0.0.0", port), RenderHealthHandler)
    print("Render HTTP server PORT =", port)
    server.serve_forever()



def seed_catalog_fixes():
    """DUSEL katalogining yangi bo'limlari va mahsulotlarini bir marta qo'shadi."""
    conn = get_db(); cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO dynamic_brands(brand) VALUES(?)", ("DUSEL",))

    def add_section(section, rows):
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", ("DUSEL", section))
        for product, price in rows:
            cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", ("DUSEL", section, product, float(price)))

    # RICH SERIYA: eski Rich katalogini tozalab, foydalanuvchi bergan yangi katalogni o‘rnatamiz.
    old_rich_sections = ["Rich", "RICH SERIYA", "RICH RANGLI ROZETKALAR", "RICH OQ", "RICH RANGLI", "AKRIL RAMKALAR"]
    for old_section in old_rich_sections:
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", old_section))
        cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("DUSEL", old_section))
        cur.execute("DELETE FROM catalog_images WHERE image_key LIKE ?", ("DUSEL|" + old_section + "%",))
        PRODUCTS.get("DUSEL", {}).pop(old_section, None)

    rich_common = [
        ("Rich VKL1",1.10),("Rich VKL2",1.25),("Rich VKL3",1.50),
        ("Rich ROZ 1",1.10),("Rich ROZ 2",1.60),
        ("Rich ROZ ZAZM 1",1.25),("Rich ROZ ZAZM 2",1.90),
        ("Rich TV",1.50),("Rich TEL",1.50),("Rich Internet",2.60),
        ("Rich TV Internet",2.60),("Rich USB 1",3.30),("Rich Premium Color",1.90),
        ("Rich Revers 1",1.30),("Rich Revers 2",1.65),
        ("Ramka 2Talik",0.80),("Ramka 3Talik",1.10),("Ramka 4Talik",1.60),("Ramka 5Talik",1.90)
    ]
    rich_white = [
        ("Rich vkl 1tali",0.80),("Rich vkl 2tali",0.90),("Rich vkl 3tali",1.20),
        ("Rich vkl 1tali indikator",1.00),("Rich vkl 2tali indikator",1.10),("Rich zvanok",1.00),
        ("Rich vkl 1tali revers",1.00),("Rich vkl 2tali revers",1.30),("Rich rozetka 1tali",0.80),
        ("Rich rozetka 2tali",1.10),("Rich rozetka zazem 1tali",0.95),("Rich rozetka zazem 2tali",1.30),
        ("Rich rozetka USB",4.00),("Rich TV",1.20),("Rich TEL",1.20),("Rich INTERNET",1.50),
        ("Rich INTERNET + TEL",2.50),("Rich TV + Internet",2.40),("Rich INTERNET + INTERNET",2.40),
        ("Rich TEL + TEL",2.00),("Rich USB",2.70),("Rich USB2",3.50),("Rich Permutator",1.70),
        ("Rich Ramka 2Tali",0.50),("Rich Ramka 3Tali",0.70),("Rich Ramka 4Tali",0.90),("Rich Ramka 5Tali",1.15),
        ("Tashqi 1 klavishli vklyuchatel",0.65),("Tashqi 2 klavishli vklyuchatel",0.75),
        ("Tashqi rozetka",0.65),("Tashqi rozetka, zazemleniyali",0.80),("Tashqi 2-lik rozetka",0.85),
        ("Tashqi 2-lik rozetka, zazemleniyali",1.00),("Tashqi telefon rozetkasi",1.00),
        ("Tashqi televizor rozetkasi",1.00),("Tashqi internet rozetkasi",1.20)
    ]
    rich_colored = {name: list(rich_common) for name in ("BLACK", "COFFEE", "SILVER", "PLATINUM")}
    add_section("RICH OQ", rich_white)
    PRODUCTS.setdefault("DUSEL", {})["RICH RANGLI"] = rich_colored
    cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", ("DUSEL", "RICH RANGLI"))
    add_section("AKRIL RAMKALAR", [
        ("Ramka 1 — COFFEE + GOLD",1.00),("Ramka 2 lik rozetka — COFFEE + GOLD",1.30),("Ramka 2 — COFFEE + GOLD",1.80),("Ramka 3 — COFFEE + GOLD",2.80),("Ramka 4 — COFFEE + GOLD",4.00),("Ramka 5 — COFFEE + GOLD",5.70),
        ("Ramka 1 — BLACK + GOLD",1.00),("Ramka 2 lik rozetka — BLACK + GOLD",1.30),("Ramka 2 — BLACK + GOLD",1.80),("Ramka 3 — BLACK + GOLD",2.80),("Ramka 4 — BLACK + GOLD",4.00),("Ramka 5 — BLACK + GOLD",5.70),
        ("Ramka 1 — WHITE + GOLD",1.00),("Ramka 2 lik rozetka — WHITE + GOLD",1.30),("Ramka 2 — WHITE + GOLD",1.80),("Ramka 3 — WHITE + GOLD",2.80),("Ramka 4 — WHITE + GOLD",4.00),("Ramka 5 — WHITE + GOLD",5.70),
        ("Ramka 1 — SILVER + NICKEL",1.00),("Ramka 2 lik rozetka — SILVER + NICKEL",1.30),("Ramka 2 — SILVER + NICKEL",1.80),("Ramka 3 — SILVER + NICKEL",2.80),("Ramka 4 — SILVER + NICKEL",4.00),("Ramka 5 — SILVER + NICKEL",5.70)
    ])

    akril={
      "ICHKI DUMALOQ AKRIL":[("AR10 10W",1.1),("AR18 18W",1.4),("AR24 24W",2.1),("AR36 36W",3.45),("AR48 48W",6)],
      "ICHKI TO'RTBURCHAK AKRIL":[("AS10 10W",1.25),("AS18 18W",1.5),("AS24 24W",2.25),("AS36 36W",3.6),("AS48 48W",6.5)],
      "TASHQI DUMALOQ AKRIL":[("ASR18 18W",1.9),("ASR24 24W",2.7),("ASR36 36W",4),("ASR48 48W",7.4)],
      "TASHQI TO'RTBURCHAK AKRIL":[("ASS18 18W",2),("ASS24 24W",2.9),("ASS36 36W",4.5),("ASS48 48W",7.6)],
      "AKRIL GALOGEN":[("UR6 6W krug",1.6),("UR12 12W krug",2.2),("UR24 24W krug",3.3),("UR36 36W krug",4.8),("US6 6W kvadrat",1.7),("US12 12W kvadrat",2.4),("US24 24W kvadrat",3.6),("US36 36W kvadrat",5),("DAXR 18W 6500K",2),("DAXR 24W 6500K",2.9),("DAXR 36W 6500K",4.3)],
      "ICHKI DUMALOQ PANEL":[("R6 6W",1.1),("R9 9W",1.45),("R12 12W",1.7),("R15 15W",2.1),("R18 18W",2.3),("R24 24W",3.8)],
      "ICHKI TO'RTBURCHAK PANEL":[("S6 6W",1.2),("S9 9W",1.7),("S12 12W",2),("S15 15W",2.3),("S18 18W",2.75),("S24 24W",4.4)],
      "TASHQI DUMALOQ PANEL":[("SR12 12W",2.1),("SR18 18W",2.9),("SR24 24W",4.4)],
      "TASHQI TO'RTBURCHAK":[("SS12 12W",2.35),("SS18 18W",3.2),("SS24 24W",4.8)],
      "PANEL 60ga60":[("S-48w",6.5),("S-60w",7),("S-72w",7.5),("SS48w naruj",11),("Art-72 6500K",9.5),("Art-96 6500K",10.5),("Ramka 60×60",3.4)]}
    for g,r in akril.items(): add_section("AKRIL-PANEL / "+g,r)

    projekt={
      "P1 MODEL":[(f"P1 {w}W",p) for w,p in [(10,1.8),(20,2.9),(30,4.5),(50,5.8),(100,10.5),(150,16),(200,21)]],
      "P7 MODEL":[(f"P7 {w}W",p) for w,p in [(10,1.7),(20,2.6),(30,3.1),(50,4.7),(100,8.2),(150,13.3),(200,16.8)]],
      "P6 MODEL":[(f"P6 {w}W",p) for w,p in [(50,6.5),(100,10),(200,18),(300,26),(400,33),(500,42),(600,63)]],
      "P8 MODEL":[(f"P8 {w}W",p) for w,p in [(50,8),(100,14),(200,22),(300,32),(400,40),(500,52),(600,65),(800,93),(1000,125)]],
      "PP MODEL":[("PP2 100W",9),("PP2 150W",12.5),("PP2 200W",15),("PP2 300W",24),("PP3 600W",50),("PP3 1000W",65),("PP3 2000W",125),("UFO LED 100W",14),("UFO 150W",18),("UFO 200W",24)],
      "P9-RGB MODEL":[("RGBP 20W",5),("RGBP 30W",7),("RGBP 50W",8),("RGBP 100W",17),("P9-50 Green",5.5),("P9-100 Green",9),("P9-150 Green",12),("P9-200 Green",14),("P9-300 Green",19),("RGBP-50",6),("RGBP-100",11),("RGBP-150",16),("RGBP-200",19),("RGBP-300",24.5),("PD7-30 datchik",6.5),("PD7-50 datchik",8)],
      "RKU-QUYOSH PANEL":[("RKU2-150W",24),("RKU1-50W",12),("RKU1-100W",17),("RKU1-150W",20),("RKU1-300W",27),("RKU1-400W",35),("Solar RKU3-100",32),("Solar RKU3-200",42),("Solar RKU3-300",51),("Solar P1-200",26),("Solar P1-300",36),("Solar P1-400",40),("Solar P2-100",21),("Solar P2-150",25),("Solar P2-200",28),("Solar P2-400",40)],
      "RKU-220V STALBA":[("RKU1-50W Yoritgich",7.5),("RKU2-50W Yoritgich",19),("RKU3-50W Yoritgich",11),("RKU3 100W Yoritgich",17)],
      "FASAD PROJECTOR":[("FP1-30 12W 3000/2000K",10),("FP1-50 18W 3000/2000K",12),("FP1-100 36W 3000/2000K",17),("FP2-30 12W 2000K",10),("FP2-50 18W 2000K",12),("FP2-100 36W 2000K",14),("FP3-30 2000K",8),("FP3-30 4500K",8),("FP3-50 2000K",10),("FP3-50 4500K",10),("FP3-100 2000K",14),("FP3-100 4500K",14),("FP3-10 10W",10),("FP8-9 9W",10),("FP8-36 36W",21)]}
    for g,r in projekt.items(): add_section("PRAJECKTOC-RKU / "+g,r)

    accessories={
      "AKSESSUARLAR":[("Dusel Perehodnik Universal",.45),("Vilka DU-59",.25),("Vilka DU-60",.25),("Vilka DU-70",.25),("DU-69 Perenoska Vilka",.45),("Mesa sotka 3TALI DU-50",.8),("Carlos sotka 3TALI VKL DU-51",1.15),("Pele sotka 3TALI S ZAZ DU-52",15),("Sotka 4tali DU-56",1.1),("Sotka 4tali vkl DU-57",1.65),("Sotka 4tali USB DU-58",3),("DUSEL 3m",2.45),("DUSEL 5m",3.35),("DUSEL 10m",5.4),("Troynik ZAZM DU-67",1.3),("Troynik BEZ ZAZ DU-68",1.1),("Rozetka zashitnik",.12),("PREMIUM 2TALI-3M Udl",2.8),("PREMIUM 2TALI -5M Udl",3.7),("PREMIUM 2TALI -10M Udl",6.4),("PREMIUM 3TALI -3M Udl",2.9),("PREMIUM 3TALI -5M Udl",3.9),("PREMIUM 3TALI -10M Udl",7),("PREMIUM 4TALI -3M Udl",3.2),("PREMIUM 4TALI -5M Udl",4.5),("PREMIUM 4TALI -10M Udl",8),("PREMIUM 5TALI -3M Udl",3.5),("PREMIUM 5TALI -5M Udl",4.7),("PREMIUM 5TALI -10M Udl",8.5),("PREMIUM 2TALI -Kolodka",1),("PREMIUM 3TALI -Kolodka",1.1),("PREMIUM 4TALI -Kolodka",1.3),("PREMIUM 5TALI -Kolodka",1.4),("Perehodnik patron 01",.27),("Perehodnik patron 02",.32),("Perehodnik patron 03",.32),("Patron E27 White",.29),("Patron E27 Black",.29),("Patron E14 White",.25),("Patron E14 Black",.25),("Pultsv-1",4),("Pult 01 (sekundsiz)",4.2),("Pult 02 (sekundli)",4.3),("Izolenta Black",.2),("Izolenta Blue",.2),("Izolenta White",.2),("Izolenta Green",.2),("Izolenta Yellow",.2),("Izolenta Red",.2)],
      "DL-BI":[("DL-BI So'tka",.42),("DL-BI 3M UDN",1.1),("DL-BI 5M UDN",1.6),("DL-BI 8M UDN",2.2),("DL-BI VILKA 2",.18),("DL-BI VILKA 3",.18),("DL-BI VILAK 4",.18)],
      "DRAYVERLAR":[("Drayver 3W",.45),("Drayver 8-24W",.55),("Drayver 48W",3),("Akril Drayver 8-24W",.6),("Akril Drayver 36-48W",.9),("Neoclassic drayver 7-7W",.5),("Neoclassic drayver 10+10W",.7),("Xrustal Galogen orga",.6),("Xrustal Drayver",.4),("Kvadrat Galogen Drayver 7 15W",.55),("Driver TS 6-9W",.45),("Driver TS 15-18W",.45)]}
    # DL-BI va DRAYVERLAR yuqori darajadagi bo'lim emas: AKSESSUARLAR ichida saqlanadi.
    # UI flat section modeli sababli ularni AKSESSUARLAR / ... ko'rinishida alohida guruh qilamiz.
    for g,r in accessories.items(): add_section("AKSESSUARLAR" if g=="AKSESSUARLAR" else "AKSESSUARLAR / "+g,r)

    add_section("GERMETIK / KALTSO",[("Germetik karobka dumaloq",.7),("Germetik karobka to‘rtburchak katta",.65),("Germetik karobka to‘rtburchak kichkina",.4),("Kaltso Dumaloq",.065),("Kaltso Dumaloq Gipsokarton",.11),("Kaltso Dumaloq Katta",.075),("Kaltso Dumaloq Qopqoqlik",.13),("Kaltso Kvadrat",.28)])
    add_section("SLIM NABOR",[("Slim nabor XC-2001 680W DUSEL",110),("Slim nabor XC-2003 650W DUSEL",120),("Slim nabor XC-2004 650W DUSEL",120),("Slim nabor XC-2005 430W DUSEL",75),("Slim nabor XC-2006 430W DUSEL",75),("Slim nabor XC-2009 720W DUSEL",100),("Slim nabor XC-2011 600W DUSEL",110),("Slim nabor XC-2013 600W DUSEL",110),("Slim nabor XC-2016 450W DUSEL",90),("Slim nabor-16 120",2.1),("Slim nabor-9 60",1.4),("Slim nabor-7 40",1.1),("90 gradus ugol",.6),("120 gradus ugol",.6),("Zvezda soidinitel",.6),("Pryamoy soidinitel",.6),("T soidinitel",.7),("X soidinitel",.7),("Soidinitel pitanya 220V",.6)])
    add_section("MIRANDA",[("001 12W White",4),("003 12W Black+Gold",4.5),("003 12W Black+Black",4.5),("003 24W White+Gold",9.5),("003 24W Black+Gold",9.5),("004 7W White",5),("004 12W Black",7.7),("004 12W White",7.7),("005 12W Black",4.7),("005 12W White",4.7),("005 20W White",6)])
    for g,r in {"RELENIY":[("DRS95-500VA",33),("DRS95-1000VA",37),("DRS95-1500VA",43),("DRS95-2000VA",50),("DRS95-3000VA",80),("DRS95-5KVA",120),("DRS95-10KVA",163),("DRS95-12KVA",177),("DRS95-15KVA",205),("DRS95-20KVA",240),("DRS45-5KVA",135),("DRS45-10KVA",181),("DRS45-12KVA",200),("DRS45-15KVA",242),("DRS45-20KVA",279),("DRS45-30KVA",511)],"LATIRNIY":[("DSS-500VA",48),("DSS-1000VA",60),("DSS-1500VA",63),("DSS-2000VA",84),("DSS-5KVA",154),("DSS-10KVA",211),("DSS-15KVA",302),("DSS-20KVA",465),("DSS-30KVA",630),("DSS-50KVA",1050)],"KATTA STABLIZATOR":[("DSO-30KVA",763),("DSO-50KVA",1350),("DSO-60KVA",1440),("DTS-1KVA",90),("DTS-3KVA",135),("DTS-5KVA",200),("DTS-15KVA",450),("DTS-20KVA",540),("DTS-30KVA",950)]}.items(): add_section("STABILIZATOR / "+g,r)

    add_section("Dekorativ Rangli Patronlar",[(x,1.8) for x in ["BRONZE","SILVER","COPPER","BLACK","CHOCO"]])
    add_section("DUSEL GILLYANDA PATRON",[("Gilyanda patron 5×10 (50sm)",5),("Gilyanda patron 10×10 (1m)",5.5),("Gilyanda patron 10×20 (50sm)",9),("Gilyanda patron 15×30 (50sm)",12),("Gilyanda patron 20×20 (1m)",11),("Gilyanda patron 20×40 (50sm)",18)])
    slim={"T9 MODEL":[("T9-IR120 6500K",4.7),("T9-IR60 6500K",3.2)],"T8 MODEL":[("T8-B60 18W",6.3),("T8-B90 24W",7.2),("T8-B120 36W",8),("T8-Comp 9W",1.9),("T8-Comp 18W",2.3),("T8 Derjatel 60sm",.6),("T8 Derjatel 120sm",.9),("T8 Derjatel 2×60sm",.9),("T8 Derjatel 2×120sm",1),("T8 60 10W",.8),("T8 120 20W",1.1),("T8 120 30W",1.45),("T8 120 50W",1.7)],"SLIM MATVIY":[("Slim 20W 60sm",2),("Slim 30W 90sm",2.5),("Slim 40W 120sm",2.8),("Slim-30W 60sm",2.8),("Slim-40W 60sm",3),("Slim 50W 6500K 60sm",4),("Slim 60W 6500K 60sm",4.1),("Slim 80W 6500K 60sm",4.4),("Slim 60W Black",4.1),("Slim 80W Black",4.4)],"T5 LAMPA":[("T5-AL 6W",1.5),("T5-AL 9W",1.8),("T5-AL 18W",2.4)],"T5-PL":[("T5-PL 6W",1),("T5-PL 9W",1.3),("T5-PL 15W",1.5),("T5-PL 18W",1.6)],"T5 LAMPA QUYVAT":[("T5-PL30 6W",1.2),("T5-PL60 9W",1.4),("T5-PL90 15W",1.7),("T5-PL120 18W",1.9)],"T6 LAMPA":[("T6-PL30 6W",.9),("T6-PL60 9W",1.1),("T6-PL90 15W",1.4),("T6-PL120 18W",1.6)],"T8 ALYUMIN":[("T8-AL 9W",2),("T8-AL 18W",2.8)],"GERMETIK SLIM LAMPALAR":[("Slim 40W IP65 Black",4.8),("Slim 40W IP65",4.8),("Slim 60W IP65 Black",6.2)],"SLIM TRANSPARENT":[("Slim G60 60W",5),("Slim G80 60W",5.3),("Slim PS60 Black",3.2),("Slim PS80 Black",4.1)]}
    for g,r in slim.items(): add_section("SLIM LED T5 / "+g,r)
    panel={"PLAFONLAR — HI-TECH":[("BR8 8W",1.6),("BR17 17W",2.5),("BR23 23W",3.8),("BS8 8W",1.8),("BS17 17W",2.9),("BS23 23W",4.3),("YR9 9W 6500K",1.9),("YR9 9W4000K",1.9),("YR18 18W 6500K",2.6),("YR18 18W 4000K",2.6),("YR24 24W 6500K",3.8),("YR24 24W 4000K",3.8),("YR36 36W 6500K",5.5),("YR36 36W 4000K",5.5),("YNR 18 6500K",2.8),("YNR 24 6500K",4.1),("YNR 36 6500K",5.8)],"AKRIL SENSOR PANEL":[("SASS 18w",4.3),("SASS 24w",5.2),("SASS 36w",6.3),("SASR 18w",4.2),("SASR 24w",5.1),("SASR 36w",6.2)],"SAUNA PLAFON":[("PR12 12W",2.2),("PR18 18W",2.6),("PR24 24W",3.4),("PS12 12W",2.2),("PS18 18W",2.6),("PS24 24W",3.4),("RPR18 18W",2.5),("RPR24 24W",3.4),("RPS18 18W",2.5),("RPS24 24W",3.4)],"HI-TECH PLAFON":[("SP-30 White",3.3),("SP-40 White",4.8),("SP-40 Gold",5)],"SENSOR PLAFON":[("DSS-12 12W",5.7),("DSS-18 18W",6.4),("DSS-24 24W",8.5),("DSR-12 12W",5.2),("DSR-18 18W",5.7),("DSR-24 24W",8)]}
    for g,r in panel.items(): add_section("AKRIL VA PANEL / "+g,r)
    add_section("IP 44 VILKA, ROZETKA",[("Dul15",.7),("Dul16",.75),("Dul17",.7),("Dul18",.9),("Dul21",1.45),("Dul11",1.3),("Dul19",2.3),("Dul20",2.8),("Dul12",1.8),("Dul13",2.3),("Dul14",3.2),("Dul22",3)])
    add_section("IP54 ROZETKA VKLUCHATEL",[("VKL 2 ROZ 1Du128",2.6),("VKL 1 ROZ 1DU127",2.4),("ROZ 2 DU126",2.3),("ROZ 1 DU125",1.2),("VKL 2 DU124",1.4),("VKL 1 DU123",1.2)])
    add_section("DUSEL DATCHIK",[("DD-01",4),("DD-02",4.3),("DD-03",4),("DD-04 WHITE",4.1),("DD-04 BLACK",4.1),("DD-05",4.1),("DD-06",3.5),("FR-06",1.5),("FR-10",2),("FR-25",2.9),("Sensor panel uchun datchik",1.75)])
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", "KARTINKA YORITGICHI"))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("DUSEL", "KARTINKA YORITGICHI"))
    add_section("OFIS YORITGICHLARI",[("ZS1-9W 40sm 6500K Gold",11)])
    add_section("TREK YORITGICH RELS",[("TS1 20W Black 6500K",2.4),("TS1 30W Black 6500K",3),("TS1 40W Black 6500K",4.4),("TS1 20W Black 4500K",2.4),("TS1 30W Black 4500K",3),("TS1 40W Black 4500K",4.4),("TS1 20W White 6500K",2.4),("TS1 30W White 6500K",3),("TS1 40W White 6500K",4.4),("TS1 20W White 4500K",2.4),("TS1 30W White 4500K",3),("TS1 40W White 4500K",4.4),("TS2 20W Black 6500K",3.3),("TS2 30W Black 6500K",4.5),("TS2 40W Black 6500K",7),("TS2 20W Black 4500K",3.3),("TS2 30W Black 4500K",4.5),("TS2 40W Black 4500K",7),("TS2 20W White 6500K",3.3),("TS2 30W White 6500K",4.5),("TS2 40W White 6500K",7),("TS2 20W White 4500K",3.3),("TS2 30W White 4500K",4.5),("TS2 40W White 4500K",7),("TS3 30W Black 6500K",5.8),("TS4-40 Black M",7),("TS4-30 White M",5.5),("TS4-40 Black T",7.5),("TS4-30 White T",6),("Rels 1M Black",1.3),("Rels 1.5M Black",1.9),("Rels 2M Black",2.6),("Rels 3M Black",3.9),("Rels 1M WHITE",1.3),("Rels 1.5M WHITE",1.9),("Rels 2M WHITE",2.6),("Rels 3M WHITE",3.9),("Soedinitel Black",.4),("Uglovoy soedinitel Black",.4),("Krugliy soedinitel Black",.7),("Avalniy soedinitel Black",.7),("T soedinitel Black",.8),("Soedinitel WHITE",.4),("Uglovoy soedinitel WHITE",.4),("Krugliy soedinitel WHITE",.7),("Avalniy soedinitel WHITE",.7),("T soedinitel WHITE",.8),("Plyus soedinitel",.9)])
    # DUSEL ichidagi guruhlar: har restartda o'chirilmaydi.
    # Admin qo'shgan/nomlagan guruhlar saqlanadi; faqat yetishmayotgan standart
    # guruh bog'lanishlari qo'shiladi.
    def add_group(group_name, children):
        for child in children:
            cur.execute(
                "INSERT OR IGNORE INTO section_groups(brand,group_name,child_section) VALUES(?,?,?)",
                ("DUSEL", group_name, child)
            )

    # 1) AKRIL VA PANEL — eski ishlagan koddagi barcha akril/panel bo'limlari
    add_group("Akril-Panel", [x for x in [
        "AKRIL-PANEL / ICHKI DUMALOQ AKRIL",
        "AKRIL-PANEL / ICHKI TO'RTBURCHAK AKRIL",
        "AKRIL-PANEL / TASHQI DUMALOQ AKRIL",
        "AKRIL-PANEL / TASHQI TO'RTBURCHAK AKRIL",
        "AKRIL-PANEL / AKRIL GALOGEN",
        "AKRIL-PANEL / ICHKI DUMALOQ PANEL",
        "AKRIL-PANEL / ICHKI TO'RTBURCHAK PANEL",
        "AKRIL-PANEL / TASHQI DUMALOQ PANEL",
        "AKRIL-PANEL / TASHQI TO'RTBURCHAK",
        "AKRIL-PANEL / PANEL 60ga60",
        "AKRIL VA PANEL / PLAFONLAR — HI-TECH",
        "AKRIL VA PANEL / AKRIL SENSOR PANEL",
        "AKRIL VA PANEL / SAUNA PLAFON",
        "AKRIL VA PANEL / HI-TECH PLAFON",
        "AKRIL VA PANEL / SENSOR PLAFON",
    ] if x in {r[0] for r in cur.execute("SELECT section FROM dynamic_sections WHERE brand=?", ("DUSEL",)).fetchall()}])

    # 2) PROYEKTORLAR
    add_group("PROYEKTORLAR", [x for x in [
        "PRAJECKTOC-RKU / P1 MODEL",
        "PRAJECKTOC-RKU / P7 MODEL",
        "PRAJECKTOC-RKU / P6 MODEL",
        "PRAJECKTOC-RKU / P8 MODEL",
        "PRAJECKTOC-RKU / PP MODEL",
        "PRAJECKTOC-RKU / P9-RGB MODEL",
        "PRAJECKTOC-RKU / RKU-QUYOSH PANEL",
        "PRAJECKTOC-RKU / RKU-220V STALBA",
        "PRAJECKTOC-RKU / FASAD PROJECTOR",
    ] if x in {r[0] for r in cur.execute("SELECT section FROM dynamic_sections WHERE brand=?", ("DUSEL",)).fetchall()}])

    # 3) AKSESSUARLAR
    add_group("AKSESSUARLAR", [x for x in [
        "AKSESSUARLAR",
        "AKSESSUARLAR / DL-BI",
        "AKSESSUARLAR / DRAYVERLAR",
    ] if x in {r[0] for r in cur.execute("SELECT section FROM dynamic_sections WHERE brand=?", ("DUSEL",)).fetchall()}])

    # 4) SLIM LED — barcha Slim/T5/T6/T8 bo'limlari bitta guruhda
    add_group("Slim", [x for x in [
        "SLIM LED T5 / T9 MODEL",
        "SLIM LED T5 / T8 MODEL",
        "SLIM LED T5 / SLIM MATVIY",
        "SLIM LED T5 / T5 LAMPA",
        "SLIM LED T5 / T5-PL",
        "SLIM LED T5 / T5 LAMPA QUYVAT",
        "SLIM LED T5 / T6 LAMPA",
        "SLIM LED T5 / T8 ALYUMIN",
        "SLIM LED T5 / GERMETIK SLIM LAMPALAR",
        "SLIM LED T5 / SLIM TRANSPARENT",
    ] if x in {r[0] for r in cur.execute("SELECT section FROM dynamic_sections WHERE brand=?", ("DUSEL",)).fetchall()}])

    # MUHIM: aralash bo‘limlarni mahsulot/model bo‘yicha avtomatik ichki papkalarga
    # ajratmaymiz. Masalan BLOK PITANIYA bitta bo‘lim bo‘lib, 12V 100W,
    # 12V 200W, 12V 400W va hokazo variantlar bevosita mahsulot sifatida chiqadi.
    # Oldingi versiya yaratgan "BLOK PITANIYA / 12V 100W MODEL" kabi
    # ortiqcha ichki bo‘limlarni qayta birlashtiramiz.
    for _brand in ('DUSEL', 'VERAL'):
        _prod = PRODUCTS.setdefault(_brand, {})
        conn = get_db(); cur = conn.cursor()
        cur.execute("SELECT section FROM dynamic_sections WHERE brand=? ORDER BY id ASC", (_brand,))
        _sections = [r[0] for r in cur.fetchall()]

        for _child in list(_sections):
            _child_s = str(_child)
            if ' / ' not in _child_s or not _child_s.upper().endswith(' MODEL'):
                continue
            _parent = _child_s.split(' / ', 1)[0].strip()
            if not _parent:
                continue

            cur.execute("SELECT product, price FROM dynamic_products WHERE brand=? AND section=? ORDER BY id ASC", (_brand, _child_s))
            _rows = cur.fetchall()
            if not _rows:
                cur.execute("DELETE FROM section_groups WHERE brand=? AND child_section=?", (_brand, _child_s))
                cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", (_brand, _child_s))
                _prod.pop(_child_s, None)
                continue

            _prod.setdefault(_parent, [])
            if isinstance(_prod[_parent], dict):
                # Rangli/nested bo‘limga aralashmaslik uchun bunday childni faqat
                # oddiy list parent bo‘lsa birlashtiramiz.
                continue
            _existing = list(_prod[_parent])
            seen = {(str(a).strip().casefold(), round(float(b), 6)) for a,b in _existing}
            for _product, _price in _rows:
                key = (str(_product).strip().casefold(), round(float(_price), 6))
                if key not in seen:
                    _existing.append((str(_product), float(_price)))
                    seen.add(key)
            _prod[_parent] = _existing

            # Parent DB bo‘limini yaratib, mahsulotlarni parentga qaytaramiz.
            cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", (_brand, _parent))
            cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (_brand, _parent))
            for _product, _price in _existing:
                cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", (_brand, _parent, str(_product), float(_price)))

            cur.execute("DELETE FROM section_groups WHERE brand=? AND child_section=?", (_brand, _child_s))
            cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (_brand, _child_s))
            cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", (_brand, _child_s))
            _prod.pop(_child_s, None)

        conn.commit(); conn.close()

    # Yakuniy Rich nazorati: eski yassi bo‘limni bazadan va xotiradagi katalogdan olib tashlaymiz.
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", "RICH SERIYA"))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("DUSEL", "RICH SERIYA"))
    PRODUCTS.get("DUSEL", {}).pop("RICH SERIYA", None)
    PRODUCTS.setdefault("DUSEL", {})["RICH OQ"] = list(rich_white)
    conn.commit()
    conn.close()


def split_dusel_led_catalog():
    """Lampalarni rang bo‘yicha toza ajratadi: OQ, LIMON va LYUSTRA.
    DUSEL LED 5W–200W mahsulotlari rangiga qarab OQ/LIMON ichida turadi.
    """
    conn = get_db()
    cur = conn.cursor()
    brand = "DUSEL"
    source = "LED LAMPA"

    # Eski LED guruhlarini tozalaymiz.
    cur.execute("SELECT child_section FROM section_groups WHERE brand=? AND group_name=?", (brand, source))
    old_children = [r[0] for r in cur.fetchall()]
    for child in old_children:
        cur.execute("DELETE FROM section_groups WHERE brand=? AND child_section=?", (brand, child))
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (brand, child))
        cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", (brand, child))
        PRODUCTS.get(brand, {}).pop(child, None)
    cur.execute("DELETE FROM section_groups WHERE brand=? AND group_name=?", (brand, source))

    cur.execute("SELECT product, price FROM dynamic_products WHERE brand=? AND section=? ORDER BY id ASC", (brand, source))
    rows = cur.fetchall()
    if not rows:
        conn.commit(); conn.close()
        load_dynamic_products()
        return

    oq, limon, lyustra = [], [], []
    watt_order = [5, 7, 9, 10, 12, 15, 18, 20, 30, 40, 50, 60, 80, 100, 150, 200]

    for product, price in rows:
        raw = str(product).strip()
        up = raw.upper()
        # Patrons, candle, MR16 va dekorativ lampalar — alohida LYUSTRA.
        if any(x in up for x in ["C30/", "C35/", "C40/", "G45/", "B45/", "CANDLE", "HL-F", "STAR", "HEART", "ST64", "LF95", "FLAME", "MR16"]):
            lyustra.append((raw, float(price)))
            continue

        m = re.search(r'\b(5|7|9|10|12|15|18|20|30|40|50|60|80|100|150|200)W\b', up)
        if not m:
            continue
        watt = int(m.group(1))
        base = "DUSEL LED " + str(watt) + "W"
        color_text = up.replace(" ", "")

        # 6500K = OQ, 3000K/4000K = LIMON.
        # Katalogda ikkala rang berilgan bo‘lsa, mahsulot ikkala bo‘limda ham chiqadi.
        if "6500K" in color_text:
            oq.append((base + " 6500K", float(price)))
        if "3000K" in color_text or "4000K" in color_text:
            warm = "3000K" if "3000K" in color_text else "4000K"
            limon.append((base + " " + warm, float(price)))

    # OQ/LIMON/LYUSTRA bo‘limlarini qayta yaratamiz.
    sections = {
        "OQ LAMPALAR": oq,
        "LIMON LAMPALAR": limon,
        "LYUSTRA LAMPALAR": lyustra,
    }
    for section, items in sections.items():
        # Dublikatlarni tartibni saqlagan holda olib tashlash.
        seen = set(); clean = []
        for item in items:
            if item[0] not in seen:
                seen.add(item[0]); clean.append(item)
        PRODUCTS.setdefault(brand, {})[section] = clean
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", (brand, section))
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (brand, section))
        for product, price in clean:
            cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", (brand, section, product, float(price)))

    # Eski LED LAMPA va watt bo‘limlarini ko‘rinishdan olib tashlaymiz.
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (brand, source))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", (brand, source))
    PRODUCTS.get(brand, {}).pop(source, None)

    # Rang bo‘limlari alohida ko‘rinadi, guruh ichiga yashirilmaydi.
    conn.commit(); conn.close()
    load_dynamic_products()


def split_veral_lamp_colors():
    """VERAL lampalarni DUSEL kabi yagona LAMPALAR daraxtiga yig‘adi.

    LAMPALAR -> OQ LAMPALAR / LIMON LAMPALAR / LYUSTRA LAMPALAR.
    Eski LED LAMPALAR va VERAL CANDLE bo‘limlari root menyuda qolmaydi.
    Rang ko‘rsatilmagan oddiy LED lampalar OQ ga tushadi.
    4000K/6500K kabi ikkala rang ko‘rsatilgan mahsulot ikkala rangda chiqadi.
    Patron/Candle kabi dekorativ lampalar LYUSTRA ichiga tushadi.
    """
    conn = get_db(); cur = conn.cursor(); brand = "VERAL"

    source_sections = []
    for s in list(PRODUCTS.get(brand, {})):
        u = str(s).upper()
        if s in ("LED LAMPALAR", "VERAL CANDLE", "LYUSTRA LAMPALAR") or "LAMP" in u or "CANDLE" in u:
            source_sections.append(s)

    rows = []
    seen_source = set()
    for source in source_sections:
        if source in seen_source:
            continue
        seen_source.add(source)
        cur.execute(
            "SELECT product, price FROM dynamic_products WHERE brand=? AND section=? ORDER BY id ASC",
            (brand, source),
        )
        rows.extend(cur.fetchall())

    if not rows:
        conn.close()
        return

    oq, limon, lyustra = [], [], []
    for product, price in rows:
        raw = str(product).strip()
        up = raw.upper().replace(" ", "")
        price = float(price)

        # C30/C35/C40/G45/B45/CANDLE/MR16 — dekorativ/patronli lampalar.
        if any(x in up for x in ("C30/", "C35/", "C40/", "G45/", "B45/", "CANDLE", "MR16")):
            lyustra.append((raw, price))
            continue

        has_6500 = "6500K" in up
        has_4000 = "4000K" in up
        has_3000 = "3000K" in up

        # OQ: Kelvin yozilmaydi, nom doim VERAL LED + quvvat bo‘ladi.
        # 4000K — LIMON. 6500K — OQ. Ikkalasi bo‘lsa ikkala rangga tushadi.
        m_w = re.search(r"\b(5|7|9|10|12|15|18|20|30|40|50|60|80|100|150|200)W\b", up)
        if m_w:
            base_name = "VERAL LED " + m_w.group(1) + "W"
            if has_6500:
                oq.append((base_name, price))
            if has_4000 or has_3000:
                warm = "4000K" if has_4000 else "3000K"
                limon.append((base_name + " " + warm, price))
            if not (has_6500 or has_4000 or has_3000):
                oq.append((base_name, price))
        else:
            # Noma'lum oddiy LED nomlari ham OQda qoladi, lekin Kelvin yozilmaydi.
            cleaned = re.sub(r"\s*(?:4000K|6500K|3000K)\s*", " ", raw, flags=re.I).strip()
            if cleaned.upper().startswith("LED "):
                cleaned = "VERAL " + cleaned
            oq.append((cleaned, price))

    sections = {
        "OQ LAMPALAR": oq,
        "LIMON LAMPALAR": limon,
        "LYUSTRA LAMPALAR": lyustra,
    }

    # Eski lamp bo‘limlarini DB + PRODUCTS dan olib tashlaymiz.
    for old in source_sections:
        if old in sections:
            continue
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (brand, old))
        cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", (brand, old))
        cur.execute("DELETE FROM section_groups WHERE brand=? AND (group_name=? OR child_section=?)", (brand, old, old))
        PRODUCTS.get(brand, {}).pop(old, None)

    # Rang bo‘limlarini toza qayta yozamiz.
    for section, items in sections.items():
        clean = []
        seen = set()
        for item in items:
            key = (str(item[0]).strip().casefold(), round(float(item[1]), 6))
            if key in seen:
                continue
            seen.add(key)
            clean.append((str(item[0]).strip(), float(item[1])))

        PRODUCTS.setdefault(brand, {})[section] = clean
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", (brand, section))
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", (brand, section))
        for product, price in clean:
            cur.execute(
                "INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)",
                (brand, section, product, float(price)),
            )

    # Rootda faqat LAMPALAR guruhi bo‘ladi; bir xil ichki bo‘lim tashqarida chiqmaydi.
    cur.execute("DELETE FROM section_groups WHERE brand=? AND (group_name=? OR child_section IN (?,?,?))", (
        brand, "LAMPALAR", "OQ LAMPALAR", "LIMON LAMPALAR", "LYUSTRA LAMPALAR"
    ))
    for child in ("OQ LAMPALAR", "LIMON LAMPALAR", "LYUSTRA LAMPALAR"):
        if PRODUCTS.get(brand, {}).get(child):
            cur.execute(
                "INSERT OR IGNORE INTO section_groups(brand,group_name,child_section) VALUES(?,?,?)",
                (brand, "LAMPALAR", child),
            )

    conn.commit(); conn.close()
    load_dynamic_products()


# ============================================================
# BOTNI ISHGA TUSHIRISH
# ============================================================

def finalize_catalog_hierarchy():
    """Final UI hierarchy requested by user.
    Premium/Rich are separated; SALID duplicate ROZETKALAR group is removed.
    Display names are human-readable while prices/models remain from catalog data.
    """
    # ---------------- SALID: remove duplicate ROZETKALAR -> ROZETKALAR group ----------------
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM section_groups WHERE brand=? AND (group_name=? OR child_section=?)", ("SALID", "ROZETKALAR", "ROZETKALAR"))
    conn.commit(); conn.close()

    salid = PRODUCTS.setdefault("SALID", {})
    if "ROZETKALAR" not in salid or not isinstance(salid.get("ROZETKALAR"), dict):
        # Keep existing catalog if available; do not invent products.
        pass

    # ---------------- DUSEL: remove old flat Rich ----------------
    dusel = PRODUCTS.setdefault("DUSEL", {})
    dusel.pop("RICH SERIYA", None)
    dusel.pop("RICH RANGLI ROZETKALAR", None)

    # ---------------- PREMIUM SERIYA ----------------
    # Premium PDF: DPO/DP model families, displayed without model codes.
    # Prices are taken from the Premium catalog; where the PDF OCR had a decimal
    # point lost (e.g. 195), the intended price is 1.95.
    premium_base = [
        ("VIKLYUCHATEL 1 TALI", 1.40),
        ("VIKLYUCHATEL 2 TALI", 1.65),
        ("VIKLYUCHATEL 3 TALI", 1.95),
        ("ZVANOK", 1.85),
        ("VIKLYUCHATEL O'TUVCHI 1 TALI", 1.50),
        ("VIKLYUCHATEL O'TUVCHI 2 TALI", 1.85),
        ("PEREKLYUCHATEL 1 TALI", 2.00),
        ("ROZETKA 1 TALI", 1.40),
        ("ROZETKA 1 TALI ZAZEMLENIYALI", 1.60),
        ("ROZETKA 2 TALI", 2.60),
        ("ROZETKA 2 TALI ZAZEMLENIYALI", 2.80),
        ("TV", 1.75),
        ("TELEFON", 2.00),
        ("INTERNET", 1.80),
        ("USB TYPE-C", 8.30),
        ("DIMMER", 4.40),
        ("INTERNET 2 TALI", 3.40),
        ("ROZETKA 1 TALI ZAZEMLENIYALI QOPQOQLI", 1.95),
        ("TV + INTERNET", 3.40),
        ("RAMKA 2 TALI", 0.90),
        ("RAMKA 3 TALI", 1.30),
        ("RAMKA 4 TALI", 1.80),
        ("RAMKA 5 TALI", 2.30),
    ]
    premium_white = [
        ("VIKLYUCHATEL 1 TALI", 1.10), ("VIKLYUCHATEL 2 TALI", 1.35),
        ("VIKLYUCHATEL 3 TALI", 1.55), ("ZVANOK", 1.55),
        ("VIKLYUCHATEL O'TUVCHI 1 TALI", 1.20), ("VIKLYUCHATEL O'TUVCHI 2 TALI", 1.55),
        ("PEREKLYUCHATEL 1 TALI", 1.70), ("ROZETKA 1 TALI", 1.10),
        ("ROZETKA 1 TALI ZAZEMLENIYALI", 1.20), ("ROZETKA 2 TALI", 2.10),
        ("ROZETKA 2 TALI ZAZEMLENIYALI", 2.50), ("TV", 1.45), ("TELEFON", 1.60),
        ("INTERNET", 1.50), ("USB TYPE-C", 8.00), ("DIMMER", 4.00),
        ("INTERNET 2 TALI", 3.00), ("ROZETKA 1 TALI ZAZEMLENIYALI QOPQOQLI", 1.95),
        ("TV + INTERNET", 3.00), ("RAMKA 2 TALI", 0.70), ("RAMKA 3 TALI", 1.10),
        ("RAMKA 4 TALI", 1.60), ("RAMKA 5 TALI", 2.00),
    ]
    premium = {
        "BLACK": list(premium_base),
        "SILVER": list(premium_base),
        "PLATINUM": list(premium_base),
        "WHITE": premium_white,
        "GOLD": list(premium_base),
    }
    dusel["PREMIUM SERIYA"] = premium

    # ---------------- RICH SERIYA ----------------
    rich_white = [
        ("VIKLYUCHATEL 1 TALI", .80), ("VIKLYUCHATEL 2 TALI", .90),
        ("VIKLYUCHATEL 3 TALI", 1.20), ("VIKLYUCHATEL INDIKATOR 1 TALI", 1.00),
        ("VIKLYUCHATEL INDIKATOR 2 TALI", 1.10), ("ZVANOK", 1.00),
        ("VIKLYUCHATEL REVERS 1 TALI", 1.00), ("VIKLYUCHATEL REVERS 2 TALI", 1.30),
        ("ROZETKA 1 TALI", .80), ("ROZETKA 2 TALI", 1.10),
        ("ROZETKA 1 TALI ZAZEMLENIYALI", .95), ("ROZETKA 2 TALI ZAZEMLENIYALI", 1.30),
        ("ROZETKA USB", 4.00), ("TV", 1.20), ("TELEFON", 1.20),
        ("INTERNET", 1.50), ("INTERNET + TELEFON", 2.50), ("TV + INTERNET", 2.40),
        ("INTERNET + INTERNET", 2.40), ("TELEFON + TELEFON", 2.00),
        ("USB", 2.70), ("USB 2 TALI", 3.50), ("PERMUTATOR", 1.70),
        ("RAMKA 2 TALI", .50), ("RAMKA 3 TALI", .70), ("RAMKA 4 TALI", .90), ("RAMKA 5 TALI", 1.15),
    ]
    rich_color = {c: [
        ("ROZETKA 1 TALI", .80), ("ROZETKA 2 TALI", 1.10),
        ("ROZETKA 1 TALI ZAZEMLENIYALI", .95), ("ROZETKA 2 TALI ZAZEMLENIYALI", 1.30),
        ("ROZETKA USB", 4.00),
    ] for c in ("BLACK", "COFFEE", "SILVER", "PLATINUM")}
    acrylic = {
        "COFFEE+GOLD": [("RAMKA 1",1.00),("RAMKA 2 + 1 TALI ROZETKA",1.30),("RAMKA 2",1.80),("RAMKA 3",2.80),("RAMKA 4",4.00),("RAMKA 5",5.70)],
        "BLACK+GOLD": [("RAMKA 1",1.00),("RAMKA 2 + 1 TALI ROZETKA",1.30),("RAMKA 2",1.80),("RAMKA 3",2.80),("RAMKA 4",4.00),("RAMKA 5",5.70)],
        "WHITE+GOLD": [("RAMKA 1",1.00),("RAMKA 2 + 1 TALI ROZETKA",1.30),("RAMKA 2",1.80),("RAMKA 3",2.80),("RAMKA 4",4.00),("RAMKA 5",5.70)],
        "SILVER+NICKEL": [("RAMKA 1",1.00),("RAMKA 2 + 1 TALI ROZETKA",1.30),("RAMKA 2",1.80),("RAMKA 3",2.80),("RAMKA 4",4.00),("RAMKA 5",5.70)],
    }

    # Make RICH a real group with three child sections.
    for key in [k for k in list(dusel) if str(k).startswith("RICH SERIYA /")]:
        dusel.pop(key, None)
    dusel["RICH SERIYA / RICH OQ"] = rich_white
    dusel["RICH SERIYA / RICH RANGLI"] = rich_color
    dusel["RICH SERIYA / AKRIL RAMKALAR"] = acrylic

    # Rebuild only Rich grouping rows in DB.
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM section_groups WHERE brand=? AND (group_name LIKE 'RICH SERIYA%' OR child_section LIKE 'RICH SERIYA%')", ("DUSEL",))
    for child in ("RICH SERIYA / RICH OQ", "RICH SERIYA / RICH RANGLI", "RICH SERIYA / AKRIL RAMKALAR"):
        cur.execute("INSERT OR IGNORE INTO dynamic_sections(brand,section) VALUES(?,?)", ("DUSEL", child))
        cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", child))
        if isinstance(dusel[child], list):
            for product, price in dusel[child]:
                cur.execute("INSERT OR IGNORE INTO dynamic_products(brand,section,product,price) VALUES(?,?,?,?)", ("DUSEL", child, product, float(price)))
        else:
            # Keep nested color catalog in PRODUCTS; DB rows are not needed for the UI.
            pass
        cur.execute("INSERT OR IGNORE INTO section_groups(brand,group_name,child_section) VALUES(?,?,?)", ("DUSEL", "RICH SERIYA", child))
    conn.commit(); conn.close()

    # ---------------- SALID labels ----------------
    # Keep model hierarchy but show short, exact model names.
    if isinstance(salid.get("ROZETKALAR"), dict):
        renamed = {}
        for old, value in salid["ROZETKALAR"].items():
            if old == "SALID DELUXE": new = "DELUXE"
            elif old == "SALID ULTRA": new = "ULTRA"
            elif old == "SALID SMART HOME": new = "SMART HOME"
            else: new = old
            renamed[new] = value
        salid["ROZETKALAR"] = renamed

    # Smart Home: human-readable product names, grouped by color.
    smart = salid.get("ROZETKALAR", {}).get("SMART HOME") if isinstance(salid.get("ROZETKALAR"), dict) else None
    if isinstance(smart, dict):
        name_map = {
            "SH07-1": "VIKLYUCHATEL 1 TALI", "SH07-2": "VIKLYUCHATEL 2 TALI", "SH07-3": "VIKLYUCHATEL 3 TALI", "SH07-4": "VIKLYUCHATEL 4 TALI",
            "SH07-1 RV": "VIKLYUCHATEL REVERS 1 TALI", "SH07-2 RV": "VIKLYUCHATEL REVERS 2 TALI",
            "SH07-1D": "DIMMER", "SH07-1ZV": "ZVANOK",
            "SH07-1 WF": "WI-FI VIKLYUCHATEL 1 TALI", "SH07-2 WF": "WI-FI VIKLYUCHATEL 2 TALI", "SH07-3 WF": "WI-FI VIKLYUCHATEL 3 TALI", "SH07-4 WF": "WI-FI VIKLYUCHATEL 4 TALI",
            "SH06 EL": "ELEKTRON TERMOSTAT SENSOR", "SH06 WAT": "SUV SENSORI",
            "SH05": "ROZETKA 1 TALI", "SH05 WF": "WI-FI ROZETKA 1 TALI", "SH05 WF-PM": "WI-FI ROZETKA + SENSOR", "SH05 IP": "ROZETKA QOPQOQLI",
            "SH05 USB": "USB TYPE-C ROZETKA", "SH05-2": "ROZETKA 2 TALI", "SH05 UN": "ROZETKA 1 TALI ZAZEMLENIYALI", "SH05 WF-UN": "WI-FI ROZETKA ZAZEMLENIYALI",
            "SH05 TEL 1/2": "TELEFON 1/2", "SH05 INT 1/2": "INTERNET 1/2", "SH05 TV 1/2": "TV 1/2", "SH05 1/2": "ROZETKA 1/2",
            "SH01 1/2": "VIKLYUCHATEL 1/2", "SH01 MW": "VIKLYUCHATEL 1 TALI PERMUTATOR", "SH01": "VIKLYUCHATEL 1 TALI", "SH01 REV": "VIKLYUCHATEL 1 TALI REVERS",
            "SH02": "VIKLYUCHATEL 2 TALI", "SH02 REV": "VIKLYUCHATEL 2 TALI REVERS", "SH03": "ZVANOK", "SH01 ZV": "ZVANOK",
            "SH11 1W": "1W YORITGICH", "SH12 BS": "SMART SENSOR BODY",
            "SH09-1+1": "SENSOR KORPUS 1+1", "SH09-2+1": "SENSOR KORPUS 2+1", "SH09-2+2": "SENSOR KORPUS 2+2", "SH09-2+3": "SENSOR KORPUS 2+3", "SH09-2x3": "SENSOR KORPUS 2X3",
            "SH08-1R": "RAMKA 1 TALI", "SH08-2R": "RAMKA 2 TALI", "SH08-3R": "RAMKA 3 TALI", "SH08-4R": "RAMKA 4 TALI", "SH08-5R": "RAMKA 5 TALI",
            "SH09-1+1R": "SENSOR 1+1 + RAMKA", "SH09-2+1R": "SENSOR 2+1 + RAMKA", "SH09-3+1R": "SENSOR 3+1 + RAMKA",
            "SH09-1+2R": "SENSOR 1+2 + RAMKA", "SH09-2+2R": "SENSOR 2+2 + RAMKA", "SH09-3+2R": "SENSOR 3+2 + RAMKA",
            "SH09-1+2+2R": "SENSOR 1+2+2 + RAMKA", "SH09-2+2+2R": "SENSOR 2+2+2 + RAMKA",
        }
        for color, rows in list(smart.items()):
            out=[]
            for product, price in rows:
                raw=str(product)
                base=raw
                # Remove trailing color from the source string.
                for c in (" White"," Black"," Golden"," Gold"," Gray"," Grey"):
                    if base.endswith(c):
                        base=base[:-len(c)]
                        break
                label=name_map.get(base, base)
                out.append((label, price))
            smart[color]=out

    # Final load keeps dynamic additions/price overrides available.
    load_dynamic_products()

    # Eski yassi Rich yozuvi dinamik bazadan qayta kelgan bo‘lsa ham
    # yakuniy katalogda ko‘rinmasin. Yangi Rich faqat ichki bo‘limlar orqali ochiladi.
    PRODUCTS.get("DUSEL", {}).pop("RICH SERIYA", None)
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", "RICH SERIYA"))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("DUSEL", "RICH SERIYA"))
    conn.commit(); conn.close()


def run():
    if not BOT_TOKEN or BOT_TOKEN == "BU_YERGA_YANGI_TOKENNI_QOYING":
        print("=" * 50)
        print("DIQQAT!")
        print("BOT_TOKEN ichiga BotFather bergan yangi tokenni yozing.")
        print("=" * 50)
        return

    init_db()
    apply_latest_pdf_catalogs()
    split_dusel_led_catalog()
    split_veral_lamp_colors()
    seed_salid_pdf_catalogs()
    seed_salid_rozetkalar_catalog()
    seed_catalog_fixes()
    finalize_catalog_hierarchy()
    load_dynamic_products()

    # Render Web Service port tekshiruvini o'tkazishi uchun HTTP serverni
    # alohida thread'da ishga tushiramiz. Telegram polling davom etadi.
    threading.Thread(target=start_render_server, daemon=True).start()

    print("DUSEL 12-DOKON BOT ISHGA TUSHDI.")
    print("Admin ID:", ADMIN_ID)
    print("WEBAPP_URL:", WEBAPP_URL or "TOPILMADI — Render External URL mavjudligini tekshiring")

    # Bir nechta instance ishlaganda eski update'larni tozalash
    first = api("getUpdates", {
        "offset": "-1",
        "timeout": "1",
        "allowed_updates": json.dumps(
            ["message", "callback_query"]
        )
    })

    offset = None

    if first and first.get("ok"):
        updates = first.get("result", [])

        if updates:
            offset = updates[-1]["update_id"] + 1

    while True:
        try:
            data = {
                "timeout": "50",
                "allowed_updates": json.dumps(
                    ["message", "callback_query"]
                )
            }

            if offset is not None:
                data["offset"] = str(offset)

            result = api(
                "getUpdates",
                data,
                attempts=3
            )

            if not result or not result.get("ok"):
                print("Telegram bilan aloqa uzildi. 5 soniyadan keyin qayta uriniladi...")
                time.sleep(5)
                continue

            updates = result.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                process_update(update)

        except KeyboardInterrupt:
            print("Bot to‘xtatildi.")
            break

        except Exception:
            print("RUN XATOSI:")
            traceback.print_exc()
            print("10 soniyadan keyin qayta ishga tushadi...")
            time.sleep(10)


if __name__ == "__main__":
    # Render saytini bot bilan bir jarayonda ishga tushiramiz.
    # Aks holda /index.html faqat fayl bo‘lib qoladi va Telegram Web App ochilmaydi.
    try:
        _web_thread = threading.Thread(target=start_render_server, daemon=True)
        _web_thread.start()
        time.sleep(0.5)
        print("WEBAPP_URL =", WEBAPP_URL or "BELGILANMAGAN")
    except Exception:
        print("WEB SERVER XATOSI:")
        traceback.print_exc()
    run()

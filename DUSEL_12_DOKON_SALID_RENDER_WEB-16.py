import urllib.request
import urllib.parse
import json
import time
import sqlite3
import traceback
import os
import re
import zipfile
import tempfile
import html
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# ============================================================
# DUSEL 12-DOKON - TELEGRAM BOT
# Standart Python kutubxonalari: urllib, json, time, sqlite3
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = 6033308194

DB_FILE = "dusel_shop.db"
API_URL = "https://api.telegram.org/bot" + BOT_TOKEN + "/"

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
    return rows


def show_admin_contacts(chat_id):
    if chat_id != ADMIN_ID:
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
    telegram = c.get("telegram", "Kiritilmagan")
    phone = c.get("phone", "Kiritilmagan")
    text = ("📞 <b>ADMIN BILAN BOG‘LANISH</b>\n\n"
            "💬 Telegram: <b>" + telegram + "</b>\n"
            "📱 Telefon: <b>" + phone + "</b>")
    send_message(chat_id, text, main_menu())

def show_brand_manage(chat_id):
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID: return
    send_message(chat_id, "🏷 <b>" + brand + "</b>\n\nAmalni tanlang:", keyboard([
        ("✏️ Nomini o‘zgartirish", "brandrename|" + brand),
        ("🗑 O‘chirish", "branddelete|" + brand),
        ("📂 Bo‘limlarni boshqarish", "sectionmanage|" + brand),
        ("⬅️ Brendlar", "brand_manage")
    ]))


def show_section_manage(chat_id, brand):
    if chat_id != ADMIN_ID: return
    sections=[]
    conn=get_db(); cur=conn.cursor()
    cur.execute("SELECT section FROM dynamic_sections WHERE brand=? ORDER BY id ASC", (brand,))
    sections=[r[0] for r in cur.fetchall()]; conn.close()
    buttons=[("📂 " + sec, "sectionaction|" + brand + "|" + sec) for sec in sections]
    buttons.append(("⬅️ Brend", "brandmanage|" + brand))
    send_message(chat_id, "📂 <b>" + brand + " BO‘LIMLARI</b>\n\nBo‘limni tanlang:", keyboard(buttons))


def show_section_actions(chat_id, brand, section):
    if chat_id != ADMIN_ID: return
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
    return {
        "keyboard": [
            [{"text": "👥 Mijozlar"}, {"text": "📦 Buyurtmalar"}],
            [{"text": "📋 Spiskalar"}, {"text": "🎁 Chegirmalar"}],
            [{"text": "📢 Xabar yuborish"}, {"text": "🛍 Mahsulotlar"}],
            [{"text": "➕ Mahsulot qo‘shish"}, {"text": "➕ Bo‘lim qo‘shish"}],
            [{"text": "➕ Brend qo‘shish"}, {"text": "📍 Dokon lokatsiyasi", "request_location": True}],
            [{"text": "🛠 Brend/bo‘lim boshqaruvi"}, {"text": "💵 Price boshqaruvi"}],
            [{"text": "📞 Admin bilan bog‘lanish"}],
            [{"text": "🖼 Rasmlar"}, {"text": "📊 Excel"}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }


def user_reply_keyboard():
    return {
        "keyboard": [
            [{"text": "🛍 Mahsulotlar"}, {"text": "🛒 Savat"}],
            [{"text": "⚙️ Sozlamalar"}],
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


def delete_catalog_image(image_key, slot):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM catalog_image_slots WHERE image_key=? AND slot=?", (image_key, int(slot)))
    conn.commit()
    conn.close()


def image_key(brand, section, color=None):
    return "|".join([brand, section] + ([color] if color else []))


def show_admin_brand_add(chat_id):
    if chat_id != ADMIN_ID:
        return
    set_state(chat_id, "admin_brand_name", {})
    send_message(chat_id, "➕ <b>YANGI BREND QO‘SHISH</b>\n\nBrend nomini yozing.\nMasalan: <code>NEW BRAND</code>\n\nBekor qilish: /cancel")


def show_admin_section_add(chat_id):
    if chat_id != ADMIN_ID:
        return
    buttons = [("🏷 " + brand, "addsecbrand|" + brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "➕ <b>BREND ICHIGA BO‘LIM QO‘SHISH</b>\n\nAvval brendni tanlang:", keyboard(buttons))


def start_section_add(chat_id, brand):
    if chat_id != ADMIN_ID:
        return
    set_state(chat_id, "admin_section_name", {"brand": brand})
    send_message(chat_id, "🏷 Brend: <b>" + brand + "</b>\n\n📂 Yangi bo‘lim nomini yozing.\nMasalan: <code>ROZETKALAR</code>\n\nBekor qilish: /cancel")


def show_admin_location(chat_id):
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
        return
    buttons=[("🏷 "+brand,"pricebrand|"+brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel","admin_home"))
    send_message(chat_id,"💵 <b>PRICE BOSHQARUVI</b>\n\nBrendni tanlang:",keyboard(buttons))


def show_admin_price_sections(chat_id, brand):
    if chat_id != ADMIN_ID: return
    buttons=[("📂 "+sec,"pricesec|"+brand+"|"+sec) for sec in PRODUCTS.get(brand,{})]
    buttons.append(("⬅️ Brendlar","admin_prices"))
    send_message(chat_id,"💵 <b>"+brand+"</b>\n\nBo‘limni tanlang:",keyboard(buttons))


def show_admin_price_products(chat_id, brand, section):
    if chat_id != ADMIN_ID: return
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
    if chat_id != ADMIN_ID: return
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


def show_admin_product_add(chat_id):
    if chat_id != ADMIN_ID:
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    buttons = [("🏷 " + brand, "prodaddbrand|" + brand) for brand in PRODUCTS]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "➕ <b>MAHSULOT QO‘SHISH</b>\n\nAvval brendni tanlang:", keyboard(buttons))


def start_product_add(chat_id, brand):
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return
    buttons = [("🖼 " + brand, "imgbrand|" + brand) for brand in PRODUCTS if PRODUCTS.get(brand)]
    buttons.append(("⬅️ Admin panel", "admin_home"))
    send_message(chat_id, "🖼 <b>KATALOG RASMLARI</b>\n\nRasm qo‘shiladigan brendni tanlang:", keyboard(buttons))


def show_admin_image_sections(chat_id, brand):
    if chat_id != ADMIN_ID:
        return
    sections = PRODUCTS.get(brand, {})
    buttons = [("📂 " + section, "imgsec|" + brand + "|" + section) for section in sections]
    buttons.append(("⬅️ Brendlar", "admin_images"))
    send_message(chat_id, "🖼 <b>" + brand + "</b>\n\nBo‘limni tanlang:", keyboard(buttons))


def start_image_upload(chat_id, brand, section, color=None, slot=1):
    key = image_key(brand, section, color)
    set_state(chat_id, "admin_image", {"key": key, "brand": brand, "section": section, "color": color or "", "slot": int(slot)})
    target = section + (" → " + color if color else "")
    send_message(chat_id, "📸 <b>Rasm " + str(slot) + "/3</b>\n\n" + target + " uchun rasm yuboring.\n\nBekor qilish: /cancel")


def show_admin_image_colors(chat_id, brand, section):
    colors = list(PRODUCTS.get(brand, {}).get(section, {}).keys())
    buttons = []
    for color in colors:
        exists = "✅" if get_catalog_images(image_key(brand, section, color)) else "➕"
        buttons.append((exists + " " + color, "imgcolor|" + brand + "|" + section + "|" + color))
    buttons.append(("⬅️ Bo‘limlar", "imgbrand|" + brand))
    send_message(chat_id, "🎨 <b>SALID ranglari</b>\n\nRasm qo‘shish yoki almashtirish uchun rangni tanlang:", keyboard(buttons))


def show_admin_image_actions(chat_id, brand, section):
    if isinstance(PRODUCTS.get(brand, {}).get(section), dict):
        show_admin_image_colors(chat_id, brand, section)
        return
    key = image_key(brand, section)
    imgs = get_catalog_images(key)
    buttons = []
    for slot in range(1, 4):
        mark = "✅" if get_catalog_image(key, slot) else "➕"
        buttons.append((mark + " Rasm " + str(slot), "imgupload|" + brand + "|" + section + "|" + str(slot)))
    buttons.append(("⬅️ Bo‘limlar", "imgbrand|" + brand))
    send_message(chat_id, "🖼 <b>" + brand + " — " + section + "</b>\n\n📸 3 tagacha rasm biriktirish mumkin.\nHozirgi rasmlar: <b>" + str(len(imgs)) + "/3</b>", keyboard(buttons))


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
    return keyboard([
        ("🛍 Mahsulotlar", "brands"),
        ("🛒 Savat", "cart"),
        ("⚙️ Sozlamalar", "settings"),
        ("📍 12-DOKON lokatsiyasi", "location"),
        ("📩 Takliflar", "suggestion")
    ])


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
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
        return
    send_message(chat_id, "📢 <b>XABAR YUBORISH</b>\n\nKimga yuborishni tanlang:", keyboard([
        ("📢 Barcha klientlarga", "msgall"),
        ("👤 Bitta klientga", "msgpick"),
        ("⬅️ Admin panel", "admin_home")
    ]))

def start_broadcast(chat_id, target_id=None):
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID: return send_message(chat_id,"❌ Sizda admin huquqi yo‘q.")
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
    if chat_id != ADMIN_ID:
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
    if chat_id != ADMIN_ID:
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


# ============================================================
# MENUS
# ============================================================

def show_brands(chat_id):
    buttons = []

    for brand, sections in PRODUCTS.items():
        if sections:
            buttons.append(
                (brand, "brand|" + brand)
            )
        else:
            buttons.append(
                (brand + " — hozircha yo‘q", "empty")
            )

    buttons.append(("🛒 Savat", "cart"))

    send_message(
        chat_id,
        "🏷 <b>Brendni tanlang:</b>",
        keyboard(buttons)
    )


def show_sections(chat_id, brand):
    sections = PRODUCTS.get(brand, {})

    if not sections:
        send_message(
            chat_id,
            "ℹ️ Bu brendda hozircha mahsulot yo‘q."
        )
        return

    buttons = []

    for section in sections:
        buttons.append(
            (section, "section|" + brand + "|" + section)
        )

    buttons.append(("⬅️ Brendlar", "brands"))

    send_message(
        chat_id,
        "🏷 <b>" + brand + "</b>\n\n"
        "📂 <b>Bo‘limni tanlang:</b>",
        keyboard(buttons)
    )


def send_catalog_photo_if_exists(chat_id, brand, section, color=None):
    fids = get_catalog_images(image_key(brand, section, color))
    if fids:
        caption = "🛍 <b>" + brand + "</b>\n📂 <b>" + section + "</b>"
        if color:
            caption += "\n🎨 <b>" + color + "</b>"
        if len(fids) == 1:
            send_photo(chat_id, fids[0], caption)
        else:
            send_media_group(chat_id, fids, caption)


def show_products(chat_id, brand, section):
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
    buttons.append(("⬅️ Bo‘limlar", "brand|" + brand))
    send_message(chat_id, "📦 <b>" + brand + "</b>\n📂 <b>" + section + "</b>\n\nMahsulotni tanlang:", keyboard(buttons))


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

def select_product(chat_id, brand, section, index):
    try:
        index = int(index)
        product, price = PRODUCTS[brand][section][index]
    except Exception:
        send_message(chat_id, "❌ Mahsulot topilmadi.")
        return

    set_state(chat_id, "quantity", {
        "brand": brand,
        "section": section,
        "product": product,
        "price": price
    })

    send_message(
        chat_id,
        "📦 <b>" + product + "</b>\n"
        "💵 Narxi: <b>$" + format(price) + "</b>\n\n"
        "🔢 Nechta dona kerak?\n"
        "Masalan: <b>10</b>"
    )


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

    if step == "admin_contact_edit" and chat_id == ADMIN_ID:
        key=(data or {}).get("key","")
        if key not in ("telegram","email","phone"):
            clear_state(chat_id); return
        value=text.strip()
        if len(value)<3:
            send_message(chat_id,"❌ Qiymat juda qisqa. Qaytadan yozing:"); return
        set_admin_contact(key,value); clear_state(chat_id)
        send_reply_message(chat_id,"✅ " + key + " saqlandi.",admin_reply_keyboard()); return

    if step == "admin_brand_rename" and chat_id == ADMIN_ID:
        old=(data or {}).get("old",""); new=text.strip()
        if len(new)<2: send_message(chat_id,"❌ Nom juda qisqa."); return
        conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE dynamic_brands SET brand=? WHERE brand=?",(new,old)); cur.execute("UPDATE dynamic_sections SET brand=? WHERE brand=?",(new,old)); cur.execute("UPDATE dynamic_products SET brand=? WHERE brand=?",(new,old)); conn.commit(); conn.close()
        load_dynamic_products(); clear_state(chat_id); send_reply_message(chat_id,"✅ Brend nomi o‘zgartirildi: " + new,admin_reply_keyboard()); return

    if step == "admin_section_rename" and chat_id == ADMIN_ID:
        brand=(data or {}).get("brand",""); old=(data or {}).get("old",""); new=text.strip()
        if len(new)<2: send_message(chat_id,"❌ Nom juda qisqa."); return
        conn=get_db(); cur=conn.cursor(); cur.execute("UPDATE dynamic_sections SET section=? WHERE brand=? AND section=?",(new,brand,old)); cur.execute("UPDATE dynamic_products SET section=? WHERE brand=? AND section=?",(new,brand,old)); conn.commit(); conn.close()
        load_dynamic_products(); clear_state(chat_id); send_reply_message(chat_id,"✅ Bo‘lim nomi o‘zgartirildi: " + new,admin_reply_keyboard()); return

    if step == "admin_brand_name" and chat_id == ADMIN_ID:
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

    if step == "admin_section_name" and chat_id == ADMIN_ID:
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

    if step == "admin_product_section" and chat_id == ADMIN_ID:
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

    if step == "admin_product_name" and chat_id == ADMIN_ID:
        product = text.strip()
        if len(product) < 2:
            send_message(chat_id, "❌ Mahsulot nomi juda qisqa. Qaytadan yozing:")
            return
        set_state(chat_id, "admin_product_price", {"brand": data.get("brand", ""), "section": data.get("section", ""), "product": product})
        send_message(chat_id, "💵 <b>Mahsulot narxini yozing.</b>\nMasalan: <code>2.50</code>")
        return

    if step == "admin_product_price" and chat_id == ADMIN_ID:
        try:
            price = float(text.strip().replace(",", "."))
        except Exception:
            send_message(chat_id, "❌ Narx noto‘g‘ri. Masalan: <code>2.50</code>")
            return
        if price < 0:
            send_message(chat_id, "❌ Narx manfiy bo‘lmasin.")
            return
        brand = data.get("brand", "")
        section = data.get("section", "")
        product = data.get("product", "")
        inserted = save_dynamic_product(brand, section, product, price)
        load_dynamic_products()
        clear_state(chat_id)
        if inserted:
            send_reply_message(chat_id, "✅ <b>Mahsulot qo‘shildi!</b>\n\n🏷 Brend: <b>" + brand + "</b>\n📂 Bo‘lim: <b>" + section + "</b>\n📦 Mahsulot: <b>" + product + "</b>\n💵 Narx: <b>$" + format(price) + "</b>", admin_reply_keyboard())
        else:
            send_reply_message(chat_id, "⚠️ Bu mahsulot shu bo‘limda allaqachon mavjud.", admin_reply_keyboard())
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

    if step == "admin_price_update" and chat_id == ADMIN_ID:
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

    if step == "admin_broadcast_all" and chat_id == ADMIN_ID:
        message_text = text.strip()
        if not message_text:
            send_message(chat_id, "❌ Xabar bo‘sh bo‘lmasin.")
            return
        ok, total = send_broadcast_all(message_text)
        clear_state(chat_id)
        send_reply_message(chat_id, f"✅ Xabar yuborildi.\n\n📨 Yetkazildi: <b>{ok}</b> / <b>{total}</b> klient", admin_reply_keyboard())
        return

    if step == "admin_broadcast_one" and chat_id == ADMIN_ID:
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

    if step == "admin_pick_client" and chat_id == ADMIN_ID:
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
            if chat_id == ADMIN_ID:
                show_daily_orders(chat_id, data.split("|",1)[1])
            return

        if data.startswith("clientorders|"):
            if chat_id == ADMIN_ID:
                show_client_orders(chat_id, int(data.split("|",1)[1]))
            return

        if data == "admin_broadcast":
            show_admin_broadcast(chat_id)
            return

        if data == "msgall":
            start_broadcast(chat_id)
            return

        if data == "msgpick":
            if chat_id == ADMIN_ID:
                rows = get_clients()
                buttons = [("👤 " + name, "msgclient|" + str(cid)) for cid,name,phone in rows]
                buttons.append(("⬅️ Xabar menyusi", "admin_broadcast"))
                send_message(chat_id, "👤 <b>Klientni tanlang:</b>", keyboard(buttons))
            return

        if data.startswith("msgclient|"):
            if chat_id == ADMIN_ID:
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
            if len(parts) == 2 and chat_id == ADMIN_ID:
                start_section_add(chat_id, parts[1])
            return

        if data == "admin_prices":
            if chat_id == ADMIN_ID: show_admin_price_brands(chat_id)
            return
        if data.startswith("pricebrand|") and chat_id == ADMIN_ID:
            show_admin_price_sections(chat_id,data.split("|",1)[1]); return
        if data.startswith("pricesec|") and chat_id == ADMIN_ID:
            parts=data.split("|",2)
            if len(parts)==3: show_admin_price_products(chat_id,parts[1],parts[2])
            return
        if data.startswith("priceedit|") and chat_id == ADMIN_ID:
            parts=data.split("|")
            try:
                if len(parts)==4:
                    show_admin_price_actions(chat_id,parts[1],parts[2],int(parts[3]))
                elif len(parts)==5:
                    show_admin_price_actions(chat_id,parts[1],parts[2],int(parts[4]),parts[3])
            except Exception: pass
            return
        if data.startswith("priceupdate|") and chat_id == ADMIN_ID:
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
        if data.startswith("pricedelete|") and chat_id == ADMIN_ID:
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
        if data.startswith("sectionaction|"):
            parts=data.split("|",2)
            if len(parts)==3: show_section_actions(chat_id, parts[1], parts[2])
            return
        if data.startswith("branddelete|") and chat_id == ADMIN_ID:
            brand=data.split("|",1)[1]
            conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM dynamic_products WHERE brand=?",(brand,)); cur.execute("DELETE FROM dynamic_sections WHERE brand=?",(brand,)); cur.execute("DELETE FROM dynamic_brands WHERE brand=?",(brand,)); conn.commit(); conn.close()
            PRODUCTS.pop(brand, None); load_dynamic_products()
            send_reply_message(chat_id, "🗑 <b>Brend o‘chirildi:</b> " + brand, admin_reply_keyboard()); return
        if data.startswith("brandrename|") and chat_id == ADMIN_ID:
            brand=data.split("|",1)[1]; set_state(chat_id,"admin_brand_rename",{"old":brand}); send_message(chat_id,"✏️ Yangi brend nomini yozing:\n\nBekor qilish: /cancel"); return
        if data.startswith("sectiondelete|") and chat_id == ADMIN_ID:
            parts=data.split("|",2); brand,section=parts[1],parts[2]
            conn=get_db(); cur=conn.cursor(); cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?",(brand,section)); cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?",(brand,section)); conn.commit(); conn.close(); load_dynamic_products()
            send_reply_message(chat_id,"🗑 <b>Bo‘lim o‘chirildi:</b> " + section, admin_reply_keyboard()); return
        if data.startswith("sectionrename|") and chat_id == ADMIN_ID:
            parts=data.split("|",2); set_state(chat_id,"admin_section_rename",{"brand":parts[1],"old":parts[2]}); send_message(chat_id,"✏️ Yangi bo‘lim nomini yozing:"); return
        if data.startswith("contact_edit|") and chat_id == ADMIN_ID:
            key=data.split("|",1)[1]; set_state(chat_id,"admin_contact_edit",{"key":key}); send_message(chat_id,"✏️ Yangi " + key + "ni yozing:"); return
        if data == "admin_contacts":
            show_admin_contacts(chat_id); return
        if data == "admin_location":
            show_admin_location(chat_id)
            return

        if data.startswith("prodaddbrand|"):
            parts = data.split("|", 1)
            if len(parts) == 2 and chat_id == ADMIN_ID:
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

        if data.startswith("imgcolor|"):
            parts = data.split("|", 3)
            if len(parts) == 4:
                # Rangli SALID bo‘limlari uchun ham 1-3 slot tanlanadi.
                key = image_key(parts[1], parts[2], parts[3])
                buttons = [("Rasm " + str(slot), "imgupload|" + parts[1] + "|" + parts[2] + "|" + parts[3] + "|" + str(slot)) for slot in range(1,4)]
                buttons.append(("⬅️ Ranglar", "imgsec|" + parts[1] + "|" + parts[2]))
                send_message(chat_id, "📸 <b>" + parts[3] + "</b> — 3 tagacha rasm", keyboard(buttons))
            return

        if data.startswith("imgupload|"):
            parts = data.split("|")
            if len(parts) == 4:
                start_image_upload(chat_id, parts[1], parts[2], slot=int(parts[3]))
            elif len(parts) == 5:
                start_image_upload(chat_id, parts[1], parts[2], parts[3], int(parts[4]))
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
            if chat_id != ADMIN_ID:
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
                show_sections(chat_id, parts[1])
            return

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
                    index = int(parts[4])
                    product, price = PRODUCTS[parts[1]][parts[2]][parts[3]][index]
                    set_state(chat_id, "quantity", {"brand": parts[1], "section": parts[2], "product": product + " (" + parts[3] + ")", "price": price})
                    send_message(chat_id, "📦 <b>" + product + " — " + parts[3] + "</b>\n💵 Narxi: <b>$" + format(price) + "</b>\n\n🔢 Nechta dona kerak?\nMasalan: <b>10</b>")
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
                # Admin do‘kon lokatsiyasini Telegram Location orqali yuborsa, saqlaymiz.
                if chat_id == ADMIN_ID and message.get("location"):
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
                if chat_id == ADMIN_ID and message.get("photo"):
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
                if chat_id == ADMIN_ID and (message.get("photo") or message.get("document")):
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
                    if chat_id == ADMIN_ID:
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

                    if chat_id == ADMIN_ID:
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
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_clients(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📋 Spiskalar":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_lists(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📢 Xabar yuborish":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_broadcast(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📦 Buyurtmalar":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_orders(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🎁 Chegirmalar":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_discounts(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "⚙️ Sozlamalar":
                    clear_state(chat_id)
                    show_settings(chat_id)
                elif text == "➕ Mahsulot qo‘shish":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_product_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🖼 Rasmlar":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_images(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📊 Excel":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_excel(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📍 12-DOKON lokatsiyasi":
                    clear_state(chat_id)
                    send_message(chat_id, shop_location_message(chat_id), user_reply_keyboard())
                elif text == "➕ Brend qo‘shish":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_brand_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "➕ Bo‘lim qo‘shish":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_section_add(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📍 Dokon lokatsiyasi":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_location(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "💵 Price boshqaruvi":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id); show_admin_price_brands(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "🛠 Brend/bo‘lim boshqaruvi":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id); show_brand_manage(chat_id)
                    else: send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "📞 Admin bilan bog‘lanish":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id); show_admin_contacts(chat_id)
                    else:
                        clear_state(chat_id); show_user_contacts(chat_id)
                elif text == "📩 Takliflar":
                    start_suggestion(chat_id)
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
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"DUSEL 12-DOKON BOT OK")

    def log_message(self, format, *args):
        return


def start_render_server():
    # Render PORT environment variable beradi.
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), RenderHealthHandler)
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

    # Eski bitta "Rich" bo'limini olib tashlaymiz; yangi rang/type bo'limlari alohida.
    cur.execute("DELETE FROM dynamic_products WHERE brand=? AND section=?", ("DUSEL", "Rich"))
    cur.execute("DELETE FROM dynamic_sections WHERE brand=? AND section=?", ("DUSEL", "Rich"))
    cur.execute("DELETE FROM catalog_images WHERE image_key=?", ("DUSEL|Rich",))

    rich_common=[
      ("Rich VKL1",1.10),("Rich VKL2",1.25),("Rich VKL3",1.50),("Rich ROZ 1",1.10),("Rich ROZ 2",1.60),
      ("Rich ROZ ZAZM 1",1.25),("Rich ROZ ZAZM 2",1.90),("Rich TV",1.50),("Rich TEL",1.50),("Rich Internet",2.60),
      ("Rich TV Internet",2.60),("Rich USB 1",3.30),("Rich Premium Color",1.90),("Rich Revers 1",1.30),("Rich Revers 2",1.65),
      ("Ramka 2Talik",.8),("Ramka 3Talik",1.1),("Ramka 4Talik",1.6),("Ramka 5Talik",1.9)]
    rich_white=[("RICH VKL 1",.8),("RICH VKL 2",.9),("RICH VKL 3",1.2),("RICH VKL INDIGATIR 1",1),("RICH VKL INDICATOR 2",1.1),("RICH ZVANOK",1),("RICH RIVERS 1",1),("RICH RIVERS 2",1.3),("RICH ROZ 1",.8),("RICH ROZ 2",1.1),("RICH ROZ ZAZM 1",.95),("RICH ROZ ZAZM 2",1.3),("RICH ROZ USB",4),("RICH TV",1.2),("RICH TEL",1.2),("RICH INTERNET",1.5),("RICH INTERNET + TEL",2.5),("RICH TV + INTER",2.4),("RICH INTER + INTE",2.4),("RICH TEL + TEL",2),("RICH USB",2.7),("RICH USB2",3.5),("RICH PERMUTATOR",1.7),("RICH RAMKA 2",.5),("RICH RAMKA 3T",.7),("RICH RAMKA 4T",.9),("RICH RAMKA 5T",1.15),("RICH NAR VKL 1",.65),("RICH NAR VKL 2",.75),("RICH NAR ROZ 1",.65),("RICH NAR ROZ ZAZM 1",.8),("RICH NAR ROZ 2",.85),("RICH NAR ROZ ZAZM 2",1),("RICH NAR TEL",1),("RICH NAR TV",1),("RICH NAR INTERNER",1.2)]
    for c,rows in [("WHITE",rich_white),("BLACK",rich_common),("COFFEE",[("Rich VVKL1",1.1)]+rich_common[1:]),("SILVER",rich_common),("PLATINUM",rich_common)]: add_section("Rich / "+c,rows)
    acrylic=[("Ramka 1",1), ("Ramka 2 lik rozetka",1.3),("Ramka 2",1.8),("Ramka 3",2.8),("Ramka 4",4),("Ramka 5",5.7)]
    for c in ["COFFEE + GOLD","BLACK + GOLD","WHITE + GOLD","SILVER + NICKEL"]: add_section("Rich / AKRIL RAMKA — "+c,acrylic)

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
    for g,r in panel.items(): add_section("AKRIL LED PANEL / "+g,r)
    add_section("IP 44 VILKA, ROZETKA",[("Dul15",.7),("Dul16",.75),("Dul17",.7),("Dul18",.9),("Dul21",1.45),("Dul11",1.3),("Dul19",2.3),("Dul20",2.8),("Dul12",1.8),("Dul13",2.3),("Dul14",3.2),("Dul22",3)])
    add_section("IP54 ROZETKA VKLUCHATEL",[("VKL 2 ROZ 1Du128",2.6),("VKL 1 ROZ 1DU127",2.4),("ROZ 2 DU126",2.3),("ROZ 1 DU125",1.2),("VKL 2 DU124",1.4),("VKL 1 DU123",1.2)])
    add_section("DUSEL DATCHIK",[("DD-01",4),("DD-02",4.3),("DD-03",4),("DD-04 WHITE",4.1),("DD-04 BLACK",4.1),("DD-05",4.1),("DD-06",3.5),("FR-06",1.5),("FR-10",2),("FR-25",2.9),("Sensor panel uchun datchik",1.75)])
    add_section("KARTINKA YORITGICHI",[("ZS1-9W 40sm 6500K Gold",11)])
    add_section("TREK YORITGICH RELS",[("TS1 20W Black 6500K",2.4),("TS1 30W Black 6500K",3),("TS1 40W Black 6500K",4.4),("TS1 20W Black 4500K",2.4),("TS1 30W Black 4500K",3),("TS1 40W Black 4500K",4.4),("TS1 20W White 6500K",2.4),("TS1 30W White 6500K",3),("TS1 40W White 6500K",4.4),("TS1 20W White 4500K",2.4),("TS1 30W White 4500K",3),("TS1 40W White 4500K",4.4),("TS2 20W Black 6500K",3.3),("TS2 30W Black 6500K",4.5),("TS2 40W Black 6500K",7),("TS2 20W Black 4500K",3.3),("TS2 30W Black 4500K",4.5),("TS2 40W Black 4500K",7),("TS2 20W White 6500K",3.3),("TS2 30W White 6500K",4.5),("TS2 40W White 6500K",7),("TS2 20W White 4500K",3.3),("TS2 30W White 4500K",4.5),("TS2 40W White 4500K",7),("TS3 30W Black 6500K",5.8),("TS4-40 Black M",7),("TS4-30 White M",5.5),("TS4-40 Black T",7.5),("TS4-30 White T",6),("Rels 1M Black",1.3),("Rels 1.5M Black",1.9),("Rels 2M Black",2.6),("Rels 3M Black",3.9),("Rels 1M WHITE",1.3),("Rels 1.5M WHITE",1.9),("Rels 2M WHITE",2.6),("Rels 3M WHITE",3.9),("Soedinitel Black",.4),("Uglovoy soedinitel Black",.4),("Krugliy soedinitel Black",.7),("Avalniy soedinitel Black",.7),("T soedinitel Black",.8),("Soedinitel WHITE",.4),("Uglovoy soedinitel WHITE",.4),("Krugliy soedinitel WHITE",.7),("Avalniy soedinitel WHITE",.7),("T soedinitel WHITE",.8),("Plyus soedinitel",.9)])
    conn.commit(); conn.close(); load_dynamic_products()

# ============================================================
# BOTNI ISHGA TUSHIRISH
# ============================================================

def run():
    if BOT_TOKEN == "BU_YERGA_YANGI_TOKENNI_QOYING":
        print("=" * 50)
        print("DIQQAT!")
        print("BOT_TOKEN ichiga BotFather bergan yangi tokenni yozing.")
        print("=" * 50)
        return

    init_db()
    seed_salid_light_catalog()
    seed_catalog_fixes()
    load_dynamic_products()

    # Render Web Service port tekshiruvini o'tkazishi uchun HTTP serverni
    # alohida thread'da ishga tushiramiz. Telegram polling davom etadi.
    threading.Thread(target=start_render_server, daemon=True).start()

    print("DUSEL 12-DOKON BOT ISHGA TUSHDI.")
    print("Admin ID:", ADMIN_ID)

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
    run()

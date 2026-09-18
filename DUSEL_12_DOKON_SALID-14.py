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

# ============================================================
# DUSEL 12-DOKON - TELEGRAM BOT
# Standart Python kutubxonalari: urllib, json, time, sqlite3
# ============================================================

BOT_TOKEN = "BU_YERGA_YANGI_TOKENNI_QOYING"
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
            "Gold Shampanskiy": [
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
            [{"text": "🖼 Rasmlar"}, {"text": "👋 Salomlashish stikeri"}],
            [{"text": "📊 Excel"}]
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


def send_sticker(chat_id, file_id):
    return api("sendSticker", {
        "chat_id": str(chat_id),
        "sticker": str(file_id)
    })


def save_catalog_image(image_key, file_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO catalog_images(image_key,file_id,updated_at) VALUES(?,?,?)",
        (image_key, file_id, time.strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_catalog_image(image_key):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT file_id FROM catalog_images WHERE image_key=?", (image_key,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


def image_key(brand, section, color=None):
    return "|".join([brand, section] + ([color] if color else []))


def save_greeting_sticker(file_id):
    save_catalog_image("__GREETING_STICKER__", file_id)


def get_greeting_sticker():
    return get_catalog_image("__GREETING_STICKER__")


def show_admin_greeting_sticker(chat_id):
    if chat_id != ADMIN_ID:
        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
        return

    current = get_greeting_sticker()
    text = (
        "👋 <b>SALOMLASHISH STIKERI</b>\n\n"
        "Botga /start bosilganda mijozga shu stiker yuboriladi.\n\n"
        "📤 Yangi stiker yuboring.\n"
        "Yangi yuborsangiz, eski stiker avtomatik almashtiriladi.\n\n"
        "❌ Bekor qilish: /cancel"
    )
    if current:
        text += "\n\n✅ Hozir salomlashish stikeri o‘rnatilgan."
    else:
        text += "\n\nℹ️ Hozircha stiker o‘rnatilmagan."

    set_state(chat_id, "admin_greeting_sticker")
    send_reply_message(chat_id, text, admin_reply_keyboard())


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


def start_image_upload(chat_id, brand, section, color=None):
    key = image_key(brand, section, color)
    set_state(chat_id, "admin_image", {"key": key, "brand": brand, "section": section, "color": color or ""})
    target = section + (" → " + color if color else "")
    send_message(chat_id, "📸 <b>Rasm yuboring</b>\n\n" + target + " uchun Telegramda bitta rasm yuboring.\n\nBekor qilish: /cancel")


def show_admin_image_colors(chat_id, brand, section):
    colors = list(PRODUCTS.get(brand, {}).get(section, {}).keys())
    buttons = []
    for color in colors:
        exists = "✅" if get_catalog_image(image_key(brand, section, color)) else "➕"
        buttons.append((exists + " " + color, "imgcolor|" + brand + "|" + section + "|" + color))
    buttons.append(("⬅️ Bo‘limlar", "imgbrand|" + brand))
    send_message(chat_id, "🎨 <b>SALID ranglari</b>\n\nRasm qo‘shish yoki almashtirish uchun rangni tanlang:", keyboard(buttons))


def show_admin_image_actions(chat_id, brand, section):
    if isinstance(PRODUCTS.get(brand, {}).get(section), dict):
        show_admin_image_colors(chat_id, brand, section)
        return
    exists = "✅ Rasm mavjud" if get_catalog_image(image_key(brand, section)) else "➕ Rasm qo‘shish"
    buttons = [("📸 " + exists, "imgupload|" + brand + "|" + section), ("⬅️ Bo‘limlar", "imgbrand|" + brand)]
    send_message(chat_id, "🖼 <b>" + brand + " — " + section + "</b>", keyboard(buttons))


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
    send_message(chat_id, "✍️ <b>" + target_text + " yuboriladigan xabarni yozing:</b>\n\nBekor qilish: /cancel")

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
    fid = get_catalog_image(image_key(brand, section, color))
    if fid:
        caption = "🛍 <b>" + brand + "</b>\n📂 <b>" + section + "</b>"
        if color:
            caption += "\n🎨 <b>" + color + "</b>"
        send_photo(chat_id, fid, caption)


def show_products(chat_id, brand, section):
    items = PRODUCTS.get(brand, {}).get(section, [])

    # SALID rangli seriyasi: avval rang tanlanadi
    if isinstance(items, dict):
        buttons = []
        colors = list(items.keys())

        for color_index, color in enumerate(colors):
            emoji = {
                "White": "⚪",
                "Grey": "🩶",
                "Black": "⚫",
                "Dark Grey": "🌑",
                "Gold Shampanskiy": "🥂"
            }.get(color, "🎨")

            # Telegram callback_data 64 bayt limitiga tushirish uchun
            # uzun rang/bo‘lim nomlarini callback ichiga yozmaymiz.
            buttons.append((emoji + " " + color, "scolor|" + str(color_index)))

        send_catalog_photo_if_exists(chat_id, brand, section)
        buttons.append(("⬅️ Bo‘limlar", "brand|" + brand))
        send_message(
            chat_id,
            "🎨 <b>SALID — Rangni tanlang</b>\n\nKerakli rangni tanlang:",
            keyboard(buttons)
        )
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
        # SALID uchun qisqa callback: uzun section/color nomlari sababli
        # Telegramning 64 bayt limitidan oshib ketmaydi.
        color_index = list(PRODUCTS.get(brand, {}).get(section, {}).keys()).index(color)
        buttons.append((product + " — $" + format(price), "sprod|" + str(color_index) + "|" + str(index)))
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

    if step == "admin_greeting_sticker" and chat_id == ADMIN_ID:
        send_message(chat_id, "👋 Salomlashish stikeri uchun stiker yuboring.\n\nBekor qilish: /cancel")
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
            url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote("DUSEL 2-blok 12-DOKON, Toshkent")
            send_message(
                chat_id,
                "📍 <b>DUSEL 2-blok 12-DOKON</b>\n\n"
                "Google Maps: <a href=\"" + url + "\">📍 Xaritada ochish</a>",
                main_menu()
            )
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
                start_image_upload(chat_id, parts[1], parts[2], parts[3])
            return

        if data.startswith("imgupload|"):
            parts = data.split("|", 2)
            if len(parts) == 3:
                start_image_upload(chat_id, parts[1], parts[2])
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

        # SALID rang — qisqa callback orqali ishlaydi
        if data.startswith("scolor|"):
            parts = data.split("|")
            if len(parts) == 2:
                try:
                    color_index = int(parts[1])
                    section = "RANGLI ROZETKA VA KLYUCHATELLAR"
                    colors = list(PRODUCTS["SALID"][section].keys())
                    if 0 <= color_index < len(colors):
                        show_color_products(chat_id, "SALID", section, colors[color_index])
                    else:
                        send_message(chat_id, "❌ Rang topilmadi.")
                except Exception:
                    send_message(chat_id, "❌ Rangni ochishda xatolik yuz berdi.")
            return

        # SALID mahsulot — qisqa callback orqali ishlaydi
        if data.startswith("sprod|"):
            parts = data.split("|")
            if len(parts) == 3:
                try:
                    color_index = int(parts[1])
                    product_index = int(parts[2])
                    section = "RANGLI ROZETKA VA KLYUCHATELLAR"
                    colors = list(PRODUCTS["SALID"][section].keys())
                    if not (0 <= color_index < len(colors)):
                        send_message(chat_id, "❌ Rang topilmadi.")
                        return
                    color = colors[color_index]
                    product, price = PRODUCTS["SALID"][section][color][product_index]
                    set_state(chat_id, "quantity", {
                        "brand": "SALID",
                        "section": section,
                        "product": product + " (" + color + ")",
                        "price": price
                    })
                    send_message(
                        chat_id,
                        "📦 <b>" + product + " — " + color + "</b>\n"
                        "💵 Narxi: <b>$" + format(price) + "</b>\n\n"
                        "🔢 Nechta dona kerak?\n"
                        "Masalan: <b>10</b>"
                    )
                except Exception:
                    send_message(chat_id, "❌ Mahsulot topilmadi.")
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
                # Admin katalog rasmi yuborsa, tanlangan joyga saqlaymiz.
                if chat_id == ADMIN_ID and message.get("photo"):
                    state_step, state_data = get_state(chat_id)
                    if state_step == "admin_image":
                        photos = message.get("photo") or []
                        if photos:
                            file_id = photos[-1].get("file_id")
                            key = (state_data or {}).get("key")
                            if file_id and key:
                                save_catalog_image(key, file_id)
                                clear_state(chat_id)
                                send_reply_message(chat_id, "✅ <b>Rasm saqlandi!</b>\n\n" + key.replace("|", " → ") + "\n\nYana rasm qo‘shishingiz mumkin: 🖼 Rasmlar", admin_reply_keyboard())
                                return

                # Admin salomlashish stikeri yuborsa, saqlab qo‘yamiz.
                if chat_id == ADMIN_ID and message.get("sticker"):
                    state_step, state_data = get_state(chat_id)
                    if state_step == "admin_greeting_sticker":
                        sticker = message.get("sticker") or {}
                        file_id = sticker.get("file_id")
                        if file_id:
                            save_greeting_sticker(file_id)
                            clear_state(chat_id)
                            send_reply_message(
                                chat_id,
                                "✅ <b>Salomlashish stikeri saqlandi!</b>\n\n"
                                "Endi mijoz /start bosganda shu stiker yuboriladi. 👋",
                                admin_reply_keyboard()
                            )
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
                    greeting_sticker = get_greeting_sticker()
                    if greeting_sticker:
                        send_sticker(chat_id, greeting_sticker)

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
                elif text == "🖼 Rasmlar":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_images(chat_id)
                    else:
                        send_message(chat_id, "❌ Sizda admin huquqi yo‘q.")
                elif text == "👋 Salomlashish stikeri":
                    if chat_id == ADMIN_ID:
                        clear_state(chat_id)
                        show_admin_greeting_sticker(chat_id)
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
                    url = "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote("DUSEL 2-blok 12-DOKON, Toshkent")
                    send_message(
                        chat_id,
                        "📍 <b>DUSEL 2-blok 12-DOKON</b>\n\n"
                        "Google Maps: <a href=\"" + url + "\">📍 Xaritada ochish</a>",
                        user_reply_keyboard()
                    )
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

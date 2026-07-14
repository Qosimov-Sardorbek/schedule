from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from datetime import datetime
import time
import asyncio
import os

import tempfile
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip() # Avtomatik bo'sh joylarni o'chirish
if not BOT_TOKEN:
    print("❌ XATOLIK: BOT_TOKEN topilmadi! .env yoki Secrets ni tekshiring.")
    exit(1)

# Debug: DNS configuration
try:
    with open("/etc/resolv.conf", "r") as f:
        print(f"🔧 DNS Config (/etc/resolv.conf):\n{f.read()}")
except Exception as e:
    print(f"⚠️ DNS Config o'qilmadi: {e}")

ADMIN_USERNAME = "sqosimovv"
BASE_URL = "https://tsue.edupage.org/timetable/view.php?num=90&class="

# -------------------------------------------------------------------------------------
# WEB SERVER QISMI (Render.com uchun)
# -------------------------------------------------------------------------------------
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlamoqda! (TSUE Schedule Bot)"

def run_web_server():
    # Render.com avtomatik PORT o'zgaruvchisini beradi (odatda 10000)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Serverni alohida oqimda (thread) ishga tushiramiz
t = Thread(target=run_web_server)
t.start()
# -------------------------------------------------------------------------------------

STRINGS = {
    "uz": {
        "welcome": "🎓 *TSUE Dars Jadvali Bot*\n\nAssalomu alaykum! 👋\n\n📌 Ushbu bot orqali siz *dars jadvalingizni rasm ko‘rinishida* ko‘rishingiz mumkin.\n\n👉 Boshlash uchun:\n🔍 *Guruh Tanlash* tugmasini bosing\nyoki guruh nomini yozing (masalan: `RST-88/25`).\n\n━━━━━━━━━━━━━━━━━━\n👨‍💻 Yaratuvchi: @sqosimovv",
        "btn_bugun": "📅 Bugun",
        "btn_guruh": "🔍 Guruh Tanlash",
        "btn_yordam": "ℹ️ Yordam",
        "btn_lang": "🌐 Tilni o'zgartirish",
        "btn_notif": "🔔 Eslatmalar",
        "btn_notif_on": "✅ Yoqish",
        "btn_notif_off": "❌ O'chirish",
        "btn_back": "⬅️ Orqaga",
        "notif_menu": "🔔 *Eslatmalar bo'limi*\n\nHolat: {}\n\n✨Har kuni soat 08:00 da dars jadvalingizni avtomatik olishni xohlaysizmi?",
        "notif_status_on": "🟢Yoqilgan",
        "notif_status_off": "🔴O'chirilgan",
        "notif_enabled": "✅ Eslatmalar yoqildi! Har kuni 08:00 da dars jadvali yuboriladi.",
        "notif_disabled": "❌ Eslatmalar o'chirildi.",
        "select_group": "Guruh nomini yozing:\nMasalan: `RST-88/25`",
        "group_selected": "✅ *{}* tanlandi!\n\n📅 'Bugun' tugmasini bosing.",
        "no_group": "❌ Avval guruh tanlang!",
        "group_not_found": "⚠️ {} topilmadi. To‘g‘ri yozing.",
        "taking_screenshot": "📸 Jadval rasmi olinmoqda...",
        "error_screenshot": "❌ Rasm olinmadi\n\nXatolik: {}\n\n🔗 Saytda ko‘ring:",
        "error_sending": "❌ Rasm yuborishda xatolik: {}",
        "today_caption": "📅 *Bugungi jadval*\n👥 *{}*\n📆 {}\n\n🔗 [Saytda ko‘rish]({})",
        "help_text": "🆘 *YORDAM BO‘LIMI*\n━━━━━━━━━━━━━━━━━━\n\n🎓 *Bu bot nima qiladi?*\n— TSUE talabalari uchun *dars jadvalini rasm ko‘rinishida* chiqarib beradi.\n\n📌 *Qanday foydalaniladi?*\n1️⃣ `🔍 Guruh Tanlash` — guruhingizni tanlang\n2️⃣ Yoki guruh nomini yozing (masalan: `RST-88/25`)\n3️⃣ `📅 Bugun` tugmasini bosing\n\n📸 Natija:\n— Bugungi darslar *rasm (screenshot)* ko‘rinishida yuboriladi\n\n⚠️ *Eslatma:*\n— Avval guruh tanlanmasa, jadval chiqmaydi\n— Guruh nomini to‘g‘ri yozing\n\n👨‍💻 *Aloqa & takliflar:*\n👉 @sqosimovv\n\n━━━━━━━━━━━━━━━━━━\n✨ Botdan unumli foydalaning!",
        "days": ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"],
        "lang_selected": "✅ O'zbek tili tanlandi!",
        "choose_lang": "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇺🇸 Choose language:"
    },
    "ru": {
        "welcome": "🎓 *Бот Расписания ТГЭУ*\n\nЗдравствуйте! 👋\n\n📌 С помощью этого бота вы можете увидеть свое *расписание в виде изображения*.\n\n👉 Чтобы начать:\n🔍 Нажмите кнопку *Выбор группы*\nили введите название группы (например: `RST-88/25`).\n\n━━━━━━━━━━━━━━━━━━\n👨‍💻 Создатель: @sqosimovv",
        "btn_bugun": "📅 Сегодня",
        "btn_guruh": "🔍 Выбор группы",
        "btn_yordam": "ℹ️ Помощь",
        "btn_lang": "🌐 Сменить язык",
        "btn_notif": "🔔 Уведомления",
        "btn_notif_on": "✅ Включить",
        "btn_notif_off": "❌ Выключить",
        "btn_back": "⬅️ Назад",
        "notif_menu": "🔔 *Раздел уведомлений*\n\nСтатус: {}\n\n✨Хотите получать расписание автоматически каждый день в 08:00?",
        "notif_status_on": "🟢Включено",
        "notif_status_off": "🔴Выключено",
        "notif_enabled": "✅ Уведомления включены! Расписание будет отправляться каждый день в 08:00.",
        "notif_disabled": "❌ Уведомления выключены.",
        "select_group": "Введите название группы:\nНапример: `RST-88/25`",
        "group_selected": "✅ *{}* выбрана!\n\n📅 Нажмите кнопку 'Сегодня'.",
        "no_group": "❌ Сначала выберите группу!",
        "group_not_found": "⚠️ {} не найдена. Введите правильно.",
        "taking_screenshot": "📸 Получение изображения расписания...",
        "error_screenshot": "❌ Изображение не получено\n\nОшибка: {}\n\n🔗 Посмотреть на сайте:",
        "error_sending": "❌ Ошибка при отправке фото: {}",
        "today_caption": "📅 *Расписание на сегодня*\n👥 *{}*\n📆 {}\n\n🔗 [Посмотреть на сайте]({})",
        "help_text": "🆘 *РАЗДЕЛ ПОМОЩИ*\n━━━━━━━━━━━━━━━━━━\n\n🎓 *Что делает этот бот?*\n— Выдает *расписание занятий в виде изображения* для студентов ТГЭУ.\n\n📌 *Как пользоваться?*\n1️⃣ `🔍 Выбор группы` — выберите свою группу\n2️⃣ Или напишите название группы (например: `RST-88/25`)\n3️⃣ Нажмите кнопку `📅 Сегодня` \n\n📸 Результат:\n— Расписание на сегодня будет отправлено в виде *изображения (скриншота)*\n\n⚠️ *Примечание:*\n— Если группа не выбрана заранее, расписание не появится\n— Пишите название группы правильно\n\n👨‍💻 *Контакты и предложения:*\n👉 @sqosimovv\n\n━━━━━━━━━━━━━━━━━━\n✨ Пользуйтесь ботом эффективно!",
        "days": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
        "lang_selected": "✅ Выбран русский язык!",
        "choose_lang": "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇺🇸 Choose language:"
    },
    "en": {
        "welcome": "🎓 *TSUE Timetable Bot*\n\nHello! 👋\n\n📌 Through this bot, you can see your *timetable as an image*.\n\n👉 To start:\n🔍 Press the *Select Group* button\nor type the group name (e.g., `RST-88/25`).\n\n━━━━━━━━━━━━━━━━━━\n👨‍💻 Creator: @sqosimovv",
        "btn_bugun": "📅 Today",
        "btn_guruh": "🔍 Select Group",
        "btn_yordam": "ℹ️ Help",
        "btn_lang": "🌐 Change Language",
        "btn_notif": "🔔 Notifications",
        "btn_notif_on": "✅ Turn ON",
        "btn_notif_off": "❌ Turn OFF",
        "btn_back": "⬅️ Back",
        "notif_menu": "🔔 *Notifications Section*\n\nStatus: {}\n\n✨Do you want to receive your timetable automatically every day at 08:00?",
        "notif_status_on": "🟢Enabled",
        "notif_status_off": "🔴Disabled",
        "notif_enabled": "✅ Notifications enabled! Timetable will be sent every day at 08:00.",
        "notif_disabled": "❌ Notifications disabled.",
        "select_group": "Type the group name:\nFor example: `RST-88/25`",
        "group_selected": "✅ *{}* selected!\n\n📅 Press 'Today'.",
        "no_group": "❌ Select a group first!",
        "group_not_found": "⚠️ {} not found. Type correctly.",
        "taking_screenshot": "📸 Taking timetable screenshot...",
        "error_screenshot": "❌ Image failed\n\nError: {}\n\n🔗 View on site:",
        "error_sending": "❌ Error sending photo: {}",
        "today_caption": "📅 *Today's Timetable*\n👥 *{}*\n📆 {}\n\n🔗 [View on site]({})",
        "help_text": "🆘 *HELP SECTION*\n━━━━━━━━━━━━━━━━━━\n\n🎓 *What does this bot do?*\n— Provides the *class schedule as an image* for TSUE students.\n\n📌 *How to use?*\n1️⃣ `🔍 Select Group` — select your group\n2️⃣ Or type the group name (e.g., `RST-88/25`)\n3️⃣ Press the `📅 Today` button\n\n📸 Result:\n— Today's classes will be sent as an *image (screenshot)*\n\n⚠️ *Note:*\n— If a group is not selected first, the schedule won't appear\n— Type the group name correctly\n\n👨‍💻 *Contact & suggestions:*\n👉 @sqosimovv\n\n━━━━━━━━━━━━━━━━━━\n✨ Use the bot productively!",
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "lang_selected": "✅ English language selected!",
        "choose_lang": "🇺🇿 Tilni tanlang / 🇷🇺 Выберите язык / 🇺🇸 Choose language:"
    }
}

# GROUP_IDS lug'ati (Siz bergan versiya)
# =====================================================================================
# EDUPAGE SAYTIDAN GURUHLARNI VA JADVALLARNI AVTOMATIK TOPISH (NO HARDCODED IDS!)
# =====================================================================================
GROUP_IDS = {} # Qo'l bilan yozilgan barcha ID lar to'liq o'chirildi! Saytdan avtomatik olinadi.
DYNAMIC_GROUPS_CACHE = {}
LAST_FETCH_TIME = 0

from playwright.sync_api import sync_playwright

def fetch_all_groups_from_edupage():
    """Edupage saytining o'zidan (tsue.edupage.org) barcha guruhlarni va ularning ID larini avtomatik o'qib oladi"""
    global DYNAMIC_GROUPS_CACHE, LAST_FETCH_TIME, GROUP_IDS
    try:
        print("🌐 Edupage saytining o'zidan barcha guruhlar ro'yxati avtomatik o'qib olinmoqda...")
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://tsue.edupage.org/timetable/view.php?num=90", timeout=60000, wait_until="networkidle")
            
            # TTViewer va JS to'liq yuklanguncha kutamiz
            try:
                page.wait_for_selector('select, table, .timetable-container, #gi1878', timeout=15000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            
            groups_dict = page.evaluate("""() => {
                let groups = {};
                if (typeof asc !== 'undefined' && asc.ttviewer && asc.ttviewer.data && asc.ttviewer.data.classes) {
                    asc.ttviewer.data.classes.forEach(c => { if (c.name && c.id) groups[c.name.trim()] = String(c.id); });
                }
                if (typeof r !== 'undefined' && r.classes) {
                    r.classes.forEach(c => { if (c.name && c.id) groups[c.name.trim()] = String(c.id); });
                }
                if (Object.keys(groups).length === 0) {
                    document.querySelectorAll('select option, [data-class-id]').forEach(opt => {
                        if (opt.value && opt.textContent) groups[opt.textContent.trim()] = String(opt.value);
                    });
                }
                return groups;
            }""")
            browser.close()
            
            if groups_dict and len(groups_dict) > 0:
                DYNAMIC_GROUPS_CACHE = groups_dict
                GROUP_IDS = groups_dict # Moslashuvchanlik uchun
                LAST_FETCH_TIME = time.time()
                print(f"✅ Edupage saytidan {len(DYNAMIC_GROUPS_CACHE)} ta guruh avtomatik topilib, xotiraga saqlandi!")
    except Exception as e:
        print(f"⚠️ Saytdan guruhlarni o'qishda xatolik: {e}")
    return DYNAMIC_GROUPS_CACHE


def find_matching_group(query_text):
    """Foydalanuvchi yozgan guruhni (rst-88 -> RST-88/25) aniqlab beradi"""
    if not query_text or not isinstance(query_text, str):
        return None
    global DYNAMIC_GROUPS_CACHE, LAST_FETCH_TIME, GROUP_IDS
    
    query = query_text.strip().upper().replace(" ", "").replace("-", "")
    
    # 1. Exact match in cache
    for g in DYNAMIC_GROUPS_CACHE.keys():
        if g.upper() == query_text.strip().upper():
            return g
    for g in DYNAMIC_GROUPS_CACHE.keys():
        clean_g = g.upper().replace(" ", "").replace("-", "").split("/")[0]
        if clean_g == query or query in clean_g or clean_g in query:
            return g

    # 2. KAFOLATLI QABUL QILISH (INSTANT FALLBACK - 0.001 soniyada):
    # Hech qachon 5 soniya kutib foydalanuvchini qiynamaymiz!
    clean_raw = query_text.strip().upper()
    if "/" in clean_raw or "-" in clean_raw or any(c.isdigit() for c in clean_raw):
        if not "/" in clean_raw and any(c.isalpha() for c in clean_raw) and any(c.isdigit() for c in clean_raw):
            return f"{clean_raw}/25" # Odatda TSUE guruhlari /25, /24, /23 bilan tugaydi
        return clean_raw

    return None


def get_group_url(g):
    gid = DYNAMIC_GROUPS_CACHE.get(g) or GROUP_IDS.get(g)
    if gid:
        return f"{BASE_URL}{gid}"
    return "https://tsue.edupage.org/timetable/view.php?num=90"


def take_timetable_screenshot(guruh):
    """Saytga o'zi kirib guruh jadvalini avtomatik topib rasmga oladi"""
    global DYNAMIC_GROUPS_CACHE, GROUP_IDS
    browser = None
    try:
        # Saytdan guruh ID sini topamiz
        group_id = DYNAMIC_GROUPS_CACHE.get(guruh)
        if not group_id:
            try:
                fetch_all_groups_from_edupage()
                group_id = DYNAMIC_GROUPS_CACHE.get(guruh)
            except Exception:
                pass

        if group_id:
            url = f"{BASE_URL}{group_id}"
        else:
            url = "https://tsue.edupage.org/timetable/view.php?num=90"
        
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{guruh}_{int(time.time())}.png")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True, 
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # Pop-up va reklamalarni to'liq yashirish
            page.add_style_tag(content="""
                .cc-window, .cc-banner, .cc-overlay, #cookie-nav, .cookie-notice, 
                .modal-backdrop, .modal, [id*='cookie'], [class*='cookie'],
                .edu-popup, .popup-window, .edu-ad, #as-debug-window,
                footer, .footer, #footer { display: none !important; }
            """)
            
            # Agar ID bo'lmasa, saytning o'zidan guruhni tanlab ochishga harakat qilamiz
            if not group_id:
                try:
                    page.wait_for_timeout(3500)
                    page.evaluate("""(targetGroup) => {
                        let targetClean = targetGroup.toUpperCase().replace(/\\s+/g, '').split('/')[0];
                        if (typeof asc !== 'undefined' && asc.ttviewer && asc.ttviewer.data && asc.ttviewer.data.classes) {
                            let found = asc.ttviewer.data.classes.find(c => c.name && (c.name.toUpperCase().includes(targetClean) || c.name.toUpperCase() === targetGroup.toUpperCase()));
                            if (found && found.id) {
                                window.location.href = 'https://tsue.edupage.org/timetable/view.php?num=90&class=' + found.id;
                            }
                        } else if (typeof r !== 'undefined' && r.classes) {
                            let found = r.classes.find(c => c.name && (c.name.toUpperCase().includes(targetClean) || c.name.toUpperCase() === targetGroup.toUpperCase()));
                            if (found && found.id) {
                                window.location.href = 'https://tsue.edupage.org/timetable/view.php?num=90&class=' + found.id;
                            }
                        }
                    }""", guruh)
                    page.wait_for_timeout(3500)
                except Exception as ex:
                    print(f"⚠️ Dynamic redirect xatosi: {ex}")

            try:
                page.wait_for_selector(".timetable-container, .timetable-grid, table.main-table, #main", timeout=15000)
            except:
                print("⚠️ 1-urinishda jadval topilmadi, print versiyaga o'tilmoqda...")

            element = page.query_selector(".timetable-container") or page.query_selector("div.timetable-grid") or page.query_selector("#main")

            if element:
                element.screenshot(path=file_path)
            else:
                print_url = url + "&print=1"
                page.goto(print_url, timeout=60000, wait_until="networkidle")
                element = page.query_selector(".timetable-container") or page.query_selector(".timetable-grid")
                if element:
                    element.screenshot(path=file_path)
                else:
                    page.screenshot(path=file_path, full_page=True)

            browser.close()
        return file_path, None

    except Exception as e:
        if browser:
            try: browser.close()
            except: pass
        return None, str(e)


def start(update, context):
    """Start with language selection"""
    lang = context.user_data.get("lang")
    if not lang:
        return choose_language(update, context)

    s = STRINGS[lang]
    keyboard = [
        [KeyboardButton(s["btn_bugun"]), KeyboardButton(s["btn_guruh"])],
        [KeyboardButton(s["btn_notif"]), KeyboardButton(s["btn_lang"])],
        [KeyboardButton(s["btn_yordam"])],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        s["welcome"],
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )

def notif_menu_handler(update, context):
    """Notification settings menu"""
    lang = context.user_data.get("lang", "uz")
    s = STRINGS[lang]
    is_enabled = context.user_data.get("notif_enabled", False)
    status_text = s["notif_status_on"] if is_enabled else s["notif_status_off"]

    keyboard = [
        [KeyboardButton(s["btn_notif_on"]), KeyboardButton(s["btn_notif_off"])],
        [KeyboardButton(s["btn_back"])]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(
        s["notif_menu"].format(status_text),
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

def daily_notification_callback(context):
    """Job callback to send daily schedules"""
    job = context.job
    chat_id = job.context['chat_id']
    user_data = context.dispatcher.user_data.get(chat_id, {})

    lang = user_data.get("lang", "uz")
    guruh = user_data.get("guruh")
    s = STRINGS[lang]

    if not guruh:
        return

    filepath, error = take_timetable_screenshot(guruh)
    if not error and filepath:
        try:
            kun = datetime.now().weekday()
            # Skip Sunday
            if kun == 6:
                return

            kun_nomi = s["days"][kun]
            caption = s["today_caption"].format(guruh, kun_nomi, get_group_url(guruh))

            with open(filepath, "rb") as photo:
                context.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="Markdown")
            os.remove(filepath)
        except Exception:
            pass

def update_notification_job(chat_id, context, enable=True):
    """Add or remove the notification job"""
    job_name = f"daily_notif_{chat_id}"
    current_jobs = context.job_queue.get_jobs_by_name(job_name)

    for job in current_jobs:
        job.schedule_removal()

    if enable:
        # Schedule daily at 08:00
        from datetime import time as dt_time
        target_time = dt_time(8, 0, 0)
        context.job_queue.run_daily(
            daily_notification_callback,
            time=target_time,
            days=(0, 1, 2, 3, 4, 5), # Mon-Sat
            name=job_name,
            context={"chat_id": chat_id}
        )

def choose_language(update, context):
    """Language selection menu"""
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg_text = STRINGS["uz"]["choose_lang"]

    if update.callback_query:
        update.callback_query.message.reply_text(msg_text, reply_markup=reply_markup)
    else:
        update.message.reply_text(msg_text, reply_markup=reply_markup)

def guruh_tanlash(update, context):
    """Guruhlar"""
    lang = context.user_data.get("lang", "uz")
    s = STRINGS[lang]
    keyboard = []

    # Mashhur guruhlar
    popular = ["RST-88/25", "MNP-80", "I-50/24"]

    for g in popular:
        keyboard.append([
            InlineKeyboardButton(
                f"{g}",
                callback_data=f"g_{g}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        s["select_group"],
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


def find_matching_group(query_text):
    if not query_text or not isinstance(query_text, str):
        return None
    query = query_text.strip().upper().replace(" ", "").replace("-", "")
    # 1. First check exact match
    for g in GROUP_IDS.keys():
        if g.upper() == query_text.strip().upper():
            return g
    # 2. Check normalized match without /, -, spaces (e.g. rst-88 -> RST-88/25)
    for g in GROUP_IDS.keys():
        clean_g = g.upper().replace(" ", "").replace("-", "").split("/")[0]
        if clean_g == query or query in clean_g or clean_g in query:
            return g
    return None


def callback_handler(update, context):
    """Callback"""
    query = update.callback_query
    query.answer()

    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        context.user_data["lang"] = lang
        s = STRINGS[lang]

        query.edit_message_text(s["lang_selected"])

        # Show main menu
        keyboard = [
            [KeyboardButton(s["btn_bugun"]), KeyboardButton(s["btn_guruh"])],
            [KeyboardButton(s["btn_notif"]), KeyboardButton(s["btn_lang"])],
            [KeyboardButton(s["btn_yordam"])],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        context.bot.send_message(
            chat_id=query.message.chat_id,
            text=s["welcome"],
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    elif data.startswith("g_"):
        guruh = data[2:]
        lang = context.user_data.get("lang", "uz")
        s = STRINGS[lang]
        context.user_data["guruh"] = guruh
        query.edit_message_text(
            s["group_selected"].format(guruh),
            parse_mode="Markdown",
        )
        # Avtomatik ravishda dars jadvalini screen qilib yuboramiz
        bugun_handler(update, context, override_guruh=guruh)


def bugun_handler(update, context, override_guruh=None):
    """Bugungi darslar - RASM bilan"""
    lang = context.user_data.get("lang", "uz")
    s = STRINGS[lang]
    guruh = override_guruh or context.user_data.get("guruh")

    message = update.message if update.message else (update.callback_query.message if update.callback_query else None)
    if not message:
        return

    if not guruh:
        message.reply_text(s["no_group"])
        return

    if guruh not in GROUP_IDS:
        message.reply_text(s["group_not_found"].format(guruh))
        return

    msg = message.reply_text(s["taking_screenshot"])

    # Screenshot olish
    filepath, error = take_timetable_screenshot(guruh)

    if error or not filepath:
        msg.edit_text(s["error_screenshot"].format(error) + "\n" + get_group_url(guruh))
        return

    try:
        kun = datetime.now().weekday()
        kun_nomi = s["days"][kun]

        caption = s["today_caption"].format(
            guruh,
            kun_nomi,
            get_group_url(guruh)
        )

        with open(filepath, "rb") as photo:
            message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode="Markdown",
            )

        msg.delete()

        try:
            os.remove(filepath)
        except Exception:
            pass

    except Exception as e:
        msg.edit_text(s["error_sending"].format(e))


def message_handler(update, context):
    """Messages"""
    text = update.message.text
    lang = context.user_data.get("lang", "uz")
    s = STRINGS[lang]

    # Check buttons in all languages to be safe
    all_bugun = [STRINGS[l]["btn_bugun"] for l in STRINGS]
    all_guruh = [STRINGS[l]["btn_guruh"] for l in STRINGS]
    all_yordam = [STRINGS[l]["btn_yordam"] for l in STRINGS]
    all_lang = [STRINGS[l]["btn_lang"] for l in STRINGS]
    all_notif = [STRINGS[l]["btn_notif"] for l in STRINGS]
    all_notif_on = [STRINGS[l]["btn_notif_on"] for l in STRINGS]
    all_notif_off = [STRINGS[l]["btn_notif_off"] for l in STRINGS]
    all_back = [STRINGS[l]["btn_back"] for l in STRINGS]

    if text in all_bugun:
        bugun_handler(update, context)

    elif text in all_guruh:
        guruh_tanlash(update, context)

    elif text in all_notif:
        notif_menu_handler(update, context)

    elif text in all_notif_on:
        context.user_data["notif_enabled"] = True
        update_notification_job(update.message.chat_id, context, enable=True)
        update.message.reply_text(s["notif_enabled"])
        start(update, context)

    elif text in all_notif_off:
        context.user_data["notif_enabled"] = False
        update_notification_job(update.message.chat_id, context, enable=False)
        update.message.reply_text(s["notif_disabled"])
        start(update, context)

    elif text in all_back:
        start(update, context)

    elif text in all_yordam:
        update.message.reply_text(
            s["help_text"],
            parse_mode="Markdown",
        )

    elif text in all_lang:
        choose_language(update, context)

    else:
        # Guruh nomini aqlli qidirish (rst-88 -> RST-88/25)
        matched_g = find_matching_group(text)
        if matched_g:
            context.user_data["guruh"] = matched_g
            update.message.reply_text(
                s["group_selected"].format(matched_g),
                parse_mode="Markdown",
            )
            # Avtomatik ravishda dars jadvali rasmini yuborish
            bugun_handler(update, context, override_guruh=matched_g)
            return

        # Default welcome message if not a group
        update.message.reply_text(
            s["welcome"],
            parse_mode="Markdown",
        )


def stats(update, context):
    """Bot statistics for Admin"""
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return

    # Count entries in dispatcher.user_data
    total_users = len(context.dispatcher.user_data)

    # Count how many have notifications active
    notif_users = 0
    for u_id in context.dispatcher.user_data:
        if context.dispatcher.user_data[u_id].get("notif_enabled", False):
            notif_users += 1

    msg = (
        "📊 *Bot statistikasi:*\n\n"
        f"👥 Umumiy foydalanuvchilar: `{total_users}`\n"
        f"🔔 Eslatma yoqqanlar: `{notif_users}`"
    )
    update.message.reply_text(msg, parse_mode="Markdown")


def broadcast(update, context):
    """Send message to all users - Admin only"""
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return

    # Get the message after /send
    text = update.message.text.replace("/send", "").strip()

    if not text:
        update.message.reply_text("❌ Xabar yozilmagan. Masalan: `/send Salom talabalar!`", parse_mode="Markdown")
        return

    msg = update.message.reply_text(f"🚀 Xabar yuborish boshlandi...")

    chat_ids = context.dispatcher.user_data.keys()
    success = 0
    failed = 0

    for chat_id in chat_ids:
        try:
            context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            success += 1
            # Add small delay to avoid flood
            time.sleep(0.05)
        except Exception:
            failed += 1

    msg.edit_text(
        f"✅ Yuborish yakunlandi!\n\n"
        f"➕ Muvaffaqiyatli: `{success}`\n"
        f"➖ Muvaffaqiyatsiz: `{failed}`",
        parse_mode="Markdown"
    )



def main():
    print("============================================================")
    print("🎓 TSUE Jadval Bot")
    print(f"📊 {len(GROUP_IDS)} ta guruh/element")
    print("📸 Screenshot rejimi")
    print("============================================================")

    from telegram.ext import PicklePersistence
    persistence = PicklePersistence(filename='bot_data.pickle')

    updater = Updater(BOT_TOKEN, use_context=True, persistence=persistence)
    dp = updater.dispatcher

    # Restart jobs for users who have them enabled
    job_queue = updater.job_queue
    def restore_jobs(dispatcher):
        chat_ids = dispatcher.user_data.keys()
        for chat_id in chat_ids:
            u_data = dispatcher.user_data.get(chat_id, {})
            if u_data.get("notif_enabled", False):
                # Manual job reconstruction since objects aren't persisted well
                job_name = f"daily_notif_{chat_id}"
                from datetime import time as dt_time
                target_time = dt_time(8, 0, 0)
                job_queue.run_daily(
                    daily_notification_callback,
                    time=target_time,
                    days=(0, 1, 2, 3, 4, 5),
                    name=job_name,
                    context={"chat_id": chat_id}
                )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("send", broadcast))
    dp.add_handler(CommandHandler("guruh", guruh_tanlash))
    dp.add_handler(CallbackQueryHandler(callback_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    print("✅ Ishga tushdi!")

    # -------------------------------------------------------------------------------------
    # DIAGNOSTIKA (Network Check)
    # -------------------------------------------------------------------------------------
    import socket
    import requests
    try:
        print("🔍 Tarmoq tekshirilmoqda...")
        ip = socket.gethostbyname("api.telegram.org")
        print(f"✅ DNS OK: api.telegram.org -> {ip}")
        
        response = requests.get("https://api.telegram.org", timeout=5)
        print(f"✅ HTTP OK: {response.status_code}")
    except Exception as e:
        print(f"❌ TARMOQ XATOSI: {e}")
    # -------------------------------------------------------------------------------------

    # Restore jobs after start
    restore_jobs(dp)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
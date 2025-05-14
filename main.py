import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN, ADMIN_IDS
from database import init_db, get_conn
from utils import t
from templates import format_event_card
from datetime import datetime

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

init_db()


def get_user_lang(user_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
        res = cur.fetchone()
        return res[0] if res else 'ru'


def set_user_lang(user_id, lang):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO users (user_id, lang) VALUES (?, ?)", (user_id, lang))
        conn.commit()


@bot.message_handler(commands=['start'])
def start_cmd(message):
    lang = get_user_lang(message.from_user.id)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(t("show_categories", lang)))
    bot.send_message(message.chat.id, t("start_message", lang), reply_markup=kb)


@bot.message_handler(commands=['lang'])
def lang_cmd(message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇬🇷 Ελληνικά", callback_data="set_lang_gr")
    )
    bot.send_message(message.chat.id, "🌐 Choose your language:\n\nthen click on /start", reply_markup=kb)


@bot.message_handler(func=lambda m: m.text in ["Показать категории", "Show categories", "Εμφάνιση κατηγοριών"])
def show_categories(message):
    lang = get_user_lang(message.from_user.id)
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, emoji, title_{} FROM categories".format(lang))
        rows = cur.fetchall()

    kb = InlineKeyboardMarkup()
    for cat_id, emoji, title in rows:
        kb.add(InlineKeyboardButton(f"{emoji} {title}", callback_data=f"cat_{cat_id}"))
    bot.send_message(message.chat.id, t("select_category", lang), reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang_"))
def lang_select_callback(call):
    lang = call.data.split("_")[-1]
    set_user_lang(call.from_user.id, lang)
    log_action(call.from_user.id, "set_lang", lang, lang)
    bot.answer_callback_query(call.id, t("language_set", lang))


@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def category_selected(call):
    lang = get_user_lang(call.from_user.id)
    cat_id = int(call.data.split("_")[1])
    log_action(call.from_user.id, "select_category", cat_id, lang)
    send_events_page(call.message.chat.id, cat_id, 0, lang, by_category=True)


@bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
def paginate_callback(call):
    _, mode, cat_id, page = call.data.split("_")
    lang = get_user_lang(call.from_user.id)
    log_action(call.from_user.id, "paginate", {"mode": mode, "cat_id": cat_id, "page": page}, lang)
    send_events_page(
        call.message.chat.id,
        int(cat_id),
        int(page),
        lang,
        by_category=(mode == "cat"),
        edit=False
    )


def send_events_page(chat_id, cat_id, page, lang, by_category=True, edit=False, message_id=None):
    per_page = 5
    offset = page * per_page

    with get_conn() as conn:
        cur = conn.cursor()
        if by_category:
            cur.execute(f"""
                SELECT * FROM events
                WHERE category_id = ? AND is_published = 1
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (cat_id, per_page + 1, offset))
        else:
            cur.execute(f"""
                SELECT * FROM events
                WHERE is_published = 1
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (per_page + 1, offset))

        events = cur.fetchall()

    if not events:
        bot.send_message(chat_id, t("no_events", lang))
        return

    for e in events[:per_page]:
        event = dict(zip([d[0] for d in cur.description], e))
        text = format_event_card(event, lang)
        btns = InlineKeyboardMarkup()
        if event['gmap_url']:
            btns.add(InlineKeyboardButton(t("map", lang), url=event['gmap_url']))
        if event['booking_url']:
            btns.add(InlineKeyboardButton(t("booking", lang), url=event['booking_url']))
        elif event['contact']:
            btns.add(InlineKeyboardButton(t("contact", lang), url=event['contact']))
        bot.send_photo(chat_id, event['image_url'], caption=text, reply_markup=btns)

    # Pagination
    nav = InlineKeyboardMarkup()
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton
                       ("⬅️", callback_data=f"page_{'cat' if by_category else 'all'}_{cat_id}_{page-1}"))
    if len(events) > per_page:
        buttons.append(InlineKeyboardButton
                       ("➡️", callback_data=f"page_{'cat' if by_category else 'all'}_{cat_id}_{page+1}"))
    if buttons:
        nav.row(*buttons)
        bot.send_message(chat_id, t("page navigation", lang), reply_markup=nav)


@bot.message_handler(commands=['weekly'])
def show_weekly(message):
    lang = get_user_lang(message.from_user.id)
    send_events_page(message.chat.id, 0, 0, lang, by_category=False)


# logging
def log_action(user_id, action, payload, lang):
    with get_conn() as conn:
        cur = conn.cursor()
        print(user_id, action, payload, lang)
        cur.execute('''
            INSERT INTO logs (user_id, action, payload, timestamp, lang)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, action, str(payload), datetime.utcnow().isoformat(), lang))
        conn.commit()


@bot.message_handler(commands=['admin_stats'])
def admin_stats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔️ Access denied.")
        return

    with get_conn() as conn:
        cur = conn.cursor()

        # User count
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]

        # Fetch lang
        cur.execute("SELECT lang, COUNT(*) FROM users GROUP BY lang")
        langs = cur.fetchall()

        # Logs count for do
        cur.execute("SELECT action, COUNT(*) FROM logs GROUP BY action")
        actions = cur.fetchall()

    stats = [f"<b>👤 Users:</b> {user_count}"]

    if langs:
        stats.append("<b>🌐 Languages:</b>")
        for lang, count in langs:
            stats.append(f" - {lang}: {count}")

    if actions:
        stats.append("<b>📊 Actions:</b>")
        for action, count in actions:
            stats.append(f" - {action}: {count}")

    bot.send_message(message.chat.id, "\n".join(stats), parse_mode="HTML")


print("Bot started...")
bot.infinity_polling()

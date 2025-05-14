# @bot.message_handler(func=lambda m: m.text == "Show categories")
# def show_categories(message):
#     lang = get_user_lang(message.from_user.id)
#     with get_conn() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT id, emoji, title_{} FROM categories".format(lang))
#         rows = cur.fetchall()
#
#     kb = InlineKeyboardMarkup()
#     for cat_id, emoji, title in rows:
#         kb.add(InlineKeyboardButton(f"{emoji} {title}", callback_data=f"cat_{cat_id}"))
#     bot.send_message(message.chat.id, t("select_category", lang), reply_markup=kb)
#
#
# @bot.message_handler(func=lambda m: m.text == "Εμφάνιση κατηγοριών")
# def show_categories(message):
#     lang = get_user_lang(message.from_user.id)
#     with get_conn() as conn:
#         cur = conn.cursor()
#         cur.execute("SELECT id, emoji, title_{} FROM categories".format(lang))
#         rows = cur.fetchall()
#
#     kb = InlineKeyboardMarkup()
#     for cat_id, emoji, title in rows:
#         kb.add(InlineKeyboardButton(f"{emoji} {title}", callback_data=f"cat_{cat_id}"))
#     bot.send_message(message.chat.id, t("select_category", lang), reply_markup=kb)


# @bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
# def category_selected(call):
#     lang = get_user_lang(call.from_user.id)
#     cat_id = int(call.data.split("_")[1])
#     send_events_page(call.message.chat.id, cat_id, 0, lang, by_category=True)


# @bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
# def paginate_callback(call):
#     _, mode, cat_id, page = call.data.split("_")
#     lang = get_user_lang(call.from_user.id)
#     cat_id = int(cat_id)
#     page = int(page)
#     send_events_page(call.message.chat.id, cat_id, page, lang, by_category=(mode == "cat"),
#     message_id=call.message.message_id, edit=True)


# @bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
# def category_selected(call):
#     lang = get_user_lang(call.from_user.id)
#     cat_id = int(call.data.split("_")[1])
#     with get_conn() as conn:
#         cur = conn.cursor()
#         cur.execute(f"""
#             SELECT * FROM events
#             WHERE category_id=? AND is_published=1
#             ORDER BY created_at DESC LIMIT 5
#         """, (cat_id,))
#         events = cur.fetchall()
#
#     if not events:
#         bot.answer_callback_query(call.id, t("no_events", lang), show_alert=True)
#         return
#
#     for e in events:
#         event = dict(zip([d[0] for d in cur.description], e))
#         text = format_event_card(event, lang)
#         btns = InlineKeyboardMarkup()
#         if event['gmap_url']:
#             btns.add(InlineKeyboardButton(t("map", lang), url=event['gmap_url']))
#         if event['booking_url']:
#             btns.add(InlineKeyboardButton(t("booking", lang), url=event['booking_url']))
#         elif event['contact']:
#             btns.add(InlineKeyboardButton(t("contact", lang), url=event['contact']))
#         bot.send_photo(call.message.chat.id, event['image_url'], caption=text, reply_markup=btns)


# @bot.message_handler(commands=['weekly'])
# def show_weekly(message):
#     lang = get_user_lang(message.from_user.id)
#     with get_conn() as conn:
#         cur = conn.cursor()
#         cur.execute(f"""
#             SELECT * FROM events
#             WHERE is_published=1
#             ORDER BY created_at DESC LIMIT 10
#         """)
#         events = cur.fetchall()
#
#     bot.send_message(message.chat.id, t("weekly_header", lang))
#     for e in events:
#         event = dict(zip([d[0] for d in cur.description], e))
#         text = format_event_card(event, lang)
#         btns = InlineKeyboardMarkup()
#         if event['gmap_url']:
#             btns.add(InlineKeyboardButton(t("map", lang), url=event['gmap_url']))
#         if event['booking_url']:
#             btns.add(InlineKeyboardButton(t("booking", lang), url=event['booking_url']))
#         bot.send_photo(message.chat.id, event['image_url'], caption=text, reply_markup=btns)

# @bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang_"))
# def lang_select_callback(call):
#     print('logged lang')
#     lang = call.data.split("_")[-1]
#     set_user_lang(call.from_user.id, lang)
#     log_action(call.from_user.id, "set_lang", lang, lang)
#     bot.answer_callback_query(call.id, t("language_set", lang))
#
#
# @bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
# def category_selected(call):
#     lang = get_user_lang(call.from_user.id)
#     cat_id = int(call.data.split("_")[1])
#     log_action(call.from_user.id, "select_category", cat_id, lang)
#     send_events_page(call.message.chat.id, cat_id, 0, lang, by_category=True)
#
#
# @bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
# def paginate_callback(call):
#     _, mode, cat_id, page = call.data.split("_")
#     lang = get_user_lang(call.from_user.id)
#     log_action(call.from_user.id, "paginate", {"mode": mode, "cat_id": cat_id, "page": page}, lang)
#     send_events_page(call.message.chat.id, int(cat_id), int(page), lang, by_category=(mode == "cat"))

# @bot.callback_query_handler(func=lambda c: c.data.startswith("set_lang_"))
# def lang_select_callback(call):
#     lang = call.data.split("_")[-1]
#     set_user_lang(call.from_user.id, lang)
#     bot.answer_callback_query(call.id, t("language_set", lang))

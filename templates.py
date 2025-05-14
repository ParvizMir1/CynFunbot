def format_event_card(event, lang):
    title = event[f'title_{lang}']
    desc = event[f'desc_{lang}'][:300]
    price = f"{event['price_from']} - {event['price_to']}" if event['price_to'] else f"{event['price_from']}+"
    text = f"<b>{title}</b>\n📍 {event['city']}\n\n{desc}\n💸 {price}"

    return text

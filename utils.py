import json
from config import DEFAULT_LANG


def load_locale(lang):
    try:
        with open(f'locales/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return load_locale(DEFAULT_LANG)


def t(key, lang):
    locale = load_locale(lang)
    return locale.get(key, key)

from telegram import KeyboardButton, ReplyKeyboardMarkup


def build_keyboard():
    keyboard = [
        [
            KeyboardButton("Список приложений"),
            KeyboardButton("Сформировать ссылку для запуска"),
            KeyboardButton("FAQ"),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard)

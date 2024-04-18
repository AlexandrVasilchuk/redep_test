import os
from dotenv import load_dotenv

load_dotenv()

# MESSAGES
GET_LAUNCH_LINKS_MESSAGE = "Выберите приложение для получения ссылки:"

BUTTON_CLICK_MESSAGE = "Ссылка для приложения {}: {}."

FAQ_MESSAGE = "Бот для мониторинга доступности приложений.\nПодробная инструкция, команды и пояснения для администратора доступны в README файле."

INTERVAL_SET_MESSAGE = (
    "Интервал проверки достпуности приложений изменен. Текущее значение - {}."
)

START_NO_ARGS = "Не указан токен. /start <token>.\nВы все еще не зарегистрированы в системе."

START_ALREADY_AUTHORIZED = "Вы уже зарегистрированы в системе."

START_REGISTERED = "Вы зарегистрированы!"

ONLY_ADMIN = "Эта команда только для администратора"

INTERVAL_ARGS = "Команда ожидает 1 аргумент: <interval>."

ADD_APPLICATION_ARGS = "Команда ожидает 3 аргумента: url - name - ads_url"

ALREADY_ADDED = "Приложение уже было добавлено. Используйте /remove {}, чтобы добавить приложение с новыми данными."

APPLICATION_ADDED = "Приложение {}: с url - {} было добавлено."

REMOVE_ARGS = "Команда ожидает 1 аргумент: <url>"

APPLICATION_DOES_NOT_EXIST_TO_REMOVE = "Приложения с таким url не существует."

GENERATE_ARGS = "Команда ожидает 1 аргумент: <key>"

TOKEN_GENERATED = "Токен: {} был зарегистрирован."

APPLICATION_UNAVAILABLE = "Приложение: {}, url: {} недоступно!"

BROADCAST_ARGS = "Команда ожидает 1 аргумент:: message."

STATUS_APPLICATION = "Приложение: {}. Ссылка - {}."

REMOVE_APPLICATION = "Приложение: {} было удалено."

INCORRECT_TOKEN = "Некорректный токен. Проверьте правильность ввода или попросите администратора сгененировать новый."

TOKEN_IS_INACTIVE = "Токен неактивен. Попросите администратора сгененировать новый"

TOKEN_LENGTH = "Длина токена должен быть не более 16 символов."

TOKEN_EXISTS = "Такой токен уже существует. Придумайте другой."

NAME_LENGTH_MESSAGE = "Длина имени приложения не может превышать {}"

URL_LENGTH_MESSAGE = "Длина url не может превышать {}"

SECRET_REPLY = "Был сгенерирован пользователь сразу с правами администратора. Этот костыль необходим для удобной проверки ТЗ."

# FILTERS
STATUS_TEXT_FILTERS = ["Список приложений"]

GET_LAUNCH_LINKS_FILTERS = ["Сформировать ссылку для запуска"]

FAQ_FILTERS = ["FAQ"]

# INTEGERS
INTERVAL_DEFAULT_VALUE = 120

REPEATING_JOB_FIRST_VALUE = 0

HTTP_200_OK = 200

MINIMAL_FAILURE_COUNTER_VALUE = 3

MAX_TOKEN_LENGTH = 16

MAX_URL_LENGTH = 256

MAX_NAME_LENGTH = 150

MAX_ADS_URL_LENGTH = 256

# SECRETS
SECRET_ADMIN_TOKEN = os.getenv("SECRET_ADMIN_TOKEN", default="SECRET_ADMIN_TOKEN")

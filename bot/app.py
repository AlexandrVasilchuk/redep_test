import asyncio
import logging
import os

import aiohttp
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import constants
from keyboard import build_keyboard
from core.db import get_async_session
from services import application_service, token_service, user_service
from utils.dependecies import Depends, inject_db

logger = logging.Logger("BOT", logging.INFO)


@inject_db
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Регистрирует пользователя, используя токен.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    Raises:
        ValueError: Если токен пользователя не действителен.

    """
    logger.info("Обработка команды start")

    if await user_service.get_user_by_attr(
        "telegram_user_id", update.message.from_user.id, session
    ):
        await update.message.reply_text(
            constants.START_ALREADY_AUTHORIZED, reply_markup=build_keyboard()
        )
        logger.info("Пользователь уже авторизован")
        return

    if not context.args:
        await update.message.reply_text(constants.START_NO_ARGS)
        logger.warning("Отсутствуют аргументы в команде start")
        return

    user_token = context.args.pop()
    print(constants.SECRET_ADMIN_TOKEN)
    if user_token == constants.SECRET_ADMIN_TOKEN:
        await user_service.create_user(
            {
            "telegram_user_id": update.message.from_user.id,
             "is_admin": True,
            }, session
        )
        await update.message.reply_text(
            constants.SECRET_REPLY, reply_markup=build_keyboard()
        )
        return
    try:
        await token_service.check_user_token(user_token, session)
    except ValueError as error:
        await update.message.reply_text(str(error))
        logger.error("Ошибка при проверке токена пользователя: %s", error)
        return

    await user_service.create_user(
        {"telegram_user_id": update.message.from_user.id}, session
    )
    await update.message.reply_text(
        constants.START_REGISTERED, reply_markup=build_keyboard()
    )
    logger.info("Пользователь успешно зарегистрирован")


@inject_db
async def set_interval(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Устанавливает интервал опроса доступности приложений.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды set_interval")

    user = await user_service.get_user_by_attr(
        "telegram_user_id", update.message.from_user.id, session
    )
    if not user.is_admin:
        await update.message.reply_text(constants.ONLY_ADMIN)
        logger.warning(
            "Попытка изменения интервала пользователем, не являющимся администратором"
        )
        return

    if len(context.args) != 1:
        await update.message.reply_text(constants.INTERVAL_ARGS)
        logger.warning("Отсутствует аргумент в команде set_interval")
        return

    interval = int(context.args.pop())
    await context.application.job_queue.stop(wait=False)
    context.application.job_queue.run_repeating(
        check_applications, interval=interval, first=0
    )
    await context.application.job_queue.start()

    await update.message.reply_text(
        constants.INTERVAL_SET_MESSAGE.format(interval)
    )
    logger.info("Интервал опроса приложений успешно изменен: %d", interval)


@inject_db
async def add_application(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Добавляет новое приложение для мониторинга.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды add_application")

    if not await user_service.is_admin(update.message.from_user.id, session):
        await update.message.reply_text(constants.ONLY_ADMIN)
        logger.warning("Попытка добавления приложения неадминистратором")
        return

    if len(context.args) != 3:
        await update.message.reply_text(constants.ADD_APPLICATION_ARGS)
        logger.warning("Недостаточно аргументов в команде add_application")
        return

    url, name, ads_url = context.args
    if await application_service.get_application_by_attr("url", url, session):
        await update.message.reply_text(constants.ALREADY_ADDED.format(url))
        logger.warning("Попытка добавления существующего приложения")
        return
    try:
        await application_service.create_application(
            {"url": url, "name": name, "ads_url": ads_url}, session
        )
    except ValueError as error:
        logger.error("Ошибка при создании приложения с некорректными данными.")
        await update.message.reply_text(str(error))
        return
    await update.message.reply_text(
        constants.APPLICATION_ADDED.format(name, url)
    )
    logger.info("Приложение успешно добавлено: %s", name)


@inject_db
async def remove_application(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет приложение из мониторинга.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды remove_application")

    if not await user_service.is_admin(update.message.from_user.id, session):
        await update.message.reply_text(constants.ONLY_ADMIN)
        logger.warning("Попытка удаления приложения неадминистратором")
        return

    if len(context.args) != 1:
        await update.message.reply_text(constants.REMOVE_ARGS)
        logger.warning("Недостаточно аргументов в команде remove_application")
        return

    url = context.args.pop()

    application = await application_service.get_application_by_attr(
        "url", url, session
    )
    if not application:
        await update.message.reply_text(
            constants.APPLICATION_DOES_NOT_EXIST_TO_REMOVE.format(url)
        )
        logger.warning("Попытка удаления несуществующего приложения")
        return

    await application_service.delete(application, session)

    await update.message.reply_text(
        constants.REMOVE_APPLICATION.format(application)
    )
    logger.info("Приложение успешно удалено: %s", application)


@inject_db
async def generate_key(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Генерирует новый токен.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды generate_key")

    if not await user_service.is_admin(update.message.from_user.id, session):
        await update.message.reply_text(constants.ONLY_ADMIN)
        logger.warning("Попытка генерации токена неадминистратором")
        return

    if len(context.args) != 1:
        await update.message.reply_text(constants.GENERATE_ARGS)
        logger.warning("Недостаточно аргументов в команде generate_key")
        return

    key = context.args.pop()
    try:
        await token_service.check_generated_token(key, session)
        await update.message.reply_text(constants.TOKEN_GENERATED.format(key))
        logger.info("Токен успешно сгенерирован: %s", key)
    except ValueError as error:
        await update.message.reply_text(str(error))
        logger.error("Ошибка генерации токена: %s", error)


async def send_message_to_all_users(bot, message: str, session: AsyncSession):
    """Отправляет сообщение всем пользователям.

    Args:
        bot: Экземпляр Telegram Bot.
        message (str): Текст сообщения.
        session (AsyncSession): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Отправка сообщения всем пользователям")

    users = await user_service.get_all_users(session)
    await asyncio.gather(
        *[
            bot.send_message(chat_id=user.telegram_user_id, text=message)
            for user in users
        ]
    )


async def request_application_info(
    context: CallbackContext, application, session: AsyncSession
):
    """Запрашивает информацию о приложении.

    Args:
        context (CallbackContext): Контекст выполнения команды.
        application: Приложение для мониторинга.
        session (AsyncSession): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Запрос информации о приложении: %s", application.name)

    async with aiohttp.ClientSession() as http_session:
        try:
            async with http_session.get(application.url) as response:
                logger.info(
                    "Статус запроса: %s, URL: %s",
                    response.status,
                    application.url,
                )

                if response.status == constants.HTTP_200_OK:
                    await application_service.reset_failure_counter(
                        application, session
                    )
                else:
                    await application_service.increment_failure_counter(
                        application, session
                    )
        except aiohttp.ClientError as error:
            await application_service.increment_failure_counter(
                application, session
            )
            logger.error(
                "Ошибка при запросе информации о приложении: %s", error
            )

    if application.failure_counter >= constants.MINIMAL_FAILURE_COUNTER_VALUE:
        await send_message_to_all_users(
            context.bot,
            constants.APPLICATION_UNAVAILABLE.format(
                application.name, application.url
            ),
            session,
        )
        await application_service.reset_failure_counter(application, session)


@inject_db
async def check_applications(
    context: CallbackContext,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Проверяет доступность приложений и отправляет уведомления при необходимости.

    Args:
        context (CallbackContext): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Выполнение периодической проверки приложений")

    applications = await application_service.get_all_applications(session)
    for application in applications:
        await request_application_info(context, application, session)


@inject_db
async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Отправляет широковещательное сообщение всем пользователям.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды broadcast")

    if not await user_service.is_admin(update.message.from_user.id, session):
        await update.message.reply_text(constants.ONLY_ADMIN)
        logger.warning("Попытка широковещательной рассылки неадминистратором")
        return

    if len(context.args) != 1:
        await update.message.reply_text(constants.BROADCAST_ARGS)
        logger.warning("Недостаточно аргументов в команде broadcast")
        return

    message = context.args.pop()
    await send_message_to_all_users(context.bot, message, session)
    logger.info("Широковещательное сообщение отправлено: %s", message)


@inject_db
async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Отправляет статус всех приложений.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды status")

    applications = await application_service.get_all_applications(session)
    await asyncio.gather(
        *[
            update.message.reply_text(
                constants.STATUS_APPLICATION.format(
                    application.name, application.url
                )
            )
            for application in applications
        ]
    )


@inject_db
async def get_launch_links(
    update: Update,
    context: CallbackContext,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Отправляет пользователю список приложений с кнопками для получения ссылок на запуск.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info("Обработка команды get_launch_links")

    applications = await application_service.get_all_applications(session)
    keyboard = [
        [InlineKeyboardButton(app.name, callback_data=str(app.id))]
        for app in applications
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        constants.GET_LAUNCH_LINKS_MESSAGE, reply_markup=reply_markup
    )


@inject_db
async def button_click(
    update: Update,
    context: CallbackContext,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Обрабатывает нажатие кнопки для получения ссылки на запуск приложения.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.
        session (AsyncSession, optional): Сессия асинхронного соединения с базой данных.

    Returns:
        None

    """
    logger.info(
        "Обработка нажатия кнопки для получения ссылки на запуск приложения"
    )

    query = update.callback_query
    application = await application_service.get_application_by_attr(
        "id", int(query.data), session
    )
    await query.message.reply_text(
        constants.BUTTON_CLICK_MESSAGE.format(
            application.name, application.url
        )
    )


async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пользователю ответ на часто задаваемый вопрос.

    Args:
        update (Update): Обновление от Telegram.
        context (ContextTypes.DEFAULT_TYPE): Контекст выполнения команды.

    Returns:
        None

    """
    logger.info("Обработка команды faq")
    await update.message.reply_text(constants.FAQ_MESSAGE)


def main() -> None:
    """Запускает бота."""

    logging.info("Bot started!")
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler(["start"], start))
    application.add_handler(CommandHandler(["add"], add_application))
    application.add_handler(CommandHandler(["remove"], remove_application))
    application.add_handler(CommandHandler(["setinterval"], set_interval))
    application.add_handler(CommandHandler(["generatekey"], generate_key))
    application.add_handler(CommandHandler(["broadcast"], broadcast))
    application.add_handler(
        CommandHandler(["getlauchlinks"], get_launch_links)
    )
    application.add_handler(CommandHandler(["status"], status))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(
        MessageHandler(filters.Text(constants.STATUS_TEXT_FILTERS), status)
    )
    application.add_handler(
        MessageHandler(
            filters.Text(constants.GET_LAUNCH_LINKS_FILTERS), get_launch_links
        )
    )
    application.add_handler(
        MessageHandler(filters.Text(constants.FAQ_FILTERS), faq)
    )

    application.job_queue.run_repeating(
        check_applications, interval=constants.INTERVAL_DEFAULT_VALUE, first=constants.REPEATING_JOB_FIRST_VALUE
    )
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

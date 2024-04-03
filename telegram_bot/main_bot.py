import sys
sys.path.append("/home/yyy/Desktop/app_with_git/app")
# Для Docker
sys.path.append("/usr/src/myapp")

import os
import re
import logging
from dotenv import load_dotenv
from typing import List, Tuple
from telegram.error import TimedOut
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters
from database_drivers.cruds import get_query_from_added_users_item_table_with_username
from database_drivers.cruds import get_query_from_added_users_item_table
from database_drivers.cruds import set_data_to_added_users_item_table
from database_drivers.cruds import delete_row_from_added_users_item_table
from database_drivers.database_engine import SessionLocal
from database_drivers.schemas import AddedItemRow

logging.basicConfig(filename="utils/logger.txt", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv("/home/yyy/Desktop/app_with_git/app/.env")
logger = logging.getLogger(__name__)

TOKEN = os.environ["TOKEN"]

MAIN_MENU_CHOOSE, SHOW_MENU_CHOOSE, DELETE_MENU_CHOOSE = 1, 2, 3
ADD_MENU_CHOOSE, ADD_URL_MENU_CHOOSE = 4, 5

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Добавить вещь в список")],
            [KeyboardButton("Показать текущий список")]
        ], 
        resize_keyboard=True,
        one_time_keyboard=True
    )

    if context.user_data.get("re_run") and update.message.text == "/start":
        logger.info(f"Пользователь {update.effective_user.name}: перезапустить приложение")
        await context.bot.send_message(
            chat_id=update._effective_chat.id,
            text="Кликните на /describe, чтобы посмотреть описание бота."
        )
    elif context.user_data.get("re_run"):
        await context.bot.send_message(
            chat_id=update._effective_chat.id,
            text="Кликните на /describe, чтобы посмотреть описание бота."
        )
    else:
        logger.info(f"Пользователь {update.effective_user.name}: запустить приложение")
        context.user_data["describe_message"] = (
            "Данный бот позволяет отслеживать изменение цен на товары, "
            "без необходимости вручную проверять данные на сайтах. Добавьте вещь в ваш список "
            "получайте уведомления, если товар станет дешевле или появится в ассортименте."
        )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=context.user_data["describe_message"]
        )

    await context.bot.send_message(
        text="Выберете действие:",
        chat_id=update.effective_chat.id, 
        reply_markup=reply_keyboard
    )

    context.user_data["re_run"] = True
    return MAIN_MENU_CHOOSE

async def get_discribe_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта функция реагирует на команду '/describe'
    и присылает сообщение с описанием функций бота.

    """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=context.user_data["describe_message"]
    )

    return MAIN_MENU_CHOOSE

async def get_current_user_list_of_items_and_message(username: str) -> Tuple[str, List[AddedItemRow]]:
    """
    Эта функция является вспомогательной.
    Возвращает текущие данные из таблицы, в которою пользователь добавлял свои вещи, 
    а также сообщение на основе этих данных. Результат возвращается в виде кортежа.

    """
    
    database_data: List[AddedItemRow] = await get_query_from_added_users_item_table_with_username(SessionLocal, username)

    counter = 0
    data_list: List[AddedItemRow] = []
    message_text = 'Текущий список:\n\n'

    for database_row in database_data:
        counter += 1
        message_text += f'{counter}: {database_row.item_url}\n'
        data_list.append(
            AddedItemRow(
                user_name=database_row.user_name,
                chat_id=database_row.chat_id,
                item_url=database_row.item_url,
                shop=database_row.shop
            )
        )

    return (message_text, data_list)

async def show_show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.name}: показать текущий список вещей")

    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Удалить вещь из списка")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    message_text, context.user_data["current_user_list_of_items"] = await get_current_user_list_of_items_and_message(update.effective_user.name)

    await context.bot.send_message(
        text=message_text,
        chat_id=update.effective_chat.id,
        disable_web_page_preview=True
    )

    await context.bot.send_message(
        text="Выберете действие:",
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return SHOW_MENU_CHOOSE

async def show_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await context.bot.send_message(
        text='Введите номер вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return DELETE_MENU_CHOOSE

async def back_from_show_menu_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

    return MAIN_MENU_CHOOSE


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    if 0 < int(update.message.text) <= len(context.user_data["current_user_list_of_items"]):
        user_name = context.user_data["current_user_list_of_items"][int(update.message.text)-1].user_name
        item_url = context.user_data["current_user_list_of_items"][int(update.message.text)-1].item_url
        shop = context.user_data["current_user_list_of_items"][int(update.message.text)-1].shop

        logger.info(f"Пользователь {update.effective_user.name}: удалить вещь из списка с сообщением '{update.message.text}'")
        await delete_row_from_added_users_item_table(SessionLocal, user_name, item_url, shop)

        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вещь удалена из списка')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы указали номер, которого не существует')

    message_text, context.user_data["current_user_list_of_items"] = await get_current_user_list_of_items_and_message(update.effective_user.name)

    await context.bot.send_message(
        text=message_text,
        chat_id=update.effective_chat.id,
        disable_web_page_preview=True
    )    

    await context.bot.send_message(
        text='Введите номер вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return DELETE_MENU_CHOOSE

async def show_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Rogov"), KeyboardButton("Red September")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    context.user_data["links_to_shop"] = {"Rogov": "rogovshop.ru", "Red September": "redseptemberdesign.com"}

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Выберете магазин в котором находится ваша вещь или нажмите "Назад", чтобы вернуться в главное меню:',
        reply_markup=reply_keyboard
    )

    return ADD_MENU_CHOOSE

async def show_add_url_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    if "/" not in update.message.text:
        context.user_data["current_shop_name"] = update.message.text

    context.user_data["enter_url_text_message"] = (
        f'Скопируйте ссылку на вашу вещь из магазина {context.user_data["links_to_shop"][context.user_data["current_shop_name"]]}'
        ' в строку или нажмите "Назад" для выхода в меню выбора магазина.\n\nКликните на /help_video, чтобы посмотреть видео-гайд. Загрузка видео займет некоторое время.'
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=context.user_data["enter_url_text_message"],
        reply_markup=reply_keyboard
    )

    return ADD_URL_MENU_CHOOSE

async def back_from_add_menu_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

    return MAIN_MENU_CHOOSE

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        url_from_message = update.message.text
        url_from_message = re.sub("(&page=[0-9]+$)|(\\?page=[0-9]+$)", "", url_from_message)
        

    logger.info(f"Пользователь {update.effective_user.name}: добавить вещь в список с сообщением '{update.message.text}'. Магазин: {context.user_data['current_shop_name']}")

    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    current_table: List[AddedItemRow] = await get_query_from_added_users_item_table(SessionLocal)

    data_to_add = AddedItemRow(
        user_name=update.effective_user.name,
        chat_id=update.effective_message.chat_id,
        item_url=url_from_message,
        shop=context.user_data["current_shop_name"]
    )

    if ''.join(data_to_add.shop.lower().split()) not in update.effective_message.text.lower().replace('-', ''):
        await context.bot.send_message(text="Ссылка должна принадлежать выбранному магазину", chat_id=update.effective_chat.id)
    elif data_to_add not in current_table:
        await set_data_to_added_users_item_table(SessionLocal, data=data_to_add)
        await context.bot.send_message(text="Вещь добавлена", chat_id=update.effective_message.chat_id)
    elif data_to_add in current_table:
        await context.bot.send_message(text="Вещь уже в списке", chat_id=update.effective_message.chat_id)

    await context.bot.send_message(
        text=context.user_data["enter_url_text_message"],
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return ADD_URL_MENU_CHOOSE

async def unrelevant_message_delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.name}: попытка удалить вещь из списка с сообщением '{update.message.text}'. Вещь не должна быть удалена")

    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вещь с этим id не удалена"
    )

    await context.bot.send_message(
        text='Введите номер вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return DELETE_MENU_CHOOSE

async def send_help_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Пользователь {update.effective_user.name}: показать видео-гайд")
    
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=open("media_content/add_tutorial.mp4", "rb")
    )

    await show_add_url_menu(update, context)

    return ADD_URL_MENU_CHOOSE

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка! Пользователь {update.effective_user.name}:", exc_info=context.error)

    if isinstance(context.error, TimedOut):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Упс, проблемы с сетью, повторите попытку позже."
        )

main_menu_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        MAIN_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Добавить вещь в список$"), show_add_item_menu),
            MessageHandler(filters.Regex("^Показать текущий список$"), show_show_menu),
            CommandHandler('describe', get_discribe_info)
        ],
        SHOW_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Удалить вещь из списка$"), show_delete_menu),
            MessageHandler(filters.Regex("^Назад$"), back_from_show_menu_to_main_menu)
        ],
        DELETE_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Назад$"), show_show_menu),
            MessageHandler(filters.Regex("^[0-9]+$"), delete_item),
            MessageHandler(filters.Regex("^(?!/start).+$"), unrelevant_message_delete_item)
        ],
        ADD_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Rogov$|^Red September$"), show_add_url_menu),
            MessageHandler(filters.Regex("^Назад$"), back_from_add_menu_to_main_menu)
        ],
        ADD_URL_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Назад$"), show_add_item_menu),
            CommandHandler("help_video", send_help_video),
            MessageHandler(filters.Regex("(^(?!/start).+$)"), add_item)
        ]
    },
    fallbacks=[CommandHandler("start", start_command)]
)

application = Application.builder().token(TOKEN).build()

application.add_handlers([main_menu_conversation_handler])
application.add_error_handler(error_handler)
application.run_polling()




import requests
import logging
import html
from typing import List, Dict, Tuple
from html.parser import HTMLParser
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters
from telegram.constants import ParseMode
from database_drivers.schemas import set_data_to_added_users_item_table
from database_drivers.schemas import get_query_from_added_users_item_table
from database_drivers.schemas import get_query_from_added_users_item_table_with_username
from database_drivers.schemas import delete_row_from_added_users_item_table

TOKEN = '6527820749:AAG1xmOjyVtGjsaGlGLu0TBCzXJgAzhdQbM'


MAIN_MENU, MAIN_MENU_FROM_OTHER_HANDLERS, MAIN_MENU_STOP_FROM_OTHER_HANDLERS, MAIN_MENU_ENTER_TO_ADD_MENU, MAIN_MENU_ENTER_TO_SHOW_MENU, MAIN_MENU_ENTER_TO_DEL_MENU = 10, 20, 30, 40, 50, 60

ADD_MENU, ADD_MENU_STOP_APP, STORE_MENU = 100, 200, 300

SHOW_MENU, DELETE_MENU = 1000, 2000


# logging.basicConfig(level=logging.info)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта команда показывает стартовое меню.

    """
    
    reply_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Добавить вещь в список', callback_data=f'{MAIN_MENU_ENTER_TO_ADD_MENU}')
            ],         
            [
                InlineKeyboardButton('Показать текущий список', callback_data=f'{MAIN_MENU_ENTER_TO_SHOW_MENU}')
            ]   
        ]
    )
    
    if update.message:
        if context.user_data.get("message_to_delete", None):
            requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["message_to_delete"]}')
            context.user_data["message_to_delete"] = None
        
        await context.bot.send_message(text='Чтобы выключить бота введите /stop', chat_id=update.effective_chat.id)
        await update.message.reply_text('Выберете действие:', reply_markup=reply_keyboard)

    elif update.callback_query:

        await update.callback_query.answer()
        await update.callback_query.edit_message_text('Выберете действие:', reply_markup=reply_keyboard)

    if update.message:
        context.user_data['current_message_to_delete_with_stop'] = update.message.id + 2
    if update.callback_query:
        context.user_data['current_message_to_delete_with_stop'] = update.callback_query.message.id

    return MAIN_MENU

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["current_message_to_delete_with_stop"]}')    
    context.user_data["current_message_to_delete_with_stop"] = None
    
    await update.message.reply_text('Бот выключен')

    return ConversationHandler.END

async def get_current_user_list_of_items_and_message(username: str) -> Tuple[str, List[Dict]]:
    """
    Эта функция является вспомогательной.
    Возвращает текущие данные из таблицы, в которою пользователь добавлял свои вещи, 
    а также сообщение на основе этих данных. Результат возвращается в виде кортежа.

    """
    
    database_data = await get_query_from_added_users_item_table_with_username(username)

    counter = 0
    data_list = []
    message_text = 'Текущий список:\n\n'

    for database_row in database_data:
        counter += 1
        message_text += f'{counter}: {database_row["item_url"]}\n'
        data_list.append(
            {
                "id": counter, 
                "user_name": database_row["user_name"], 
                "item_url": database_row["item_url"], 
                "store": database_row["store"]
            }
        )

    return (message_text, data_list)


async def show_current_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню, в котором отображаются добавленные пользователем вещи.

    """

    reply_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Удалить вещь из списка', callback_data='Delete item')],
            [InlineKeyboardButton('Назад', callback_data='Back to start menu')]
        ]
    )

    context.user_data["message_to_delete"] = update.callback_query.message.message_id
    context.user_data["current_user"] = update.callback_query.from_user.username
    context.user_data["current_list_message"], context.user_data["current_user_list_of_items"] = await get_current_user_list_of_items_and_message(context.user_data['current_user'])

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=context.user_data["current_list_message"], reply_markup=reply_keyboard, parse_mode=None)

    return SHOW_MENU
    
async def show_current_list_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показываетс меню в котором вещи можно удалить из списка желаемого.

    """


    reply_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Назад', callback_data='Back to show menu from delete menu')]
        ]
    )


    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=f'{context.user_data["current_list_message"]}\nВведите id вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления', reply_markup=reply_keyboard)
        context.user_data["message_to_delete"] = update.callback_query.message.message_id ### проверить id или message_id
    
    elif update.message:
        context.user_data["current_list_message"], context.user_data["current_user_list_of_items"] = await get_current_user_list_of_items_and_message(context.user_data['current_user'])
        context.user_data["message_to_delete"] = update.message.id + 2 ### проверить id или message_id
        await update.message.reply_text(text=f'{context.user_data["current_list_message"]}\nВведите id вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления', reply_markup=reply_keyboard)

    return DELETE_MENU

async def delete_item_in_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта функиция удаляет выбранную вещь.

    """
    
    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["message_to_delete"]}')
    context.user_data["message_to_delete"] = None

    if 0 < int(update.message.text) <= len(context.user_data["current_user_list_of_items"]):
        user_name = context.user_data["current_user_list_of_items"][int(update.message.text)-1]["user_name"]
        item_url = context.user_data["current_user_list_of_items"][int(update.message.text)-1]["item_url"]
        store = context.user_data["current_user_list_of_items"][int(update.message.text)-1]["store"]

        await delete_row_from_added_users_item_table(user_name, item_url, store)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вещь удалена из списка')

    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы указали номер, которого не существует')

    await show_current_list_delete_menu(update, context)

    return DELETE_MENU

async def catch_unrelevant_messages_in_delete_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта функция отлавливает нерелевантные сообщения 
    в меню удаления вещей.

    """

    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["message_to_delete"]}')
    context.user_data["message_to_delete"] = None
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Некорректная команда')
    await show_current_list_delete_menu(update, context)

    return DELETE_MENU

async def show_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Вызывает меню в котором отображаются доступные магазины. 
    Для добавления вещи в список желаемого, необходимо нажать на кнопку магазина.

    """
    
    reply_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Ushatava', callback_data='Ushatava'),
                InlineKeyboardButton('Street Beat', callback_data='Street Beat'),
            ],
            [
                InlineKeyboardButton('OSKELLY', callback_data='OSKELLY'),
                InlineKeyboardButton('SuperStep', callback_data='SuperStep'),
            ],
            [
                InlineKeyboardButton('Назад', callback_data='Back to start menu')
            ]
        ]
    )

    if update.callback_query:

        context.user_data["message_to_delete"] = update.callback_query.message.message_id
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text='Выберете магазин в котором находится ваша вещь или нажмите "Назад", чтобы вернуться в главное меню:',
            reply_markup=reply_keyboard
        )

    elif update.message:

        await update.message.reply_text(
            text='Выберете магазин в котором находится ваша вещь или нажмите "Назад", чтобы вернуться в главное меню:',
            reply_markup=reply_keyboard
        )
        context.user_data["message_to_delete"] = update.message.id + 2

    if update.message:
        context.user_data['current_message_to_delete_with_stop'] = update.message.id + 2

    return ADD_MENU

async def add_item_in_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Добавляет вещь в список желаемого.

    """
    
    current_table = await get_query_from_added_users_item_table()
    for row in current_table:
        row.pop('id')

    data_to_add = {'user_name': update.message.from_user.username, 'item_url': update.message.text, 'store': context.user_data['current_store_name']}

    if data_to_add not in current_table:
        await context.bot.send_message(text='Вещь добавлена', chat_id=update.effective_message.chat_id)
        await set_data_to_added_users_item_table(data=data_to_add)
    else:
        await context.bot.send_message(text='Вещь уже в списке', chat_id=update.effective_message.chat_id)

    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["message_to_delete"]}')
    context.user_data["message_to_delete"] = None

    await show_add_item_menu(update, context)

    return ADD_MENU

async def back_to_main_menu_from_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await start_command(update, context)

    return ConversationHandler.END
    
async def stop_command_from_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["current_message_to_delete_with_stop"]}')
    context.user_data["current_message_to_delete_with_stop"] = None 

    await update.message.reply_text('Бот выключен из add_menu')

    return ADD_MENU_STOP_APP

async def start_command_from_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта функция перезапускает приложение при вводе команды /start,
    если пользователь находится в меню добавления вещей.

    """

    requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteMessage?chat_id={update.effective_chat.id}&message_id={context.user_data["message_to_delete"]}')
    context.user_data["message_to_delete"] = None    

    await start_command(update, context)

    return ConversationHandler.END

async def show_store_menu_in_add_item_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Эта функция показывает меню выбранного магазина.
    
    """

    reply_keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('Назад', callback_data='Back to add item menu')]
        ]
    )

    context.user_data['current_store_name'] = update.callback_query.data

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        'Вставьте URL вашей вещи в строку или нажмите "Назад" для выхода в меню выбора магазина', 
        reply_markup=reply_keyboard
    )

    if update.callback_query:
        context.user_data['message_to_delete'] = update.callback_query.message.id

    return STORE_MENU

application = Application.builder().token(TOKEN).build()

adding_item_conversation = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(show_add_item_menu, pattern=f'^{MAIN_MENU_ENTER_TO_ADD_MENU}$')
    ],
    states={
        ADD_MENU: [
            CallbackQueryHandler(show_store_menu_in_add_item_menu, pattern='^Ushatava$|^Street Beat$|^OSKELLY$|^SuperStep$')
        ],
        STORE_MENU: [
            CallbackQueryHandler(show_add_item_menu, pattern='Back to add item menu'),
            MessageHandler(filters.TEXT, add_item_in_add_item_menu)
        ]
    },
    fallbacks=[
        CallbackQueryHandler(back_to_main_menu_from_add_item_menu, pattern='^Back to start menu$'),
        CommandHandler('stop', stop_command_from_add_item_menu),
        CommandHandler('start', start_command_from_add_item_menu)
    ],
    map_to_parent={
        ADD_MENU_STOP_APP: ConversationHandler.END
    }
)

main_menu_conversation = ConversationHandler(
    entry_points=[
        CommandHandler('start', start_command)
    ],
    states={
            MAIN_MENU: [
                CallbackQueryHandler(show_current_list_menu, pattern=f'^{MAIN_MENU_ENTER_TO_SHOW_MENU}$'),
                adding_item_conversation
            ],
            MAIN_MENU_FROM_OTHER_HANDLERS: [CallbackQueryHandler(start_command, pattern='^Back to start menu$')],
            SHOW_MENU: [
                CallbackQueryHandler(show_current_list_delete_menu, pattern='^Delete item$'),
                CallbackQueryHandler(start_command, pattern='^Back to start menu$')
            ],
            DELETE_MENU: [
                CallbackQueryHandler(show_current_list_menu, pattern='^Back to show menu from delete menu$'),
                MessageHandler(filters=filters.Regex('^[0-9]+$'), callback=delete_item_in_delete_menu),
                MessageHandler(filters.ALL, callback=catch_unrelevant_messages_in_delete_item_menu)
            ]
    },
    fallbacks=[
        CommandHandler('stop', stop_command),
        CommandHandler('start', start_command)
    ]
)
application.add_handler(main_menu_conversation)
application.run_polling()
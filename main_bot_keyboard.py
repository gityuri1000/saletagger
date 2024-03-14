from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, filters

TOKEN = '6527820749:AAG1xmOjyVtGjsaGlGLu0TBCzXJgAzhdQbM'

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

    await context.bot.send_message(
        text="Выберете действие:",
        chat_id=update.effective_chat.id, 
        reply_markup=reply_keyboard
    )

    return MAIN_MENU_CHOOSE


async def show_show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Удалить вещь из списка")],
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
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
        text='Введите id вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вещь удалена"
    )

    await context.bot.send_message(
        text='Введите id вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
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

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вставьте URL вашей вещи в строку или нажмите "Назад" для выхода в меню выбора магазина',
        reply_markup=reply_keyboard
    )

    return ADD_URL_MENU_CHOOSE

async def back_from_add_menu_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_command(update, context)

    return MAIN_MENU_CHOOSE

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вещь добавлена"
    )

    await context.bot.send_message(
        text='Вставьте URL вашей вещи в строку или нажмите "Назад" для выхода в меню выбора магазина',
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return ADD_URL_MENU_CHOOSE

async def unrelevant_message_delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        text='Введите id вещи, которую вы хотите удалить, или нажмите "Назад" для выхода из режима удаления',
        chat_id=update.effective_chat.id,
        reply_markup=reply_keyboard
    )

    return DELETE_MENU_CHOOSE


main_menu_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_command)],
    states={
        MAIN_MENU_CHOOSE: [
            MessageHandler(filters.Regex("^Добавить вещь в список$"), show_add_item_menu),
            MessageHandler(filters.Regex("^Показать текущий список$"), show_show_menu)
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
            MessageHandler(filters.Regex("^(?!/start).+$"), add_item)
        ]
    },
    fallbacks=[CommandHandler("start", start_command)]
)

application = Application.builder().token(TOKEN).build()

application.add_handlers([main_menu_conversation_handler])
application.run_polling()




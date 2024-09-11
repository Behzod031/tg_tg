from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import MessageHandler, Filter

# Вставь свой токен бота
TOKEN = '7063597194:AAHNYaA5qZYfq5OeX7g4f0wzOiNJ6TIymLM'

# Создай объект Updater и передай ему токен
updater = Updater(TOKEN)

# Получи диспетчер для регистрации обработчиков
dp = updater.dispatcher

# Удаляем вебхуки, если они установлены
updater.bot.delete_webhook()

# Определение функций обработчиков

def start(update: Update, context: CallbackContext):
    """Отправляет приветственное сообщение"""
    update.message.reply_text('Здравствуйте! Выберите филиал РОПа.')

def branch_selection(update: Update, context: CallbackContext):
    """Обрабатывает выбор филиала"""
    keyboard = [
        ['Vatan', 'Zo\'rsan'],
        ['Red house', 'Rohat'],
        ['Yunusobod']
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите филиал РОПа:', reply_markup=reply_markup)

def object_selection(update: Update, context: CallbackContext):
    """Обрабатывает выбор объекта"""
    branch = update.message.text
    if branch in ['Vatan', 'Zo\'rsan', 'Red house', 'Rohat', 'Yunusobod']:
        keyboard = [
            ['Vatan', 'Zo\'rsan'],
            ['Orzular', 'Parlament'],
            ['Vodiiy', 'Muhabbat shahri'],
            ['Salom Qo\'yliq', 'Ocean']
        ]
        reply_markup = telegram.ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        update.message.reply_text('Выберите объект:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Выберите филиал сначала.')

def handle_message(update: Update, context: CallbackContext):
    """Обрабатывает текстовые сообщения"""
    text = update.message.text
    if text in ['Vatan', 'Zo\'rsan', 'Red house', 'Rohat', 'Yunusobod']:
        branch_selection(update, context)
    elif text in ['Vatan', 'Zo\'rsan', 'Orzular', 'Parlament', 'Vodiiy', 'Muhabbat shahri', 'Salom Qo\'yliq', 'Ocean']:
        update.message.reply_text(f'Вы выбрали объект: {text}')
    else:
        update.message.reply_text('Неизвестная команда. Используйте команды выбора филиала или объекта.')

# Регистрируем обработчики команд и сообщений
dp.add_handler(CommandHandler('start', start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Запускаем поллинг
updater.start_polling()

# Останавливаем бота при получении сигнала завершения
updater.idle()

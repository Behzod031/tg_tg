import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import asyncio
import requests

# Этапы разговора
BRANCH, PROPERTY_CLASS, OBJECT, APARTMENT_COUNT, AMOUNT, CONFIRMATION, FINAL_CONFIRMATION = range(7)

# Клавиатуры для выбора вариантов
branch_keyboard = [['Vatan', 'Zo’rsan', 'Red House', 'Rohat', 'Yunusobod']]
property_class_keyboard = [['Квартира', 'Паркинг']]
object_keyboard = [['Vatan', 'Zo’rsan', 'Orzular', 'Parlament', 'Qo’yliq', 'Vodiiy', 'Muhabbat shahri', 'Ocean']]
confirmation_keyboard = [['Да', 'Нет']]
final_confirmation_keyboard = [['Подтверждаю', 'Не подтверждаю']]

# URL API Sheetsu
SHEETSU_API_URL = "https://sheetdb.io/api/v1/nsu9dn2lkthwl"  # Замените на ваш URL

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> int:
    context.user_data['data_list'] = []
    reply_markup = ReplyKeyboardMarkup(branch_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Выберите филиал:', reply_markup=reply_markup)
    return BRANCH


async def select_branch(update: Update, context: CallbackContext) -> int:
    context.user_data['branch'] = update.message.text
    reply_markup = ReplyKeyboardMarkup(property_class_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Выберите класс недвижимости:', reply_markup=reply_markup)
    return PROPERTY_CLASS


async def select_property_class(update: Update, context: CallbackContext) -> int:
    context.user_data['property_class'] = update.message.text
    reply_markup = ReplyKeyboardMarkup(object_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Выберите объект:', reply_markup=reply_markup)
    return OBJECT


async def select_object(update: Update, context: CallbackContext) -> int:
    context.user_data['object'] = update.message.text
    await update.message.reply_text('Введите количество квартир:')
    return APARTMENT_COUNT


async def input_apartment_count(update: Update, context: CallbackContext) -> int:
    context.user_data['apartment_count'] = update.message.text
    await update.message.reply_text('Введите сумму:')
    return AMOUNT


async def input_amount(update: Update, context: CallbackContext) -> int:
    context.user_data['amount'] = update.message.text
    reply_markup = ReplyKeyboardMarkup(confirmation_keyboard, one_time_keyboard=True)
    await update.message.reply_text('Подтвердите данные (Да/Нет):', reply_markup=reply_markup)
    return CONFIRMATION


async def confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Да':
        reply_markup = ReplyKeyboardMarkup(final_confirmation_keyboard, one_time_keyboard=True)
        await update.message.reply_text('Подтвердите финальное подтверждение:', reply_markup=reply_markup)
        return FINAL_CONFIRMATION
    else:
        await update.message.reply_text('Отменено. Попробуйте снова.')
        return ConversationHandler.END


async def final_confirmation(update: Update, context: CallbackContext) -> int:
    if update.message.text == 'Подтверждаю':
        # Формирование данных для отправки
        data = {
            "data": [{
                "Дата": "",
                "Филиал": context.user_data['branch'],
                "Объект": context.user_data['object'],
                "Класс недвижимости": context.user_data['property_class'],
                "Количество квартир": context.user_data['apartment_count'],
                "Сумма": context.user_data['amount']
            }]
        }

        # Отправка данных в Sheetsu
        try:
            response = requests.post(SHEETSU_API_URL, json=data)
            if response.status_code == 201:
                await update.message.reply_text('Данные успешно сохранены.')
            else:
                await update.message.reply_text(f'Произошла ошибка при сохранении данных: {response.text}')
        except Exception as e:
            logger.error(f'Ошибка при записи данных в Sheetsu: {e}')
            await update.message.reply_text('Произошла ошибка при сохранении данных.')
    else:
        await update.message.reply_text('Подтверждение отменено.')
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text('Операция отменена.')
    return ConversationHandler.END


# Обработчик ошибок
async def error_handler(update: Update, context: CallbackContext) -> None:
    logger.error(f'Update {update} caused error {context.error}')


def main() -> None:
    # Ваш токен бота
    TOKEN = '7546176223:AAFavj6PqY0qlLWldFUNLHqG8HMxltfoWVU'

    # Инициализация бота
    application = Application.builder().token(TOKEN).build()

    # Настройка ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BRANCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_branch)],
            PROPERTY_CLASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_property_class)],
            OBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_object)],
            APARTMENT_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_apartment_count)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_amount)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
            FINAL_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, final_confirmation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Добавление хендлера разговоров
    application.add_handler(conv_handler)

    # Добавление обработчика ошибок
    application.add_error_handler(error_handler)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()

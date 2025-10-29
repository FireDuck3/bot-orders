from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, ConversationHandler, filters
)

BOT_TOKEN = "7218519134:AAHRHXhHGBDdkrM_Sl7-gfW-xiZkUmT_D24"
ADMIN_ID = 1725226806  


ASK_NAME, ASK_PHONE, ASK_COURSE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Записатись на курс", callback_data="signup")],
        [InlineKeyboardButton("Про нас", callback_data="about")],
        [InlineKeyboardButton("Контакти", callback_data="contacts")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть дію:", reply_markup=markup)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signup":
        await query.edit_message_text("Введіть, будь ласка, ваше ім’я:")
        return ASK_NAME

    elif query.data == "about":
        await query.edit_message_text("Ми проводимо освітні курси з різних напрямів!")
        return ConversationHandler.END

    elif query.data == "contacts":
        await query.edit_message_text("Зв’яжіться з нами: @your_contact_username")
        return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Дякую! Тепер введіть ваш номер телефону:")
    return ASK_PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Курс по шахах", callback_data="chess")],
        [InlineKeyboardButton("Курс по дайвінгу", callback_data="diving")],
        [InlineKeyboardButton("Курс по їзді на конях", callback_data="horses")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть свій курс:", reply_markup=markup)
    return ASK_COURSE

async def get_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    course_map = {
        "chess": "Курс по шахах",
        "diving": "Курс по дайвінгу",
        "horses": "Курс по їзді на конях"
    }
    course = course_map.get(query.data, "Невідомий курс")
    context.user_data["course"] = course

    name = context.user_data.get("name")
    phone = context.user_data.get("phone")

    msg = (f"📩 Нова заявка!\n"
           f"👤 Ім’я: {name}\n"
           f"📞 Телефон: {phone}\n"
           f"📚 Курс: {course}")
    await context.bot.send_message(ADMIN_ID, msg)

    await query.edit_message_text("Дякую! Ваша заявка надіслана адміну ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Реєстрацію скасовано.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(main_menu_handler)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_COURSE: [CallbackQueryHandler(get_course)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()

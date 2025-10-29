from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, ConversationHandler, filters
)

BOT_TOKEN = "YOUR_TOKEN_HERE"
ADMIN_ID = 123456789  # Replace with your Telegram ID

# Conversation states
ASK_NAME, ASK_PHONE, ASK_COURSE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Register for a Course", callback_data="signup")],
        [InlineKeyboardButton("About Us", callback_data="about")],
        [InlineKeyboardButton("Contacts", callback_data="contacts")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose an action:", reply_markup=markup)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "signup":
        await query.edit_message_text("Please enter your name:")
        return ASK_NAME

    elif query.data == "about":
        await query.edit_message_text("We provide educational courses in various fields!")
        return ConversationHandler.END

    elif query.data == "contacts":
        await query.edit_message_text("Contact us: @your_contact_username")
        return ConversationHandler.END


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Thank you! Now enter your phone number:")
    return ASK_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Chess Course", callback_data="chess")],
        [InlineKeyboardButton("Diving Course", callback_data="diving")],
        [InlineKeyboardButton("Horse Riding Course", callback_data="horses")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Please choose your course:", reply_markup=markup)
    return ASK_COURSE


async def get_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    course_map = {
        "chess": "Chess Course",
        "diving": "Diving Course",
        "horses": "Horse Riding Course"
    }
    course = course_map.get(query.data, "Unknown Course")
    context.user_data["course"] = course

    name = context.user_data.get("name")
    phone = context.user_data.get("phone")

    msg = (f"📩 New Registration!\n"
           f"👤 Name: {name}\n"
           f"📞 Phone: {phone}\n"
           f"📚 Course: {course}")
    await context.bot.send_message(ADMIN_ID, msg)

    await query.edit_message_text("Thank you! Your application has been sent to the admin ✅")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration cancelled.")
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

import os
import threading
from flask import Flask
from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, PreCheckoutQueryHandler, CallbackQueryHandler
)

TOKEN = os.environ.get("BOT_TOKEN")
flask_app = Flask(__name__)
user_lang = {}

TEXTS = {
    "fr": {"welcome": "Salut ! Je suis en ligne et je fonctionne bien.\nTape /premium pour débloquer l'accès illimité.", "thanks": "Merci pour ton achat ! Ton accès premium est activé. 🎉"},
    "en": {"welcome": "Hi! I'm online and working well.\nType /premium to unlock unlimited access.", "thanks": "Thank you for your purchase! Your premium access is now active. 🎉"},
    "ar": {"welcome": "مرحبا! أنا متصل وأعمل بشكل جيد.\nاكتب /premium لفتح الوصول غير المحدود.", "thanks": "شكرا لشرائك! تم تفعيل وصولك المميز. 🎉"},
    "es": {"welcome": "¡Hola! Estoy en línea y funciono bien.\nEscribe /premium para desbloquear el acceso ilimitado.", "thanks": "¡Gracias por tu compra! Tu acceso premium está activo. 🎉"},
    "ru": {"welcome": "Привет! Я в сети и хорошо работаю.\nНапиши /premium, чтобы открыть неограниченный доступ.", "thanks": "Спасибо за покупку! Твой премиум-доступ активирован. 🎉"},
}

@flask_app.route("/")
def home():
    return "Le bot est en ligne."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Français", callback_data="lang_fr"), InlineKeyboardButton("English", callback_data="lang_en")],
        [InlineKeyboardButton("العربية", callback_data="lang_ar"), InlineKeyboardButton("Español", callback_data="lang_es")],
        [InlineKeyboardButton("Русский", callback_data="lang_ru")],
    ]
    await update.message.reply_text("Choisis ta langue / Choose your language 👇", reply_markup=InlineKeyboardMarkup(keyboard))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = query.data.replace("lang_", "")
    user_lang[query.from_user.id] = lang
    await query.answer()
    await query.edit_message_text(TEXTS[lang]["welcome"])

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_invoice(
        chat_id=update.effective_chat.id,
        title="Premium",
        description="Débloque l'accès illimité au bot",
        payload="premium_subscription",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Premium", 100)],
    )

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = user_lang.get(update.effective_user.id, "fr")
    await update.message.reply_text(TEXTS[lang]["thanks"])

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CallbackQueryHandler(set_language, pattern="^lang_"))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.run_polling()
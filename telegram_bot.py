import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import telegraph
import time
from datetime import datetime

# Bot configuration
TOKEN = "YOUR_BOT_TOKEN"
OWNER_ID = "YOUR_OWNER_ID"
REQUIRED_CHANNELS = ["@channel1", "@channel2"]
TELEGRAPH_TOKEN = "YOUR_TELEGRAPH_TOKEN"

# Database simulation (replace with actual database)
user_data = {}
payment_requests = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check channel membership
    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                keyboard = [[InlineKeyboardButton("Join Channels", callback_data="join_channels")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "Please join our channels first!",
                    reply_markup=reply_markup
                )
                return
        except:
            await update.message.reply_text(f"Please join {channel} first!")
            return

    # Show main menu
    keyboard = [
        ["💰 Deposit", "👤 Profile"],
        ["📊 Status"],
        ["📱 INSTA REPORT", "📱 TG REPORT"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Generate QR code using Telegraph
    telegraph_client = telegraph.Telegraph(TELEGRAPH_TOKEN)
    qr_path = "path_to_qr_code.png"  # Generate QR code here
    
    keyboard = [
        [InlineKeyboardButton("Contact", url=f"tg://user?id={OWNER_ID}")],
        [InlineKeyboardButton("Submit Payment", callback_data="submit_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Scan QR code to deposit:\n[QR Code Link]",
        reply_markup=reply_markup
    )

async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_data.get(user_id, {"total_amount": 0, "name": update.effective_user.first_name})
    
    keyboard = [[InlineKeyboardButton("Payment History", callback_data="payment_history")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Profile:\nName: {user['name']}\nID: {user_id}\nTotal Amount: ₹{user['total_amount']}",
        reply_markup=reply_markup
    )

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = len(user_data)
    await update.message.reply_text(f"Total Users: {total_users}")

async def handle_tg_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_data.get(user_id, {"balance": 0})
    
    if user["balance"] >= 20:
        await update.message.reply_text("Enter target user ID for reporting (8 reports):")
        context.user_data["report_mode"] = "tg"
    else:
        await update.message.reply_text("Insufficient balance. Minimum ₹20 required for 8 reports.")

async def handle_insta_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = user_data.get(user_id, {"balance": 0})
    
    if user["balance"] >= 20:
        await update.message.reply_text("Enter Instagram username for reporting (8 reports):")
        context.user_data["report_mode"] = "insta"
    else:
        await update.message.reply_text("Insufficient balance. Minimum ₹20 required for 8 reports.")

async def handle_payment_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.message.reply_text("Enter the amount you paid:")
    context.user_data["awaiting_payment_amount"] = True

async def handle_payment_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_payment_amount" not in context.user_data:
        return
    
    amount = update.message.text
    user_id = update.effective_user.id
    
    try:
        amount = float(amount)
        payment_requests[user_id] = amount
        
        # Notify owner
        keyboard = [
            [
                InlineKeyboardButton("Accept", callback_data=f"accept_{user_id}_{amount}"),
                InlineKeyboardButton("Decline", callback_data=f"decline_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"New payment request:\nUser: {user_id}\nAmount: ₹{amount}",
            reply_markup=reply_markup
        )
        
        await update.message.reply_text("Payment submission received. Waiting for approval.")
        del context.user_data["awaiting_payment_amount"]
    except:
        await update.message.reply_text("Please enter a valid amount.")

async def handle_report_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "report_mode" not in context.user_data:
        return
    
    target = update.message.text
    mode = context.user_data["report_mode"]
    
    for i in range(8):
        await update.message.reply_text(f"Reporting {target} ({i+1}/8)...")
        await asyncio.sleep(3)
    
    await update.message.reply_text("Reporting completed!")
    del context.user_data["report_mode"]

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^💰 Deposit$"), handle_deposit))
    application.add_handler(MessageHandler(filters.Regex("^👤 Profile$"), handle_profile))
    application.add_handler(MessageHandler(filters.Regex("^📊 Status$"), handle_status))
    application.add_handler(MessageHandler(filters.Regex("^📱 TG REPORT$"), handle_tg_report))
    application.add_handler(MessageHandler(filters.Regex("^📱 INSTA REPORT$"), handle_insta_report))
    application.add_handler(CallbackQueryHandler(handle_payment_submission, pattern="^submit_payment$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report_target))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import telegraph
import time
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv("7869282132:AAFPwZ8ZrFNQxUOPgAbgDm1oInXzDx5Wk74")
OWNER_ID = os.getenv("7548678061")
REQUIRED_CHANNELS = ["@Teamsankinetworkk", "@SankiProfession"]
TELEGRAPH_TOKEN = os.getenv("https://graph.org/file/42f55ac11d620daa28dbb-26f56822035c88260f.jpg")
MONGODB_URL = os.getenv("mongodb+srv://tsgcoder:tsgcoder@cluster0.1sodg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# MongoDB setup
client = MongoClient(MONGODB_URL)
db = client['telegram_bot']
users_collection = db['users']
payments_collection = db['payments']
reports_collection = db['reports']

# Telegraph setup
telegraph_client = telegraph.Telegraph(TELEGRAPH_TOKEN)

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

    # Create/Update user in MongoDB
    users_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": update.effective_user.username,
                "first_name": update.effective_user.first_name,
                "last_login": datetime.now()
            }
        },
        upsert=True
    )

    # Show main menu
    keyboard = [
        ["💰 Deposit", "👤 Profile"],
        ["📊 Status"],
        ["📱 INSTA REPORT", "📱 TG REPORT"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def handle_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Upload QR code to Telegraph
    qr_path = "path_to_qr_code.png"  # Generate QR code here
    with open(qr_path, 'rb') as f:
        telegraph_response = telegraph_client.upload_file(f)
        qr_url = f"https://telegra.ph{telegraph_response[0]['src']}"
    
    keyboard = [
        [InlineKeyboardButton("Contact", url=f"tg://user?id={OWNER_ID}")],
        [InlineKeyboardButton("Submit Payment", callback_data="submit_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Scan QR code to deposit:\n{qr_url}",
        reply_markup=reply_markup
    )

async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        user_data = {
            "total_amount": 0,
            "name": update.effective_user.first_name
        }
    
    keyboard = [[InlineKeyboardButton("Payment History", callback_data="payment_history")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Profile:\nName: {user_data['name']}\nID: {user_id}\nTotal Amount: ₹{user_data.get('total_amount', 0)}",
        reply_markup=reply_markup
    )

async def handle_payment_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    payments = payments_collection.find({"user_id": user_id}).sort("timestamp", -1)
    
    history_text = "Payment History:\n\n"
    for payment in payments:
        date = payment['timestamp'].strftime("%Y-%m-%d %H:%M")
        history_text += f"Amount: ₹{payment['amount']} - {date}\n"
    
    await update.callback_query.message.reply_text(history_text)

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = users_collection.count_documents({})
    await update.message.reply_text(f"Total Users: {total_users}")

async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE, report_type="tg"):
    user_id = update.effective_user.id
    user_data = users_collection.find_one({"user_id": user_id})
    
    if not user_data or user_data.get('balance', 0) < 20:
        await update.message.reply_text("Insufficient balance. Minimum ₹20 required for 8 reports.")
        return
    
    await update.message.reply_text(f"Enter {'Telegram ID' if report_type == 'tg' else 'Instagram username'} for reporting (8 reports):")
    context.user_data["report_mode"] = report_type

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
        # Store payment request in MongoDB
        payments_collection.insert_one({
            "user_id": user_id,
            "amount": amount,
            "status": "pending",
            "timestamp": datetime.now()
        })
        
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

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^💰 Deposit$"), handle_deposit))
    application.add_handler(MessageHandler(filters.Regex("^👤 Profile$"), handle_profile))
    application.add_handler(MessageHandler(filters.Regex("^📊 Status$"), handle_status))
    application.add_handler(MessageHandler(filters.Regex("^📱 TG REPORT$"), 
                                         lambda update, context: handle_report(update, context, "tg")))
    application.add_handler(MessageHandler(filters.Regex("^📱 INSTA REPORT$"), 
                                         lambda update, context: handle_report(update, context, "insta")))
    application.add_handler(CallbackQueryHandler(handle_payment_submission, pattern="^submit_payment$"))
    application.add_handler(CallbackQueryHandler(handle_payment_history, pattern="^payment_history$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_payment_amount))
    
    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()

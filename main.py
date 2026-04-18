import logging
import asyncio
import re
import os
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- Render အတွက် ၂၄ နာရီ နိုးနေစေမယ့် Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "Dark Secret Bot is Alive 24/7!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- အချက်အလက်များ ---
TOKEN = '8640690172:AAFOBdHGfdtItAaJnBqkYSV-yyPJXsuAaYw'
OWNER_ID = 7079259609 

# Admin က ပို့လိုက်တဲ့ message ID တွေကို သိမ်းထားဖို့
admin_sent_messages = {}

# --- Start Menu ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("VIP ဝင်ပါမယ်", callback_data='join_vip')],
        [InlineKeyboardButton("VIP အကြောင်း သိချင်ပါတယ်", callback_data='info_vip')],
        [InlineKeyboardButton("မဝင်တော့ပါ", callback_data='exit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "<b>Dark Secret Opportunities</b>\n\n"
        "- VIP Membership is Lifetime\n\n"
        "ဆက်လက် လုပ်ဆောင်ရန် အောက်က ခလုတ်များကို ရွေးချယ်ပါ။"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')

# --- ခလုတ်များ Logic ---
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == 'info_vip':
        info_text = (
            "<b>VIP အကြောင်း အသေးစိတ် ⭐</b>\n\n"
            "Special VIP Details ⭐\n"
            "( 10000 MMK - တစ်သက်စာ အပြီး )\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "Premium Vip Details ⭐\n"
            "( 20000 MMK -- တစ်သက်စာ အပြီး )\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "Diamond VIP Details ⭐ ( For Boss 😎 )\n"
            "( 30000 MMK -- တစ်သက်စာ အပြီး)\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "ပိုမို သိရှိရန်အတွက် အောက်က လင့်ကို နှိပ်ပါ။"
        )
        keyboard = [[InlineKeyboardButton("🔗 ပိုမို သိရှိရန်", url='https://t.me/abtdarksecretvip/3')],
                    [InlineKeyboardButton("🔙 နောက်ပြန်ဆုတ်ရန်", callback_data='back_to_main')]]
        await query.edit_message_text(text=info_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

    elif data == 'join_vip':
        payment_text = (
            "<b>Dark Secret တစ်သက်စာဝင်ခ [ Life Time ]</b>\n\n"
            "Payment For Dark Secret Premium VIP\n\n"
            "💵 <b>KBZPay Account</b>\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "Name  :  Kyaw Swar Win\n\n"
            "Phone : <code>09893426849</code>\n\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "💴 <b>WavePay Account</b>\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "Name  : Kyaw Swar Win\n\n"
            "Phone : <code>09459934749</code>\n\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            "ငွေလွှဲ ပီးပြီးပါက ငွေလွှဲပြေစာ ပို့ပေးဖို့ တောင်းဆိုပါတယ်။"
        )
        await query.edit_message_text(text=payment_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 နောက်ပြန်ဆုတ်ရန်", callback_data='back_to_main')]]), parse_mode='HTML')

    elif data == 'exit':
        await query.edit_message_text("ကျေးဇူးတင်ပါတယ်ဗျ။ နောက်လည်း လာအားပေးနိုင်ပါတယ်!", 
                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 နောက်ပြန်ဆုတ်ရန်", callback_data='back_to_main')]]))

    elif data == 'back_to_main':
        await start(update, context)

    # --- Admin Controls (Confirm/Cancel/Retry) ---
    elif data.startswith('admin_'):
        parts = data.split('_')
        action, user_id = parts[1], int(parts[2])
        original_caption = query.message.caption

        if action == 'confirm':
            confirm_text = "✅ <b>Owner ဘက်မှ အချက်အလက်ကို အတည်ပြုလိုက်ပါပြီဗျ။</b>\n\nလူကြီးမင်းအတွက် VIP Group Link လေး ပို့ပေးလိုက်ပါပြီဗျ။"
            link_kb = [[InlineKeyboardButton("🔓 VIP Group သို့ဝင်ရန်", url='https://t.me/+OOB0ZgrSFkgwMzY1')]]
            sent_msg = await context.bot.send_message(chat_id=user_id, text=confirm_text, reply_markup=InlineKeyboardMarkup(link_kb), parse_mode='HTML')
            admin_sent_messages[user_id] = sent_msg.message_id
            
            retry_kb = [[InlineKeyboardButton("🔄 ပြန်လည်ရွေးချယ်ရန်", callback_data=f"admin_retry_{user_id}")]]
            await query.edit_message_caption(caption=f"{original_caption}\n\n✅ <b>အတည်ပြုထားပါသည်</b>", reply_markup=InlineKeyboardMarkup(retry_kb), parse_mode='HTML')

        elif action == 'cancel':
            cancel_msg = "❌ <b>လူကြီးမင်း၏ Payment စစ်ဆေးရာတွင် မှားယွင်းနေပါသည်။ ကျေးဇူးပြု၍ ပြန်လည်စစ်ဆေးပေးပါ။</b>"
            sent_msg = await context.bot.send_message(chat_id=user_id, text=cancel_msg, parse_mode='HTML')
            admin_sent_messages[user_id] = sent_msg.message_id
            
            retry_kb = [[InlineKeyboardButton("🔄 ပြန်လည်ရွေးချယ်ရန်", callback_data=f"admin_retry_{user_id}")]]
            await query.edit_message_caption(caption=f"{original_caption}\n\n❌ <b>ငြင်းပယ်ထားပါသည်</b>", reply_markup=InlineKeyboardMarkup(retry_kb), parse_mode='HTML')

        elif action == 'retry':
            # User ဆီ ပို့ထားတာကို Delete လုပ်ခြင်း
            if user_id in admin_sent_messages:
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=admin_sent_messages[user_id])
                except:
                    pass
            
            # မူလ Button ကို ပြန်ပြောင်းခြင်း (Caption အဟောင်းကို မပျက်အောင် ထိန်းထားသည်)
            admin_kb = [[InlineKeyboardButton("✅ Confirm", callback_data=f"admin_confirm_{user_id}"),
                         InlineKeyboardButton("❌ Cancel", callback_data=f"admin_cancel_{user_id}")]]
            
            # Caption ထဲက အတည်ပြုချက်စာသားကို ဖယ်ပြီး မူလအချက်အလက်ကိုပဲ ထားခြင်း
            clean_caption = original_caption.split('\n\n✅')[0].split('\n\n❌')[0]
            await query.edit_message_caption(caption=clean_caption, reply_markup=InlineKeyboardMarkup(admin_kb), parse_mode='HTML')

# --- Owner ID: Message (Reply Function) ---
async def handle_owner_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != OWNER_ID: return
    text = update.message.text
    # 7079259609 : စာသား ပုံစံဖြင့် စာပြန်ခြင်း
    match = re.match(r'^(\d+)\s*:\s*(.*)', text)
    if match:
        target_id, reply_text = int(match.group(1)), match.group(2)
        try:
            await context.bot.send_message(chat_id=target_id, text=reply_text)
            await update.message.reply_text(f"✅ User {target_id} ထံ စာပို့ပြီးပါပြီ။")
        except:
            await update.message.reply_text("❌ ပို့လို့မရပါ။ User က Bot ကို Block ထားနိုင်ပါတယ်။")

# --- Screenshot Received ---
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text("စလစ် ကို လက်ခံရရှိပါပြီ။ ခေတ္တစောင့်ဆိုင်းပေးပါဗျ။")
    
    admin_kb = [[InlineKeyboardButton("✅ Confirm", callback_data=f"admin_confirm_{user.id}"),
                 InlineKeyboardButton("❌ Cancel", callback_data=f"admin_cancel_{user.id}")]]
    
    await context.bot.send_photo(
        chat_id=OWNER_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"🔔 <b>စလစ်အသစ် ရောက်ရှိလာပါပြီ</b>\nName: {user.first_name}\nID: <code>{user.id}</code>",
        reply_markup=InlineKeyboardMarkup(admin_kb),
        parse_mode='HTML'
    )

if __name__ == '__main__':
    keep_alive() # Web Server စတင်ခြင်း
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_owner_message))
    print("Dark Secret Bot is running successfully with 24/7 Hosting...")
    application.run_polling()

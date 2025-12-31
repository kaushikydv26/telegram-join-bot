from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3, random, string

BOT_TOKEN = "7933292406:AAHaF1JJznyI779zl25CWaxRenbKNQisHz8"

CHANNELS = ["@Voucher_Vault"]

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, code TEXT)")
db.commit()

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{c[1:]}")] for c in CHANNELS]
    buttons.append([InlineKeyboardButton("✅ I've Joined", callback_data="check")])
    await update.message.reply_text(
        "Join all channels then click **I've Joined**",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id

    for ch in CHANNELS:
        member = await context.bot.get_chat_member(ch, uid)
        if member.status not in ("member", "administrator", "creator"):
            await q.answer("❌ Join all channels first", show_alert=True)
            return

    cur.execute("SELECT code FROM users WHERE id=?", (uid,))
    row = cur.fetchone()

    if row:
        code = row[0]
    else:
        code = gen_code()
        cur.execute("INSERT INTO users VALUES (?,?)", (uid, code))
        db.commit()

    await q.message.delete()
    await q.message.chat.send_message(
        f"✅ Verified\n\n🎟 Your Code:\n`{code}`",
        parse_mode="Markdown"
    )

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(check, pattern="check"))
app.run_polling()

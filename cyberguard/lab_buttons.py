"""Telegram handlers for the isolated Cyber Range lab manager."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes
from .labs import LabManager

manager = LabManager()

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧪 إنشاء مختبر", callback_data="lab:create")],
        [InlineKeyboardButton("📊 المختبرات", callback_data="lab:list")],
        [InlineKeyboardButton("▶️ تشغيل", callback_data="lab:run")],
        [InlineKeyboardButton("⏹️ إيقاف", callback_data="lab:stop")],
        [InlineKeyboardButton("🔄 إعادة ضبط", callback_data="lab:reset")],
    ])

async def show_labs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Cyber Range\nاختر العملية:", reply_markup=keyboard())

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    action = q.data.split(":", 1)[1]

    if action == "create":
        lab = manager.create(uid)
        await q.edit_message_text(f"✅ تم إنشاء المختبر\n🆔 {lab.lab_id}\n📊 الحالة: {lab.status}", reply_markup=keyboard())
        return

    labs = [x for x in manager.list() if x.owner_id == uid]
    if not labs:
        await q.edit_message_text("ℹ️ لا يوجد لديك مختبر. أنشئ مختبرًا أولًا.", reply_markup=keyboard())
        return
    lab = labs[-1]
    if action == "list":
        text = "📊 مختبراتك:\n\n" + "\n".join(f"🆔 {x.lab_id}\n📌 {x.name}\n⚙️ {x.status}" for x in labs)
    elif action in {"run", "stop", "reset"}:
        status = {"run":"running", "stop":"stopped", "reset":"reset"}[action]
        lab = manager.set_status(lab.lab_id, status)
        text = f"✅ تم تحديث المختبر\n🆔 {lab.lab_id}\n⚙️ الحالة: {lab.status}"
    else:
        text = "⚠️ العملية غير معروفة."
    await q.edit_message_text(text, reply_markup=keyboard())

def handlers():
    return [CallbackQueryHandler(callback, pattern=r"^lab:")]

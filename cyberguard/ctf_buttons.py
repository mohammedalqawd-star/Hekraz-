"""Telegram UI for safe local CTF challenges."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from .ctf import get_challenges


def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Beginner", callback_data="ctflevel:Beginner"), InlineKeyboardButton("🟡 Intermediate", callback_data="ctflevel:Intermediate")],
        [InlineKeyboardButton("📋 كل التحديات", callback_data="ctfall")],
        [InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")],
    ])


def challenge_menu(level=None):
    challenges = get_challenges(level)
    rows = [[InlineKeyboardButton(f"🧩 {c.title} · {c.points} نقطة", callback_data=f"ctfchallenge:{c.id}")] for c in challenges]
    rows.append([InlineKeyboardButton("⬅️ CTF Academy", callback_data="ctf")])
    return InlineKeyboardMarkup(rows)


def challenge_text(challenge):
    return (f"🏆 {challenge.title}\n\n"
            f"📊 المستوى: {challenge.level}\n"
            f"🎯 الهدف:\n{challenge.objective}\n\n"
            f"💡 التلميح:\n{challenge.hint}\n\n"
            f"🧪 هذا التحدي يعمل على بيانات تدريبية محلية فقط.")

async def show_ctf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🏆 CTF Academy\n\nتحديات تدريبية آمنة داخل Cyber Range.\nاختر المستوى:"
    await update.message.reply_text(text, reply_markup=menu())

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action, value = q.data.split(":", 1) if ":" in q.data else (q.data, "")
    if action == "ctflevel":
        await q.edit_message_text(f"🏆 {value}\n\nاختر تحديًا:", reply_markup=challenge_menu(value))
    elif action == "ctfall":
        await q.edit_message_text("🏆 كل التحديات\n\nاختر تحديًا:", reply_markup=challenge_menu())
    elif action == "ctfchallenge":
        challenge = next((c for c in get_challenges() if c.id == value), None)
        if not challenge:
            await q.edit_message_text("❌ التحدي غير موجود.", reply_markup=menu())
        else:
            await q.edit_message_text(challenge_text(challenge), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ التحديات", callback_data=f"ctflevel:{challenge.level}")]]))
    await q.answer()

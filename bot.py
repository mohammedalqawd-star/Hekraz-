import logging
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB = os.getenv("DB_PATH", "cyberguard.db")


def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS users (telegram_id INTEGER PRIMARY KEY, first_seen TEXT DEFAULT CURRENT_TIMESTAMP)")
        con.execute("CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")


def audit(user_id: int, action: str):
    with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO audit_logs(user_id, action) VALUES (?, ?)", (user_id, action))


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ الأمن الدفاعي", callback_data="defensive"), InlineKeyboardButton("🧪 المختبرات", callback_data="labs")],
        [InlineKeyboardButton("🌍 أمن الويب", callback_data="web"), InlineKeyboardButton("🌐 أمن الشبكات", callback_data="network")],
        [InlineKeyboardButton("🏆 CTF Academy", callback_data="ctf"), InlineKeyboardButton("🧠 Cyber AI", callback_data="ai")],
        [InlineKeyboardButton("🎯 MITRE ATT&CK", callback_data="mitre"), InlineKeyboardButton("🚨 الاستجابة للحوادث", callback_data="ir")],
        [InlineKeyboardButton("🦠 تحليل البرمجيات", callback_data="malware"), InlineKeyboardButton("📊 التقارير", callback_data="reports")],
        [InlineKeyboardButton("🧰 مركز الأدوات", callback_data="tools"), InlineKeyboardButton("👤 حسابي", callback_data="account")],
    ])


def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with sqlite3.connect(DB) as con:
        con.execute("INSERT OR IGNORE INTO users(telegram_id) VALUES (?)", (user.id,))
    audit(user.id, "start")
    await update.message.reply_text(
        "🛡️ CyberGuard AI\n\nمنصة تعليمية للأمن السيبراني والمختبرات المعزولة وCTF.\n\n⚠️ الاختبارات العملية مخصصة للأنظمة المملوكة أو المصرح بها فقط.",
        reply_markup=main_menu(),
    )


TEXT = {
    "defensive": ("🛡️ الأمن الدفاعي", "تحليل السجلات، كشف التهديدات، تقوية الأنظمة، وإرشادات الاستجابة."),
    "labs": ("🧪 المختبرات", "مختبرات تدريب معزولة وCTF لتعلم الاختبار الأمني دون استهداف أنظمة حقيقية."),
    "web": ("🌍 أمن الويب", "شرح OWASP Top 10، طرق الاكتشاف داخل المختبر، الأثر، الحماية والإصلاح."),
    "network": ("🌐 أمن الشبكات", "مفاهيم DNS وHTTP وTLS وحركة المرور والجدران النارية وIDS/IPS."),
    "ctf": ("🏆 CTF Academy", "مسارات Beginner وIntermediate وAdvanced مع تحديات تدريبية آمنة."),
    "ai": ("🧠 Cyber AI", "مساعد يشرح المفاهيم الأمنية والسجلات والتنبيهات والكود الآمن."),
    "mitre": ("🎯 MITRE ATT&CK", "تعلم التكتيكات والتقنيات مع التركيز على الكشف والتخفيف داخل بيئة تدريبية."),
    "ir": ("🚨 الاستجابة للحوادث", "تدريب على الكشف والتحقيق والاحتواء والقضاء والاسترداد والتقرير."),
    "malware": ("🦠 تحليل البرمجيات", "تحليل ثابت وآمن للتجزئة والبيانات الوصفية والسلاسل وIOC ومفاهيم YARA داخل المختبر."),
    "reports": ("📊 التقارير", "إنشاء تقارير تدريبية منظمة للنتائج والمخاطر والتوصيات."),
    "tools": ("🧰 مركز الأدوات", "شرح الأدوات ووظيفتها ومتطلباتها واستخدامها داخل المختبر فقط. لا توجد أزرار وهمية."),
    "account": ("👤 حسابي", "حساب Telegram وسجل الأنشطة التعليمية."),
}


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    audit(q.from_user.id, q.data)
    if q.data == "home":
        await q.edit_message_text("🛡️ CyberGuard AI\n\nاختر قسمًا:", reply_markup=main_menu())
        return
    title, body = TEXT.get(q.data, ("غير متاح", "هذه الوظيفة غير متاحة حاليًا."))
    await q.edit_message_text(f"{title}\n\n📌 ماذا يفعل؟\n{body}\n\n🔐 الاستخدام العملي محصور بالمختبرات المعزولة والأنظمة المصرح بها.", reply_markup=back_menu())


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return
    await update.message.reply_text("👑 لوحة المشرف\n\nالمستخدمون والسجلات وقاعدة البيانات الأساسية جاهزة للتوسعة.")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود في متغيرات البيئة")
    init_db()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.run_polling()

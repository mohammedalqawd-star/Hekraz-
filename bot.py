import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from cyberguard.storage import Storage
from cyberguard.admin_service import AdminService

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB = os.getenv("DB_PATH", "cyberguard.db")

storage = Storage(DB)
admin_service = AdminService(storage)


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


def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"), InlineKeyboardButton("👥 المستخدمون", callback_data="admin_users")],
        [InlineKeyboardButton("🔐 الأدوار", callback_data="admin_roles"), InlineKeyboardButton("🧪 المختبرات", callback_data="admin_labs")],
        [InlineKeyboardButton("📋 التفويضات", callback_data="admin_auth"), InlineKeyboardButton("🧾 سجل التدقيق", callback_data="admin_audit")],
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")],
    ])


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    storage.ensure_user(user.id, "admin" if user.id == ADMIN_ID else "user")
    storage.audit(user.id, "start")
    await update.message.reply_text(
        "🛡️ CyberGuard AI\n\nمنصة تعليمية للأمن السيبراني والمختبرات المعزولة وCTF.\n\n⚠️ الاختبارات العملية مخصصة للأنظمة المملوكة أو المصرح بها فقط.",
        reply_markup=main_menu(),
    )


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    storage.ensure_user(user_id, "admin" if user_id == ADMIN_ID else "user")
    storage.audit(user_id, q.data)

    if q.data == "home":
        await q.edit_message_text("🛡️ CyberGuard AI\n\nاختر قسمًا:", reply_markup=main_menu())
        return

    if q.data.startswith("admin_"):
        if not admin_service.is_admin(user_id):
            await q.edit_message_text("⛔ هذه الوظيفة للمشرف فقط.", reply_markup=back_menu())
            return
        await admin_callback(q, context)
        return

    title, body = TEXT.get(q.data, ("غير متاح", "هذه الوظيفة غير متاحة حاليًا."))
    await q.edit_message_text(
        f"{title}\n\n📌 ماذا يفعل؟\n{body}\n\n🔐 الاستخدام العملي محصور بالمختبرات المعزولة والأنظمة المصرح بها.",
        reply_markup=back_menu(),
    )


async def admin_callback(q, context):
    user_id = q.from_user.id
    action = q.data
    if action == "admin_stats":
        users = admin_service.users(user_id)
        audits = admin_service.audit_logs(user_id, 100000)
        await q.edit_message_text(f"📊 الإحصائيات\n\n👥 المستخدمون: {len(users)}\n🧾 سجلات التدقيق: {len(audits)}", reply_markup=admin_menu())
    elif action == "admin_users":
        rows = admin_service.users(user_id)
        if not rows:
            text = "👥 لا يوجد مستخدمون بعد."
        else:
            text = "👥 المستخدمون\n\n" + "\n".join(f"• `{uid}` — {role}" for uid, role, _ in rows[:30])
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    elif action == "admin_roles":
        await q.edit_message_text("🔐 الأدوار\n\nuser — مستخدم\nanalyst — محلل\nadmin — مدير\n\nلتغيير دور مستخدم استخدم:\n/setrole USER_ID ROLE", reply_markup=admin_menu())
    elif action == "admin_labs":
        await q.edit_message_text("🧪 المختبرات\n\nإدارة المختبرات المعزولة متاحة من وحدة المختبر. لا يتم تشغيل أهداف حقيقية من لوحة الإدارة.", reply_markup=admin_menu())
    elif action == "admin_auth":
        await q.edit_message_text("📋 التفويضات\n\nبوابة التفويض مخصصة لتسجيل نطاق ومدة الاختبار. التنفيذ الهجومي على أهداف حقيقية غير متاح.", reply_markup=admin_menu())
    elif action == "admin_audit":
        rows = admin_service.audit_logs(user_id, 20)
        text = "🧾 آخر سجلات التدقيق\n\n" + ("\n".join(f"• {uid} — {action} — {created}" for uid, action, _, created in rows) or "لا توجد سجلات.")
        await q.edit_message_text(text[:4000], reply_markup=admin_menu())
    elif action == "admin_broadcast":
        context.user_data["awaiting_broadcast"] = True
        await q.edit_message_text("📢 أرسل الآن الرسالة التي تريد إرسالها لجميع مستخدمي البوت.\n\nاكتب /cancel للإلغاء.", reply_markup=admin_menu())


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    storage.ensure_user(user_id, "admin" if user_id == ADMIN_ID else "user")
    if not admin_service.is_admin(user_id):
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط.")
        return
    await update.message.reply_text("👑 CyberGuard AI — لوحة الإدارة", reply_markup=admin_menu())


async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    actor = update.effective_user.id
    if not admin_service.is_admin(actor):
        await update.message.reply_text("⛔ للمشرف فقط.")
        return
    if len(context.args) != 2:
        await update.message.reply_text("الاستخدام: /setrole USER_ID user|analyst|admin")
        return
    try:
        target = int(context.args[0])
        admin_service.set_role(actor, target, context.args[1])
        await update.message.reply_text("✅ تم تحديث الدور.")
    except (ValueError, PermissionError) as exc:
        await update.message.reply_text(f"❌ {exc}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_broadcast", None)
    await update.message.reply_text("تم الإلغاء.")


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_broadcast"):
        return
    actor = update.effective_user.id
    if not admin_service.is_admin(actor):
        context.user_data.pop("awaiting_broadcast", None)
        return
    context.user_data.pop("awaiting_broadcast", None)
    sent = 0
    failed = 0
    for (uid, _, _) in admin_service.users(actor):
        try:
            await context.bot.send_message(chat_id=uid, text=update.message.text)
            sent += 1
        except Exception:
            failed += 1
    storage.audit(actor, "broadcast", f"sent={sent}, failed={failed}")
    await update.message.reply_text(f"📢 اكتمل الإرسال.\n\n✅ نجح: {sent}\n⚠️ فشل: {failed}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN غير موجود في متغيرات البيئة")
    storage.init()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("setrole", setrole))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message))
    app.run_polling()

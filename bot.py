import logging
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from cyberguard.storage import Storage
from cyberguard.admin_service import AdminService
from cyberguard.lab_buttons import callback as lab_callback, show_labs
from cyberguard.education import TOOLS, tool_text
from cyberguard.ctf import CTFEngine

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB = os.getenv("DB_PATH", "cyberguard.db")
storage = Storage(DB)
admin_service = AdminService(storage)
ctf = CTFEngine()


def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛡️ الدفاعي", callback_data="defensive"), InlineKeyboardButton("🔴 الاختبار التعليمي", callback_data="offensive")],
        [InlineKeyboardButton("🧪 المختبرات", callback_data="labs"), InlineKeyboardButton("🌍 أمن الويب", callback_data="web")],
        [InlineKeyboardButton("🌐 أمن الشبكات", callback_data="network"), InlineKeyboardButton("🏆 CTF", callback_data="ctf")],
        [InlineKeyboardButton("🧠 Cyber AI", callback_data="ai"), InlineKeyboardButton("🎯 MITRE ATT&CK", callback_data="mitre")],
        [InlineKeyboardButton("🚨 الحوادث", callback_data="ir"), InlineKeyboardButton("🦠 تحليل البرمجيات", callback_data="malware")],
        [InlineKeyboardButton("📊 التقارير", callback_data="reports"), InlineKeyboardButton("🧰 الأدوات", callback_data="tools")],
        [InlineKeyboardButton("👤 حسابي", callback_data="account"), InlineKeyboardButton("👑 الإدارة", callback_data="admin")],
    ])


def back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")]])


def admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats"), InlineKeyboardButton("👥 المستخدمون", callback_data="admin_users")],
        [InlineKeyboardButton("🔐 الأدوار", callback_data="admin_roles"), InlineKeyboardButton("🧪 المختبرات", callback_data="admin_labs")],
        [InlineKeyboardButton("📋 التفويضات", callback_data="admin_auth"), InlineKeyboardButton("🧾 التدقيق", callback_data="admin_audit")],
        [InlineKeyboardButton("📢 إرسال للجميع", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")],
    ])


def ctf_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Beginner", callback_data="ctf_level:Beginner"), InlineKeyboardButton("🟡 Intermediate", callback_data="ctf_level:Intermediate")],
        [InlineKeyboardButton("🔴 Advanced", callback_data="ctf_level:Advanced"), InlineKeyboardButton("🏆 نقاطي", callback_data="ctf_score")],
        [InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")],
    ])


def challenge_menu(challenges):
    rows = [[InlineKeyboardButton(f"🧩 {c.title} [{c.level}]", callback_data=f"ctf_challenge:{c.id}")] for c in challenges]
    rows.append([InlineKeyboardButton("🏆 نقاطي", callback_data="ctf_score"), InlineKeyboardButton("⬅️ CTF", callback_data="ctf")])
    return InlineKeyboardMarkup(rows)


TEXT = {
 "defensive": ("🛡️ الأمن الدفاعي", "كشف التهديدات، تحليل السجلات، التقوية والاستجابة."),
 "offensive": ("🔴 اختبار الاختراق التعليمي", "تعلم الاستطلاع والتعداد وتقييم المخاطر ومفاهيم الويب والشبكات داخل Cyber Range معزول فقط. لا توجد عمليات اختراق حقيقية ضد أهداف خارجية."),
 "web": ("🌍 أمن الويب", "OWASP Top 10: الشرح، الاكتشاف داخل المختبر، الأثر، الحماية والإصلاح."),
 "network": ("🌐 أمن الشبكات", "DNS وHTTP وTLS وتحليل الحركة والجدران النارية وIDS/IPS."),
 "ai": ("🧠 Cyber AI", "شرح السجلات والتنبيهات والمفاهيم الأمنية والكود الآمن."),
 "mitre": ("🎯 MITRE ATT&CK", "تعلم التكتيكات والتقنيات مع الكشف والتخفيف."),
 "ir": ("🚨 الاستجابة للحوادث", "كشف وتحقيق واحتواء وقضاء واسترداد وتقرير."),
 "malware": ("🦠 تحليل البرمجيات", "Hash وMetadata وStrings وIOC ومفاهيم YARA والتحليل الثابت داخل المختبر. لا إنشاء أو نشر برمجيات خبيثة."),
 "reports": ("📊 التقارير", "تنظيم النتائج والمخاطر والتوصيات في تقارير تدريبية."),
 "account": ("👤 حسابي", "معرف Telegram وسجل النشاط التعليمي."),
}


def tools_menu():
    keys = list(TOOLS)
    rows = [[InlineKeyboardButton(TOOLS[k][0], callback_data=f"tool:{k}") for k in keys[i:i+2]] for i in range(0, len(keys), 2)]
    rows.append([InlineKeyboardButton("⬅️ الرئيسية", callback_data="home")])
    return InlineKeyboardMarkup(rows)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    storage.ensure_user(u.id, "admin" if u.id == ADMIN_ID else "user")
    storage.audit(u.id, "start")
    await update.message.reply_text("🛡️ CyberGuard AI\n\nمنصة تعليمية للأمن السيبراني وCyber Range وCTF.\n\n⚠️ الاستخدام العملي للمختبرات المعزولة أو الأنظمة المصرح بها فقط.", reply_markup=main_menu())


async def labs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    storage.ensure_user(update.effective_user.id, "admin" if update.effective_user.id == ADMIN_ID else "user")
    await show_labs(update, context)


async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧰 مركز الأدوات\n\nاختر أداة لمعرفة وظيفتها واستخدامها الآمن:", reply_markup=tools_menu())


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    storage.ensure_user(uid, "admin" if uid == ADMIN_ID else "user")
    if not admin_service.is_admin(uid):
        await update.message.reply_text("⛔ هذا الأمر للمشرف فقط."); return
    await update.message.reply_text("👑 CyberGuard AI — لوحة الإدارة", reply_markup=admin_menu())


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    storage.ensure_user(uid, "admin" if uid == ADMIN_ID else "user")
    storage.audit(uid, q.data)

    if q.data.startswith("lab:"):
        await lab_callback(update, context); return
    if q.data == "labs":
        from cyberguard.lab_buttons import keyboard
        await q.edit_message_text("🧪 Cyber Range\n\nمختبرات تدريب معزولة:", reply_markup=keyboard()); return
    if q.data == "ctf":
        await q.edit_message_text("🏆 CTF Academy\n\nاختر المستوى أو اعرض نقاطك:\n\n🧪 جميع التحديات تعمل محليًا داخل بيئة تدريبية.", reply_markup=ctf_menu()); return
    if q.data.startswith("ctf_level:"):
        level = q.data.split(":", 1)[1]
        challenges = ctf.list(level)
        if not challenges:
            await q.edit_message_text(f"🏆 {level}\n\nلا توجد تحديات بهذا المستوى حاليًا.", reply_markup=ctf_menu()); return
        await q.edit_message_text(f"🏆 تحديات {level}\n\nاختر تحديًا:", reply_markup=challenge_menu(challenges)); return
    if q.data.startswith("ctf_challenge:"):
        challenge_id = q.data.split(":", 1)[1]
        c = ctf.get(challenge_id)
        if not c:
            await q.edit_message_text("❌ التحدي غير موجود.", reply_markup=ctf_menu()); return
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💡 Hint", callback_data=f"ctf_hint:{c.id}")],
            [InlineKeyboardButton("📝 إرسال الإجابة", callback_data=f"ctf_submit:{c.id}")],
            [InlineKeyboardButton("⬅️ التحديات", callback_data=f"ctf_level:{c.level}")],
        ])
        await q.edit_message_text(f"🧩 {c.title}\n\n🎯 الهدف:\n{c.goal}\n\n📚 المستوى: {c.level}\n\n⚠️ التحدي تدريبي محلي ولا يستهدف أنظمة خارجية.", reply_markup=keyboard); return
    if q.data.startswith("ctf_hint:"):
        c = ctf.get(q.data.split(":", 1)[1])
        await q.edit_message_text(f"💡 Hint\n\n{c.hint if c else 'التحدي غير موجود.'}", reply_markup=ctf_menu()); return
    if q.data.startswith("ctf_submit:"):
        challenge_id = q.data.split(":", 1)[1]
        context.user_data["ctf_waiting"] = challenge_id
        await q.edit_message_text("📝 أرسل إجابتك الآن في رسالة نصية.\n\n/cancel للإلغاء.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ CTF", callback_data="ctf")]])); return
    if q.data == "ctf_score":
        await q.edit_message_text(f"🏆 نقاطك الحالية: {ctf.score(uid)}", reply_markup=ctf_menu()); return
    if q.data == "tools":
        await q.edit_message_text("🧰 مركز الأدوات\n\nكل بطاقة تشرح الأداة ومهمتها ومتطلباتها:", reply_markup=tools_menu()); return
    if q.data.startswith("tool:"):
        await q.edit_message_text(tool_text(q.data.split(":",1)[1]), reply_markup=tools_menu()); return
    if q.data == "admin":
        if not admin_service.is_admin(uid):
            await q.edit_message_text("⛔ للمشرف فقط.", reply_markup=back()); return
        await q.edit_message_text("👑 لوحة إدارة CyberGuard AI\n\nاختر إجراءً:", reply_markup=admin_menu()); return
    if q.data == "home":
        await q.edit_message_text("🛡️ CyberGuard AI\n\nاختر قسمًا:", reply_markup=main_menu()); return
    if q.data.startswith("admin_"):
        if not admin_service.is_admin(uid):
            await q.edit_message_text("⛔ للمشرف فقط.", reply_markup=back()); return
        await admin_callback(q, context); return
    title, body = TEXT.get(q.data, ("غير متاح", "هذه الوظيفة غير متاحة حاليًا."))
    await q.edit_message_text(f"{title}\n\n📌 المهمة\n{body}\n\n🔐 التنفيذ العملي محصور بالمختبرات المعزولة والأنظمة المصرح بها.", reply_markup=back())


async def admin_callback(q, context):
    uid = q.from_user.id; action = q.data
    if action == "admin_stats":
        users = admin_service.users(uid); audits = admin_service.audit_logs(uid, 100000)
        await q.edit_message_text(f"📊 الإحصائيات\n\n👥 المستخدمون: {len(users)}\n🧾 التدقيق: {len(audits)}", reply_markup=admin_menu())
    elif action == "admin_users":
        rows = admin_service.users(uid); text = "👥 المستخدمون\n\n" + ("\n".join(f"• `{x}` — {r}" for x,r,_ in rows[:30]) or "لا يوجد مستخدمون.")
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_menu())
    elif action == "admin_roles":
        await q.edit_message_text("🔐 الأدوار\n\nuser — مستخدم\nanalyst — محلل\nadmin — مدير\n\n/setrole USER_ID ROLE", reply_markup=admin_menu())
    elif action == "admin_labs":
        await q.edit_message_text("🧪 إدارة المختبرات المعزولة من قسم المختبر.", reply_markup=admin_menu())
    elif action == "admin_auth":
        await q.edit_message_text("📋 التفويضات\n\nسجّل نطاق ومدة التفويض قبل أي اختبار عملي. لا ينفذ البوت اختراقًا حقيقيًا على أهداف خارجية.", reply_markup=admin_menu())
    elif action == "admin_audit":
        rows = admin_service.audit_logs(uid, 20); text = "🧾 آخر السجلات\n\n" + ("\n".join(f"• {u} — {a} — {c}" for u,a,_,c in rows) or "لا توجد سجلات.")
        await q.edit_message_text(text[:4000], reply_markup=admin_menu())
    elif action == "admin_broadcast":
        context.user_data["awaiting_broadcast"] = True
        await q.edit_message_text("📢 أرسل الرسالة الآن لإرسالها للمستخدمين. /cancel للإلغاء.", reply_markup=admin_menu())


async def setrole(update: Update, context: ContextTypes.DEFAULT_TYPE):
    actor = update.effective_user.id
    if not admin_service.is_admin(actor): await update.message.reply_text("⛔ للمشرف فقط."); return
    if len(context.args) != 2: await update.message.reply_text("/setrole USER_ID user|analyst|admin"); return
    try: admin_service.set_role(actor, int(context.args[0]), context.args[1]); await update.message.reply_text("✅ تم تحديث الدور.")
    except (ValueError, PermissionError) as e: await update.message.reply_text(f"❌ {e}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_broadcast", None)
    context.user_data.pop("ctf_waiting", None)
    await update.message.reply_text("تم الإلغاء.")


async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    waiting = context.user_data.get("ctf_waiting")
    if waiting:
        ok = ctf.submit(uid, waiting, update.message.text)
        context.user_data.pop("ctf_waiting", None)
        if ok:
            storage.audit(uid, "ctf_solved", waiting)
            await update.message.reply_text(f"✅ إجابة صحيحة!\n\n🏆 +100 نقطة\n📊 مجموع نقاطك: {ctf.score(uid)}", reply_markup=ctf_menu())
        else:
            await update.message.reply_text("❌ إجابة غير صحيحة. جرّب مرة أخرى من خلال اختيار التحدي.", reply_markup=ctf_menu())
        return
    if context.user_data.get("awaiting_broadcast"):
        if not admin_service.is_admin(uid):
            context.user_data.pop("awaiting_broadcast", None); return
        context.user_data.pop("awaiting_broadcast", None)
        sent = failed = 0
        for target, _, _ in admin_service.users(uid):
            try:
                await context.bot.send_message(chat_id=target, text=update.message.text); sent += 1
            except Exception:
                failed += 1
        storage.audit(uid, "broadcast", f"sent={sent},failed={failed}")
        await update.message.reply_text(f"📢 اكتمل الإرسال\n\n✅ {sent}  ⚠️ {failed}")


if __name__ == "__main__":
    if not TOKEN: raise RuntimeError("BOT_TOKEN غير موجود في متغيرات البيئة")
    storage.init()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("labs", labs_command))
    app.add_handler(CommandHandler("tools", tools_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("setrole", setrole))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))
    app.run_polling()

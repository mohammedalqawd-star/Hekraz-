"""Safe educational catalog for CyberGuard AI."""

TOOLS = {
    "web_headers": ("🌐 HTTP Security Headers", "فحص رؤوس HTTP وتحليل ضوابط الحماية.", "يعمل فعليًا على localhost داخل المختبر."),
    "dns_lookup": ("🔎 DNS Lookup", "حل اسم المضيف وعرض عناوينه.", "يعمل على localhost/loopback في وضع التشغيل العملي."),
    "tls_inspector": ("🔐 TLS Inspector", "عرض إصدار TLS وCipher ومعلومات الشهادة.", "يعمل فعليًا على خدمة TLS محلية."),
    "file_hash": ("🦠 File Hash Analyzer", "حساب SHA-256 وحجم الملف للتحليل الجنائي الآمن.", "يعمل على الملفات الموجودة في بيئة البوت."),
    "nmap": ("Nmap", "استكشاف المنافذ والخدمات داخل المختبر.", "تشغيل فعلي محصور بـ localhost/loopback."),
    "zap": ("OWASP ZAP", "فحص أمان تطبيق ويب محلي.", "تشغيل اختياري إذا كان ZAP مثبتًا، وعلى localhost فقط."),
    "wireshark": ("Wireshark/TShark", "عرض وتحليل حركة شبكة المختبر.", "التقاط محدود على loopback فقط."),
    "yara": ("YARA", "فحص الملفات بقواعد YARA للكشف عن أنماط محددة.", "تشغيل فعلي على ملفات المختبر."),
    "bandit": ("Bandit", "فحص كود Python بحثًا عن مشكلات أمنية.", "تشغيل فعلي على مسار مشروع محلي."),
}

RUNNABLE = {"web_headers", "dns_lookup", "tls_inspector", "file_hash", "nmap", "zap", "wireshark", "yara", "bandit"}


def tool_text(key: str) -> str:
    item = TOOLS.get(key)
    if not item:
        return "❌ الأداة غير موجودة."
    name, job, use = item
    run = "\n\n▶️ التشغيل: متاح فعليًا" if key in RUNNABLE else ""
    return f"🧰 {name}\n\n📌 ما هي؟\n{job}\n\n🎯 لماذا مهمة؟\n{use}\n\n🔒 النطاق: Cyber Range / localhost / loopback فقط.{run}"

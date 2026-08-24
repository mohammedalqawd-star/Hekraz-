"""Safe educational catalog for CyberGuard AI."""

TOOLS = {
    "web_headers": ("🌐 HTTP Security Headers", "فحص رؤوس HTTP وتحليل ضوابط الحماية.", "يعمل فعليًا على localhost داخل المختبر."),
    "dns_lookup": ("🔎 DNS Lookup", "حل اسم المضيف وعرض عناوينه.", "يعمل على localhost/loopback في وضع التشغيل العملي."),
    "tls_inspector": ("🔐 TLS Inspector", "عرض إصدار TLS وCipher ومعلومات الشهادة.", "يعمل فعليًا على خدمة TLS محلية."),
    "file_hash": ("🦠 File Hash Analyzer", "حساب SHA-256 وحجم الملف للتحليل الجنائي الآمن.", "يعمل على الملفات الموجودة في بيئة البوت."),
    "nmap": ("Nmap", "استكشاف الشبكات والمنافذ.", "للتعلم فقط؛ التنفيذ العملي محصور بالمختبر المعزول."),
    "zap": ("OWASP ZAP", "اختبار أمان تطبيقات الويب.", "للاستخدام داخل Cyber Range فقط."),
    "wireshark": ("Wireshark", "تحليل حزم وحركة الشبكة.", "لتحليل مختبرك أو شبكة مصرح بها."),
    "yara": ("YARA", "كتابة قواعد للتعرف على أنماط الملفات.", "مفيد في أبحاث البرمجيات الخبيثة والدفاع."),
    "bandit": ("Bandit", "فحص كود Python بحثًا عن مشكلات أمنية.", "مفيد ضمن CI وفحص المشاريع التي تملكها."),
}

RUNNABLE = {"web_headers", "dns_lookup", "tls_inspector", "file_hash"}


def tool_text(key: str) -> str:
    item = TOOLS.get(key)
    if not item:
        return "❌ الأداة غير موجودة."
    name, job, use = item
    run = "\n\n▶️ التشغيل: متاح" if key in RUNNABLE else "\n\n📚 التشغيل العملي: متاح فقط عبر المختبر المعزول بعد ربط محرك الأداة."
    return f"🧰 {name}\n\n📌 ما هي؟\n{job}\n\n🎯 لماذا مهمة؟\n{use}\n\n🔒 النطاق: Cyber Range / أصول مصرح بها فقط.{run}"

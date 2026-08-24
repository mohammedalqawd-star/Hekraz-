"""Safe educational catalog for CyberGuard AI.
No live exploitation or malware generation is exposed here.
"""
TOOLS = {
    "nmap": ("Nmap", "استكشاف الشبكات والمنافذ", "يُستخدم داخل مختبر تملكه أو تملك تفويضًا لاختباره."),
    "zap": ("OWASP ZAP", "اختبار أمان تطبيقات الويب", "استخدم الوضع الآمن/السلبي داخل المختبر."),
    "wireshark": ("Wireshark", "تحليل حزم وحركة الشبكة", "مفيد لفهم DNS وHTTP وTLS واكتشاف السلوك غير الطبيعي."),
    "yara": ("YARA", "كتابة قواعد للتعرّف على أنماط الملفات", "مفيد في أبحاث البرمجيات الخبيثة والدفاع."),
    "bandit": ("Bandit", "فحص كود Python بحثًا عن مشكلات أمنية", "مفيد ضمن CI وفحص المشاريع التي تملكها."),
}

def tool_text(key: str) -> str:
    item = TOOLS.get(key)
    if not item:
        return "الأداة غير موجودة."
    name, job, use = item
    return f"🧰 {name}\n\n📌 ما هي؟\n{job}\n\n🎯 لماذا مهمة؟\n{use}\n\n🔐 الاستخدام العملي: داخل المختبر أو على أصول مصرح بها فقط."

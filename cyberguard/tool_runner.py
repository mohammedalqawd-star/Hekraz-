"""Safe runtime tools for CyberGuard AI.

All network execution is restricted to localhost/loopback. External targets are rejected.
The module performs defensive inspection and lab scanning; it does not exploit targets.
"""
from __future__ import annotations

import hashlib
import ipaddress
import shutil
import socket
import ssl
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


def _local_target(target: str) -> str:
    value = target.strip()
    if not value:
        raise ValueError("الهدف فارغ")
    host = value.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
    if host.lower() == "localhost":
        return host
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_loopback:
            return host
    except ValueError:
        pass
    raise ValueError("التنفيذ العملي محصور في localhost/127.0.0.1")


def _local_url(target: str, default_scheme: str = "http") -> str:
    value = target.strip()
    if "://" not in value:
        value = f"{default_scheme}://{value}"
    _local_target(value)
    return value


def _run(cmd: list[str], timeout: int = 30) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = (p.stdout + ("\n" + p.stderr if p.stderr else "")).strip()
        return output or f"انتهى التنفيذ برمز {p.returncode}"
    except FileNotFoundError:
        return f"❌ البرنامج غير مثبت: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return "⏱️ انتهى الوقت المحدد للأداة."
    except Exception as e:
        return f"❌ فشل التنفيذ: {type(e).__name__}: {e}"


def http_headers(target: str) -> str:
    host = _local_target(target)
    url = _local_url(target)
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "CyberGuard-AI-Lab/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            headers = dict(response.headers.items())
            missing = [h for h in ("Content-Security-Policy", "X-Content-Type-Options", "X-Frame-Options", "Strict-Transport-Security") if h not in headers]
            lines = [f"🌐 الهدف: {host}", f"📡 الحالة: {response.status}", "", "📋 الرؤوس:"]
            lines += [f"• {k}: {v}" for k, v in list(headers.items())[:30]]
            lines += ["", "⚠️ رؤوس حماية غير موجودة:"] + ([f"• {x}" for x in missing] if missing else ["• لا توجد ضمن المجموعة المفحوصة"])
            return "\n".join(lines)
    except urllib.error.HTTPError as e:
        return f"🌐 الهدف: {host}\n📡 HTTP {e.code}\n\n" + "\n".join(f"• {k}: {v}" for k, v in e.headers.items())
    except Exception as e:
        return f"❌ تعذر الاتصال بالمختبر: {type(e).__name__}: {e}"


def dns_lookup(target: str) -> str:
    host = _local_target(target)
    try:
        infos = socket.getaddrinfo(host, None)
        addresses = sorted({item[4][0] for item in infos})
        return f"🔎 DNS Lookup\n\n📌 الهدف: {host}\n📍 العناوين:\n" + "\n".join(f"• {x}" for x in addresses)
    except Exception as e:
        return f"❌ فشل DNS: {type(e).__name__}: {e}"


def tls_inspect(target: str) -> str:
    value = target.strip()
    raw_host = value.split("://", 1)[-1].split("/", 1)[0]
    host = _local_target(value)
    port = 443
    if ":" in raw_host and not raw_host.startswith("["):
        host, port_text = raw_host.rsplit(":", 1)
        port = int(port_text)
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, port), timeout=8) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as sock:
                cert = sock.getpeercert()
                return f"🔐 TLS Inspector\n\n📌 الهدف: {host}:{port}\n🔒 TLS: {sock.version()}\n🔑 Cipher: {sock.cipher()[0]}\n📜 Subject: {cert.get('subject', 'غير متاح')}\n📜 Issuer: {cert.get('issuer', 'غير متاح')}"
    except Exception as e:
        return f"❌ تعذر فحص TLS: {type(e).__name__}: {e}"


def file_hash(path: str) -> str:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise ValueError("الملف غير موجود")
    h = hashlib.sha256()
    size = 0
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            size += len(chunk)
            h.update(chunk)
    return f"🦠 File Analyzer\n\n📄 الملف: {p.name}\n📦 الحجم: {size} bytes\n🔐 SHA-256: {h.hexdigest()}"


def nmap_scan(target: str) -> str:
    host = _local_target(target)
    if not shutil.which("nmap"):
        return "❌ Nmap غير مثبت."
    return "🧰 Nmap — فحص المختبر\n\n" + _run(["nmap", "-sV", "-Pn", "--top-ports", "100", "-T2", host], 45)


def zap_scan(target: str) -> str:
    url = _local_url(target)
    baseline = shutil.which("zap-baseline.py")
    if baseline:
        return "🧰 OWASP ZAP — فحص محلي\n\n" + _run([baseline, "-t", url, "-m", "2"], 90)
    zap = shutil.which("zap.sh")
    if zap:
        return "🧰 OWASP ZAP — فحص محلي\n\n" + _run([zap, "-cmd", "-quickurl", url, "-quickprogress"], 90)
    return "❌ OWASP ZAP غير مثبت."


def tshark_capture(target: str) -> str:
    _local_target(target)
    if not shutil.which("tshark"):
        return "❌ TShark غير مثبت."
    return "🧰 Wireshark/TShark — loopback لمدة 5 ثوانٍ\n\n" + _run([
        "tshark", "-i", "lo", "-a", "duration:5", "-c", "50", "-T", "fields",
        "-e", "frame.number", "-e", "ip.src", "-e", "ip.dst", "-e", "tcp.dstport",
    ], 12)


def yara_scan(target: str) -> str:
    if "|" not in target:
        raise ValueError("الصيغة: /مسار/rule.yar|/مسار/الملف")
    rule_text, sample_text = [x.strip() for x in target.split("|", 1)]
    rule = Path(rule_text).expanduser().resolve()
    sample = Path(sample_text).expanduser().resolve()
    if not rule.is_file() or not sample.exists():
        raise ValueError("ملف القاعدة أو الملف المراد فحصه غير موجود")
    if not shutil.which("yara"):
        return "❌ YARA غير مثبت."
    return "🧰 YARA\n\n" + _run(["yara", str(rule), str(sample)], 20)


def bandit_scan(target: str) -> str:
    p = Path(target).expanduser().resolve()
    if not p.exists():
        raise ValueError("مسار المشروع غير موجود")
    exe = shutil.which("bandit")
    if not exe:
        return "❌ Bandit غير مثبت."
    return "🧰 Bandit\n\n" + _run([exe, "-r", str(p), "-f", "txt"], 60)


def run(tool_id: str, target: str) -> str:
    if tool_id == "web_headers":
        return http_headers(target)
    if tool_id == "dns_lookup":
        return dns_lookup(target)
    if tool_id == "tls_inspector":
        return tls_inspect(target)
    if tool_id == "file_hash":
        return file_hash(target)
    if tool_id == "nmap":
        return nmap_scan(target)
    if tool_id == "zap":
        return zap_scan(target)
    if tool_id == "wireshark":
        return tshark_capture(target)
    if tool_id == "yara":
        return yara_scan(target)
    if tool_id == "bandit":
        return bandit_scan(target)
    raise ValueError("الأداة غير مدعومة للتنفيذ")

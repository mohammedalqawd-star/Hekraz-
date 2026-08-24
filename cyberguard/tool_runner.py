"""Safe runtime tools for CyberGuard AI.

Runtime execution is deliberately restricted to localhost/loopback targets.
The module performs defensive inspection only; it does not exploit targets.
"""
from __future__ import annotations

import hashlib
import ipaddress
import socket
import ssl
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
    raise ValueError("التنفيذ العملي لهذه الأداة محصور في localhost/127.0.0.1")


def http_headers(target: str) -> str:
    host = _local_target(target)
    url = target if "://" in target else f"http://{target}"
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
    host = _local_target(target)
    port = 443
    if ":" in host and not host.startswith("["):
        host, port_text = host.rsplit(":", 1)
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


def run(tool_id: str, target: str) -> str:
    if tool_id == "web_headers":
        return http_headers(target)
    if tool_id == "dns_lookup":
        return dns_lookup(target)
    if tool_id == "tls_inspector":
        return tls_inspect(target)
    raise ValueError("الأداة غير مدعومة للتنفيذ")

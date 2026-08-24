# 🛡️ CyberGuard AI

Telegram-based educational cybersecurity platform focused on defensive security, isolated labs, CTF training, web/network security, incident response, MITRE ATT&CK concepts, and secure coding.

## Safety boundary
Practical security testing is restricted to systems the user owns or is explicitly authorized to test. Offensive concepts are taught through isolated labs and CTF scenarios. The project does not provide malware deployment, credential theft, persistence, evasion, or attacks against real targets.

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN='YOUR_BOT_TOKEN'
export ADMIN_ID='YOUR_TELEGRAM_ID'
python bot.py
```

Never commit secrets. Use environment variables or your hosting provider's secret manager.

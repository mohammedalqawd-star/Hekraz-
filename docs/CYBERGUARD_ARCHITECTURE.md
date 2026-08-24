# CyberGuard AI — Architecture

## Scope
CyberGuard AI is an educational and defensive cybersecurity platform. Practical offensive exercises run only inside isolated labs/CTF environments or against explicitly authorized assets.

## Modules
- Telegram interface with Inline Keyboard
- RBAC and administrator controls
- Authorization records and audit logging
- Isolated Cyber Range lab lifecycle
- CTF Academy
- Web/API/network security education
- Malware research using safe analysis workflows
- MITRE ATT&CK and OWASP knowledge modules
- Incident-response playbooks
- Security reports
- Secure coding checks

## Tool card contract
Every tool must expose:
1. What it is
2. What it does
3. Why it matters
4. When to use it
5. Requirements
6. Lab usage
7. Results
8. Safety boundary

Buttons must invoke an implemented handler. If a feature is not installed, the bot must explicitly report that it is unavailable rather than pretending to run it.

## Authorization
Before a practical test:
- authorization ID
- target/scope
- start time
- expiry time
- approving administrator

Only targets permitted by the authorization record may be used.

## Safety boundary
The project does not implement credential theft, malware deployment, persistence, evasion, destructive actions, or automated attacks against real third-party systems. Those concepts may be demonstrated through isolated training labs and CTF scenarios.

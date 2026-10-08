"""Email. Either through Resend (RESEND_API_KEY) or any ordinary mail account
over SMTP (SMTP_HOST, SMTP_USER, SMTP_PASSWORD), which can be a Gmail address
with an app password. With neither set nothing is sent, and the message is
kept in OUTBOX so local testing can see what would have gone."""
import json, logging, os, smtplib, ssl, urllib.request, urllib.error
from email.message import EmailMessage

RESEND_KEY = os.environ.get("RESEND_API_KEY", "")
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465") or 465)
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
FROM = os.environ.get("MAIL_FROM", "") or (f"Saga Devi <{SMTP_USER}>" if SMTP_USER else "Saga Devi <readings@example.com>")
OUTBOX = []
log = logging.getLogger("wyrd.mail")


def ready():
    return bool(RESEND_KEY or (SMTP_HOST and SMTP_USER and SMTP_PASSWORD))


def send(to, subject, html, text=""):
    try:
        if RESEND_KEY: return _resend(to, subject, html, text)
        if SMTP_HOST and SMTP_USER and SMTP_PASSWORD: return _smtp(to, subject, html, text)
    except Exception as e:                       # mail trouble never breaks a page
        log.error("mail failed: %s", e)
        return False
    OUTBOX.append({"to": to, "subject": subject, "html": html, "text": text})
    del OUTBOX[:-50]
    log.warning("mail not sent (no mail settings): %s -> %s", subject, to)
    return False


def _resend(to, subject, html, text):
    body = {"from": FROM, "to": [to], "subject": subject, "html": html}
    if text: body["text"] = text
    req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json",
                                          "User-Agent": "wyrd-console"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return 200 <= r.status < 300


def _smtp(to, subject, html, text):
    m = EmailMessage()
    m["From"], m["To"], m["Subject"] = FROM, to, subject
    m.set_content(text or "Open this message in an email app that shows HTML.")
    m.add_alternative(html, subtype="html")
    if SMTP_PORT == 465:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=20) as s:
            s.login(SMTP_USER, SMTP_PASSWORD); s.send_message(m)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as s:
            s.starttls(context=ssl.create_default_context()); s.login(SMTP_USER, SMTP_PASSWORD); s.send_message(m)
    return True

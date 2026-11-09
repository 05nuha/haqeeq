"""
main.py  —  OWNER: Person A (Cyber / Replit owner)
The web server. It receives WhatsApp messages from Twilio, runs the engine,
replies in Arabic, and saves every report to the database.

It also registers the dashboard (Person B's file) with ONE line:
    app.register_blueprint(dashboard_bp)
That single line is the only place the two halves meet.
"""
import os
import random
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from db import init_db, add_report
from engine import verify_image, check_text
from dashboard import dashboard_bp   # Person B owns dashboard.py

app = Flask(__name__)
app.register_blueprint(dashboard_bp)
init_db()

EMIRATES = ["Dubai", "Sharjah", "Abu Dhabi", "Ajman", "Al Ain", "Ras Al Khaimah",
            "Fujairah", "Umm Al Quwain"]

ARABIC = {
    "genuine":    "✅ صحيح — هذا محتوى رسمي موثّق.",
    "verified":   "✅ صحيح — هذا محتوى رسمي موثّق.",
    "altered":    "🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله.",
    "unverified": "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً.",
    "scam_risk":  "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء.",
}


@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    resp = MessagingResponse()
    sender = request.form.get("From", "").replace("whatsapp:", "")
    masked = (sender[:6] + "•••" + sender[-3:]) if len(sender) > 9 else sender
    num_media = int(request.form.get("NumMedia", 0))
    emirate = random.choice(EMIRATES)   # demo: real system would use the sender's area

    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        path = f"incoming_{random.randint(1000, 9999)}.jpg"
        got = requests.get(
            media_url,
            auth=(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"]),
        )
        with open(path, "wb") as f:
            f.write(got.content)
        result = verify_image(path)
        add_report(masked, "image", result["verdict"], result.get("matched_id"),
                   result.get("distance"), emirate, result.get("detail"), path)
        resp.message(ARABIC.get(result["verdict"], result["verdict"]))
    else:
        text = request.form.get("Body", "")
        result = check_text(text)
        add_report(masked, "text", result["verdict"], None, None, emirate,
                   result.get("detail"), None)
        resp.message(ARABIC.get(result["verdict"], result["verdict"]))

    return str(resp)


@app.route("/")
def home():
    return "Haqeeq is running. Open /dashboard"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

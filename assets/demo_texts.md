# Demo texts (all fictional — for the live demo; paste into the WhatsApp sandbox chat)

Every link below is a deliberately fake placeholder (`.example`); do not replace with real domains.

## Scam texts (expected verdict: scam_risk, Arabic reply 🔴)

1. Dubai Police fine (Arabic)
   `عاجل: تم تسجيل مخالفة مرورية باسمك من شرطة دبي. سدد الغرامة الآن خلال 24 ساعة عبر الرابط لتجنب مضاعفة المبلغ: http://dubai-police-fines.example/pay`
2. Dubai Police fine (English)
   `URGENT: A traffic fine has been issued in your name by Dubai Police. Pay now within 24 hours via this link to avoid double charges: http://dubai-police-fines.example/pay`
3. Emirates ID suspended (Arabic)
   `تنبيه من الهيئة: تم إيقاف هويتك الإماراتية مؤقتاً. لإعادة التفعيل أرسل رمز التحقق OTP الذي وصلك الآن.`
4. Emirates ID suspended (English)
   `ICP notice: your Emirates ID has been suspended. To reactivate, reply with the OTP code you just received.`
5. Prize (Arabic)
   `مبروك! فزت بجائزة نقدية 50,000 درهم في السحب الشهري. للاستلام حوّل رسوم التوصيل 250 درهماً فوراً عبر الرابط: http://uae-prize.example/claim`
6. Prize (English)
   `Congratulations! You won AED 50,000 in the monthly draw. Transfer the AED 250 delivery fee immediately to claim: http://uae-prize.example/claim`

## Benign text (expected: unverified ⚪ "No official source" — never a scam verdict)

- `مرحبا، هل الاجتماع غداً الساعة العاشرة؟`
- `hello`

## Arabic correction message for the "explosions in Downtown Dubai" fake (Push official correction)

> تصحيح رسمي: الصورة المتداولة بعنوان "انفجارات في وسط مدينة دبي" غير صحيحة ولا تعكس أي حدث حقيقي. لا تقم بإعادة إرسالها. للحصول على المعلومات الرسمية، تابع القنوات الحكومية الموثّقة فقط. (نموذج تجريبي)

English gloss: Official correction: the circulating image "Explosions in Downtown Dubai" is false and does not reflect any real event. Do not forward it. Follow verified government channels only. (Demo)

## Image demo script (files in this folder tree)

| Beat | File | Expected |
|---|---|---|
| 1 genuine | `official/public_holiday_notice.png` | ✅ genuine |
| 2 showstopper | `screenshots/public_holiday_notice_screenshot.jpg` | ✅ genuine |
| 3 doctored | `doctored/public_holiday_notice_doctored_date.png` | 🔴 altered |
| 4 fake rumour | `fakes/explosions_downtown.png` | ⚪ unverified |

"""Generate ALL clearly-fictional demo images (1080x1350) with proper Arabic shaping.

    python scripts/make_assets.py

Outputs (idempotent, deterministic):
  assets/official/*.png + registry.json     8 fictional official announcements
  assets/doctored/*.png                      2 doctored versions (small region edited)
  assets/screenshots/*.jpg                   2 recompressed/resized "screenshots" of official posts
  assets/fakes/*.png                         2 fake-rumour graphics (stylised, no real photos)
  assets/unrelated/*.png                     2 unrelated images

Fonts: assets/fonts/Cairo-VF.ttf (SIL OFL 1.1, Google Fonts). Needs: pillow, arabic-reshaper, python-bidi.
Every image carries the same small "DEMO / نموذج تجريبي" tag; the logo is a placeholder circle, NOT a real logo.
"""
import json
import math
import os
import random

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
FONT = os.path.join(A, "fonts", "Cairo-VF.ttf")
W, H = 1080, 1350
_reshaper = arabic_reshaper.ArabicReshaper(configuration={"support_ligatures": True})
_fonts = {}
from PIL import features as _features
_RAQM = _features.check('raqm')


def font(size, weight=400):
    k = (size, weight)
    if k not in _fonts:
        f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM if _RAQM else ImageFont.Layout.BASIC)
        f.set_variation_by_axes([weight, 0])
        _fonts[k] = f
    return _fonts[k]


def ar(s):
    """RAQM (HarfBuzz) does shaping + bidi itself, so pass logical text through.
    Fallback to arabic-reshaper + python-bidi if libraqm is unavailable."""
    if _RAQM:
        return s
    return get_display(_reshaper.reshape(s))


def tw(d, s, f):
    return d.textlength(s, font=f)


def text_r(d, x_right, y, s, size, fill, weight=400, shape=True, minx=None):
    """Right-aligned; auto-shrinks to stay right of `minx` (default 30px page margin)."""
    minx = 30 if minx is None else minx
    t = ar(s) if shape else s
    while size > 14 and tw(d, t, font(size, weight)) > x_right - minx:
        size -= 1
    f = font(size, weight)
    d.text((x_right - tw(d, t, f), y), t, font=f, fill=fill)


def text_c(d, cx, y, s, size, fill, weight=400, shape=True):
    t = ar(s) if shape else s
    while size > 14 and tw(d, t, font(size, weight)) > 2 * min(cx, W - cx) - 60:
        size -= 1
    f = font(size, weight)
    d.text((cx - tw(d, t, f) / 2, y), t, font=f, fill=fill)


def text_l(d, x, y, s, size, fill, weight=400):
    d.text((x, y), s, font=font(size, weight), fill=fill)


def wrap_ar(d, s, size, weight, max_w):
    f = font(size, weight)
    lines, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if tw(d, ar(t), f) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para_r(d, x_right, y, s, size, fill, max_w, weight=400, lh=1.55):
    for ln in wrap_ar(d, s, size, weight, max_w):
        text_r(d, x_right, y, ln, size, fill, weight)
        y += int(size * lh)
    return y


def logo(d, cx, cy, r, fg, bg):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg, outline=fg, width=5)
    d.ellipse((cx - r * .55, cy - r * .55, cx + r * .55, cy + r * .55), outline=fg, width=3)
    text_c(d, cx, cy - r * .30, "LOGO", int(r * .5), fg, 700, shape=False)


def demo_tag(d, fg=(120, 120, 120), bg=None, y=None):
    s = "DEMO / نموذج تجريبي"
    f = font(22, 600)
    t = ar(s)
    w = tw(d, t, f)
    x, yy = W - w - 26, (H - 44) if y is None else y
    if bg:
        d.rectangle((x - 10, yy - 4, x + w + 10, yy + 34), fill=bg)
    d.text((x, yy), t, font=f, fill=fg)


def ref_line(d, ref, fg, y, x_left=40):
    text_l(d, x_left, y, f"Ref: {ref}", 24, fg, 600)


# --------------------------------------------------------------------------------------
# 8 official announcements, each with its OWN layout/colours (keeps pHash distances large)
# `key` is the line that gets doctored in the doctored variants.
# --------------------------------------------------------------------------------------
POSTS = [
    dict(id="public_holiday_notice", title="Public holiday notice", title_ar="إشعار بالعطلة الرسمية",
         issuer="UAE Government Media Office", issuer_ar="المكتب الإعلامي لحكومة الإمارات", date="2026-11-24",
         ref="GMO/HOL/2026/114", layout="top_band", c1=(0, 98, 62), c2=(214, 170, 60),
         head="إعلان عطلة رسمية بمناسبة اليوم الوطني",
         body="تعلن حكومة دولة الإمارات أن عطلة اليوم الوطني الخامس والخمسين ستكون وفق الجدول التالي لجميع الجهات الاتحادية والقطاع الخاص.",
         key_label="العطلة الرسمية", key="من الاثنين 1 ديسمبر إلى الأربعاء 3 ديسمبر 2026",
         key2="استئناف الدوام: الخميس 4 ديسمبر 2026", foot="نتمنى للجميع عطلة سعيدة."),
    dict(id="mohre_announcement", title="MOHRE announcement", title_ar="إعلان وزارة الموارد البشرية والتوطين",
         issuer="Ministry of Human Resources & Emiratisation (MOHRE)", issuer_ar="وزارة الموارد البشرية والتوطين",
         date="2026-10-18", ref="MOHRE/ANN/2026/0731", layout="side_band", c1=(18, 52, 110), c2=(232, 238, 248),
         head="تحديث إجراءات تصاريح العمل للقطاع الخاص",
         body="تُعلن الوزارة عن تبسيط إجراءات إصدار تصاريح العمل الجديدة إلكترونياً عبر المنصة الرقمية، مع مدة معالجة لا تتجاوز يومي عمل.",
         key_label="مدة المعالجة", key="يومان (2) عمل", key2="لا حاجة لزيارة مراكز الخدمة",
         foot="للمزيد: القنوات الرسمية للوزارة فقط."),
    dict(id="weekend_schedule_notice", title="Weekend schedule notice", title_ar="إشعار جدول عطلة نهاية الأسبوع",
         issuer="Federal Authority for Government Human Resources", issuer_ar="الهيئة الاتحادية للموارد البشرية الحكومية",
         date="2026-09-02", ref="FAHR/WKD/2026/052", layout="dark_gold", c1=(14, 26, 48), c2=(226, 183, 79),
         head="جدول الدوام الأسبوعي للجهات الاتحادية",
         body="يُعمل بنظام الدوام من الاثنين إلى الخميس من 7:30 صباحاً حتى 3:30 عصراً، ويوم الجمعة من 7:30 صباحاً حتى 12:00 ظهراً.",
         key_label="عطلة نهاية الأسبوع", key="السبت والأحد", key2="الجمعة: دوام نصف يوم",
         foot="ينطبق على الموظفين الاتحاديين."),
    dict(id="golden_visa_update", title="Golden Visa update", title_ar="تحديث شروط التأشيرة الذهبية",
         issuer="Federal Authority for Identity, Citizenship, Customs & Port Security", issuer_ar="الهيئة الاتحادية للهوية والجنسية والجمارك وأمن المنافذ",
         date="2026-08-11", ref="ICP/GV/2026/2209", layout="gold_bottom", c1=(30, 30, 34), c2=(201, 154, 46),
         head="تحديث شروط الإقامة الذهبية للمستثمرين",
         body="تُحدّث الهيئة شروط الإقامة الذهبية لمستثمري العقار، ويمكن التقديم إلكترونياً عبر الموقع الرسمي للهيئة.",
         key_label="الحد الأدنى للاستثمار العقاري", key="2,000,000 درهم", key2="مدة الإقامة: 10 سنوات",
         foot="الشروط قابلة للتحديث وفق القرارات الرسمية."),
    dict(id="school_calendar", title="School calendar 2026-2027", title_ar="التقويم المدرسي 2026-2027",
         issuer="Ministry of Education", issuer_ar="وزارة التربية والتعليم", date="2026-07-20",
         ref="MOE/CAL/2026/009", layout="table", c1=(214, 90, 40), c2=(255, 246, 214),
         head="التقويم المدرسي للعام الدراسي 2026-2027",
         body="تعتمد الوزارة التقويم التالي للمدارس الحكومية والخاصة التي تتبع المنهج الوطني.",
         rows=[("بداية الفصل الأول", "24 أغسطس 2026"), ("إجازة نهاية الفصل الأول", "7 – 25 ديسمبر 2026"),
               ("بداية الفصل الثاني", "4 يناير 2027"), ("إجازة الربيع", "22 مارس – 2 أبريل 2027"),
               ("نهاية العام الدراسي", "2 يوليو 2027")],
         key="2 يوليو 2027", foot="قد تختلف مواعيد بعض المدارس الخاصة."),
    dict(id="ramadan_hours", title="Ramadan working hours", title_ar="ساعات العمل في شهر رمضان",
         issuer="Ministry of Human Resources & Emiratisation (MOHRE)", issuer_ar="وزارة الموارد البشرية والتوطين",
         date="2026-12-30", ref="MOHRE/RMD/2026/880", layout="crescent", c1=(54, 30, 110), c2=(120, 214, 200),
         head="تخفيض ساعات العمل خلال شهر رمضان",
         body="تُخفَّض ساعات العمل اليومية ساعتين في القطاع الخاص طوال الشهر الفضيل، دون أي خصم من الأجر.",
         key_label="التخفيض اليومي", key="ساعتان (2)", key2="طوال شهر رمضان المبارك",
         foot="رمضان كريم."),
    dict(id="icp_emirates_id", title="Emirates ID renewal", title_ar="تجديد الهوية الإماراتية",
         issuer="Federal Authority for Identity, Citizenship, Customs & Port Security", issuer_ar="الهيئة الاتحادية للهوية والجنسية والجمارك وأمن المنافذ",
         date="2026-06-05", ref="ICP/EID/2026/4417", layout="diagonal", c1=(176, 24, 40), c2=(245, 245, 245),
         head="تجديد الهوية الإماراتية عبر التطبيق الرسمي",
         body="يمكن تجديد الهوية الإماراتية إلكترونياً عبر التطبيق الرسمي للهيئة فقط. لا تشارك رمز التحقق مع أي جهة.",
         key_label="رسوم التجديد", key="370 درهماً", key2="الدفع داخل التطبيق الرسمي فقط",
         foot="الهيئة لا تطلب أبداً رمز التحقق عبر الرسائل."),
    dict(id="rta_notice", title="RTA traffic and parking notice", title_ar="إشعار المرور والمواقف",
         issuer="Roads and Transport Authority (RTA)", issuer_ar="هيئة الطرق والمواصلات",
         date="2026-10-02", ref="RTA/TRF/2026/3305", layout="stripes", c1=(20, 20, 20), c2=(224, 36, 54),
         head="تعديلات على المواقف والحركة المرورية",
         body="تُعلن الهيئة عن تعديل ساعات المواقف المدفوعة في المناطق المحددة ابتداءً من الشهر القادم.",
         key_label="المواقف المدفوعة", key="من 8 صباحاً إلى 10 مساءً", key2="مجاني أيام الجمعة والعطلات",
         foot="التفاصيل في القنوات الرسمية للهيئة."),
]


def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def issuer_block(d, p, x_right, y, fg, sub, maxw=700):
    text_r(d, x_right, y, p["issuer_ar"], 34, fg, 700, minx=270)
    # English name may be long: shrink
    size = 24
    while tw(d, p["issuer"], font(size, 500)) > maxw and size > 16:
        size -= 1
    f = font(size, 500)
    d.text((x_right - tw(d, p["issuer"], f), y + 50), p["issuer"], font=f, fill=sub)


def render_post(p, key=None, key2=None):
    """Render one announcement. `key`/`key2` override the doctorable lines."""
    key = key if key is not None else p["key"]
    key2 = key2 if key2 is not None else p.get("key2")
    L = p["layout"]
    c1, c2 = p["c1"], p["c2"]
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    ink = (28, 28, 32)
    ref = p["ref"]

    if L == "top_band":
        d.rectangle((0, 0, W, 270), fill=c1)
        d.rectangle((0, 270, W, 286), fill=c2)
        logo(d, 150, 135, 78, c2, c1)
        issuer_block(d, p, W - 60, 70, (255, 255, 255), (214, 232, 222), 780)
        text_c(d, W / 2, 330, "إعلان رسمي", 46, c1, 700)
        text_r(d, W - 70, 420, p["head"], 52, ink, 700)
        y = para_r(d, W - 70, 520, p["body"], 36, (60, 60, 66), W - 140)
        rr(d, (70, 760, W - 70, 1090), 28, fill=(238, 247, 242), outline=c1, width=5)
        text_c(d, W / 2, 790, p["key_label"], 40, c1, 700)
        text_c(d, W / 2, 885, key, 42, ink, 700)
        text_c(d, W / 2, 990, key2, 40, (70, 70, 76), 600)
        text_r(d, W - 70, 1150, p["foot"], 34, (60, 60, 66))
        d.rectangle((0, 1250, W, H), fill=c1)
        text_l(d, 40, 1275, f"Date: {p['date']}", 26, (255, 255, 255), 600)
        ref_line(d, ref, (255, 255, 255), 1310)
        demo_tag(d, (255, 255, 255))

    elif L == "side_band":
        d.rectangle((0, 0, 300, H), fill=c1)
        logo(d, 150, 170, 84, (255, 255, 255), c1)
        for i in range(5):
            d.rectangle((60, 340 + i * 70, 240, 346 + i * 70), fill=(255, 255, 255))
        text_l(d, 36, 1150, p["date"], 28, (255, 255, 255), 700)
        text_l(d, 36, 1190, ref[:16], 20, (210, 220, 240), 600)
        text_l(d, 36, 1214, ref[16:], 20, (210, 220, 240), 600)
        d.rectangle((300, 0, W, 110), fill=c2)
        text_r(d, W - 40, 22, p["issuer_ar"], 40, c1, 700)
        f = font(22, 600)
        t = p["issuer"]
        d.text((W - 40 - tw(d, t, f), 74), t, font=f, fill=(70, 86, 120))
        text_r(d, W - 50, 200, "إعلان", 44, (200, 60, 40), 700)
        y = 270
        for ln in wrap_ar(d, p["head"], 56, 700, W - 300 - 100):
            text_r(d, W - 50, y, ln, 56, ink, 700)
            y += 88
        y = para_r(d, W - 50, y + 24, p["body"], 34, (60, 60, 66), W - 300 - 100)
        d.rectangle((340, 820, W - 50, 828), fill=c1)
        text_r(d, W - 50, 860, p["key_label"], 38, c1, 700)
        text_r(d, W - 50, 930, key, 60, (200, 60, 40), 700)
        text_r(d, W - 50, 1040, key2, 36, (60, 60, 66), 600)
        text_r(d, W - 50, 1180, p["foot"], 32, (90, 90, 96))
        demo_tag(d, (110, 110, 120))

    elif L == "dark_gold":
        d.rectangle((0, 0, W, H), fill=c1)
        d.rectangle((0, 0, W, 24), fill=c2)
        d.rectangle((0, H - 24, W, H), fill=c2)
        logo(d, W / 2, 190, 92, c2, c1)
        text_c(d, W / 2, 320, p["issuer_ar"], 40, (255, 255, 255), 700)
        text_c(d, W / 2, 380, p["issuer"], 26, (190, 200, 220), 500, shape=False)
        d.line((140, 450, W - 140, 450), fill=c2, width=4)
        yy = 490
        for ln in wrap_ar(d, p["head"], 52, 700, W - 160):
            text_c(d, W / 2, yy, ln, 52, c2, 700)
            yy += 84
        yy = 700
        for ln in wrap_ar(d, p["body"], 34, 400, W - 200):
            text_c(d, W / 2, yy, ln, 34, (230, 234, 242))
            yy += 56
        rr(d, (140, 930, W - 140, 1160), 26, outline=c2, width=5)
        text_c(d, W / 2, 955, p["key_label"], 36, (190, 200, 220), 600)
        text_c(d, W / 2, 1030, key, 64, c2, 700)
        text_c(d, W / 2, 1115, key2, 30, (230, 234, 242))
        text_l(d, 60, 1230, f"{p['date']}   |   {ref}", 24, (170, 180, 200), 600)
        demo_tag(d, (190, 200, 220), y=1270)

    elif L == "gold_bottom":
        d.rectangle((0, 0, W, H), fill=(250, 247, 240))
        d.rectangle((0, 0, 40, H), fill=c2)
        logo(d, 160, 150, 72, c1, (250, 247, 240))
        text_r(d, W - 60, 80, p["issuer_ar"], 30, c1, 700)
        f = font(20, 500)
        t = p["issuer"]
        d.text((W - 60 - tw(d, t, f), 124), t, font=f, fill=(90, 90, 96))
        d.line((90, 270, W - 60, 270), fill=c1, width=3)
        yy = 310
        for ln in wrap_ar(d, p["head"], 58, 700, W - 200):
            text_r(d, W - 80, yy, ln, 58, c1, 700)
            yy += 92
        para_r(d, W - 80, yy + 20, p["body"], 34, (70, 70, 76), W - 200)
        d.rectangle((0, 820, W, 1200), fill=c1)
        d.polygon([(0, 820), (W, 820), (W, 780), (0, 860)], fill=c2)
        text_c(d, W / 2, 880, p["key_label"], 38, (230, 200, 120), 700)
        text_c(d, W / 2, 950, key, 84, (255, 255, 255), 700)
        text_c(d, W / 2, 1090, key2, 40, (230, 230, 235), 600)
        text_r(d, W - 80, 1230, p["foot"], 28, (90, 90, 96))
        text_l(d, 80, 1290, f"{p['date']} | {ref}", 22, (100, 100, 106), 600)
        demo_tag(d, (110, 110, 116), y=1296)

    elif L == "table":
        d.rectangle((0, 0, W, H), fill=c2)
        d.rectangle((0, 0, W, 200), fill=c1)
        d.ellipse((W - 190, 30, W - 30, 190), outline=(255, 255, 255), width=6)
        text_c(d, W - 110, 80, "LOGO", 36, (255, 255, 255), 700, shape=False)
        text_r(d, W - 220, 40, p["issuer_ar"], 46, (255, 255, 255), 700)
        text_r(d, W - 220, 110, p["issuer"], 28, (255, 232, 214), 500, shape=False)
        yy = 250
        for ln in wrap_ar(d, p["head"], 50, 700, W - 140):
            text_r(d, W - 70, yy, ln, 50, c1, 700)
            yy += 80
        para_r(d, W - 70, yy + 10, p["body"], 32, (70, 60, 50), W - 140)
        y0 = 560
        for i, (a, b) in enumerate(p["rows"]):
            fill = (255, 255, 255) if i % 2 == 0 else (255, 233, 178)
            d.rectangle((60, y0, W - 60, y0 + 100), fill=fill, outline=c1, width=3)
            d.line((540, y0, 540, y0 + 100), fill=c1, width=3)
            val = b
            if i == len(p["rows"]) - 1:
                val = key  # last row is the doctorable line
            text_r(d, W - 90, y0 + 22, a, 34, ink, 700)
            text_c(d, 300, y0 + 22, val, 32, c1, 700)
            y0 += 100
        text_r(d, W - 70, 1130, p["foot"], 30, (90, 80, 70))
        text_l(d, 60, 1230, f"Date: {p['date']}", 26, c1, 700)
        ref_line(d, ref, c1, 1270, 60)
        demo_tag(d, (110, 100, 90), y=1296)

    elif L == "crescent":
        for y in range(H):
            t = y / H
            col = tuple(int(c1[i] * (1 - t) + (16, 12, 44)[i] * t) for i in range(3))
            d.line((0, y, W, y), fill=col)
        d.ellipse((90, 90, 330, 330), fill=c2)
        d.ellipse((150, 70, 370, 300), fill=c1)
        for sx, sy, sr in [(420, 130, 8), (520, 230, 6), (640, 110, 9), (760, 190, 5), (900, 120, 7)]:
            d.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 245, 200))
        logo(d, W - 150, 170, 70, (255, 255, 255), c1)
        text_c(d, W / 2, 380, p["issuer_ar"], 40, (255, 255, 255), 700)
        text_c(d, W / 2, 440, p["issuer"], 24, (210, 200, 240), 500, shape=False)
        yy = 540
        for ln in wrap_ar(d, p["head"], 56, 700, W - 160):
            text_c(d, W / 2, yy, ln, 56, c2, 700)
            yy += 88
        yy += 20
        for ln in wrap_ar(d, p["body"], 34, 400, W - 200):
            text_c(d, W / 2, yy, ln, 34, (236, 232, 250))
            yy += 56
        d.ellipse((W / 2 - 250, 930, W / 2 + 250, 1200), outline=c2, width=6)
        text_c(d, W / 2, 970, p["key_label"], 34, (210, 200, 240), 600)
        text_c(d, W / 2, 1040, key, 60, (255, 255, 255), 700)
        text_c(d, W / 2, 1125, key2, 28, c2, 600)
        text_l(d, 50, 1280, f"{p['date']} | {ref}", 22, (200, 190, 230), 600)
        demo_tag(d, (200, 190, 230), y=1296)

    elif L == "diagonal":
        d.rectangle((0, 0, W, H), fill=(250, 250, 250))
        d.polygon([(0, 0), (W, 0), (W, 470), (0, 760)], fill=c1)
        logo(d, 150, 140, 78, (255, 255, 255), c1)
        text_r(d, W - 50, 80, p["issuer_ar"], 36, (255, 255, 255), 700, minx=260)
        f = font(22, 500)
        t = p["issuer"]
        d.text((W - 50 - tw(d, t, f), 132), t, font=f, fill=(255, 220, 224))
        yy = 250
        for ln in wrap_ar(d, p["head"], 52, 700, W - 140):
            text_r(d, W - 60, yy, ln, 52, (255, 255, 255), 700)
            yy += 82
        para_r(d, W - 60, 800, p["body"], 34, (50, 50, 56), W - 140)
        rr(d, (60, 1010, W - 60, 1190), 20, fill=(255, 235, 238), outline=c1, width=4)
        text_r(d, W - 100, 1025, p["key_label"], 32, c1, 700)
        text_r(d, W - 100, 1075, key, 46, ink, 700)
        text_r(d, W - 100, 1135, key2, 28, (80, 80, 86), 600)
        text_l(d, 60, 1215, f"{p['date']} | {ref}", 22, (90, 90, 96), 600)
        text_r(d, W - 60, 1255, p["foot"], 26, (90, 90, 96))
        demo_tag(d, (110, 110, 116), y=1300)

    elif L == "stripes":
        d.rectangle((0, 0, W, H), fill=(240, 240, 240))
        for i in range(9):
            d.rectangle((0, i * 36, W, i * 36 + 18), fill=c1 if i % 2 == 0 else c2)
        d.rectangle((0, 340, W, 470), fill=c1)
        logo(d, 150, 405, 56, (255, 255, 255), c1)
        text_r(d, W - 50, 360, p["issuer_ar"], 40, (255, 255, 255), 700)
        f = font(24, 500)
        d.text((W - 50 - tw(d, p["issuer"], f), 418), p["issuer"], font=f, fill=(210, 210, 214))
        yy = 520
        for ln in wrap_ar(d, p["head"], 54, 700, W - 120):
            text_r(d, W - 60, yy, ln, 54, ink, 700)
            yy += 86
        para_r(d, W - 60, yy + 10, p["body"], 34, (70, 70, 76), W - 120)
        d.rectangle((60, 880, 300, 1120), fill=c2)
        text_c(d, 180, 930, "P", 140, (255, 255, 255), 700, shape=False)
        text_r(d, W - 340, 900, p["key_label"], 36, c2, 700)
        text_r(d, W - 340, 970, key, 48, ink, 700)
        text_r(d, W - 340, 1050, key2, 32, (70, 70, 76), 600)
        d.rectangle((0, 1180, W, H), fill=c1)
        text_r(d, W - 50, 1196, p["foot"], 28, (255, 255, 255), 600)
        text_l(d, 50, 1250, f"{p['date']}   |   {ref}", 24, (220, 220, 224), 600)
        demo_tag(d, (220, 220, 224), y=1296)
    return img


# ------------------------------------------ fakes & unrelated -------------------------

def breaking_frame(d, headline_ar, headline_en, sub_ar, accent):
    d.rectangle((0, 1010, W, 1350), fill=(14, 14, 18))
    d.rectangle((0, 1010, W, 1030), fill=accent)
    d.rectangle((40, 1060, 330, 1130), fill=accent)
    text_c(d, 185, 1068, "عاجل", 52, (255, 255, 255), 700)
    text_r(d, W - 40, 1052, headline_ar, 54, (255, 255, 255), 700)
    text_r(d, W - 40, 1128, headline_en, 30, (255, 220, 120), 600, shape=False)
    text_r(d, W - 40, 1190, sub_ar, 30, (200, 200, 208), 500)
    # tiny print
    text_l(d, 40, 1296, "FAKE / DEMO — fictional graphic, not a real event", 24, (255, 120, 120), 700)


def make_explosions():
    rng = random.Random(40)
    img = Image.new("RGB", (W, H), (20, 24, 44))
    d = ImageDraw.Draw(img)
    for y in range(1010):
        t = y / 1010
        d.line((0, y, W, y), fill=(int(24 + 190 * t ** 2.2), int(22 + 80 * t ** 2.4), int(52 - 20 * t)))
    # skyline silhouettes
    x = 0
    while x < W:
        bw = rng.randint(60, 120)
        bh = rng.randint(260, 620)
        d.rectangle((x, 1010 - bh, x + bw, 1010), fill=(14, 14, 20))
        for wy in range(1010 - bh + 20, 1000, 36):
            for wx in range(x + 10, x + bw - 14, 24):
                if rng.random() < .35:
                    d.rectangle((wx, wy, wx + 8, wy + 14), fill=(250, 210, 120))
        x += bw + rng.randint(0, 10)
    # explosion bursts (stylised)
    for cx, cy, r in [(300, 700, 150), (640, 560, 210), (860, 760, 120)]:
        for k in range(14, 0, -1):
            rr_ = r * k / 14
            col = (255, int(60 + 190 * (1 - k / 14)), int(20 + 150 * (1 - k / 14) ** 2))
            pts = []
            for a in range(0, 360, 12):
                jr = rr_ * (0.75 + 0.35 * rng.random())
                pts.append((cx + jr * math.cos(math.radians(a)), cy + jr * math.sin(math.radians(a))))
            d.polygon(pts, fill=col)
    breaking_frame(d, "انفجارات في وسط مدينة دبي", "EXPLOSIONS IN DOWNTOWN DUBAI", "مصادر غير مؤكدة — تداولوا الخبر", (200, 20, 30))
    demo_tag(d, (230, 230, 230), bg=(14, 14, 18), y=H - 44)
    return img


def make_burj():
    rng = random.Random(828)
    img = Image.new("RGB", (W, H), (30, 40, 70))
    d = ImageDraw.Draw(img)
    for y in range(1010):
        t = y / 1010
        d.line((0, y, W, y), fill=(int(40 + 120 * t), int(60 + 70 * t), int(110 + 30 * t)))
    # ground haze
    d.rectangle((0, 900, W, 1010), fill=(70, 60, 60))
    # tower, tapered, broken at top; leaning
    base = [(380, 1010), (500, 1010), (500, 400), (470, 380), (440, 640), (420, 800)]
    d.polygon([(360, 1010), (620, 1010), (560, 700), (520, 380), (470, 330), (440, 600)], fill=(205, 212, 222))
    d.polygon([(480, 330), (520, 380), (560, 700), (620, 1010), (540, 1010), (500, 700)], fill=(160, 168, 182))
    # break + falling segment
    d.polygon([(520, 380), (700, 250), (740, 300), (560, 460)], fill=(190, 196, 208))
    for _ in range(90):  # debris & dust
        px, py = rng.randint(300, 900), rng.randint(300, 1000)
        s = rng.randint(4, 22)
        d.rectangle((px, py, px + s, py + s), fill=(110 + rng.randint(0, 80),) * 3)
    for cx, cy, r in [(520, 900, 260), (760, 940, 200), (330, 950, 180)]:
        for k in range(8, 0, -1):
            g = 90 + k * 14
            d.ellipse((cx - r * k / 8, cy - r * k / 8 * .55, cx + r * k / 8, cy + r * k / 8 * .55), fill=(g, g - 6, g - 14))
    breaking_frame(d, "انهيار برج خليفة", "BURJ KHALIFA COLLAPSE", "فيديو متداول — لم يتم التحقق منه", (210, 110, 10))
    demo_tag(d, (230, 230, 230), bg=(14, 14, 18), y=H - 44)
    return img


def make_unrelated_dunes():
    img = Image.new("RGB", (W, H), (255, 200, 120))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=(int(255 - 90 * t), int(150 + 50 * (1 - t)), int(90 + 120 * (1 - t))))
    d.ellipse((700, 260, 940, 500), fill=(255, 244, 200))
    for i, (col, base, amp) in enumerate([((214, 140, 70), 820, 90), ((190, 110, 54), 960, 120), ((150, 80, 40), 1120, 140)]):
        pts = [(0, H)]
        for x in range(0, W + 20, 20):
            pts.append((x, base + amp * math.sin(x / 190 + i * 1.7) * .6))
        pts.append((W, H))
        d.polygon(pts, fill=col)
    text_c(d, W / 2, 90, "Desert sunset (stock-style art)", 40, (90, 40, 20), 700, shape=False)
    demo_tag(d, (60, 30, 10))
    return img


def make_unrelated_recipe():
    img = Image.new("RGB", (W, H), (244, 250, 240))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 180), fill=(70, 140, 70))
    text_c(d, W / 2, 50, "وصفة كبسة الدجاج", 80, (255, 255, 255), 700)
    items = ["دجاج - 1 كيلو", "أرز بسمتي - 3 أكواب", "بصل وطماطم", "بهارات الكبسة", "ماء - 5 أكواب"]
    y = 260
    for it in items:
        d.ellipse((W - 120, y + 12, W - 90, y + 42), fill=(240, 160, 40))
        text_r(d, W - 150, y, it, 48, (40, 60, 40), 600)
        y += 110
    d.rectangle((80, 900, W - 80, 1200), outline=(70, 140, 70), width=8)
    for i in range(12):
        d.ellipse((140 + i * 70, 960 + (i % 3) * 60, 200 + i * 70, 1020 + (i % 3) * 60), fill=(250, 240, 200), outline=(200, 150, 60), width=4)
    demo_tag(d, (90, 110, 90))
    return img


# ------------------------------------------------------------------------------------

def main():
    for sub in ("official", "doctored", "screenshots", "fakes", "unrelated"):
        os.makedirs(os.path.join(A, sub), exist_ok=True)
    registry = []
    by_id = {p["id"]: p for p in POSTS}
    for p in POSTS:
        render_post(p).save(os.path.join(A, "official", p["id"] + ".png"), optimize=True)
        registry.append({k: p[k] for k in ("id", "title", "title_ar", "issuer", "date")})
    with open(os.path.join(A, "official", "registry.json"), "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

    # doctored: SAME render, only the key line changes
    hp = by_id["public_holiday_notice"]
    render_post(hp, key="من الاثنين 1 ديسمبر إلى الجمعة 12 ديسمبر 2026").save(
        os.path.join(A, "doctored", "public_holiday_notice_doctored_date.png"), optimize=True)
    gv = by_id["golden_visa_update"]
    render_post(gv, key="200,000 درهم").save(os.path.join(A, "doctored", "golden_visa_update_doctored_amount.png"), optimize=True)

    # screenshots: recompress + rescale (like a WhatsApp forward / phone screenshot)
    for pid, scale in (("public_holiday_notice", 0.62), ("mohre_announcement", 0.74)):
        im = Image.open(os.path.join(A, "official", pid + ".png")).convert("RGB")
        im = im.resize((int(W * scale), int(H * scale)), Image.LANCZOS)
        im.save(os.path.join(A, "screenshots", pid + "_screenshot.jpg"), "JPEG", quality=70)

    make_explosions().save(os.path.join(A, "fakes", "explosions_downtown.png"), optimize=True)
    make_burj().save(os.path.join(A, "fakes", "burj_collapse.png"), optimize=True)
    make_unrelated_dunes().save(os.path.join(A, "unrelated", "desert_sunset.png"), optimize=True)
    make_unrelated_recipe().save(os.path.join(A, "unrelated", "recipe_card.png"), optimize=True)
    print("assets written under", A)


if __name__ == "__main__":
    main()

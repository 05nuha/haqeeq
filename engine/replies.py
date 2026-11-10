ARABIC_REPLIES = {
    "genuine":    "✅ صحيح — يتطابق مع مرجع رسمي متاح.",
    "altered":    "🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله.",
    "unverified": "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً.",
    "scam_risk":  "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء.",
}


def reply_for(result):
    v = result.get("verdict", "unverified")
    msg = ARABIC_REPLIES.get(v, ARABIC_REPLIES["unverified"])
    if v == "scam_risk" and result.get("ai_reason"):
        msg += "\n🤖 " + str(result["ai_reason"])
    elif v == "altered" and result.get("changed_pct") is not None:
        if result["changed_pct"] >= 0.1:
            msg += f"\nتم رصد تعديل في {result['changed_pct']:.1f}% من الصورة."
        else:   # a small localised edit (e.g. one digit of a date): a "0.0%" would read as "no change"
            msg += "\nتم رصد تعديل موضعي في جزء صغير من الصورة (مثل تاريخ أو رقم)."
    return msg

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
        msg += f"\nتم رصد تعديل في {result['changed_pct']:.1f}% من الصورة."
    return msg

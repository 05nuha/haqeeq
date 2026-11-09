"""python -m engine.gemini_probe  -- lists models available to GEMINI_API_KEY and runs one test classification."""
import os
import sys

import requests

from .text_check import ai_text_check, _model


def main():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("Set GEMINI_API_KEY first.")
    r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                     headers={"x-goog-api-key": key}, timeout=15)
    print("HTTP", r.status_code)
    for m in r.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in m["name"]:
            print(" ", m["name"].split("/")[-1])
    print("\nUsing model:", _model(), "(override with GEMINI_MODEL)")
    out = ai_text_check("عاجل: سيتم إيقاف هويتك الإماراتية، أرسل رمز OTP عبر الرابط فوراً")
    print("Result:", out if out else "FAILED (check key / model name / quota)")


if __name__ == "__main__":
    main()

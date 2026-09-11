"""
ml_model.py
-----------
Placeholder SIF classifier — a direct server-side port of the
mockClassify() keyword matcher that used to live in the browser
(hsse-console/script.js). It exists so the backend is fully wired
end-to-end today.

WHEN YOUR REAL MODEL IS READY (DistilRoBERTa fine-tune, or
embeddings + XGBoost), replace the body of classify_report() below
with a call to it. Keep the same function signature and return
shape so nothing else in main.py needs to change:

    def classify_report(text: str) -> dict:
        return {
            "sif_potential": bool,
            "confidence": float,       # 0.0–1.0
            "rule_tag": str | None,    # one of the IOGP Life-Saving Rules, or None
            "precursor_keywords": list[str],
        }

For the real model, a natural place to load it is once at module
import time (e.g. `model = joblib.load("model.pkl")` for an
XGBoost pipeline, or `pipeline = transformers.pipeline(...)` for a
Hugging Face model), so it isn't reloaded on every request.
"""

import random

PRECURSOR_KEYWORDS = {
    "Energy Isolation": ["energy isolation", "lockout", "tagout", "isolation", "live circuit", "de-energ"],
    "Confined Space": ["confined space", "gas testing", "atmospheric", "ventilation", "manhole"],
    "Hot Work": ["hot work", "welding", "grinding", "spark", "flammable"],
    "Line of Fire": ["line of fire", "suspended load", "crane", "dropped object", "pinch point"],
    "Working at Height": ["scaffold", "height", "fall protection", "harness", "ladder"],
}


def classify_report(text: str) -> dict:
    lower = (text or "").lower()
    hits: list[str] = []
    best_rule = None

    for rule, keywords in PRECURSOR_KEYWORDS.items():
        matched = [k for k in keywords if k in lower]
        if matched:
            hits.extend(matched)
            best_rule = rule  # last-matching rule wins, same behavior as the JS version

    sif_potential = len(hits) > 0
    if sif_potential:
        confidence = min(0.99, 0.62 + len(hits) * 0.11 + random.random() * 0.08)
    else:
        confidence = random.random() * 0.25

    return {
        "sif_potential": sif_potential,
        "confidence": round(confidence, 2),
        "rule_tag": best_rule if sif_potential else None,
        "precursor_keywords": hits,
    }
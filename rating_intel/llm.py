"""Optional AI-assisted labelling with strict validation and automatic fallback to the rules.

Design rules
- OFF by default. The pipeline is fully functional without it. No paid provider is implemented.
- A provider is any object with `complete(prompt: str) -> str`. The only built-in one is a LOCAL Ollama server
  (free, runs on your machine). Tests use a fake provider.
- The model is only asked about reviews the deterministic rules did NOT label (the recall gap).
- Every model answer is validated: JSON object, `labels` is a list of known category ids, `evidence` is a
  quote that really occurs in the review. Anything else is rejected, retried, and finally dropped.
- LLM labels are stored in separate columns and never overwrite rule labels or enter the headline counts.
- Status: validated with a fake provider only. It has NOT been measured against a real model on hand labels;
  measure precision/recall on the audit sample (scripts/validate_classifier.py logic) before trusting it.
"""
import json
import re
import time
import urllib.request

from .taxonomy import CATEGORIES

VALID_IDS = [c["id"] for c in CATEGORIES]
MIN_EVIDENCE_CHARS = 8  # a one-word quote such as "app" would validate almost any label


def build_prompt(text, categories=CATEGORIES):
    lines = [f"- {c['id']}: {c['label']}" for c in categories]
    return (
        "You label complaints in a Google Play review of an employee commute app.\n"
        "Choose zero or more category ids from the list. Use ONLY ids from the list.\n"
        "Quote one short phrase from the review as evidence (copy it exactly).\n"
        'Reply with JSON only: {"labels": ["ID", ...], "evidence": "exact quote"}\n\n'
        "Categories:\n" + "\n".join(lines) + "\n\nReview:\n" + text.strip()[:1500]
    )


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


def parse_llm_labels(raw, text, valid_ids=VALID_IDS):
    """Validate a model answer. Returns (labels, error). `error` is None when the answer is acceptable."""
    if not isinstance(raw, str) or not raw.strip():
        return [], "empty_response"
    cleaned = _FENCE.sub("", raw.strip())
    try:
        obj = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        return [], "invalid_json"
    if not isinstance(obj, dict):
        return [], "not_an_object"
    labels = obj.get("labels")
    if not isinstance(labels, list) or not all(isinstance(x, str) for x in labels):
        return [], "labels_not_list_of_strings"
    unknown = [x for x in labels if x not in valid_ids]
    if unknown:
        return [], f"unknown_ids:{','.join(unknown[:3])}"
    labels = sorted(set(labels))
    if labels:
        ev = obj.get("evidence")
        if not isinstance(ev, str) or not ev.strip():
            return [], "missing_evidence"
        ev_n = " ".join(ev.split()).lower()
        if len(ev_n) < MIN_EVIDENCE_CHARS:
            return [], "evidence_too_short"
        if ev_n not in " ".join(text.split()).lower():
            return [], "evidence_not_in_text"
    return labels, None


def label_with_llm(text, provider, retries=2, base_sleep=1.0, sleep=time.sleep):
    """Ask the provider; retry on provider errors or invalid answers. Returns dict(labels, source, errors)."""
    errors = []
    for attempt in range(retries + 1):
        try:
            raw = provider.complete(build_prompt(text))
        except Exception as exc:  # network, timeout, server error
            errors.append(f"provider_error:{type(exc).__name__}")
        else:
            labels, err = parse_llm_labels(raw, text)
            if err is None:
                return {"labels": labels, "source": "llm", "errors": errors}
            errors.append(err)
        if attempt < retries:
            sleep(base_sleep * (2 ** attempt))
    return {"labels": [], "source": "rules_fallback", "errors": errors}


def hybrid_label(text, rule_hits, provider, retries=2, sleep=time.sleep):
    """Rules first. Only when the rules found nothing and a provider exists is the model consulted."""
    if rule_hits or provider is None or not isinstance(text, str) or not text.strip():
        return {"labels": [], "source": "rules", "errors": []}
    return label_with_llm(text, provider, retries=retries, sleep=sleep)


class OllamaProvider:
    """Local, free LLM server (https://ollama.com). Nothing leaves your machine."""

    def __init__(self, url="http://localhost:11434", model="llama3.1:8b", timeout=60):
        self.url, self.model, self.timeout = url.rstrip("/"), model, timeout

    def complete(self, prompt):
        body = json.dumps({"model": self.model, "prompt": prompt, "stream": False, "format": "json",
                           "options": {"temperature": 0}}).encode("utf-8")
        req = urllib.request.Request(self.url + "/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 (local URL by config)
            return json.loads(resp.read().decode("utf-8")).get("response", "")


def load_env_file(path):
    """Minimal KEY=VALUE reader (no python-dotenv dependency). Missing file -> {}."""
    out = {}
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    out[k.strip()] = v.strip().strip('"').strip("'")
    except OSError:
        pass
    return out


def provider_from_env(env):
    """Build a provider from env-style dict. RI_LLM_PROVIDER: none (default) | ollama."""
    name = (env.get("RI_LLM_PROVIDER") or "none").strip().lower()
    if name in ("", "none"):
        return None
    if name == "ollama":
        return OllamaProvider(env.get("RI_OLLAMA_URL", "http://localhost:11434"),
                              env.get("RI_OLLAMA_MODEL", "llama3.1:8b"),
                              float(env.get("RI_LLM_TIMEOUT", "60")))
    raise ValueError(f"Unsupported RI_LLM_PROVIDER '{name}'. Only 'none' and 'ollama' (local) are implemented; "
                     "paid providers are intentionally not included.")

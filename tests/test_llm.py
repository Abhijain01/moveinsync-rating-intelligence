import json

import pytest

from rating_intel.llm import (VALID_IDS, hybrid_label, label_with_llm, parse_llm_labels, provider_from_env)

TEXT = "App keeps crashing when I open it"


class Fake:
    def __init__(self, answers):
        self.answers, self.calls = list(answers), 0

    def complete(self, prompt):
        self.calls += 1
        a = self.answers[min(self.calls - 1, len(self.answers) - 1)]
        if isinstance(a, Exception):
            raise a
        return a


def good(labels=("CRASH_LOAD_PERF",), ev="keeps crashing"):
    return json.dumps({"labels": list(labels), "evidence": ev})


def nosleep(_):
    pass


def test_valid_answer_and_fenced_json():
    assert parse_llm_labels(good(), TEXT) == (["CRASH_LOAD_PERF"], None)
    assert parse_llm_labels("```json\n" + good() + "\n```", TEXT) == (["CRASH_LOAD_PERF"], None)
    assert parse_llm_labels(json.dumps({"labels": []}), TEXT) == ([], None)  # no labels needs no evidence


@pytest.mark.parametrize("raw,err", [
    ("", "empty_response"), (None, "empty_response"), ("not json", "invalid_json"), ("[1,2]", "not_an_object"),
    (json.dumps({"labels": "CRASH_LOAD_PERF"}), "labels_not_list_of_strings"),
    (json.dumps({"labels": [1]}), "labels_not_list_of_strings"),
    (json.dumps({"labels": ["MADE_UP"], "evidence": "x"}), "unknown_ids:MADE_UP"),
    (json.dumps({"labels": ["CRASH_LOAD_PERF"]}), "missing_evidence"),
    (json.dumps({"labels": ["CRASH_LOAD_PERF"], "evidence": "totally invented quote"}), "evidence_not_in_text"),
    (json.dumps({"labels": ["CRASH_LOAD_PERF"], "evidence": "app"}), "evidence_too_short"),
])
def test_invalid_answers_are_rejected(raw, err):
    labels, e = parse_llm_labels(raw, TEXT)
    assert labels == [] and e == err


def test_retry_then_success():
    p = Fake(["garbage", RuntimeError("timeout"), good()])
    r = label_with_llm(TEXT, p, retries=2, sleep=nosleep)
    assert r["source"] == "llm" and r["labels"] == ["CRASH_LOAD_PERF"] and p.calls == 3
    assert r["errors"] == ["invalid_json", "provider_error:RuntimeError"]


def test_persistent_failure_falls_back_to_rules():
    p = Fake([RuntimeError("down")])
    r = label_with_llm(TEXT, p, retries=2, sleep=nosleep)
    assert r["source"] == "rules_fallback" and r["labels"] == [] and p.calls == 3


def test_backoff_sleep_schedule():
    slept = []
    label_with_llm(TEXT, Fake(["bad"]), retries=2, base_sleep=1.0, sleep=slept.append)
    assert slept == [1.0, 2.0]


def test_hybrid_skips_model_when_rules_hit_or_no_provider_or_empty_text():
    p = Fake([good()])
    assert hybrid_label(TEXT, True, p)["source"] == "rules" and p.calls == 0
    assert hybrid_label(TEXT, False, None)["source"] == "rules"
    assert hybrid_label("  ", False, p)["source"] == "rules" and p.calls == 0
    assert hybrid_label(TEXT, False, p, sleep=nosleep)["source"] == "llm" and p.calls == 1


def test_provider_from_env():
    assert provider_from_env({}) is None and provider_from_env({"RI_LLM_PROVIDER": "none"}) is None
    assert provider_from_env({"RI_LLM_PROVIDER": "ollama"}).model
    with pytest.raises(ValueError):
        provider_from_env({"RI_LLM_PROVIDER": "openai"})  # paid providers are intentionally unsupported


def test_valid_ids_cover_taxonomy():
    assert "CRASH_LOAD_PERF" in VALID_IDS and len(VALID_IDS) == 26

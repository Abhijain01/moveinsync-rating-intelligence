"""Compare two cleaned snapshots (older vs newer) of the same app."""
import pandas as pd


def compare_snapshots(old, new):
    """Return a dict of counts and DataFrames describing what changed between two cleaned snapshots.

    - new_reviews: ids only in `new`
    - missing_in_new: ids only in `old` (deleted by reviewers or Google, or `new` is a partial pull)
    - edited: same id, different text
    - rescored: same id, different star rating
    - reply_added: same id, no reply before and a reply now
    """
    o = old.set_index("review_id")
    n = new.set_index("review_id")
    common = o.index.intersection(n.index)
    new_ids = n.index.difference(o.index)
    gone = o.index.difference(n.index)
    oc, nc = o.loc[common], n.loc[common]
    edited = common[(oc["text_norm"].fillna("") != nc["text_norm"].fillna("")).to_numpy()]
    rescored = common[(oc["score"] != nc["score"]).to_numpy()]
    reply_added = common[((~oc["has_reply"].astype(bool)) & nc["has_reply"].astype(bool)).to_numpy()]
    partial = bool(len(new) and len(old) and str(new["date_ist"].min()) > str(old["date_ist"].min()))
    return {
        "old_rows": len(old), "new_rows": len(new), "common": len(common),
        "new_reviews": n.loc[new_ids].reset_index() if len(new_ids) else n.iloc[0:0].reset_index(),
        "n_new": len(new_ids), "n_missing_in_new": len(gone),
        "missing_in_new": o.loc[gone].reset_index()[["review_id", "date_ist", "score"]] if len(gone) else pd.DataFrame(columns=["review_id", "date_ist", "score"]),
        "n_edited": len(edited), "n_rescored": len(rescored), "n_reply_added": len(reply_added),
        "new_snapshot_may_be_partial": partial,
    }


def new_review_score_mix(new_reviews):
    if new_reviews.empty:
        return {}
    return {int(k): int(v) for k, v in new_reviews["score"].value_counts().sort_index().items()}

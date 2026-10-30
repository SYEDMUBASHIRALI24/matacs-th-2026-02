"""Deterministic scoring step of the triage flow.

Input : extractions.json (facts the AI extracted, already validated)
        criteria.json    (the admin's criteria, weights and scoring methods)
Output: ranked list printed to the screen.

No AI and no API keys here: the same input always gives the same output.
Run:  python score.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
criteria = json.loads((HERE / "criteria.json").read_text())
facts = json.loads((HERE / "extractions.json").read_text())


def gate(f):
    """Mandatory pass/fail checks, then manipulation flag. Returns (status, why)."""
    if not f["licence_held"]:
        return "ineligible", "licence not held by bidder"
    if not (f["wsib"] and f["insurance_5m"]):
        return "ineligible", "WSIB or insurance not confirmed"
    if f["injection_flag"]:
        return "flagged", "embedded instruction aimed at the AI reviewer"
    return "eligible", ""


def raw_score(c, f, pool):
    """Score 0..1 for one criterion. 'pool' = eligible bids, used for relative methods."""
    m = c["method"]
    if m == "count_capped":
        return min(f["installs_100kw_5y"], c["cap"]) / c["cap"]
    if m == "lowest_over_price":
        if f["price"] is None or f["price"] > criteria["price_ceiling"]:
            return 0.0
        return min(p["price"] for p in pool) / f["price"]
    if m == "shortest_over_weeks":
        if f["weeks"] is None or f["weeks"] > criteria["max_weeks"]:
            return 0.0  # missing or over the limit earns nothing
        return min(p["weeks"] for p in pool if p["weeks"]) / f["weeks"]
    if m == "warranty_blend":
        panel = min(f["panel_years"] / c["panel_cap"], 1)
        work = min(f["workmanship_years"] / c["workmanship_cap"], 1)
        return c["panel_share"] * panel + (1 - c["panel_share"]) * work
    if m == "checklist":
        return sum(bool(f[i]) for i in c["items"]) / len(c["items"])
    raise ValueError(f"unknown method {m}")


def score(f, pool):
    parts = {c["id"]: round(c["weight"] * raw_score(c, f, pool), 2)
             for c in criteria["weighted"]}
    return round(sum(parts.values()), 1), parts


status = {k: gate(f) for k, f in facts.items()}
# Ineligible and flagged bids are excluded BEFORE relative scoring,
# so a cheap disqualified bid cannot distort everyone else's price score.
pool = [f for k, f in facts.items() if status[k][0] == "eligible"]

results = []
for k, f in facts.items():
    st, why = status[k]
    if st == "eligible":
        total, parts = score(f, pool)
        results.append((k, st, total, parts, why))
    else:
        # flagged bids get a reviewer-only "shadow" score; ineligible get none
        shadow = score(f, pool)[0] if st == "flagged" else None
        results.append((k, st, shadow, {}, why))

# tie-break: score, then lower price, then letter
ranked = sorted([r for r in results if r[1] == "eligible"],
                key=lambda r: (-r[2], facts[r[0]]["price"], r[0]))
for i, r in enumerate(ranked, 1):
    print(f"#{i} {r[0]}  {r[2]:5.1f}  {r[3]}")
for r in results:
    if r[1] != "eligible":
        extra = f" (reviewer-only shadow score {r[2]})" if r[2] is not None else ""
        print(f"-- {r[0]}  {r[1]}: {r[4]}{extra}")

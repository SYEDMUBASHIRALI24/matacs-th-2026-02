# Write-up: AI Proposal Triage (MATACS-TH-2026-02)

**Design in one line:** AI reads messy text and extracts facts. Plain code applies the rules, does the maths and ranks. A person checks and decides. Details of the flow are in `diagram/`.

**Assumptions:** (1) "Last 5 years" means since late 2021. (2) A proposal that gives no completion time earns 0 on timeline and is shown to the reviewer as "missing information". (3) Relative scores (price, timeline) are calculated only among eligible bids. (4) Proposal text is treated as untrusted data, never as instructions.

## 1. AI vs. rules

**AI is used for two things only:**
- **Extraction (step 6):** turning free text into structured facts with a verbatim quote and page for each. Proposals are written in different ways (a start year in one, a "last N years" count in another), so reading them is where AI adds real value.
- **Wording (step 11):** a short plain-English reason, built from the score breakdown. It can reword but cannot change a number.

**Plain code or rules are used for everything else:** intake checks, criteria loading, mandatory pass/fail, scoring formulas, ranking, tie-breaks, logging.

**Why this line:** reading is fuzzy and AI is good at it. Scoring must be repeatable, auditable and not influenceable by text inside a proposal, so it is code. This also keeps cost low, because AI runs once per proposal.

## 2. Consistency and explainability

- Each proposal is extracted **once**. The result is stored against the file hash, prompt version and model version. Re-ranking reads the stored facts, so **ranking twice gives the same result**, because scoring is pure code.
- AI output is not perfectly repeatable even at temperature 0, so the stored extraction is the record of truth. If a re-extraction is ever run, differences are shown to the reviewer as a diff.
- Every extracted fact carries a quote and page. Code checks the quote really exists in the source text, which catches invented facts.
- The reviewer sees a table per proposal: each criterion, the fact found (with its quote), the formula, the points and the total. The one-line reason is generated from this table, so it cannot disagree with it.
- Sample result: A 97.8, E 87.7, D 73.5. B is ineligible. C is flagged (see `ranking.json`).

## 3. Human in the loop

**The tool recommends. A person decides.**
- Reviewer checks the ranking and can: correct a wrongly extracted fact (re-scores instantly, code only), contact a bidder for missing information (D's timeline), clear or reject a flag (C), or override a rank with a written reason.
- Ineligible and flagged proposals are always shown with reasons, never silently dropped, so a wrong rejection can be reversed.
- The final award is a separate human action. The tool never awards.
- **Audit log:** who uploaded what, file hashes, criteria version, prompt and model version, extracted facts with quotes, scores, flags, every override (who, when, why), and the final decision.

## 4. Changing criteria

- Criteria are **versioned**. A scoring run stores the version it used and never changes afterwards.
- If an admin edits criteria or weights, a new version is created (weights must total 100%). Old results stay visible, labelled "scored under v1", with a banner "criteria have changed".
- **Weight or formula change:** re-score from the stored facts. Code only, instant, no AI cost.
- **New criterion needing a new fact:** extract only that field again, then re-score.
- The reviewer chooses whether to re-score; both rankings are kept for comparison. Once an award is confirmed, that project's result is locked, and later edits apply only to future runs.

## 5. Risks and safeguards

| Risk | Safeguard |
|---|---|
| **Wrong extraction** (misread number, wrong year) | Quote + page for each fact, code verifies the quote and cross-checks numbers, reviewer can correct and re-score. |
| **Made-up facts** | "not stated" is the default. A fact without a verifiable quote is rejected and retried once, then flagged. |
| **Manipulation / hidden instructions** (C has one) | Text is passed as quoted data. A rule-based scan and the AI both report instruction-like text. Flagged proposals are not auto-ranked. AI never sets scores, so such text has nothing to act on. |
| **Bias** | Bidder names are hidden from scoring. Only admin criteria are scored (no brand, size or location preference). Same formulas for everyone. Periodic review of overrides and outcomes. |
| **Unfair formulas** (e.g. cheap but unqualified bid distorting price scores) | Ineligible and flagged bids are removed before relative scoring. B's low price does not lower anyone else's price score. |
| **Vague or missing info** (D's timeline, B's unconfirmed subcontractor licence) | Missing = no credit, never guessed. Mandatory items must be held by the bidder and stated, so a promise to hire later fails. |
| **Poor PDFs** | OCR fallback. Unreadable pages are marked and the proposal is flagged if key facts are missing. |
| **Cost** | One AI call per proposal, cached. Everything else is code. Input length limit. |
| **Model change** | Model and prompt versions are pinned and logged. The sample set is a regression test before any upgrade. |
| **Over-trust** | Human review is required before any decision. Scores are shown as a recommendation with evidence. |

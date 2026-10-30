# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Syed Mubashir Ali
- **Reference:** MATACS-TH-2026-02
- **Role:** Associate Software Developer
- **Time actually spent:** about 90 minutes

## Files

| File | What it is |
|---|---|
| [WRITEUP.md](WRITEUP.md) | Answers to the five questions |
| [diagram/process-flow.png](diagram/process-flow.png) | Process flow from upload to ranked output (AI, rule and human steps) |
| [PROMPTS.md](PROMPTS.md) | The extraction prompt and the reason-wording prompt |
| [ranking.json](ranking.json) | Expected ranking of proposals A to E |
| [prototype/](prototype) | Optional: small deterministic scorer (`python prototype/score.py`) |

## Short summary

AI only reads the proposals and extracts facts with evidence quotes. Plain code checks the mandatory criteria, calculates the scores and ranks. A human reviews, can override and makes the final award. Proposals are treated as untrusted data. Proposal C contains an instruction aimed at automated reviewers, so it is flagged for a person instead of being ranked.

## How I used AI tools

I used Claude to draft the first version of the flow, prompts and write-up, and to check my files before submitting. When I reviewed the draft, I found that some wording had been copied from the brief and proposals, which the brief does not allow, so I rewrote those phrases in my own words. I also checked the scoring myself by running score.py, and I decided to keep the proposal with the missing completion time ranked (timeline scored 0) because timeline is a weighted criterion, not a mandatory one.

## Notes

- Only the fictional samples were used, referred to by letter. No brief text or proposal text is copied here.
- No API keys are used. The prototype does not call any AI service.

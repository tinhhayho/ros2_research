# Fact-check — 2026-07-20

## Part 1: AUTOSAR history (compact-deck slide 2 + timeline diagram)

**Trigger**: user asked to re-verify the deck's history content against primary sources.
**How produced**: packaged `fact-check` workflow (run `wf_d6b656b7-102`), 21 claims
(H1–H21) extracted from the *Why AUTOSAR exists* slide and the `autosar-timeline`
diagram. One Sonnet verifier per claim against primary sources, plus an adversarial
second opinion on every non-clean verdict. 24 agents, 0 errors.

**Result: 18 correct, 3 partially-correct, 0 wrong.** All founding facts (2002 talks,
July 2003 Development Agreement, founding five + Siemens VDO, Sep 2003 VDI Baden-Baden
debut, Heinecke et al. 2006 attribution, licensing model, Rivian/Sonatus), all CP dates
(1.0 May 2005, 4.0 Dec 2009, 4.2.1 Oct 2014 SOME/IP Transformer, 4.4.0 Oct 2018), the
AP line (17-03 first, DDS since 18-03, 19-03 last standalone), the R19-11 unification,
R25-11 (2025-11-27, internal R4.11.0), the DDS-Transformer-on-CP status, and the
R25-11 module removals (Fls/Eep/TTCAN/LdCom) were confirmed against autosar.org and
the release documents.

### Findings (the 3 partially-correct claims)

1. **H3 — partner count is stale.** The deck says "~360 partners today". AUTOSAR's own
   `AUTOSAR_EXP_Introduction_Part1.pdf` (partner status 09.04.2026, HTTP Last-Modified
   2026-04-09) charts year-end totals 2021=317, 2022=349, 2023=366, 2024=359,
   **2025=339** (regional map Asia 164 + Europe 128 + NA 41 + Africa 6 = 339). The
   marketing page rounds to "350+". The count peaked in 2023 and is trending down.
   The deck's "~360" matches the superseded 2024 snapshot.
   **Fix**: "about 340 partners (339 at the end of 2025)"; cite the partner-status date.
2. **H13 — Foundation R1.0.0 date: sources conflict.** The public history page groups
   FO 1.0.0 under **October 2016**, but the Foundation Release Overview's own change
   history dates the initial release **2016-11-30**. The "carries the shared
   meta-model/schema" half is confirmed.
   **Fix**: timeline node becomes "Nov 2016" (document's own date), sources caption
   notes the history-page discrepancy.
3. **H14 — "last standalone FO" is the wrong frame.** FO 1.5.1 (2019-03-29) was the
   last release under the Foundation-specific 1.x numbering; Foundation itself
   continues as a distinct standard inside every unified release (R19-11 explicitly
   "supersedes R1.5", through R25-11 today).
   **Fix**: reword to "last FO release before the unified R{yy}-11 line"; harmonize
   the parallel CP 4.4.0 and AP 19-03 node labels to the same unambiguous phrasing
   (their facts verified correct; only the word "standalone" is ambiguous).

Verifier-consistency note (for the record): the CP/AP "last standalone" labels passed
while the FO one was flagged; the underlying dates agree everywhere, the disagreement
is only over what "standalone" means. Resolved by dropping the word on all three nodes.

Corrections land in: compact deck slide 2 (body + say-note + gloss citation), the
`autosar-timeline` SVG + drawio mirror, and the same figures wherever the full deck or
blog repeats them. Applied in the post-3-repo fix pass (see Part 2 when it completes).

## Part 2: new repo-analysis slides (3-repo rework)

**Trigger**: user replaced the deck's 4-repo section with 3 chosen repos
(`Fang717/arccore-core-21`, `autoas/as`, `langroodi/Adaptive-AUTOSAR`).
**How produced**: workflow `compact-deck-3repos` (run `wf_2de18e20-527`, 25 agents,
0 errors): per-repo clone-and-pin research → slide rewrite (8 slides → 6; langroodi
kept byte-for-byte except renumbering) → build + PDF overflow check → three max-effort
verifiers (parity, citation, style) with two repair rounds → packaged fact-check over
the 12 new external claims (Sonnet verify + adversarial second pass).

**Fact-check result: 11 correct, 1 partially-correct, 0 wrong.**

- Confirmed: arccore-core-21 identity (bulk upload of Arctic Core 21.0.0), its
  README-GPL-2.0-but-no-LICENSE-file status, AUTOSAR 4.0.3-era vintage (release
  macros + 2013/2014 copyrights + bundled lwip-2.0.3), full Classic BSW module map,
  MCU ports under `core/mcal/arch/`; autoas/as identity ("Simple AUTOSAR Basic
  Software", from-scratch Classic 4.4 stack by Parai Wang), module coverage, Python
  generators + Qt tooling + SCons, single-maintainer status, and its internally
  inconsistent licence (LICENSE: dual GPLv3/commercial vs README: evaluation/study
  only vs GitHub: "Other").
- **Partially-correct (fixed)**: the bulk-upload date. The initial commit's UTC
  timestamp is 2024-06-28T03:28:51Z ("Jun 27" only in US timezones), and one later
  commit briefly added/removed a site-verification HTML file, so "the other commits
  only edit the README" was not exactly true. Slide now says "in June 2024, and no
  later commit touches the code".

**Research-stage corrections worth recording** (caught by the clone-based research
agent, never reached the slides): the `my.arccore.com/hg/arc/` Mercurial origin —
reported earlier in conversation from a summarized page fetch — is *not evidenced*
anywhere in the arccore-core-21 clone (only `arccore.com/my-arccore` and
`support.arccore.com` appear, in `core/readme.md`); the claim was dropped rather
than cited.

**Verification outcome**: parity and citation verifiers passed (langroodi wording
provably unchanged; every pin/quote/tree/excerpt/permalink traced to the pinned
clones; the CAPI partner-gated fact + autosar.org/capi citation relocated to the
shape-of-code slide). The style verifier left 4 minor gloss-coverage nits after two
repair rounds; they were fixed in the follow-up pass below.

## Part 3: consolidated fix pass

Run `post-3repo-fixes` (`wf_c7e971c6-4e6`) applies, in one verified pass: the three
Part-1 history corrections (partner count ~360 → about 340/339 end-2025 with the
2026-04-09 status date; Foundation R1.0.0 Oct → Nov 2016 per the release document's
own 2016-11-30 date, discrepancy noted in the timeline sources caption; "last
standalone FO/CP/AP" → "last … before the unified line" on all three timeline nodes,
SVG + drawio mirror in lockstep), the terminology alignment "function cluster" →
"functional cluster" (the spec's own term, deck + full deck + blogs), the
"protocol-agnostic" gloss entry on the ara::com slide, the four residual gloss nits,
and the June-2024 provenance fix. Verified by a single max-effort verifier against
the literal edit list; results recorded in the workflow run.

**Resolution**: final verifier verdict PASS after one repair round (the repair fixed a
tight functional-clusters slide with a scoped style block; SVG↔drawio text extracted
and compared, 327 words each, identical). Foundation-date sweep found zero prose
sites — the timeline diagram was the only carrier of the Oct-2016 date. Follow-up by
the orchestrator: the full deck's regional partner breakdown was still the Jan-2025
snapshot next to the new end-2025 total; aligned to the same Apr-2026 status source
(Asia 164 > Europe 128 > NA 41) and rebuilt. Known open issue, pre-existing and
unrelated to these edits: four dense full-deck reference slides (PDF pages ~22, 29,
30, 32) overflow at the bottom; identical before and after the edits, left for a
separate approved restyle pass.

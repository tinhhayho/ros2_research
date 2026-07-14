# Information audit — 2026-07-14 (scope: the new node/graph/DDS teaching content)

**How produced:** three parallel read-only audit passes with non-overlapping scopes over
the content added 2026-07-14 — (1) technical claims in the three new deck slides + blog
§2.6 + new glossary entries + the new Open-RMF bullet, cross-checked against the repo's
own teaching docs and research trail; (2) the two new figures (`node-process-graph`,
`dds-scope`) vs prose vs older figures + SVG↔drawio identity; (3) cross-document
consistency (blog↔deck↔glossary↔transcript↔asset closure). Every MAJOR/MINOR finding
then went through an independent adversarial verification pass (instructed to refute),
and the survivors were re-verified against the cited lines by the orchestrating pass.
No web access — external facts tagged. 37 claims checked; transcript coverage of the new
slides was explicitly out of scope (that update is queued).

**Verdict:** the conceptual content is solid — the model (node = identity, executor owns
threads, graph = discovered, DDS = processes, micro-ROS = library + agent) checks out
against the repo's own docs, the figures and prose are near-verbatim consistent, asset
closure is complete, and the text does **not** regress into the previously corrected
"DDS is not RT" folklore (row 7). The two real defects are both *overclaims introduced
today*: an unconditional composition⇒intra-process claim, and an uncaptured number —
the second one violating the repo's own "no fabricated output" rule.

## MAJOR (both adversarially confirmed, then re-verified at source)

1. **Composition presented as automatically implying intra-process zero-copy** —
   `slides/research-deck.md:190-192` ("1 process = N nodes (composition — co-located
   nodes talk **intra-process**: pointer pass, no serialization, no network)"),
   repeated in the glossary (`:1180` "composition / intra-process — … their
   zero-serialization message path"), the blog (`docs/blog-robot-software-stacks-2026-07.md:232-234`
   and `:261` "intra-process, DDS bypassed"), and both new figures
   (`node-process-graph.svg` "intra-process — pointer pass, no serialization";
   `dds-scope.svg` "intra-process: pointers, DDS bypassed"). Reality: rclcpp
   intra-process comms is **opt-in per node/publisher**
   (`NodeOptions().use_intra_process_comms(true)`), C++ only (not rclpy); composed
   nodes that don't opt in still use the normal rmw/DDS path. The repo's own deeper
   text is already careful (`research/ros2-deep-dive-2026-07.md:112-114` "combined
   with intra-process communication it **can** skip serialization"; deck slide 8 "intra-process
   C++ **can** bypass serialization") — the new content dropped the hedge. Five
   locations to fix (slide, glossary, blog ×2, two figures).

2. **"5–7 OS threads … try `ps -T` on demo-1" is an uncaptured number** —
   `slides/research-deck.md:201` (gloss) and, with no hedge at all,
   `docs/blog-robot-software-stacks-2026-07.md:240`. No `docs/img/` artifact, no
   claims-audit row, not labeled illustrative — a direct violation of the repo's
   "every number in docs/slides comes from a real captured run". (Contrast: the ~50 µs
   PREEMPT_RT figure is explicitly labeled illustrative in row 8.) Also externally
   sensitive: thread counts differ by RMW vendor. **Preferred fix per repo culture:
   capture it** — run demo-1, capture `ps -T` for one node into
   `docs/img/demo1_threads.txt`, quote the real count, add an own-run claims row;
   fallback: hedge as illustrative.

## NIT

- `slides/research-deck.md:196` — "One stuck callback starves its whole executor" is
  stated as universal right after distinguishing Single vs MultiThreadedExecutor; strictly
  it starves a single-threaded executor (a multi-threaded one degrades, not starves).
- `slides/research-deck.md:1181` — glossary "remapping — renaming a node's **topics** at
  launch time" narrows the feature: remapping also covers node names and namespaces.

## Claim inventory summary

37 claims checked: 33 confirmed · 1 mismatch (MAJOR 1) · 2 trail-gap (MAJOR 2, both
docs) · 1 `[VERIFY-EXTERNALLY]` (the 5–7 range itself — plausible per RMW vendor
behavior, unverifiable without a run; resolved if the capture fix is taken).

## Strengths

1. Figures and prose are near-verbatim consistent; SVG ↔ drawio-pages XML text identical
   for both new pages; `diagrams.drawio` tabs match the standalone sources — no drift.
2. The R18-03 AUTOSAR-Adaptive DDS-binding callout reuses an already-audited claim
   (row A9) instead of introducing a new unverified one.
3. "RMF Core is itself ROS 2 nodes" is introduced once (blog §2.6) and cross-referenced,
   not restated divergently, in §4.1 and the deck's Open-RMF slide.
4. The demo-1 "5 nodes" figure remains capture-backed (`docs/img/demo1_node_list.txt`).
5. The new content stays clear of the corrected "DDS not RT" absolute (row 7) — the
   RT framing remains scoped to construction discipline, not middleware incapability.

## Status

Findings presented 2026-07-14 and approved same day; all fixes applied:

- **MAJOR 1** — "opt-in" + rclcpp-only wording fixed in all five locations (deck slide,
  glossary, blog ×2, both figures' SVG + drawio XML); manifest row **R16** added.
- **MAJOR 2** — resolved the preferred way: a real capture was taken
  (`docs/img/demo1_threads.txt`, talker_cpp under rmw_fastrtps_cpp) and the true number
  — **15 threads**, not the drafted "5–7" — now appears in deck and blog with the
  artifact cited; manifest row **R15** (own-run) added. The 2× error in the drafted
  figure is itself the best argument for the capture rule.
- Both NITs fixed (single-threaded-executor scoping; remapping definition widened to
  topics/name/namespace).
- The queued transcript update proceeds against the corrected slides.

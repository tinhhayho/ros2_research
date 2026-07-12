# How unified memory actually works on Jetson/DRIVE Thor — fact-check of a second third-party report (July 2026)

**What this is.** A second third-party report ("Unified Memory Architecture in NVIDIA
Jetson Thor and DRIVE Thor", dated 2026-07-12) was submitted for review — this one about
the *mechanism* of unified memory, not just the specs. Same workflow as
`jetson-thor-memory-2026-07.md`: three parallel research passes against primary sources
with hard fetch budgets, then an independent audit pass closing the flagged gaps.
Per-claim rows added to `research/claims-audit-2026-07.md` (U-series).

**Headline result: the big architectural picture is right, but the mechanism story is
dGPU folklore transplanted onto an iGPU.** The report describes Thor's unified memory
using discrete-GPU vocabulary — page migration, oversubscription, prefetch-to-device,
"weaker coherence than Grace Hopper" — none of which describes what actually happens on
a single-SoC, single-pool, hardware-coherent design.

---

## 1. Verdict table (original claim → verdict)

| # | Original claim | Verdict | Correction / note |
|---|---|---|---|
| 1 | Single monolithic SoC, one shared LPDDR5X pool, no separate CPU/GPU memories | ✅ Confirmed | Matches datasheet + CUDA for Tegra appnote |
| 2 | "Neither platform uses NVLink-C2C" | ⚠️ Right for Jetson, open for DRIVE | NVIDIA staff: "Jetson T5000 does not support NVLink C2C". The 2022 dual-Thor-via-C2C config was announced but **no evidence it shipped**; the single die absorbed the original ~2,000-TOPS target. DRIVE C2C ("GSC") docs are partner-gated |
| 3 | Unified virtual address space; `cudaMallocManaged` fully supported | ⚠️ Partially right | Supported — but on Thor (CUDA 13.0) managed allocations are **not GPU-cached**; Thor is the first Tegra with `concurrentManagedAccess = 1`* |
| 4 | "CUDA driver handles page residency and **migration** when necessary" | ❌ **Wrong** | Nothing migrates — there is no second pool to migrate to. The appnote's term is **coherency and cache maintenance**, and on Thor the hardware does it. "Migration" never appears in the Tegra managed-memory docs |
| 5 | "Migration cost significantly lower than PCIe dGPUs" | ❌ **Wrong framing** | Not cheaper migration — **no copy at all** (zero-copy: one DRAM pool). The appnote: duplicate allocations and transfers "can be avoided" |
| 6 | "Coherence not as strong as Grace Hopper's NVLink-C2C + ATS" | ❌ **Wrong axis** | Thor has **Sysmem Full Coherency** — two-way, hardware, on-die. No NVIDIA source ranks coherence "strength"; GH200's ATS solves a **cross-die** problem Thor doesn't have. The honest difference is **scale**: GH200 = 2 dies, 2 memory types (480 GB LPDDR5X + 96/144 GB HBM3/e) over a 900 GB/s link; Thor = 1 die, 1 pool, 128 GB |
| 7 | "No ATS-like features on Thor" | ❌ **Wrong** | CUDA 13.0 blog: the GPU accesses pageable memory "**via the host's page tables**" — functionally what ATS provides, done more directly through the on-die fabric. (What Jetson lacks is the *PCIe*-ATS protocol — irrelevant to an iGPU) |
| 8 | Oversubscription of large datasets: "Moderate" | ❌ **Concept doesn't apply** | CUDA defines oversubscription against a *single processor's* capacity (dGPU framebuffer < host RAM). One 128 GB pool has no such boundary; the limit is the shared-capacity budget vs the OS and other processes |
| 9 | "Optimize with `cudaMemAdvise(SetPreferredLocation)` + `cudaMemPrefetchAsync`" | ⚠️ Mostly dGPU advice | `cudaMemAdvise` is **absent from the Tegra appnote** — there is no other "location" to prefer on one pool. `cudaMemPrefetchAsync` works on Thor (first Tegra where it's supported*) — what it does on a one-pool system is **not spelled out in official docs**; a forum-level answer suggests page-table pre-population (unverified — see §4) |
| 10 | Comparison row: discrete RTX = "Page Migration (**Software**)" | ❌ **Wrong** | Since Pascal, UM migration is triggered by a **hardware** Page Migration Engine (GPU page faults), with the driver moving pages over PCIe; Linux adds HMM for pageable memory. "Software migration" mislabels it |
| 11 | Apple Silicon analogy ("more similar to Apple than to Grace Hopper") | ✅ Structurally right | One die, one pool, HW-coherent — closer to Apple UMA than to GH200's two-tier design. Physical caveat: the report's "soldered onto the package" is **unverified** — every prior Jetson is memory-down on the module PCB (not Apple-style PoP), but no Thor teardown surfaced to prove either way* |
| 12 | "Single memory controller serving both" | ⚠️ Oversimplified | NVIDIA's own terminology is a **Memory Subsystem with a scalable coherence fabric** (TRM) / "Memory Control Fabric" (official block diagram) — multiple LPDDR5X channels behind a fabric, not one monolithic controller. Channel count not public (TRM gated) |
| 13 | DRIVE Thor = same SoC, automotive-qualified (AEC-Q100) | ⚠️ Partially right | AEC-Q100 is real but it's the **stress/reliability qualification** standard — the functional-safety claim is ISO 26262 (ASIL). Public SKU differences: FSI safety island (DRIVE/IGX only, not Jetson T5000); 64 vs 128 GB is a **T4000-vs-T5000 tier split**, not a Jetson-vs-DRIVE split |
| 14 | Report's perf table: frequent CPU↔GPU sharing only "Good" | ⚠️ Unsupported grading | No NVIDIA source grades this. Real caveat that exists: full coherency "may involve… coherence related overhead… benchmark with and without Full Coherency" (appnote). The grading itself is invented |
| 15 | "Thor presented at Hot Chips" (implied by references) | ❌ Wrong | Hot Chips 2025 program has NVIDIA sessions on GB10, ConnectX-8, RTX 5090, photonics — **no Thor session**. Thor's GA announcement was *timed to* Hot Chips week; that's not a talk. Primary technical doc remains the gated Thor TRM |

*Items marked \* were closed by the audit pass — see §4.

---

## 2. How it actually works (corrected mechanism story)

One pool, no journeys. Every allocator — `cudaMalloc`, `cudaHostAlloc`,
`cudaMallocManaged`, plain `malloc` — lands in the same physical LPDDR5X. What differs
per allocator is **who can cache it and who keeps the caches coherent**:

- **Pre-Thor Tegra (Orin):** one-way I/O coherency. The GPU could snoop CPU caches; the
  CPU couldn't see GPU caches, so managed memory cost explicit cache-maintenance
  operations at kernel launch/sync. That is what "unified memory overhead" meant on
  Orin — never page migration.
- **Thor:** **Sysmem Full Coherency** — two-way, maintained by the hardware fabric (the
  Unified Coherency Fabric + 16 MB system cache). The GPU walks the **host's page
  tables** to reach pageable memory (`malloc`/`mmap`) directly, GPU-cached, coherent.
  That's why NVIDIA's Thor guidance flips to plain system memory as the fastest shared
  path — and why `cudaMallocManaged` (not GPU-cached in CUDA 13.0) is the ergonomic
  option, not the fast one.
- **`cudaMemPrefetchAsync` on Thor**: supported for the first time on a Tegra
  (`concurrentManagedAccess = 1`), but official docs don't spell out what it does on a
  one-pool system — the generic Programming Guide wording ("may migrate data to reside
  closer to the specified processor") has nowhere to migrate to here. A forum-level
  explanation (page-table pre-population to avoid first-touch faults) is plausible but
  unverified; benchmark before relying on it. What is certain: it does not "move data
  to the device" — there is no device-side pool.

## 3. The comparison table, corrected

| Platform | Dies | Physical pools | CPU↔GPU coherence | The real difference |
|---|---|---|---|---|
| GH200/GB200 | 2 (superchip) | 2 types: 480 GB LPDDR5X + 96/144 GB HBM3/e | HW-coherent over NVLink-C2C (900 GB/s) + ATS shared page table | **Scale**: 576–624 GB, HBM bandwidth for the GPU |
| Jetson/DRIVE Thor | 1 SoC | 1 pool: 64/128 GB LPDDR5X | HW-coherent **by construction** (on-die fabric) | **Efficiency**: zero-copy at 40–130 W, but 273 GB/s ceiling for everyone |
| Discrete RTX + x86 | 2+ (PCIe) | 2 pools (GDDR + host RAM) | Not coherent; HW page-fault engine + driver migration (HMM on Linux) | Migration is real here — this is where the report's vocabulary belongs |

Ranking "unified memory strength" GH200 > Thor > RTX confuses coherence (where Thor
concedes nothing) with capacity/bandwidth scale (where GH200 wins outright).

## 4. Audit-pass closures (what held, what got softened)

- **Confirmed from the appnote directly**: "`cudaDeviceProp::concurrentManagedAccess`
  can be 1 only on Thor or later Tegra devices"; `cudaMemPrefetchAsync()` "is not
  supported if `cudaDeviceProp::concurrentManagedAccess` is 0".
- **Confirmed absence**: no mention of `cudaMemAdvise` /
  `cudaMemAdviseSetPreferredLocation` anywhere in the fetched appnote — the report's
  recommendation is dGPU boilerplate (absence claim, scoped to public docs).
- **Softened**: "prefetch = pre-mapping, not copying" could not be substantiated in the
  Programming Guide or appnote — kept only as a labeled, unverified forum-level
  explanation.
- **Softened**: on-module vs on-package DRAM — no Thor teardown photo found (STH's
  hands-on shows specs and a block diagram only). Stated as inferred from Jetson SoM
  convention, not asserted.
- **Re-fetched directly**: GH200 datasheet capacities (480 GB LPDDR5X + 96 GB HBM3 /
  144 GB HBM3e, up to 624 GB combined) and the Hot Chips 2025 program (four NVIDIA
  sessions — RTX 5090, ConnectX-8, photonics, GB10 — none about Thor).

## 5. What this means for our stack

- The corrected story **strengthens** our deck's slide 25: allocator choice is the whole
  game on Thor; there is no migration to tune, only cache/coherence behavior to pick.
- When someone quotes GH200-style advice (`cudaMemAdvise`, prefetch-to-device,
  oversubscription tricks) for Thor, it is a smell — the mental model is from the wrong
  machine.
- For DRIVE-side work, don't repeat "same SoC as Jetson" unqualified: FSI and
  qualification differ, and dual-Thor/C2C claims from 2022 should be treated as
  unshipped until shown otherwise.

## Sources

- CUDA for Tegra application note (incl. 13.x archive versions) — docs.nvidia.com
- "What's new in CUDA Toolkit 13.0 for Jetson Thor" — developer.nvidia.com/blog
- CUDA Programming Guide, Unified Memory chapter — docs.nvidia.com
- "NVIDIA Grace Hopper Superchip Architecture in Depth" — developer.nvidia.com/blog
- "Understanding Memory Management on Hardware-Coherent Platforms" — developer.nvidia.com/blog
- Grace Hopper product page — nvidia.com
- Thor SoC TRM DP-11881-002 (MSS/coherence-fabric wording; full PDF developer-gated)
- forums.developer.nvidia.com NVIDIA-staff answers: "Jetson T5000 does not support
  NVLink C2C"; "Jetson Thor does not support FSI. IGX Thor supports FSI."; Jetson PCIe-ATS
  thread
- Hot Chips 2025 program — hc2025.hotchips.org
- DRIVE Thor 2022 announcement (dual-Thor NVLink-C2C config) — blogs.nvidia.com

# Jetson Thor / DRIVE Thor memory architecture — fact-check and corrected report (July 2026)

**What this is.** A third-party summary report ("Jetson Thor & DRIVE Thor memory
architecture", dated 2026-07-12) was submitted for review before its content goes into
our slides. This document is the result of our standard verification workflow: three
parallel research passes against primary NVIDIA sources with hard fetch budgets, then an
**independent audit pass** that re-fetched every headline claim. Two primary PDFs (the
Jetson Thor datasheet and the DRIVE AGX Thor deck) resisted the audit agent's web-fetch
tooling, so we downloaded both and read them locally with `pdftotext` — every datasheet
number below is primary-verified, not retailer-corroborated. Verdicts below; the
corrected narrative follows. Per-claim rows were also added to
`research/claims-audit-2026-07.md`.

**Headline result: the numbers were mostly right, three architectural claims were wrong
or outdated** — including the one developers would act on (`cudaMallocManaged`
recommendation, which is backwards on Thor).

---

## 1. Verdict table (original claim → verdict)

| # | Original claim | Verdict | Correction / note |
|---|---|---|---|
| 1 | T5000: 128 GB LPDDR5X, 256-bit, 273 GB/s | ✅ Confirmed | Datasheet DS-11945-001 v1.5, p.3 |
| 2 | T4000 / DRIVE Thor: 64 GB, 273 GB/s (same bandwidth) | ✅ Confirmed | Same 256-bit bus; datasheet v1.5 *itself corrected* the T4000 memory row (changelog, Jun 2026) |
| 3 | "4266 MHz" memory clock | ✅ Confirmed | NVIDIA's literal figure; data rate ≈ 8533 MT/s is *our derivation* (273 GB/s ÷ 32 B), not an NVIDIA-printed number |
| 4 | No HBM; LPDDR5X is a power/reliability trade | ✅ Confirmed | — |
| 5 | UVM with **full cache coherence** = biggest memory upgrade on Thor | ✅ Confirmed | CUDA for Tegra appnote: "Sysmem Full Coherency is supported on Tegra devices starting with Thor SoC" (Orin had one-way I/O coherency only) |
| 6 | `cudaMallocManaged` recommended, reduces latency | ❌ **Wrong — backwards** | In CUDA 13.0 managed allocations are **not GPU-cached** on Thor. NVIDIA's own guidance: plain pageable / host-registered memory over the full-coherence path **outperforms both pinned and managed**. Managed = ergonomic, not fast |
| 7 | "Non-unified supported, Unified recommended" | ⚠️ Imprecise | All allocators land in the same physical LPDDR5X. NVIDIA's guidance is allocator-per-workload (`cudaMalloc` for GPU-only, pinned for small buffers, pageable+coherence for shared), not a blanket UM recommendation |
| 8 | On-chip SRAM "limited, no numbers" | ⚠️ Partially wrong | CPU caches **are** published: L1 64+64 KB/core, L2 1 MB/core, **16 MB shared system cache**. GPU L2 size: not found in the datasheet (likely unpublished) |
| 9 | Power 40–130 W (both columns) | ⚠️ Partially right | T5000 TMP = 130 W (modes 70/90/120/MAXN) ✅; the 40 W floor appears only on the marketing page, lowest *named* datasheet mode is 70 W. **T4000 TMP = 90 W** (modes 70/MAXN) — the table's shared "40–130 W" column is wrong for T4000 |
| 10 | Server GPUs "H100/B100 – HBM3e, 3.35–8+ TB/s" | ⚠️ Mislabeled | Range is right; **H100 SXM is HBM3** (3.35 TB/s — bandwidth primary-confirmed; the "HBM3" label itself is datasheet/secondary-corroborated). HBM3e starts at H200 (4.8 TB/s, primary) / B100 / B200 (~8 TB/s, primary via DGX B200 page) |
| 11 | 12–30× less bandwidth than server HBM | ✅ Confirmed | 3350/273 ≈ 12.3× · 4800/273 ≈ 17.6× · 8000/273 ≈ 29.3× |
| 12 | Server power 700 W+ | ✅ Confirmed | H100 SXM 700 W, B200 ~1000 W |
| 13 | "Unified Memory on servers = inefficient, mostly non-unified" | ❌ **Outdated** | True for classic x86 + PCIe boxes; **wrong for GH200/GB200**: NVLink-C2C is hardware-coherent at up to 900 GB/s, CPU/GPU access each other's memory without page migration |
| 14 | Quantization cuts memory traffic 2–4× | ✅ Confirmed | FP8 = 2×, FP4 = 4× vs FP16. Thor has native FP4 + Transformer Engine (T5000: 2070 FP4 TFLOPS sparse) |
| 15 | Memory-bound above ~10–20 B params | ✅ Confirmed (direction) | LLM decode is bandwidth-bound; roofline in §4 quantifies it |
| 16 | T4000 compute implied same as T5000 | ❌ Wrong (by omission) | T4000: 12× Neoverse V3AE (not 14), 1536 CUDA cores, **1200 FP4 TFLOPS sparse** vs T5000's 2070 |

Audit pass re-fetched claims 1–3, 5–6, 8–14 from primary sources (see
`claims-audit-2026-07.md` for URLs and access dates).

---

## 2. The memory system, corrected

One physical pool of **LPDDR5X on a 256-bit bus at 4266 MHz (≈ 8533 MT/s effective), 273
GB/s peak**, shared by everything on the die — 14 (T5000) or 12 (T4000) Neoverse V3AE
cores, the Blackwell iGPU, and the accelerators — behind a **16 MB shared system cache**.
CPU side: 64+64 KB L1 and 1 MB L2 per core. There is no HBM anywhere in the Thor family;
that is the deliberate trade for a 130 W (T5000) / 90 W (T4000) module.

What is genuinely new on Thor is not the DRAM — Orin was also unified-memory — but the
**coherence model**. Orin had one-way I/O coherency: the GPU could snoop CPU caches, the
CPU could not see GPU-cache updates. Thor is the first Tegra with **Sysmem Full
Coherency**: two-way, hardware-managed. That changes the allocator advice:

| Allocator | On Thor (CUDA 13.0) |
|---|---|
| `malloc` / `mmap` (pageable, GPU-accessed directly) | **Fastest shared path** — GPU-cached, full HW coherence |
| `cudaHostAlloc` (pinned) | Fine for small buffers; no longer the top shared-memory path |
| `cudaMallocManaged` | Easy, but **not GPU-cached on Thor** — do not pick it for latency |
| `cudaMalloc` | GPU-only buffers, as always |

The reviewed report recommended `cudaMallocManaged` for low latency — the opposite of
NVIDIA's Thor guidance. On a perception(GPU)→planning(CPU) pipeline the low-latency
option is now plain system memory over the coherence fabric.

## 3. The bottleneck, quantified

273 GB/s is 12–30× below data-center HBM (H100 HBM3 3.35 TB/s → B200 HBM3e ~8 TB/s at
~1000 W). For autoregressive LLM/VLA decode — which is bandwidth-bound, weights re-read
per token — the **derived** roofline at batch 1 is:

| Model (after quantize) | Bytes/token read | Peak-roofline tok/s | ~Realistic (60–80% of peak) |
|---|---|---|---|
| 10 B @ FP4 | 5 GB | ~55 | ~33–44 |
| 10 B @ FP8 | 10 GB | ~27 | ~16–22 |
| 20 B @ FP4 | 10 GB | ~27 | ~16–22 |
| 20 B @ FP8 | 20 GB | ~14 | ~8–11 |

*Derived arithmetic (tokens/s ≈ bandwidth ÷ model bytes), not a measured run; ignores
KV-cache traffic (grows with context) and prefill (compute-bound).* Our own GR00T N1.7
(3 B) run on an RTX 4080 SUPER sits comfortably above these lines precisely because 3 B
is small — the roofline explains why edge VLA models cluster in the 2–10 B range and why
FP4 matters more on Thor than on an H100.

Mitigations NVIDIA actually ships on Thor: native FP4/FP8 Transformer Engine (2–4× less
traffic), TensorRT kernel fusion, MIG 2-way partitioning (JetPack 7.2 technology
preview: 12 SM inference + 8 SM control) — plus the 16 MB system cache absorbing
CPU↔GPU sharing.

## 4. Server comparison, corrected

The "unified memory is inefficient on servers" line is true only for the x86 + PCIe-GPU
generation the report had in mind. **GH200 / GB200** pair Grace with the GPU over
**NVLink-C2C: hardware-coherent, up to 900 GB/s** — CPU and GPU access each other's
memory with no page migration, ~7× a PCIe Gen5 x16 link. The honest comparison is:
Thor = full coherence over one on-die fabric at edge power; Grace superchips = the same
idea at rack power; classic PCIe boxes = the only tier where the report's claim holds.

## 5. What this means for our stack

- The perception(GPU) → planning(CPU) handoff pattern from our placement-rules slide gets
  cheaper on Thor — but only if the code uses the right allocator (§2), not managed memory.
- Model sizing for Thor-class robots is a bandwidth budget before it is a TOPS budget:
  273 GB/s ÷ model bytes is the first number to compute.
- T4000 (the SKU DRIVE Thor matches on memory) keeps the full 273 GB/s — memory-bound
  workloads degrade less than the 1200-vs-2070-TFLOPS compute gap suggests.

## Sources

- Jetson Thor Series Modules Datasheet DS-11945-001 v1.5 (Jun 2026) — developer.nvidia.com (PDF)
- CUDA for Tegra application note — docs.nvidia.com/cuda/cuda-for-tegra-appnote
- "What's new in CUDA Toolkit 13.0 for Jetson Thor" — developer.nvidia.com/blog
- DRIVE AGX Thor Development Platform deck (Dec 2025) — developer.nvidia.com (PDF)
- JetPack 7.2 release notes / MIG technology-preview blog — developer.nvidia.com
- H100 / H200 product pages — nvidia.com/en-us/data-center
- Grace Hopper architecture in depth (NVLink-C2C) — developer.nvidia.com/blog
- Jetson Thor GA — nvidianews.nvidia.com (Aug 25, 2025)
- Roofline table: our own derivation (assumptions stated in §3), July 2026

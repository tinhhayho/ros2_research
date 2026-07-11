# NVIDIA Physical AI Ecosystem — Technical Report (July 2026)

**The Isaac GR00T Development Platform + Cosmos, end to end**

*Prepared: 2026-07-11. Method: three budget-capped research passes plus an independent
audit pass that re-fetched primary sources for the 14 load-bearing claims: 11 CONFIRMED,
2 CORRECTED, 1 partially unverifiable — corrections are applied below and flagged ⚠AUDIT.
Facts inherited from the July 2026 ecosystem survey in `robot-software-stack-2026-07.md` are
reused, not re-researched. Community-sourced (non-NVIDIA) numbers are tagged [community].*

---

## 1. Executive Summary

NVIDIA has assembled the most complete vertically-integrated platform for "Physical AI" —
robots controlled by foundation models — spanning world models (**Cosmos 3**), robot policy
models (**Isaac GR00T N1.7**), simulation and training (**Isaac Sim 6 / Isaac Lab /
Lab-Arena**), human-demonstration capture (**Isaac Teleop**), an accelerated ROS 2 runtime
(**Isaac ROS 4.5**), and a purpose-built edge computer (**Jetson AGX Thor**). As of July 2026
every software layer is publicly downloadable, most of it under genuinely open licenses
(Apache-2.0, BSD-3, OpenMDW-1.1, open weights on Hugging Face), and the July 6, 2026
NVIDIA × Hugging Face announcement wired GR00T 1.7 and Isaac Teleop directly into LeRobot,
the de-facto open robot-learning library.

The honest counterweight: the stack is **hardware-locked** (no CPU fallback anywhere;
CUDA/TensorRT required end to end), **young at the deployment edge** (batch-1 GR00T inference
on Thor is ~94 ms official / 22–24 Hz [community] — workable via action chunking, but far from
desktop-GPU headroom), **version-fragmented** (Humble/Orin vs Jazzy/Thor splits break
tutorials), and **not safety-certified** in its robotics SKU (the Functional Safety Island
lives in the industrial IGX Thor, not Jetson AGX Thor). For teams that accept the hardware
commitment, the sim→data→train→evaluate→deploy loop is the most polished in robotics today;
for everyone else it is a set of à-la-carte accelerators on top of the classical
ROS 2 + Gazebo baseline.

## 2. NVIDIA's Physical AI Strategy

NVIDIA frames robotics as a **three-computer problem** (blogs.nvidia.com "three computers"):

1. **Train** — DGX/cloud GPUs: pretrain/post-train Cosmos and GR00T.
2. **Simulate & generate** — OVX/RTX workstations running Omniverse: Isaac Sim for physics,
   Cosmos for synthetic data and world-model evaluation, Isaac Lab(-Arena) for RL/IL and
   benchmarking.
3. **Deploy** — Jetson Thor on the robot: TensorRT-optimized policies inside an Isaac ROS /
   ROS 2 graph.

The strategic through-line is *data flywheel economics*: real robot data is scarce and
expensive, so NVIDIA monetizes the machinery that manufactures training data (simulation,
world models, teleop capture) and the silicon at both ends. Openness is deliberate funnel
design — weights, code, and datasets are free; the GPUs are not.

**Suggested figure 1:** three columns (Train / Simulate / Deploy) with component logos and
arrows showing checkpoint + dataset flow left→right and telemetry/data flow right→left.

## 3. Component Deep Dive

### 3.1 NVIDIA Cosmos 3 — the world foundation model

- **Confirmed real and current** (⚠AUDIT: confirmed against NVIDIA Newsroom + HF):
  announced **May 31, 2026 (COMPUTEX)**; technical report arXiv:2606.02800.
- **Architecture — Mixture-of-Transformers (MoT), "omnimodal"** (both are genuine NVIDIA
  terminology): a **Reasoner tower** (VLM-style, text/plan output) coupled with a
  **Generator tower** (diffusion, video/image/audio output) in one checkpoint that jointly
  processes text/image/video/audio/**action**. Two sizes: **Nano 16B** (8B reasoner + 8B
  generator) and **Super 64B** (32B + 32B); an Edge variant is "coming soon" [UNVERIFIED].
- Trained on ~**20 trillion multimodal tokens** (~1B images, 400M real+synthetic videos,
  audio, text, human+robot action data). License: **OpenMDW-1.1** (Linux Foundation) — a
  notable move away from the earlier NVIDIA Open Model License.
- **Role in the stack:** (a) synthetic-data engine (generate/augment robot video +
  trajectories), (b) world-model-in-the-loop evaluator (imagine outcomes before acting),
  (c) **backbone for World Action Models (WAMs)** — WAM is an official NVIDIA glossary term
  for models that predict world evolution *and* actions jointly.
- **Continuity:** the prior lines — Cosmos-**Predict 2.5** (future-state video), **Transfer
  2.5** (ControlNet-style sim2real domain transfer), **Reason 2** (physical-common-sense
  VLM) — still ship and are still what **GR00T-Dreams/DreamGen** (synthetic trajectory
  generation from one image + prompt) cites as of July 2026; migration to Cosmos 3 is implied
  but unconfirmed [UNVERIFIED].
- Serving paths: Diffusers (research), vLLM-Omni (production, OpenAI-compatible API),
  NIM container (Reasoner).

| | Cosmos 3 (WFM) | Traditional sim (Isaac Sim/Gazebo) |
|---|---|---|
| World representation | learned, generative video+state | hand-built USD/SDF scenes, analytic physics |
| Physics fidelity | plausible, not guaranteed | deterministic, tunable, verifiable |
| Novel-scene cost | a text/image prompt | asset + scene engineering |
| Use in pipeline | data augmentation, imagination, evaluation | ground-truth training + regression testing |
| Failure mode | hallucinated dynamics | reality gap |

They are complements, not substitutes — NVIDIA's own pipeline uses both (Transfer 2.5
photorealizes Isaac Sim renders; Cosmos evaluates policies that Isaac Lab trained).

### 3.2 Isaac GR00T N1.7 — the robot policy model

- **Confirmed real** (⚠AUDIT: HF blog `nvidia/gr00t-n1-7`): **Early Access April 17, 2026**,
  now generally available with **commercial licensing**; adopters cited include Humanoid,
  LG, NEURA, Noble Machines. Weights: **`nvidia/GR00T-N1.7-3B`** (base). A separate
  **`GR00T-H-N1.7`** exists — a post-trained **surgical/healthcare variant** (Open-H
  dataset), resolved by the audit as a distinct model, not a naming clash.
- **Architecture — "Action Cascade"** (official term): **Cosmos-Reason2-2B** backbone
  (Qwen3-VL-derived — note the recursion: Cosmos is now *inside* GR00T) performs structured
  **task/subtask reasoning** and emits high-level action tokens → a **32-layer DiT action
  head** denoises them into continuous motor commands. Actions are expressed in a
  **relative end-effector space shared between robot and human data**, which is what lets
  N1.7 pretrain on **20,854 hours of human egocentric video** (vs N1.6's
  few-thousand-hour robot-teleop corpus). Finger-level dexterity up to 22-DoF hands.
- **Lineage:** N1 (Mar 2025, first open humanoid VLA) → N1.5 (3B, frozen VLM + DiT) →
  N1.6 (Sept 2025, Cosmos-Reason-2B backbone) → **N1.7 (Apr 2026, Action Cascade + human
  video pretraining + subtask reasoning)**.
- **Whole-body control is deliberately decoupled:** N1.7 outputs task-space actions; the
  separate **GR00T-WholeBodyControl ("SONIC")** model (NVlabs) converts them to whole-body
  joint commands for locomotion+manipulation. This mirrors the industry-wide cascade
  (VLA ~1–10 Hz → policy ~50 Hz → 1 kHz joint control) documented in our stack survey.
- **Post-training workflow** (the part a robotics team actually touches):
  data in **LeRobot v2 format + `meta/modality.json`**; embodiment selected via
  `EmbodimentTag` (pre-registered: Unitree G1/G1-Sonic, YAM bimanual, AGIBot Genie-1,
  LIBERO Panda, OXE DROID, SimplerEnv; `NEW_EMBODIMENT` for custom robots); full-model
  fine-tune via `gr00t/experiment/launch_finetune.py` (default ~2,000 steps; bundled sample
  datasets are as small as **3–5 episodes**; LoRA existed for N1/N1.5 but is not surfaced in
  N1.7 docs [UNVERIFIED]). Evaluation: open-loop MSE (`open_loop_eval.py`) and closed-loop
  via a policy server + `PolicyClient` (sim or real).
- **Hardware floors** (⚠AUDIT confirmed from README): **inference ≥16 GB VRAM**
  (RTX 4090/L40/H100/Jetson Thor cited), **fine-tuning ≥40 GB recommended**.

### 3.3 Isaac Sim 6 + Isaac Lab + Isaac Lab-Arena

- **Isaac Sim 6.0.1** (June 22, 2026): Omniverse-based simulator; **core is Apache-2.0 on
  GitHub** but depends on the proprietary-licensed Omniverse Kit SDK — "open source" is
  layered. Min spec: RTX 4080-class, **16 GB VRAM**, 32 GB RAM, Ubuntu 22.04/24.04. New in
  6.x: MCP server + natural-language "Skills" for AI coding assistants. Omniverse base
  licensing loosened ~May 2026 (free for dev *and* production) [UNVERIFIED exact scope —
  community-sourced].
- **Isaac Lab** (BSD-3, rolling): the RL/imitation-learning layer — GPU-parallel
  (thousands of envs; ~150K env-steps/s reported on a G1 walking task), Gymnasium API,
  RSL-RL/SKRL/SB3 integrations, 30+ ready environments. This is where the industry's
  humanoid RL locomotion policies are actually trained.
- **Isaac Lab-Arena** (⚠AUDIT confirmed): the missing evaluation piece — a composable
  benchmark framework over Isaac Lab (scenes × embodiments × tasks), GPU-parallel policy
  evaluation claiming **up to 13.5× faster (10 h suite → <1 h)**. Ships G1 pick-and-place,
  GR1 door manipulation, Franka lifting; community suites include RoboCasa (138+ tasks),
  LIBERO, DexBench; dedicated `isaaclab_arena_gr00t` integration package. **Status: alpha
  v0.2.x — "early community code drop," unstable APIs.** Plan around churn.

### 3.4 Isaac Teleop — the data-collection frontend

- **Confirmed** at `github.com/NVIDIA/IsaacTeleop`: "the unified framework for sim & real
  robot teleoperation" — successor to the Blueprint-era GR00T-Teleop workflow.
- Devices: **Apple Vision Pro** (CloudXR immersive streaming, 26-keypoint hand tracking),
  **Meta Quest 3**, **Pico 4 Ultra** (WebXR/CloudXR.js). No SteamVR support found.
- **Headset-free demo exists**: a desktop browser client using IWER (Immersive Web Emulator
  Runtime) — you can trial the pipeline with zero XR hardware.
- Records human demonstrations into **LeRobot-format datasets** (MCAP recording is referenced
  in docs navigation but was not primary-source-verified [UNVERIFIED], as was the exact
  `isaacteleop~=1.0.0` pip pin [UNVERIFIED]). Integrates with Isaac Lab (sim teleop) and
  Isaac ROS (real robots).

### 3.5 Isaac ROS — the deployment runtime

- **Isaac ROS 4.5.0 (July 6, 2026)**: CUDA-accelerated **ROS 2 Jazzy** packages.
  **NITROS** provides zero-copy, type-negotiated GPU transport between nodes; flagship GEMs
  map one-to-one onto classical components: **cuVSLAM** (vs slam_toolbox), **nvblox**
  (vs costmap_2d; <300 ms dense-3D obstacle updates), **Isaac Perceptor** (bundled AMR
  perception + Nav2; Nova Carter reference robot), **cuMotion/Manipulator** (vs MoveIt),
  FoundationPose, AprilTag.
- **x86_64 + discrete RTX is a first-class target** (4.5.0 benchmarks on RTX 5090/DGX
  Spark) — but there is **no CPU fallback anywhere**.
- **The version trap:** Isaac ROS 3.x = Humble on Orin; 4.x = Jazzy on Thor/x86. Following
  "latest" docs on an Orin Nano silently breaks.
- **Gap to know:** there is **no turnkey GR00T inference ROS 2 node** — the GR00T repo ships
  a standalone policy server/inference script that you wrap in a ROS 2 node yourself; Isaac
  ROS supplies the perception/manipulation pipeline around it, not the VLA runtime itself.

### 3.6 Jetson AGX Thor (T5000) — the robot brain

⚠AUDIT: all specs below re-verified against NVIDIA's launch blog/product page.

| Spec | AGX Thor (T5000) | AGX Orin 64GB | Uplift |
|---|---|---|---|
| GPU | Blackwell, 2,560 CUDA / 96 Tensor cores | Ampere, 2,048 CUDA / 64 Tensor | — |
| AI compute | **2,070 TFLOPS sparse FP4** (1,035 dense FP4 / sparse FP8) | 275 TOPS INT8 | ~7.5× |
| CPU | 14× Arm **Neoverse-V3AE** @2.6 GHz | 12× Cortex-A78AE | server-class cores |
| Memory | **128 GB LPDDR5X, 273 GB/s** | 64 GB, 204.8 GB/s | 2× cap, 1.33× BW |
| Power | **40–130 W** | 15–60 W | bigger envelope |
| Devkit | **$3,499** (1 TB NVMe, 100 GbE QSFP28) | ~$2,000 | — |

- A lower tier exists: **Thor T4000** — 1,536 CUDA cores, 64 GB, 1,200 sparse-FP4 TFLOPS,
  40–70 W (⚠AUDIT confirmed on the product page).
- **JetPack 7.0** = Jetson Linux 38.2, **Ubuntu 24.04, kernel 6.8, PREEMPT_RT kernel
  option** — the robotics-relevant real-time story is finally stock.
- **MIG (⚠AUDIT — corrected):** Thor is the first Jetson with MIG, arriving in
  **JetPack 7.2**, but it partitions into **two** hardware-isolated GPU instances
  (12-SM + 8-SM) — *not* seven, as one research pass claimed. Two slices are still exactly
  what a robot wants: one guaranteed-latency slice for the control-critical policy, one for
  perception/other workloads.
- **Sensor I/O:** Holoscan SDK 3.7 + Holoscan Sensor Bridge in JetPack 7; 100 GbE backbone.
- **Functional safety (⚠AUDIT — important nuance):** the **IGX Thor** industrial SKU (same
  T5000 silicon) carries a physically isolated **Functional Safety Island**, pre-certifiable
  to IEC 61508 SIL 3 / ISO 26262 ASIL-D. The robotics **Jetson AGX Thor has no such
  certification** — any "Jetson = ASIL-D" claim is conflation. Robots still need a safety
  PLC / safety-rated MCU beside the Jetson.

### 3.7 Supporting elements

- **NVIDIA Physical AI Dataset** = a *family* of `PhysicalAI-*` datasets on Hugging Face
  (10M+ downloads collectively): e.g. **PhysicalAI-Robotics-NuRec** (62.9 GB, Gaussian-splat
  USD reconstructions from real captures, CC-BY-4.0), GR00T-X-Embodiment-Sim, AV and
  warehouse sets. The July 6 announcement cites **350,000+ real/sim trajectories and 57M
  grasps** as "the largest open source physical AI dataset" (⚠AUDIT confirmed quote).
- **Hugging Face LeRobot** (July 6, 2026 joint announcement): **GR00T 1.7 and Isaac Teleop
  are integrated into LeRobot**; Cosmos 3 integration is "planned," not shipped. Data
  standard: **LeRobotDataset v3.0** (lerobot ≥ 0.4.0) — multi-episode Parquet/MP4 files,
  relational metadata, Hub streaming (`StreamingLeRobotDataset`). NVIDIA already publishes
  v3-format ports (e.g. `nvidia/BridgeData2_LeRobot_v3`).

## 4. End-to-End Workflow Analysis

**Suggested figure 2:** a loop diagram — (Sim scene / NuRec splats) → Isaac Teleop demos →
LeRobotDataset v3 → GR00T fine-tune (DGX/RTX) → Lab-Arena evaluation → TensorRT engine →
Isaac ROS graph on Thor → field data → back to dataset.

Step by step, with the actual artifacts that move between stages:

1. **Author or capture the world.** Build USD scenes in Isaac Sim, or reconstruct real
   spaces via the NuRec pipeline (cuSFM + FoundationStereo + nvblox + 3DGUT → Gaussian-splat
   USD). Cosmos Transfer 2.5 photorealizes sim renders to shrink the perception domain gap.
2. **Collect demonstrations.** Isaac Teleop (Vision Pro/Quest/browser-IWER) drives the sim
   or real robot; demonstrations land as **LeRobotDataset v3** episodes. Cosmos
   (GR00T-Dreams) can synthetically multiply this data from single images + prompts.
3. **Post-train GR00T.** `launch_finetune.py` on the merged real+synthetic dataset with the
   robot's `EmbodimentTag` (or `NEW_EMBODIMENT` + `modality.json`). ≥40 GB VRAM class GPU(s).
4. **Evaluate at scale.** Isaac Lab-Arena runs the checkpoint against task suites
   GPU-parallel (10 h → <1 h class speedups); open-loop MSE for quick regression, closed-loop
   policy-server runs for behavior.
5. **Optimize & deploy.** `export_onnx` + `build_tensorrt_engine.py` produce a
   **per-architecture** TensorRT engine (Thor ≠ Orin ≠ RTX — rebuild each time; Orin is
   limited to DiT-head-only TRT because TRT 10.3 lacks backbone support there ⚠AUDIT).
   The policy runs as a service you wrap in a ROS 2 node, surrounded by Isaac ROS
   perception (cuVSLAM/nvblox) and, below it, the classical ros2_control/fieldbus/MCU
   layers that NVIDIA's stack deliberately does not replace.
6. **Close the loop.** Field recordings (MCAP/rosbag2) feed back into the dataset.

**Integration seams to budget for:** the LeRobot-v2-format expectation in GR00T tooling vs
LeRobotDataset v3 elsewhere (conversion exists but is a seam); no turnkey GR00T ROS 2 node;
Lab-Arena alpha API churn; CUDA/Python matrix differences per platform (Thor CUDA 13.0 /
Orin 12.6+Py3.10 / x86 12.8+Py3.12).

## 5. Hardware-Software Co-Design: GR00T on Thor

- **Official numbers** (⚠AUDIT — corrected against the Isaac-GR00T deployment README):
  full-pipeline TensorRT inference — **Thor 144.9 ms → 93.8 ms**; H100 85.8 → 27.9 ms;
  RTX Pro 5000 (72 GB) 126.4 → 40.5 ms. (An earlier research pass misread this as
  117→92 ms DiT-only on Thor with an RTX 5090 comparator — wrong on all three counts.)
- **Community measurements** [community, dev-forum]: GR00T N1.6 at 41–45 ms → **22–24 Hz**
  on Thor vs 12.5–13 ms → 76–80 Hz on RTX 5090 (π0.5 similar: 23 Hz vs 57 Hz). The official
  and community numbers differ in setup (pipeline scope, precision, input regime) — treat
  them as bounds, not contradictions.
- **What that means for control:** raw batch-1 VLA inference on Thor does **not** hit a 50 Hz
  action rate. The system design answer is (a) **action chunking** — one inference emits an
  execution horizon of multiple action steps, so effective command rate ≫ inference rate;
  (b) the **cascade** — GR00T runs at its natural 5–20 Hz while SONIC/whole-body and
  ros2_control layers run at 50 Hz–1 kHz below it; (c) **MIG (2-way)** to give the policy a
  guaranteed GPU slice under a perception load.
- **Precision headroom:** Thor's headline 2,070 TFLOPS is sparse FP4, but published GR00T
  engines are BF16/FP16 — **no public FP4 GR00T numbers exist** (⚠AUDIT: absent), so the
  marketing-TOPS-to-policy-latency gap is real and currently unquantified.
- **Determinism:** JetPack 7's PREEMPT_RT option covers the CPU side; GPU inference latency
  variance under MIG is the open question NVIDIA hasn't published for Thor [UNVERIFIED].
- **Power/thermal** [community]: sustained AI loads draw ~100–120 W of the 40–130 W
  envelope; reviewers call passive/small-fan cooling inadequate — for a mobile robot this is
  a battery-and-chassis-level design input, a big step from Orin's 15–60 W class.

## 6. Strengths, Limitations & Open Challenges

**Strengths** — only credible end-to-end story (world model → policy → sim → teleop → eval →
edge silicon) from one vendor with wired-together tooling; genuinely open artifacts (weights,
Apache/BSD/OpenMDW licenses, CC-BY datasets); LeRobot integration meets the community where
it already is; Thor's 128 GB unified memory is uniquely sized for on-robot foundation models;
human-egocentric-video pretraining (20,854 h) attacks robotics' data bottleneck at the root.

**Limitations** — total CUDA/TensorRT lock-in with zero CPU fallback; edge inference still
5–8× slower than desktop for the same policy; per-platform engine rebuilds and a
CUDA/Python/ROS-distro compatibility matrix that actively bites; Lab-Arena is alpha; Isaac
Sim demands 16 GB+ VRAM just to open; no safety certification on the robotics SKU; Cosmos 3
is too large for hobbyist GPUs (Nano 16B ≈ 32 GB in BF16 — workstation-class), and the
Predict/Transfer→Cosmos 3 migration is unfinished, leaving two overlapping model families.

**Open challenges** — no published FP4 policy-inference results; GPU latency determinism
under mixed loads unpublished; VLA evaluation methodology (Lab-Arena suites vs real-world
transfer) still unproven; long-horizon "subtask reasoning" claims lack public benchmarks
[UNVERIFIED magnitude]; and the classical robotics layers (ros2_control, fieldbus, safety
PLC) remain entirely the integrator's problem — NVIDIA's stack ends above the 1 kHz line.

## 7. Ecosystem & Openness

The July 6, 2026 Hugging Face partnership is the strategically interesting move: rather than
building a closed Apple-style garden, NVIDIA pushed GR00T and Teleop *into* the community's
own library (LeRobot), published the largest open physical-AI dataset (350K+ trajectories,
57M grasps), and moved Cosmos 3 to a Linux Foundation license (OpenMDW-1.1). Combined with
Isaac Sim's Apache-2.0 core and Lab's BSD-3, the *software* openness is real. The moat is
placed precisely where openness ends: CUDA, TensorRT, NITROS, and Jetson. Meanwhile the
healthcare variant (GR00T-H-N1.7) signals a vertical-fine-tune product pattern to expect in
other domains.

## 8. Strategic Implications & Future Outlook

- **Robotics developers:** the pragmatic posture is *hybrid* — keep the vendor-neutral
  ROS 2 + Gazebo + ros2_control baseline, adopt Isaac components à la carte where GPU
  acceleration pays (cuVSLAM, nvblox, Lab for RL), and treat GR00T post-training via LeRobot
  as the lowest-cost entry into VLA experimentation.
- **Hardware teams:** Thor resets the on-robot compute envelope (128 GB, 100 GbE, PREEMPT_RT,
  2-way MIG) but also the power/thermal/safety budget; the T4000 tier and the unresolved
  FP4 question will decide real BOM economics. Safety architecture stays external
  (IGX or PLC).
- **Enterprises:** expect the three-computer pattern to become the procurement unit; the
  data flywheel (Teleop + Cosmos SDG + field MCAP) is where lasting differentiation and
  lock-in both live. Watch next: Cosmos 3 Edge, Cosmos-3-based GR00T-Dreams, Lab-Arena GA,
  and FP4 VLA benchmarks.

## 9. Hands-on demos (by hardware tier)

**Tier A — this repo's machine (x86, RTX 5070 Ti 16 GB):**
1. **GR00T N1.7 zero-shot inference** (16 GB floor — exactly at spec):
   `uv run python scripts/deployment/standalone_inference_script.py --model-path nvidia/GR00T-N1.7-3B --dataset-path demo_data/droid_sample --embodiment-tag OXE_DROID_RELATIVE_EEF_RELATIVE_JOINT` (github.com/NVIDIA/Isaac-GR00T)
2. **Open-loop eval** of any checkpoint: `gr00t/eval/open_loop_eval.py` (light).
3. **Isaac Sim 6.0 + ROS 2 Jazzy bridge** tutorial, then an **Isaac Lab** locomotion example
   (reduced parallel envs at 16 GB).
4. **Isaac Teleop browser demo** — no headset: `pip install "isaacteleop[cloudxr,retargeters]" --extra-index-url https://pypi.nvidia.com` + the IWER web client.
5. **Isaac Lab-Arena** Franka-lift task via its Docker (`./docker/run_docker.sh`, `-g` for GR00T pkg).
6. *Not* runnable here: Cosmos 3 (Nano needs ~32 GB BF16), GR00T fine-tuning (≥40 GB rec.).

**Tier B — Jetson Orin Nano Super ($249):** Isaac ROS 3.x/Humble GEMs (cuVSLAM, nvblox,
AprilTag), small VLM demos; GR00T only via DiT-head-only TRT at low rates — a learning tier,
not a GR00T deployment tier.

**Tier C — Thor devkit ($3,499):** the full path — JetPack 7 + PREEMPT_RT, 2-way MIG,
Holoscan Sensor Bridge, full-pipeline TensorRT (≈94 ms official GR00T latency), Seeed's
SO-101 arm fine-tune→deploy guide as the best published end-to-end walkthrough.

## Key Takeaways

1. **The platform is real and complete** — Cosmos 3 (May 2026), GR00T N1.7 (Apr 2026),
   Lab-Arena, Teleop, Isaac ROS 4.5, Thor: every layer shipped and publicly downloadable as
   of July 2026, with LeRobot integration since July 6.
2. **Architecture recursion is the signature move:** Cosmos-Reason2 is GR00T N1.7's
   backbone — world model and action model are converging into WAMs.
3. **Edge inference is the bottleneck:** ~94 ms (official) / 22–24 Hz [community] GR00T on
   Thor vs 3× faster on desktop RTX; action chunking + the control cascade make it workable,
   FP4 remains unproven.
4. **Openness is strategic and layered:** open weights/code/datasets, closed CUDA/TensorRT
   underneath — the moat is exactly at the hardware line, and nothing runs on CPU.
5. **Safety is not included:** functional safety lives in IGX Thor's isolated island;
   robotics Jetson deployments still need external safety-rated hardware.
6. **NVIDIA's stack ends above 1 kHz:** joint control, fieldbus, and RTOS firmware remain
   classical engineering — the exact layer an embedded team already owns.
7. **Audit matters:** independent re-verification corrected 2 of 14 headline claims
   (MIG 2-not-7 instances; the real TensorRT benchmark table) — treat all secondhand
   Physical-AI numbers with suspicion.

## References (verified July 11, 2026)

- NVIDIA Newsroom — *NVIDIA Launches Cosmos 3* (May 31, 2026): nvidianews.nvidia.com/news/nvidia-launches-cosmos-3-the-open-frontier-foundation-model-for-physical-ai
- arXiv:2606.02800 — *Cosmos 3: Omnimodal World Models for Physical AI* (Jun 2026)
- Hugging Face — nvidia/Cosmos3-Nano, nvidia/Cosmos3-Super model cards
- Hugging Face blog — *GR00T N1.7* (Apr 17, 2026): huggingface.co/blog/nvidia/gr00t-n1-7
- GitHub — NVIDIA/Isaac-GR00T (+ `scripts/deployment/README.md` TensorRT benchmarks)
- Hugging Face — nvidia/GR00T-N1.7-3B; nvidia/GR00T-H-N1.7; NVlabs/GR00T-WholeBodyControl
- NVIDIA blog — *Hugging Face LeRobot × NVIDIA* (Jul 6, 2026): blogs.nvidia.com/blog/hugging-face-lerobot-models-frameworks-open-robotics/
- Hugging Face blog — *LeRobotDataset v3* : huggingface.co/blog/lerobot-datasets-v3
- GitHub — isaac-sim/IsaacLab-Arena; NVIDIA dev blog *Simplify Generalist Robot Policy Evaluation…*
- GitHub — NVIDIA/IsaacTeleop; docs nvidia.github.io/IsaacTeleop
- NVIDIA dev blog — *Introducing NVIDIA Jetson Thor* ; Jetson Thor product page (T5000/T4000)
- NVIDIA dev blog — *JetPack 7.2 memory efficiency / MIG on Thor* (2-instance partitioning)
- NVIDIA dev blog — *NVIDIA IGX Thor* (Functional Safety Island, IEC 61508 SIL 3 / ISO 26262 ASIL-D)
- Isaac ROS releases: nvidia-isaac-ros.github.io/releases (4.5.0, Jul 6, 2026)
- Hugging Face — nvidia/PhysicalAI-Robotics-NuRec (CC-BY-4.0)
- [community] NVIDIA dev forums — Thor/RTX real-time VLA inference thread; ThinkRobotics Thor devkit review
